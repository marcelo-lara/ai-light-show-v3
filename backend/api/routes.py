from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
import os
import json
from engine.analyzer import AudioAnalyzer
from engine.renderer import FrameRenderer
from engine.preset_schema import PresetSchema
from pydantic import ValidationError

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

def run_generation(job_id: str, request: GenerateRequest):
    global CURRENT_SONG, CURRENT_CANVAS
    # Ensure job status shape remains a dict created by the API
    if job_id not in JOB_STATUS or not isinstance(JOB_STATUS[job_id], dict):
        JOB_STATUS[job_id] = {"status": "GENERATING"}
    else:
        JOB_STATUS[job_id]["status"] = "GENERATING"
    try:
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
            
        renderer = FrameRenderer(
            song_path=song_path,
            seed=request.seed,
            preset_id=request.preset_id,
            preset_version=request.preset_version,
            params=request.params
        )
        
        output_path = renderer.export()
        CURRENT_SONG = request.song_id
        CURRENT_CANVAS = os.path.basename(output_path)
        
        print(f"Generation complete for {request.song_id}")
        if isinstance(JOB_STATUS.get(job_id), dict):
            JOB_STATUS[job_id]["status"] = "COMPLETED"
            JOB_STATUS[job_id]["canvas"] = CURRENT_CANVAS
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
    
    # 08.B1: Generation status payload with details
    JOB_STATUS[job_id] = {
        "status": "PENDING",
        "song_id": request.song_id,
        "preset_id": request.preset_id,
        "seed": request.seed,
        "progress": 0
    }
    
    background_tasks.add_task(run_generation, job_id, request)
    return {"message": "Generation started in background", "job": job_id}

@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    return {"status": JOB_STATUS.get(job_id, "UNKNOWN")}

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
