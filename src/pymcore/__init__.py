"""
PyM Core - Universal container system for infrastructure modeling.

Provides a flexible architecture for modeling infrastructure elements
with hybrid parameter management and extensible container system.
"""

from .container_extension import ContainerExtension, ContainerNotFoundError, ContainerRegistry
from .element_repository import ElementRepository, RepositoryError
from .generic_element import GenericElement, ParameterMetadata, ParameterNotDefinedError
from .geometry import ElementGeometry
from .geometry import ParameterDescriptor as GeometryParameterDescriptor
from .helper import (
    ValueConversionError,
    as_bool,
    as_float,
    as_int,
    as_str,
    is_bool,
    is_float,
    is_int,
    is_str,
)
from .hybrid_parameter_interface import HybridParameterInterface, ParameterConfigurationError
from .parameter_descriptor import ParameterDescriptor
from .parameter_registry import ParameterMapping, ParameterRegistry
from .types import Unit, ValueType
from .unit_converter import UnitConversionError, UnitConverter

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
