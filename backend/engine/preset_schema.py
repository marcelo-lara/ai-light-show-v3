try:
    from pydantic import BaseModel, Field, validator
except Exception:
    # Minimal fallback to avoid hard dependency in test environments
    from typing import Any
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def dict(self):
            return self.__dict__
    def Field(default_factory=None):
        return default_factory() if default_factory else None
    def validator(name):
        def _decorator(f):
            return f
        return _decorator

from typing import List, Dict, Any, Optional

class ParameterSchema(BaseModel):
    id: str = ""
    label: str = ""
    type: str = "int"
    default: Any = None
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    options: Optional[List[str]] = None
    ui_group: str = "General"

class LayerConfig(BaseModel):
    id: str = ""
    layer_type: str = ""
    blend_mode: str = "max"
    params: Dict[str, Any] = Field(default_factory=dict)

class PaletteSchema(BaseModel):
    primary: str = "#000000"
    secondary: str = "#000000"
    accent: str = "#000000"
    background: str = "#000000"

class ModulatorConfig(BaseModel):
    id: str = ""
    type: str = "lfo"
    params: Dict[str, Any] = Field(default_factory=dict)

class PresetSchema(BaseModel):
    preset_id: str = ""
    version: str = "1.0"
    name: str = ""
    description: str = ""
    tags: List[str] = Field(default_factory=list)
    parameters: List[ParameterSchema] = Field(default_factory=list)
    palette: Optional[PaletteSchema] = None
    blend_mode: str = "max"
    modulators: List[ModulatorConfig] = Field(default_factory=list)
    layers: List[LayerConfig] = Field(default_factory=list)

    @validator("version")
    def version_must_be_v1(cls, v):
        if not str(v).startswith("1."):
            raise ValueError("Unsupported preset version")
        return v
