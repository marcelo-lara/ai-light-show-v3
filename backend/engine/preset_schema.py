from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Literal

class ParameterSchema(BaseModel):
    id: str
    label: str
    type: Literal["int", "float", "boolean", "color", "select"]
    default: Any
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    options: Optional[List[str]] = None
    ui_group: str = "General"

class LayerConfig(BaseModel):
    id: str
    layer_type: str
    blend_mode: str = "max"
    params: Dict[str, Any] = Field(default_factory=dict)

class PaletteSchema(BaseModel):
    primary: str
    secondary: str
    accent: str
    background: str

class ModulatorConfig(BaseModel):
    id: str
    type: Literal["lfo", "envelope"]
    params: Dict[str, Any] = Field(default_factory=dict)

class PresetSchema(BaseModel):
    preset_id: str
    version: str
    name: str
    description: str
    tags: List[str]
    parameters: List[ParameterSchema] = Field(default_factory=list)
    palette: Optional[PaletteSchema] = None
    blend_mode: str = "max"
    modulators: List[ModulatorConfig] = Field(default_factory=list)
    layers: List[LayerConfig] = Field(default_factory=list)

    @validator("version")
    def version_must_be_v1(cls, v):
        if not v.startswith("1."):
            raise ValueError("Unsupported preset version")
        return v
