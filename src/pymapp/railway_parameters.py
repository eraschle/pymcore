"""
Railway infrastructure parameter roles.

Minimal ENUM definitions for railway-specific infrastructure elements
following the principle of "LESS IS MORE" - only essential parameters.
"""

from enum import Enum


class RailwayParameters(Enum):
    """Railway infrastructure parameter roles - keep minimal"""

    # Universal geometric parameters
    HEIGHT = "height"
    WIDTH = "width"
    LENGTH = "length"
    DIAMETER = "diameter"
    DEPTH = "depth"

    # Material parameters
    MATERIAL = "material"
    CONCRETE_GRADE = "concrete_grade"
    RAIL_PROFILE = "rail_profile"

    # Railway-specific parameters
    GAUGE = "gauge"  # Track gauge (1435mm standard)
    CURVE_RADIUS = "curve_radius"  # Track curve radius
    LOAD_CAPACITY = "load_capacity"  # Cantilever load capacity
    FOUNDATION_DEPTH = "foundation_depth"  # Pole foundation depth
    POLE_CONNECTION = "pole_connection"  # Cantilever to pole connection
    SPACING = "spacing"  # Sleeper spacing

    def __str__(self) -> str:
        """String representation returns the enum value."""
        return self.value
