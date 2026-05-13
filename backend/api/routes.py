from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
import os
import json
from engine.analyzer import AudioAnalyzer
from engine.renderer import FrameRenderer
from engine.preset_schema import PresetSchema
from engine.fixture_mapping import (
    PixelOrigin,
    PixelOrdering,
    PixelMapping,
    FixtureInstance,
    PointOfInterest,
    MappingConfig,
    FixtureMapper,
    DMXExporter,
    ExportManifest,
)
from pydantic import ValidationError
import numpy as np

router = APIRouter()

# Global State
CURRENT_SONG = None
CURRENT_CANVAS = None
JOB_STATUS = {}

# 01.B4: Supported versions
SUPPORTED_RENDER_SCHEMA = "v1"
SUPPORTED_PRESET_VERSIONS = ["1.0.0"]


def find_canvas_for_song(song_id: str):
    canvas_dir = "/data/canvas"
    if not os.path.exists(canvas_dir):
        return None

    candidates = [
        entry for entry in os.listdir(canvas_dir)
        if entry.startswith(f"{song_id}.") and entry.endswith(".json")
    ]
    if not candidates:
        return None

    candidates.sort(
        key=lambda entry: os.path.getmtime(os.path.join(canvas_dir, entry)),
        reverse=True,
    )
    return candidates[0]

class GenerateRequest(BaseModel):
    song_id: str
    preset_id: str = "undersea_pulse_01"
    preset_version: str = "1.0.0"
    seed: int
    params: dict = {}
    canvas_name: str = "default"  # Epic 08.B8: Canvas naming contract

def run_generation(job_id: str, request: GenerateRequest):
    global CURRENT_SONG, CURRENT_CANVAS
    # Ensure job status shape remains a dict created by the API
    if job_id not in JOB_STATUS or not isinstance(JOB_STATUS[job_id], dict):
        JOB_STATUS[job_id] = {"status": "GENERATING"}
    else:
        JOB_STATUS[job_id]["status"] = "GENERATING"
    try:
        # Epic 08.B6: Mark analysis phase started with status text
        if isinstance(JOB_STATUS.get(job_id), dict):
            JOB_STATUS[job_id]["phase"] = "analysis"
            JOB_STATUS[job_id]["phase_label"] = "Analyzing audio..."
            JOB_STATUS[job_id]["progress"] = 0
            JOB_STATUS[job_id]["current_frame"] = 0
            JOB_STATUS[job_id]["total_frames"] = 0
        song_path = f"/data/songs/{request.song_id}.mp3"
        if not os.path.exists(song_path):
            print(f"Error: Song {song_path} not found")
            if isinstance(JOB_STATUS.get(job_id), dict):
                JOB_STATUS[job_id]["status"] = "FAILED"
            else:
                JOB_STATUS[job_id] = "FAILED"
            return
            
        preset_path = f"/data/presets/{request.preset_id}.json"
        if not os.path.exists(preset_path):
            print(f"Error: Preset {preset_path} not found")
            if isinstance(JOB_STATUS.get(job_id), dict):
                JOB_STATUS[job_id]["status"] = "FAILED"
            else:
                JOB_STATUS[job_id] = "FAILED"
            return
            
        with open(preset_path, 'r') as f:
            preset_data = json.load(f)
            
        try:
            preset = PresetSchema(**preset_data)
            if preset.version != request.preset_version:
                print(f"Error: Preset version mismatch")
                if isinstance(JOB_STATUS.get(job_id), dict):
                    JOB_STATUS[job_id]["status"] = "FAILED"
                else:
                    JOB_STATUS[job_id] = "FAILED"
                return
        except ValidationError as e:
            print(f"Preset Validation Error: {e}")
            if isinstance(JOB_STATUS.get(job_id), dict):
                JOB_STATUS[job_id]["status"] = "FAILED"
            else:
                JOB_STATUS[job_id] = "FAILED"
            return
            
        # Instantiate renderer (this may perform analysis during init)
        renderer = FrameRenderer(
            song_path=song_path,
            seed=request.seed,
            preset_id=request.preset_id,
            preset_version=request.preset_version,
            params=request.params
        )

        # Analysis completed by renderer init; capture diagnostics
        total_frames = int(renderer.analysis_data['duration'] * renderer.fps)
        if isinstance(JOB_STATUS.get(job_id), dict):
            JOB_STATUS[job_id]["phase"] = "render"
            JOB_STATUS[job_id]["phase_label"] = "Rendering frames..."
            JOB_STATUS[job_id]["total_frames"] = total_frames
            JOB_STATUS[job_id]["analysis_diagnostics"] = renderer.analysis_data.get('diagnostics', {})

        # Epic 08.B7: Progress callback updates at least every 200 frames
        frame_count = 0
        def progress_cb(phase, current, total):
            nonlocal frame_count
            if isinstance(JOB_STATUS.get(job_id), dict):
                JOB_STATUS[job_id]["phase"] = phase
                JOB_STATUS[job_id]["current_frame"] = current
                JOB_STATUS[job_id]["total_frames"] = total
                try:
                    JOB_STATUS[job_id]["progress"] = int((current / total) * 100) if total and total > 0 else 0
                except Exception:
                    JOB_STATUS[job_id]["progress"] = 0
                frame_count = current

        # Epic 08.B8: Use canvas_name in export path (format: {song_name}.{canvas_name}.json)
        output_path = renderer.export(progress_callback=progress_cb, canvas_name=request.canvas_name)
        CURRENT_SONG = request.song_id
        CURRENT_CANVAS = os.path.basename(output_path)
        
        print(f"Generation complete for {request.song_id}")
        if isinstance(JOB_STATUS.get(job_id), dict):
            JOB_STATUS[job_id]["status"] = "COMPLETED"
            JOB_STATUS[job_id]["canvas"] = CURRENT_CANVAS
            JOB_STATUS[job_id]["render_diagnostics"] = getattr(renderer, 'render_diagnostics', {})
        else:
            JOB_STATUS[job_id] = "COMPLETED"
    except Exception as e:
        print(f"Generation failed: {e}")
        if isinstance(JOB_STATUS.get(job_id), dict):
            JOB_STATUS[job_id]["status"] = "FAILED"
        else:
            JOB_STATUS[job_id] = "FAILED"

@router.post("/load_song/{song_id}")
async def load_song(song_id: str):
    global CURRENT_SONG, CURRENT_CANVAS
    song_path = f"/data/songs/{song_id}.mp3"
    if not os.path.exists(song_path):
        raise HTTPException(status_code=404, detail=f"Song {song_id}.mp3 not found")
        
    CURRENT_SONG = song_id
    if not CURRENT_CANVAS or not CURRENT_CANVAS.startswith(f"{song_id}."):
        CURRENT_CANVAS = find_canvas_for_song(song_id)
    
    return {
        "current_song": CURRENT_SONG,
        "current_canvas": CURRENT_CANVAS,
        "message": f"Loaded {song_id}"
    }

@router.get("/current_state")
async def get_current_state():
    return {
        "current_song": CURRENT_SONG,
        "current_canvas": CURRENT_CANVAS
    }

@router.post("/generate")
async def generate_show(request: GenerateRequest, background_tasks: BackgroundTasks):
    # 01.B4: Backend compatibility checks (Reject early)
    song_path = f"/data/songs/{request.song_id}.mp3"
    if not os.path.exists(song_path):
        raise HTTPException(status_code=404, detail=f"Song {request.song_id}.mp3 not found in data/songs/")
        
    preset_path = f"/data/presets/{request.preset_id}.json"
    if not os.path.exists(preset_path):
        raise HTTPException(status_code=404, detail=f"Preset {request.preset_id} not found")
    
    with open(preset_path, 'r') as f:
        preset_data = json.load(f)
    
    try:
        preset = PresetSchema(**preset_data)
        if preset.version not in SUPPORTED_PRESET_VERSIONS:
             raise HTTPException(status_code=400, detail=f"Unsupported preset version: {preset.version}")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid preset schema: {e}")

    job_id = f"{request.song_id}_{request.seed}"
    
    # 08.B1, 08.B9: Generation status payload with phase, progress, and canvas naming
    JOB_STATUS[job_id] = {
        "status": "PENDING",
        "song_id": request.song_id,
        "preset_id": request.preset_id,
        "seed": request.seed,
        "canvas_name": request.canvas_name,
        "progress": 0,
        "phase": "pending",
        "phase_label": "Queued...",
        "current_frame": 0,
        "total_frames": 0
    }
    
    background_tasks.add_task(run_generation, job_id, request)
    return {"message": "Generation started in background", "job": job_id}

@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    job_status = JOB_STATUS.get(job_id, "UNKNOWN")
    if isinstance(job_status, dict):
        return job_status
    return {"status": job_status}

@router.get("/songs")
async def list_songs():
    songs_dir = "/data/songs"
    if not os.path.exists(songs_dir):
        return []
    return [f.replace(".mp3", "") for f in os.listdir(songs_dir) if f.endswith(".mp3")]

@router.get("/canvas")
async def list_canvas_files():
    canvas_dir = "/data/canvas"
    if not os.path.exists(canvas_dir):
        return []
    return [f for f in os.listdir(canvas_dir) if f.endswith(".json")]

@router.get("/presets")
async def list_presets():
    presets_dir = "/data/presets"
    if not os.path.exists(presets_dir):
        return []

    presets = []
    for entry in sorted(os.listdir(presets_dir)):
        if not entry.endswith(".json"):
            continue

        preset_path = os.path.join(presets_dir, entry)
        with open(preset_path, 'r') as handle:
            preset_data = json.load(handle)

        try:
            presets.append(PresetSchema(**preset_data).model_dump())
        except ValidationError:
            continue

    return presets

@router.get("/canvas/{canvas_id}/metadata")
async def get_canvas_metadata(canvas_id: str):
    # 08.B2: Metadata payload support
    canvas_path = f"/data/canvas/{canvas_id}"
    if not os.path.exists(canvas_path):
         raise HTTPException(status_code=404, detail="Canvas not found")
    
    with open(canvas_path, 'r') as f:
        data = json.load(f)
    
    # Strip actual frame data to return only metadata
    return {k: v for k, v in data.items() if k != "frames"}


# Epic 10: Fixture Mapping Endpoints

@router.get("/fixtures")
async def list_fixtures():
    """List all available fixtures (Epic 10.B2a)."""
    fixtures_path = "/data/fixtures/fixtures.json"
    
    if not os.path.exists(fixtures_path):
        return {"fixtures": []}
    
    try:
        with open(fixtures_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load fixtures: {e}")


@router.get("/pois")
async def list_points_of_interest():
    """List all points of interest (Epic 10.B2b)."""
    pois_path = "/data/fixtures/pois.json"
    
    if not os.path.exists(pois_path):
        return {"points_of_interest": []}
    
    try:
        with open(pois_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load POIs: {e}")


@router.get("/mapping/validate")
async def validate_mapping():
    """
    Validate current fixture mapping configuration (Epic 10.B2).
    
    Returns:
        Validation results with errors, warnings, and coverage metrics
    """
    try:
        # Load fixtures and POIs
        fixtures_path = "/data/fixtures/fixtures.json"
        pois_path = "/data/fixtures/pois.json"
        
        fixtures_data = {}
        pois_data = {}
        
        if os.path.exists(fixtures_path):
            with open(fixtures_path, 'r') as f:
                fixtures_data = json.load(f)
        
        if os.path.exists(pois_path):
            with open(pois_path, 'r') as f:
                pois_data = json.load(f)
        
        # Create pixel mapping (default: top_left, row_major, linear)
        pixel_mapping = PixelMapping(
            canvas_width=100,
            canvas_height=50,
            origin=PixelOrigin.TOP_LEFT,
            row_major=True,
            ordering=PixelOrdering.LINEAR,
        )
        
        # Convert fixture data to instances
        fixture_instances = []
        if "fixtures" in fixtures_data:
            for fixture_dict in fixtures_data["fixtures"]:
                try:
                    fixture_instances.append(FixtureInstance(**fixture_dict))
                except Exception:
                    pass
        
        # Convert POI data to instances
        poi_instances = []
        if "points_of_interest" in pois_data:
            for poi_dict in pois_data["points_of_interest"]:
                try:
                    poi_instances.append(PointOfInterest(**poi_dict))
                except Exception:
                    pass
        
        # Create mapping config
        mapping_config = MappingConfig(
            canvas_mapping=pixel_mapping,
            fixtures=fixture_instances,
            points_of_interest=poi_instances,
        )
        
        # Validate
        mapper = FixtureMapper(mapping_config)
        validation = mapper.validate_mapping()
        
        return {
            "valid": validation.valid,
            "errors": validation.errors,
            "warnings": validation.warnings,
            "coverage": validation.coverage,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {e}")


@router.post("/export/dmx")
async def export_dmx(render_id: str, gamma: float = 2.2, brightness_limit: float = 1.0):
    """
    Export render to DMX format with gamma correction and brightness limiting (Epic 10.B5-B7).
    
    Args:
        render_id: Render ID to export
        gamma: Gamma correction exponent (default 2.2 for sRGB)
        brightness_limit: Brightness limit 0..1
        
    Returns:
        DMX frame data and metadata
    """
    try:
        # Load canvas metadata
        canvas_path = f"/data/canvas/{render_id}.json"
        if not os.path.exists(canvas_path):
            raise HTTPException(status_code=404, detail=f"Canvas {render_id} not found")
        
        with open(canvas_path, 'r') as f:
            canvas_data = json.load(f)
        
        # Load fixtures
        fixtures_path = "/data/fixtures/fixtures.json"
        fixtures_data = {}
        if os.path.exists(fixtures_path):
            with open(fixtures_path, 'r') as f:
                fixtures_data = json.load(f)
        
        # Create pixel mapping
        pixel_mapping = PixelMapping(
            canvas_width=100,
            canvas_height=50,
            origin=PixelOrigin.TOP_LEFT,
            row_major=True,
            ordering=PixelOrdering.LINEAR,
        )
        
        # Convert fixtures
        fixture_instances = []
        if "fixtures" in fixtures_data:
            for fixture_dict in fixtures_data["fixtures"]:
                try:
                    fixture_instances.append(FixtureInstance(**fixture_dict))
                except Exception:
                    pass
        
        # Create mapping config and exporter
        mapping_config = MappingConfig(
            canvas_mapping=pixel_mapping,
            fixtures=fixture_instances,
        )
        
        export_manifest = ExportManifest(
            render_id=render_id,
            mapping_config=mapping_config,
            gamma_value=gamma,
            brightness_limit=brightness_limit,
            export_format="dmx",
        )
        
        exporter = DMXExporter(export_manifest)
        
        # Get canvas frame data (use first frame for demo)
        # In production, would get from rendered frame
        sample_pixels = np.zeros((100 * 50, 3), dtype=np.uint8)
        
        # Export
        dmx_frame = exporter.export_dmx_frame(sample_pixels)
        
        # Validate
        validation = exporter.validate_export()
        
        return {
            "dmx_frame": dmx_frame,
            "validation": {
                "valid": validation.valid,
                "errors": validation.errors,
                "warnings": validation.warnings,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DMX export error: {e}")
