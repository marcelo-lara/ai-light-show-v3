try:
    from pydantic import BaseModel, Field
except Exception:
    # Minimal fallback for tests without pydantic
    def Field(default_factory=None):
        return default_factory() if default_factory else None
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def dict(self):
            return self.__dict__

from typing import List, Dict, Any, Optional
import math
import random

class TransitionSchema(BaseModel):
    type: str = "hard_cut" # "hard_cut", "crossfade", "beat_flash"
    duration: float = 0.0
    params: Dict[str, Any] = Field(default_factory=dict)
    
class SceneSchema(BaseModel):
    start: float = 0.0
    end: float = 0.0
    preset_id: str = ""
    params: Dict[str, Any] = Field(default_factory=dict)
    seed: int = 0
    intensity: float = 1.0
    transition: Optional[TransitionSchema] = None
    
class TimelineSchema(BaseModel):
    scenes: List[SceneSchema] = Field(default_factory=list)

class TimelineDirector:
    def __init__(self, analysis_data: dict, available_presets: List[str] = None):
        self.analysis_data = self.analysis_data = analysis_data
        self.available_presets = available_presets or ["undersea_pulse_01", "all_layers_test", "mod_test"]
        
    def generate_auto_timeline(self, seed: int = 42) -> TimelineSchema:
        random.seed(seed)
        structure = self.analysis_data.get('structure', {})
        duration = self.analysis_data.get('duration', 0.0)
        
        sections = structure.get('section_candidates', [])
        
        # If no sections, fallback to phrases or just one big scene
        if not sections or len(sections) == 0:
            return TimelineSchema(scenes=[
                SceneSchema(start=0.0, end=duration, preset_id=random.choice(self.available_presets), seed=seed)
            ])
            
        scenes = []
        for i, sec_start in enumerate(sections):
            end = sections[i+1] if i + 1 < len(sections) else duration
            preset = random.choice(self.available_presets)
            # pseudo intensity based on section index
            intensity = 0.5 + (i % 3) * 0.25
            
            scenes.append(SceneSchema(
                start=sec_start,
                end=end,
                preset_id=preset,
                seed=seed + i,
                intensity=intensity,
                transition=TransitionSchema(type="crossfade", duration=2.0) if i > 0 else None
            ))
            
        return TimelineSchema(scenes=scenes)
