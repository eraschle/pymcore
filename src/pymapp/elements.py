"""
Railway infrastructure element implementations.

Domain-specific implementations for railway infrastructure using
PyM Core components with ENUM-based parameter access.
"""

from typing import Any

from pymcore import GenericElement, HybridParameterInterface, ParameterRegistry
from pymcore.types import Unit, ValueType

from .railway_parameters import RailwayParameters


class RailwayElement:
    """Base class for railway infrastructure elements."""

    def __init__(self, element_id: str, element_type: str):
        """Initialize railway element with ENUM-based parameter interface."""
        self._core_element = GenericElement(element_id, element_type)

        # Define parameters directly in GenericElement for now
        self._define_element_parameters()

        # Use Plugin mode with ParameterRegistry for future-proofing
        registry = ParameterRegistry()
        self._setup_parameters(registry)

        self._interface = HybridParameterInterface(
            element=self._core_element,
            mapping_name=f"{element_type}_parameters",
            registry=registry,
        )

    def _define_element_parameters(self) -> None:
        """Define parameters in GenericElement - to be overridden by subclasses."""
        pass

    def _setup_parameters(self, registry: ParameterRegistry) -> None:
        """Setup parameter definitions - to be overridden by subclasses."""
        pass

    def _set_value(self, key: str, value: Any, unit: Unit | None = None) -> None:
        """Set value with optional unit conversion."""
        param_value = key if isinstance(key, str) else key.value
        if param_value is None:
            # self._core_element.define_parameter(
            #     name=key,
            #     unit=unit,
            #     value_type=ValueType.FLOAT,
            # )
            return
        self._interface.set_value(role_or_key=key, value=value, unit=unit)

    @property
    def element_id(self) -> str:
        """Get element ID."""
        return self._core_element.element_id

    @property
    def element_type(self) -> str:
        """Get element type."""
        return self._core_element.element_type

    def get_core_element(self) -> GenericElement:
        """Get the underlying GenericElement for repository operations."""
        return self._core_element

    @property
    def height(self) -> float:
        """Get/set pole height in millimeters."""
        return self._interface.get_value(RailwayParameters.HEIGHT.value, 0.0)

    def set_height(self, value: float, unit: Unit | None = None) -> None:
        """Set height with specified unit."""
        self._set_value(RailwayParameters.HEIGHT.value, value, unit)


class Pole(RailwayElement):
    """Railway pole/mast implementation (Mast)"""

    def __init__(self, element_id: str):
        super().__init__(element_id, "pole")

    def _define_element_parameters(self) -> None:
        """Define pole parameters in GenericElement."""
        self._core_element.define_parameter(
            RailwayParameters.HEIGHT.value, ValueType.FLOAT, Unit.MILLIMETER
        )
        self._core_element.define_parameter(
            RailwayParameters.DIAMETER.value, ValueType.FLOAT, Unit.MILLIMETER
        )
        self._core_element.define_parameter(
            RailwayParameters.MATERIAL.value, ValueType.STRING, Unit.NONE
        )
        self._core_element.define_parameter(
            RailwayParameters.FOUNDATION_DEPTH.value, ValueType.FLOAT, Unit.MILLIMETER
        )

    def _setup_parameters(self, registry: ParameterRegistry) -> None:
        """Setup pole-specific parameters."""
        from pymcore.parameter_descriptor import ParameterDescriptor

        # Register pole parameters
        registry.register_parameter(
            ParameterDescriptor(
                semantic_key=RailwayParameters.HEIGHT.value,
                data_type=float,
                unit=Unit.MILLIMETER,
                description="Pole height above ground",
            )
        )

        registry.register_parameter(
            ParameterDescriptor(
                semantic_key=RailwayParameters.DIAMETER.value,
                data_type=float,
                unit=Unit.MILLIMETER,
                description="Pole diameter",
            )
        )

        registry.register_parameter(
            ParameterDescriptor(
                semantic_key=RailwayParameters.MATERIAL.value,
                data_type=str,
                unit=Unit.NONE,
                description="Pole material",
            )
        )

        registry.register_parameter(
            ParameterDescriptor(
                semantic_key=RailwayParameters.FOUNDATION_DEPTH.value,
                data_type=float,
                unit=Unit.MILLIMETER,
                description="Foundation depth below ground",
            )
        )

    @property
    def diameter(self) -> float:
        """Get/set pole diameter in millimeters."""
        return self._interface.get_value(RailwayParameters.DIAMETER.value, 0.0)

    def set_diameter(self, value: float, unit: Unit | None = None) -> None:
        self._set_value(RailwayParameters.DIAMETER.value, value, unit)

    @property
    def material(self) -> str:
        """Get/set pole material."""
        return self._interface.get_value(RailwayParameters.MATERIAL.value, "")

    def set_material(self, value: str) -> None:
        self._set_value(RailwayParameters.MATERIAL.value, value)

    @property
    def foundation_depth(self) -> float:
        """Get/set foundation depth in millimeters."""
        return self._interface.get_value(RailwayParameters.FOUNDATION_DEPTH.value, 0.0)

    def set_foundation_depth(self, value: float, unit: Unit | None = None) -> None:
        self._set_value(RailwayParameters.FOUNDATION_DEPTH.value, value, unit)


class Foundation(RailwayElement):
    """Railway foundation implementation (Fundament)"""

    def __init__(self, element_id: str):
        super().__init__(element_id, "foundation")

    def _define_element_parameters(self) -> None:
        """Define foundation parameters in GenericElement."""
        self._core_element.define_parameter(
            RailwayParameters.HEIGHT.value, ValueType.FLOAT, Unit.MILLIMETER
        )
        self._core_element.define_parameter(
            RailwayParameters.WIDTH.value, ValueType.FLOAT, Unit.MILLIMETER
        )
        self._core_element.define_parameter(
            RailwayParameters.LENGTH.value, ValueType.FLOAT, Unit.MILLIMETER
        )
        self._core_element.define_parameter(
            RailwayParameters.DEPTH.value, ValueType.FLOAT, Unit.MILLIMETER
        )
        self._core_element.define_parameter(
            RailwayParameters.CONCRETE_GRADE.value, ValueType.STRING, Unit.NONE
        )

    def _setup_parameters(self, registry: ParameterRegistry) -> None:
        """Setup foundation-specific parameters."""
        from pymcore.parameter_descriptor import ParameterDescriptor

        registry.register_parameter(
            ParameterDescriptor(
                semantic_key=RailwayParameters.WIDTH.value,
                data_type=float,
                unit=Unit.MILLIMETER,
                description="Foundation width",
            )
        )

        registry.register_parameter(
            ParameterDescriptor(
                semantic_key=RailwayParameters.LENGTH.value,
                data_type=float,
                unit=Unit.MILLIMETER,
                description="Foundation length",
            )
        )

        registry.register_parameter(
            ParameterDescriptor(
                semantic_key=RailwayParameters.DEPTH.value,
                data_type=float,
                unit=Unit.MILLIMETER,
                description="Foundation depth",
            )
        )

        registry.register_parameter(
            ParameterDescriptor(
                semantic_key=RailwayParameters.CONCRETE_GRADE.value,
                data_type=str,
                unit=Unit.NONE,
                description="Concrete grade specification",
            )
        )

    @property
    def width(self) -> float:
        """Get/set foundation width in millimeters."""
        return self._interface.get_value(RailwayParameters.WIDTH.value, 0.0)

    def set_width(self, value: float, unit: Unit | None = None) -> None:
        self._set_value(RailwayParameters.WIDTH.value, value, unit)

    @property
    def length(self) -> float:
        """Get/set track length in millimeters."""
        return self._interface.get_value(RailwayParameters.LENGTH.value, 0.0)

    def set_length(self, value: float, unit: Unit | None = None) -> None:
        self._set_value(RailwayParameters.LENGTH.value, value, unit)

    @property
    def depth(self) -> float:
        """Get/set foundation depth in millimeters."""
        return self._interface.get_value(RailwayParameters.DEPTH.value, 0.0)

    def set_depth(self, value: float, unit: Unit | None = None) -> None:
        self._set_value(RailwayParameters.DEPTH.value, value, unit)

    @property
    def concrete_grade(self) -> str:
        """Get/set concrete grade."""
        return self._interface.get_value(RailwayParameters.CONCRETE_GRADE.value, "")

    def set_concrete_grade(self, value: str, unit: Unit | None = None) -> None:
        self._set_value(RailwayParameters.CONCRETE_GRADE.value, value, unit)


class Track(RailwayElement):
    """Railway track implementation (Gleis)"""

    def __init__(self, element_id: str):
        super().__init__(element_id, "track")

    def _define_element_parameters(self) -> None:
        """Define track parameters in GenericElement."""
        self._core_element.define_parameter(
            RailwayParameters.LENGTH.value, ValueType.FLOAT, Unit.MILLIMETER
        )
        self._core_element.define_parameter(
            RailwayParameters.GAUGE.value, ValueType.FLOAT, Unit.MILLIMETER
        )
        self._core_element.define_parameter(
            RailwayParameters.RAIL_PROFILE.value, ValueType.STRING, Unit.NONE
        )
        self._core_element.define_parameter(
            RailwayParameters.CURVE_RADIUS.value, ValueType.FLOAT, Unit.MILLIMETER
        )

    def _setup_parameters(self, registry: ParameterRegistry) -> None:
        """Setup track-specific parameters."""
        from pymcore.parameter_descriptor import ParameterDescriptor

        registry.register_parameter(
            ParameterDescriptor(
                semantic_key=RailwayParameters.LENGTH.value,
                data_type=float,
                unit=Unit.MILLIMETER,
                description="Track section length",
            )
        )

        registry.register_parameter(
            ParameterDescriptor(
                semantic_key=RailwayParameters.GAUGE.value,
                data_type=float,
                unit=Unit.MILLIMETER,
                description="Track gauge (1435mm standard)",
            )
        )

        registry.register_parameter(
            ParameterDescriptor(
                semantic_key=RailwayParameters.RAIL_PROFILE.value,
                data_type=str,
                unit=Unit.NONE,
                description="Rail profile specification",
            )
        )

        registry.register_parameter(
            ParameterDescriptor(
                semantic_key=RailwayParameters.CURVE_RADIUS.value,
                data_type=float,
                unit=Unit.MILLIMETER,
                description="Curve radius (0 for straight track)",
                default_value=0.0,
            )
        )

    @property
    def length(self) -> float:
        """Get/set track length in millimeters."""
        return self._interface.get_value(RailwayParameters.LENGTH.value, 0.0)

    def set_length(self, value: float, unit: Unit | None = None) -> None:
        self._set_value(RailwayParameters.LENGTH.value, value, unit)

    @property
    def gauge(self) -> float:
        """Get/set track gauge in millimeters."""
        return self._interface.get_value(RailwayParameters.GAUGE.value, 1435.0)

    def set_gauge(self, value: float, unit: Unit | None = None) -> None:
        self._set_value(RailwayParameters.GAUGE.value, value, unit)

    @property
    def rail_profile(self) -> str:
        """Get/set rail profile."""
        return self._interface.get_value(RailwayParameters.RAIL_PROFILE.value, "")

    def set_rail_profile(self, value: str, unit: Unit | None = None) -> None:
        self._set_value(RailwayParameters.RAIL_PROFILE.value, value, unit)

    @property
    def curve_radius(self) -> float:
        """Get/set curve radius in millimeters (0 for straight)."""
        return self._interface.get_value(RailwayParameters.CURVE_RADIUS.value, 0.0)

    def set_curve_radius(self, value: float, unit: Unit | None = None) -> None:
        self._set_value(RailwayParameters.CURVE_RADIUS.value, value, unit)


class Cantilever(RailwayElement):
    """Railway cantilever implementation (Ausleger)"""

    def __init__(self, element_id: str):
        super().__init__(element_id, "cantilever")

    def _define_element_parameters(self) -> None:
        """Define cantilever parameters in GenericElement."""
        self._core_element.define_parameter(
            RailwayParameters.LENGTH.value,
            value_type=ValueType.FLOAT,
            unit=Unit.MILLIMETER,
        )
        self._core_element.define_parameter(
            RailwayParameters.HEIGHT.value,
            value_type=ValueType.FLOAT,
            unit=Unit.MILLIMETER,
        )
        self._core_element.define_parameter(
            RailwayParameters.LOAD_CAPACITY.value,
            value_type=ValueType.FLOAT,
            unit=Unit.KILOGRAM,
        )
        self._core_element.define_parameter(
            RailwayParameters.POLE_CONNECTION.value,
            value_type=ValueType.STRING,
            unit=Unit.NONE,
        )

    def _setup_parameters(self, registry: ParameterRegistry) -> None:
        """Setup cantilever-specific parameters."""
        from pymcore.parameter_descriptor import ParameterDescriptor

        registry.register_parameter(
            ParameterDescriptor(
                semantic_key=RailwayParameters.LENGTH.value,
                data_type=float,
                unit=Unit.MILLIMETER,
                description="Cantilever length",
            )
        )

        registry.register_parameter(
            ParameterDescriptor(
                semantic_key=RailwayParameters.HEIGHT.value,
                data_type=float,
                unit=Unit.MILLIMETER,
                description="Cantilever height",
            )
        )

        registry.register_parameter(
            ParameterDescriptor(
                semantic_key=RailwayParameters.LOAD_CAPACITY.value,
                data_type=float,
                unit=Unit.KILOGRAM,
                description="Maximum load capacity",
            )
        )

        registry.register_parameter(
            ParameterDescriptor(
                semantic_key=RailwayParameters.POLE_CONNECTION.value,
                data_type=str,
                unit=Unit.NONE,
                description="Connection type to pole",
            )
        )

    @property
    def length(self) -> float:
        """Get/set cantilever length in millimeters."""
        return self._interface.get_value(RailwayParameters.LENGTH.value, 0.0)

    def set_length(self, value: float, unit: Unit | None = None) -> None:
        self._set_value(RailwayParameters.LENGTH.value, value, unit)

    @property
    def load_capacity(self) -> float:
        """Get/set load capacity in kilograms."""
        return self._interface.get_value(RailwayParameters.LOAD_CAPACITY.value, 0.0)

    def set_load_capacity(self, value: float, unit: Unit | None = None) -> None:
        self._set_value(RailwayParameters.LOAD_CAPACITY.value, value, unit)

    @property
    def pole_connection(self) -> str:
        """Get/set pole connection type."""
        return self._interface.get_value(RailwayParameters.POLE_CONNECTION.value, "")

    def set_pole_connection(self, value: str, unit: Unit | None = None) -> None:
        self._set_value(RailwayParameters.POLE_CONNECTION.value, value, unit)


class Sleeper(RailwayElement):
    """Railway sleeper implementation (Schwelle)"""

    def __init__(self, element_id: str):
        super().__init__(element_id, "sleeper")

    def _define_element_parameters(self) -> None:
        """Define sleeper parameters in GenericElement."""
        self._core_element.define_parameter(
            RailwayParameters.LENGTH.value, ValueType.FLOAT, Unit.MILLIMETER
        )
        self._core_element.define_parameter(
            RailwayParameters.WIDTH.value, ValueType.FLOAT, Unit.MILLIMETER
        )
        self._core_element.define_parameter(
            RailwayParameters.HEIGHT.value, ValueType.FLOAT, Unit.MILLIMETER
        )
        self._core_element.define_parameter(
            RailwayParameters.MATERIAL.value, ValueType.STRING, Unit.NONE
        )
        self._core_element.define_parameter(
            RailwayParameters.SPACING.value, ValueType.FLOAT, Unit.MILLIMETER
        )

    def _setup_parameters(self, registry: ParameterRegistry) -> None:
        """Setup sleeper-specific parameters."""
        from pymcore.parameter_descriptor import ParameterDescriptor

        registry.register_parameter(
            ParameterDescriptor(
                semantic_key=RailwayParameters.LENGTH.value,
                data_type=float,
                unit=Unit.MILLIMETER,
                description="Sleeper length",
            )
        )

        registry.register_parameter(
            ParameterDescriptor(
                semantic_key=RailwayParameters.WIDTH.value,
                data_type=float,
                unit=Unit.MILLIMETER,
                description="Sleeper width",
            )
        )

        registry.register_parameter(
            ParameterDescriptor(
                semantic_key=RailwayParameters.HEIGHT.value,
                data_type=float,
                unit=Unit.MILLIMETER,
                description="Sleeper height",
            )
        )

        registry.register_parameter(
            ParameterDescriptor(
                semantic_key=RailwayParameters.MATERIAL.value,
                data_type=str,
                unit=Unit.NONE,
                description="Sleeper material",
            )
        )

        registry.register_parameter(
            ParameterDescriptor(
                semantic_key=RailwayParameters.SPACING.value,
                data_type=float,
                unit=Unit.MILLIMETER,
                description="Standard spacing between sleepers",
            )
        )

    @property
    def length(self) -> float:
        """Get/set sleeper length in millimeters."""
        return self._interface.get_value(RailwayParameters.LENGTH.value, 0.0)

    def set_length(self, value: float, unit: Unit | None = None) -> None:
        self._set_value(RailwayParameters.LENGTH.value, value, unit)

    @property
    def width(self) -> float:
        """Get/set sleeper width in millimeters."""
        return self._interface.get_value(RailwayParameters.WIDTH.value, 0.0)

    def set_width(self, value: float, unit: Unit | None = None) -> None:
        self._set_value(RailwayParameters.WIDTH.value, value, unit)

    @property
    def material(self) -> str:
        """Get/set sleeper material."""
        return self._interface.get_value(RailwayParameters.MATERIAL.value, "")

    def set_material(self, value: str) -> None:
        self._set_value(RailwayParameters.MATERIAL.value, value)

    @property
    def spacing(self) -> float:
        """Get/set standard spacing in millimeters."""
        return self._interface.get_value(RailwayParameters.SPACING.value, 600.0)

    def set_spacing(self, value: float, unit: Unit | None = None) -> None:
        self._set_value(RailwayParameters.SPACING.value, value, unit)
