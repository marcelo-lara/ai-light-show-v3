"""
Fixture mapping and DMX export for lighting control.
Epic 10.B1, 10.B2, 10.B3, 10.B4, 10.B5, 10.B6, 10.B7
"""

import numpy as np
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum


class PixelOrigin(str, Enum):
    """Canonical pixel order origin (Epic 10.B1)."""
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"


class PixelOrdering(str, Enum):
    """Canonical pixel ordering (Epic 10.B1)."""
    LINEAR = "linear"  # Sequential left-to-right, top-to-bottom
    SERPENTINE = "serpentine"  # Snake pattern: L-R, R-L, L-R...
    CUSTOM = "custom"  # Custom ordering provided


@dataclass
class PixelMapping:
    """
    Canonical pixel coordinate to flat index mapping (Epic 10.B1).
    
    Default: origin=TOP_LEFT, row_major=True, ordering=LINEAR
    This means: pixels indexed 0..N-1 go left-to-right, top-to-bottom
    Pixel at canvas position (x, y) = (0..1, 0..1) normalized
    Maps to flat index for canvas_width x canvas_height grid
    """
    canvas_width: int
    canvas_height: int
    origin: PixelOrigin = PixelOrigin.TOP_LEFT
    row_major: bool = True
    ordering: PixelOrdering = PixelOrdering.LINEAR
    custom_order: Optional[List[int]] = None  # If ordering=CUSTOM, specify index map


@dataclass
class FixtureInstance:
    """
    Fixture definition with DMX address and canvas location (Epic 10.B2a).
    """
    fixture_type_id: str  # e.g. "par64", "moving_head", "wash"
    canvas_location: Dict[str, float]  # {"x": 0..1, "y": 0..1} - normalized canvas position
    dmx_address: int  # 1-512 for DMX universe 1
    dmx_footprint: int  # Number of DMX channels used (e.g. 3 for RGB, 16 for moving head)
    pan_range: Tuple[float, float] = (0, 360)  # Degrees
    tilt_range: Tuple[float, float] = (0, 90)  # Degrees
    metadata: Dict = field(default_factory=dict)


@dataclass
class PointOfInterest:
    """
    Point of interest on canvas with associated fixtures (Epic 10.B2b).
    """
    poi_id: str
    canvas_location: Dict[str, float]  # {"x": 0..1, "y": 0..1}
    associated_fixtures: List[str]  # List of fixture_type_id
    per_fixture_calibration: Dict[str, Dict] = field(default_factory=dict)  # fixture_id -> calibration data


@dataclass
class MappingConfig:
    """Canvas to fixture mapping configuration (Epic 10.B2)."""
    canvas_mapping: PixelMapping
    fixtures: List[FixtureInstance]
    points_of_interest: List[PointOfInterest] = field(default_factory=list)
    fixture_order: List[str] = field(default_factory=list)  # Fixture rendering order


@dataclass
class ExportManifest:
    """
    Export configuration for DMX/lighting (Epic 10.B5, 10.B6, 10.B7).
    """
    render_id: str
    mapping_config: MappingConfig
    gamma_value: float = 2.2  # Standard: 2.2 for sRGB (Epic 10.B6)
    brightness_limit: float = 1.0  # 0..1, cap output to percentage (Epic 10.B7)
    export_format: str = "dmx"  # "dmx", "artnet", "sACN"


@dataclass
class MappingValidation:
    """Validation results for fixture mapping."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    coverage: Dict[str, float] = field(default_factory=dict)  # {"pixels_mapped": 0.95, ...}


class CanvasPixelMapper:
    """Maps canvas coordinates to flat pixel indices (Epic 10.B1, 10.B3-B4)."""

    def __init__(self, pixel_mapping: PixelMapping):
        self.pixel_mapping = pixel_mapping

    def normalized_to_pixel_index(self, x: float, y: float) -> int:
        """
        Convert normalized canvas coordinates (0..1, 0..1) to flat pixel index.
        
        Args:
            x: 0..1 (left to right)
            y: 0..1 (top to bottom by default)
            
        Returns:
            Flat index 0..canvas_width*canvas_height-1
        """
        # Clamp to valid range
        x = max(0, min(1, x))
        y = max(0, min(1, y))

        # Convert to pixel coordinates
        px = int(x * self.pixel_mapping.canvas_width)
        py = int(y * self.pixel_mapping.canvas_height)

        # Ensure boundaries
        px = min(px, self.pixel_mapping.canvas_width - 1)
        py = min(py, self.pixel_mapping.canvas_height - 1)

        # Apply origin transform
        if self.pixel_mapping.origin == PixelOrigin.TOP_RIGHT:
            px = self.pixel_mapping.canvas_width - 1 - px
        elif self.pixel_mapping.origin == PixelOrigin.BOTTOM_LEFT:
            py = self.pixel_mapping.canvas_height - 1 - py
        elif self.pixel_mapping.origin == PixelOrigin.BOTTOM_RIGHT:
            px = self.pixel_mapping.canvas_width - 1 - px
            py = self.pixel_mapping.canvas_height - 1 - py

        # Apply ordering (Epic 10.B3-B4)
        if self.pixel_mapping.ordering == PixelOrdering.LINEAR:
            # Row-major: top-to-bottom, left-to-right
            if self.pixel_mapping.row_major:
                index = py * self.pixel_mapping.canvas_width + px
            else:
                # Column-major: left-to-right, top-to-bottom
                index = px * self.pixel_mapping.canvas_height + py
        elif self.pixel_mapping.ordering == PixelOrdering.SERPENTINE:
            # Snake pattern: alternate row direction
            if self.pixel_mapping.row_major:
                if py % 2 == 0:
                    # Even rows: L-to-R
                    index = py * self.pixel_mapping.canvas_width + px
                else:
                    # Odd rows: R-to-L
                    index = py * self.pixel_mapping.canvas_width + (
                        self.pixel_mapping.canvas_width - 1 - px
                    )
            else:
                # Column serpentine
                if px % 2 == 0:
                    index = px * self.pixel_mapping.canvas_height + py
                else:
                    index = px * self.pixel_mapping.canvas_height + (
                        self.pixel_mapping.canvas_height - 1 - py
                    )
        elif self.pixel_mapping.ordering == PixelOrdering.CUSTOM:
            if not self.pixel_mapping.custom_order:
                index = py * self.pixel_mapping.canvas_width + px
            else:
                linear_index = py * self.pixel_mapping.canvas_width + px
                if linear_index < len(self.pixel_mapping.custom_order):
                    index = self.pixel_mapping.custom_order[linear_index]
                else:
                    index = linear_index
        else:
            index = py * self.pixel_mapping.canvas_width + px

        return index

    def pixel_index_to_normalized(self, index: int) -> Tuple[float, float]:
        """Reverse mapping: flat index to normalized coordinates."""
        w = self.pixel_mapping.canvas_width
        h = self.pixel_mapping.canvas_height

        # Undo ordering to get pixel coordinates
        if self.pixel_mapping.ordering == PixelOrdering.LINEAR:
            if self.pixel_mapping.row_major:
                py = index // w
                px = index % w
            else:
                px = index // h
                py = index % h
        elif self.pixel_mapping.ordering == PixelOrdering.SERPENTINE:
            if self.pixel_mapping.row_major:
                py = index // w
                py_offset = index % w
                if py % 2 == 0:
                    px = py_offset
                else:
                    px = w - 1 - py_offset
            else:
                px = index // h
                px_offset = index % h
                if px % 2 == 0:
                    py = px_offset
                else:
                    py = h - 1 - px_offset
        else:
            if self.pixel_mapping.row_major:
                py = index // w
                px = index % w
            else:
                px = index // h
                py = index % h

        # Undo origin transform
        if self.pixel_mapping.origin == PixelOrigin.TOP_RIGHT:
            px = w - 1 - px
        elif self.pixel_mapping.origin == PixelOrigin.BOTTOM_LEFT:
            py = h - 1 - py
        elif self.pixel_mapping.origin == PixelOrigin.BOTTOM_RIGHT:
            px = w - 1 - px
            py = h - 1 - py

        # Convert to normalized
        x = px / w if w > 0 else 0
        y = py / h if h > 0 else 0

        return (x, y)


class FixtureMapper:
    """Maps fixtures to canvas locations (Epic 10.B2)."""

    def __init__(self, mapping_config: MappingConfig):
        self.mapping_config = mapping_config
        self.canvas_mapper = CanvasPixelMapper(mapping_config.canvas_mapping)

    def get_fixture_pixel_range(self, fixture: FixtureInstance) -> Tuple[int, int]:
        """Get pixel range for a fixture on canvas."""
        x = fixture.canvas_location.get("x", 0)
        y = fixture.canvas_location.get("y", 0)
        pixel_idx = self.canvas_mapper.normalized_to_pixel_index(x, y)
        return (pixel_idx, pixel_idx + 1)

    def validate_mapping(self) -> MappingValidation:
        """
        Validate fixture mapping for errors and coverage (Epic 10.B2).
        
        Returns:
            MappingValidation with error/warning list and coverage metrics
        """
        errors = []
        warnings = []
        coverage = {}

        # Check fixture addresses
        used_addresses = set()
        for fixture in self.mapping_config.fixtures:
            if fixture.dmx_address < 1 or fixture.dmx_address > 512:
                errors.append(
                    f"Fixture {fixture.fixture_type_id}: Invalid DMX address {fixture.dmx_address} (must be 1-512)"
                )
            if fixture.dmx_address + fixture.dmx_footprint - 1 > 512:
                errors.append(
                    f"Fixture {fixture.fixture_type_id}: DMX footprint exceeds universe (address {fixture.dmx_address} + {fixture.dmx_footprint})"
                )

            # Check for overlapping addresses
            for addr in range(fixture.dmx_address, fixture.dmx_address + fixture.dmx_footprint):
                if addr in used_addresses:
                    warnings.append(f"Fixture {fixture.fixture_type_id}: DMX address overlap at channel {addr}")
                used_addresses.add(addr)

        # Check canvas locations
        total_pixels = (
            self.mapping_config.canvas_mapping.canvas_width
            * self.mapping_config.canvas_mapping.canvas_height
        )
        mapped_pixels = len(self.mapping_config.fixtures)
        coverage["fixtures"] = mapped_pixels
        coverage["total_pixels"] = total_pixels
        coverage["coverage_percent"] = (mapped_pixels / total_pixels * 100) if total_pixels > 0 else 0

        # Check for duplicate POI IDs
        poi_ids = [poi.poi_id for poi in self.mapping_config.points_of_interest]
        if len(poi_ids) != len(set(poi_ids)):
            warnings.append("Duplicate POI IDs detected")

        # Check fixture order references
        fixture_ids = {f.fixture_type_id for f in self.mapping_config.fixtures}
        for fid in self.mapping_config.fixture_order:
            if fid not in fixture_ids:
                warnings.append(f"Fixture order references unknown fixture: {fid}")

        return MappingValidation(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            coverage=coverage,
        )


class DMXExporter:
    """
    Exports canvas render data to DMX format (Epic 10.B5-B7).
    """

    def __init__(self, export_manifest: ExportManifest):
        self.manifest = export_manifest
        self.mapper = FixtureMapper(export_manifest.mapping_config)

    def apply_gamma_correction(self, value: float, gamma: float = None) -> int:
        """
        Apply gamma correction to normalize brightness (Epic 10.B6).
        
        Args:
            value: 0..1 float value
            gamma: Gamma exponent (default from manifest)
            
        Returns:
            0..255 uint8 value after gamma correction
        """
        if gamma is None:
            gamma = self.manifest.gamma_value

        # Gamma encode: out = in^(1/gamma)
        corrected = pow(max(0, min(1, value)), 1.0 / gamma)
        return int(corrected * 255)

    def apply_brightness_limit(self, rgb: np.ndarray) -> np.ndarray:
        """
        Apply brightness limiting (Epic 10.B7).
        
        Args:
            rgb: (N, 3) array of RGB values 0..255
            
        Returns:
            Brightness-limited RGB values
        """
        if self.manifest.brightness_limit >= 1.0:
            return rgb

        # Scale all channels by brightness limit
        limited = (rgb * self.manifest.brightness_limit).astype(np.uint8)
        return limited

    def export_dmx_frame(self, canvas_pixels: np.ndarray) -> Dict[str, object]:
        """
        Convert canvas frame to DMX data.
        
        Args:
            canvas_pixels: (H*W, 3) RGB array 0..255
            
        Returns:
            DMX frame with metadata and channel data
        """
        # Create DMX universe (512 channels, 0-indexed)
        dmx_data = np.zeros(512, dtype=np.uint8)

        # Map fixtures
        for fixture in self.manifest.mapping_config.fixtures:
            pixel_start, pixel_end = self.mapper.get_fixture_pixel_range(fixture)

            # Get pixel color for this fixture
            if pixel_start < len(canvas_pixels):
                pixel_color = canvas_pixels[pixel_start]
            else:
                pixel_color = np.array([0, 0, 0], dtype=np.uint8)

            # Apply gamma correction
            r_corrected = self.apply_gamma_correction(pixel_color[0] / 255.0)
            g_corrected = self.apply_gamma_correction(pixel_color[1] / 255.0)
            b_corrected = self.apply_gamma_correction(pixel_color[2] / 255.0)

            # Write to DMX address
            dmx_addr = fixture.dmx_address - 1  # Convert to 0-indexed
            if fixture.dmx_footprint >= 3:
                dmx_data[dmx_addr] = r_corrected
                dmx_data[dmx_addr + 1] = g_corrected
                dmx_data[dmx_addr + 2] = b_corrected

        # Apply brightness limiting
        dmx_data_limited = self.apply_brightness_limit(dmx_data)

        return {
            "render_id": self.manifest.render_id,
            "dmx_universe": dmx_data_limited.tolist(),
            "format": self.manifest.export_format,
            "gamma": self.manifest.gamma_value,
            "brightness_limit": self.manifest.brightness_limit,
        }

    def validate_export(self) -> MappingValidation:
        """Validate export configuration before sending."""
        return self.mapper.validate_mapping()
