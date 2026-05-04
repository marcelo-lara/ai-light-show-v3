from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
import os
from engine.analyzer import AudioAnalyzer
from engine.renderer import FrameRenderer

router = APIRouter()

class GenerateRequest(BaseModel):
    song_name: str
    show_id: str
    beat_sensitivity: int = 50
    wave_speed: int = 10
    wave_height: int = 5
    size_multiplier: int = 50

JOB_STATUS = {}

def run_generation(job_id: str, song_name: str, show_id: str, params: dict):
    JOB_STATUS[job_id] = "GENERATING"
    try:
        song_path = f"/data/songs/{song_name}.mp3"
        if not os.path.exists(song_path):
            print(f"Error: Song {song_path} not found")
            JOB_STATUS[job_id] = "FAILED"
            return
            
        renderer = FrameRenderer(song_path, params=params)
        renderer.export(show_id=show_id)
        
        print(f"Generation complete for {song_name}.{show_id}")
        JOB_STATUS[job_id] = "COMPLETED"
    except Exception as e:
        print(f"Generation failed: {e}")
        JOB_STATUS[job_id] = "FAILED"

@router.post("/generate")
async def generate_show(request: GenerateRequest, background_tasks: BackgroundTasks):
    song_path = f"/data/songs/{request.song_name}.mp3"
    if not os.path.exists(song_path):
        raise HTTPException(status_code=404, detail=f"Song {request.song_name}.mp3 not found in data/songs/")
        
    job_id = f"{request.song_name}.{request.show_id}"
    params = {
        "beat_sensitivity": request.beat_sensitivity,
        "wave_speed": request.wave_speed,
        "wave_height": request.wave_height,
        "size_multiplier": request.size_multiplier
    }
    
    JOB_STATUS[job_id] = "PENDING"
    background_tasks.add_task(run_generation, job_id, request.song_name, request.show_id, params)
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
