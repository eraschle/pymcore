"""
Geometry system for PyM Core.

Provides descriptor-based geometry properties that automatically sync
with element parameters without requiring explicit synchronization.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .generic_element import GenericElement

logger = logging.getLogger(__name__)


class ParameterDescriptionError(Exception):
    pass


class ParameterDescriptor:
    """
    Descriptor that provides automatic parameter synchronization.

    When accessed, it reads/writes directly to the element's parameter store,
    ensuring geometry and parameters always stay in sync.
    """

    def __init__(self, parameter_name: str, default_value: float = 0.0):
        """
        Initialize parameter descriptor.

        Parameters
        ----------
        parameter_name : str
            Name of the parameter in the element's parameter store
        default_value : float
            Default value if parameter doesn't exist
        """
        self.param_name = parameter_name
        self.default_value = default_value

    def __get__(self, obj: ElementGeometry | None, objtype=None) -> float:
        """Get parameter value from element."""
        if obj is None:
            logger.error(
                f"Accessing {self.param_name} on None object - return {self.default_value}"
            )
            return self.default_value

        existing_value = obj._element.value_by(self.param_name, default=self.default_value)
        if existing_value is None:
            logger.error(f"Accessing Value {existing_value} of {self.param_name} on {obj._element}")
            raise ParameterDescriptionError(
                f"Parameter {self.param_name} has not been defined in element"
            )

        existing_value = obj._element.value_by(self.param_name, default=self.default_value)
        if existing_value is None:
            logger.warning(
                f"Parameter {self.param_name} not found, returning default {self.default_value}"
            )
            return self.default_value

        return existing_value.value

    def __set__(self, obj: ElementGeometry, value: float) -> None:
        """Set parameter value in element."""
        obj._element.set_value(self.param_name, value, unit=None)


class ElementGeometry:
    """
    Geometry container that synchronizes with element parameters.

    All geometric properties are descriptors that read/write directly
    to the underlying element's parameter store.
    """

    # Descriptors for common geometric properties
    height = ParameterDescriptor("height")
    width = ParameterDescriptor("width")
    length = ParameterDescriptor("length")
    depth = ParameterDescriptor("depth")
    diameter = ParameterDescriptor("diameter")

    def __init__(self, element: GenericElement):
        """
        Initialize geometry linked to an element.

        Parameters
        ----------
        element : GenericElement
            The element this geometry belongs to
        """
        self._element = element

    def _sync_from_parameters(self) -> None:
        """
        Sync geometry from parameters.

        This method is called automatically when parameters change.
        Since we use descriptors, no explicit sync is needed.
        """
        # Descriptors handle synchronization automatically
        pass

    def get_dimensions(self) -> dict[str, float]:
        """
        Get all dimensional parameters as a dictionary.

        Returns
        -------
        dict[str, float]
            Dictionary of all available dimensions
        """
        dimensions = {}

        # Check which geometric parameters exist
        geometric_params = ["height", "width", "length", "depth", "diameter"]

        for param in geometric_params:
            if self._element.has_value(param):
                dimensions[param] = getattr(self, param)

        return dimensions

    def calculate_volume(self) -> float:
        """
        Calculate volume based on available dimensions.

        Uses appropriate formula based on available parameters.

        Returns
        -------
        float
            Volume in cubic millimeters
        """
        dimensions = self.get_dimensions()

        # Cylindrical volume (pole)
        if "diameter" in dimensions and "height" in dimensions:
            radius = dimensions["diameter"] / 2
            return 3.14159 * radius * radius * dimensions["height"]

        # Rectangular volume (foundation, sleeper)
        if all(param in dimensions for param in ["width", "length", "height"]):
            return dimensions["width"] * dimensions["length"] * dimensions["height"]

        # Alternative rectangular with depth instead of height
        if all(param in dimensions for param in ["width", "length", "depth"]):
            return dimensions["width"] * dimensions["length"] * dimensions["depth"]

        # Linear volume (track with default cross-section)
        if "length" in dimensions:
            # Assume default cross-section for tracks
            default_cross_section = 100.0 * 100.0  # 100mm x 100mm default
            return dimensions["length"] * default_cross_section

        return 0.0

    def get_bounding_box(self) -> dict[str, float]:
        """
        Get bounding box dimensions.

        Returns
        -------
        dict[str, float]
            Bounding box with min_x, max_x, min_y, max_y, min_z, max_z
        """
        dimensions = self.get_dimensions()

        # Default centered at origin
        bbox = {
            "min_x": 0.0,
            "max_x": 0.0,
            "min_y": 0.0,
            "max_y": 0.0,
            "min_z": 0.0,
            "max_z": 0.0,
        }

        # Update based on available dimensions
        if "width" in dimensions:
            half_width = dimensions["width"] / 2
            bbox["min_x"] = -half_width
            bbox["max_x"] = half_width

        if "length" in dimensions:
            half_length = dimensions["length"] / 2
            bbox["min_y"] = -half_length
            bbox["max_y"] = half_length

        if "height" in dimensions:
            bbox["max_z"] = dimensions["height"]
        elif "depth" in dimensions:
            bbox["min_z"] = -dimensions["depth"]

        return bbox
