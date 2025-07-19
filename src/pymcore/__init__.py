"""
PyM Core - Universal container system for infrastructure modeling.

Provides a flexible architecture for modeling infrastructure elements
with hybrid parameter management and extensible container system.
"""

from .types import ValueType, Unit
from .unit_converter import UnitConverter, UnitConversionError
from .generic_element import GenericElement, ParameterMetadata, ParameterNotDefinedError
from .geometry import ElementGeometry, ParameterDescriptor as GeometryParameterDescriptor
from .parameter_descriptor import ParameterDescriptor
from .parameter_registry import ParameterRegistry, ParameterMapping
from .hybrid_parameter_interface import HybridParameterInterface, ParameterConfigurationError
from .container_extension import ContainerExtension, ContainerRegistry, ContainerNotFoundError
from .element_repository import ElementRepository, RepositoryError
from .helper import (
    is_int,
    as_int,
    is_str,
    as_str,
    is_float,
    as_float,
    is_bool,
    as_bool,
    ValueConversionError,
)

__version__ = "0.1.0"

__all__ = [
    "ValueType",
    "Unit",
    "UnitConverter",
    "UnitConversionError",
    "GenericElement",
    "ElementGeometry",
    "GeometryParameterDescriptor",
    "ParameterDescriptor",
    "ParameterMetadata",
    "ParameterNotDefinedError",
    "ParameterRegistry",
    "ParameterMapping",
    "HybridParameterInterface",
    "ParameterConfigurationError",
    "ContainerExtension",
    "ContainerRegistry",
    "ContainerNotFoundError",
    "ElementRepository",
    "RepositoryError",
    "is_int",
    "as_int",
    "is_str",
    "as_str",
    "is_float",
    "as_float",
    "is_bool",
    "as_bool",
    "ValueConversionError",
]
