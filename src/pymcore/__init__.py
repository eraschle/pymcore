"""
PyM Core - Universal container system for infrastructure modeling.

Provides a flexible architecture for modeling infrastructure elements
with hybrid parameter management and extensible container system.
"""

from .types import ValueType, UnitType
from .unit_converter import UnitConverter, UnitConversionError
from .generic_element import GenericElement
from .geometry import ElementGeometry, ParameterDescriptor as GeometryParameterDescriptor
from .parameter_descriptor import ParameterDescriptor
from .parameter_registry import ParameterRegistry, ParameterMapping
from .hybrid_parameter_interface import HybridParameterInterface, ParameterConfigurationError
from .container_extension import ContainerExtension, ContainerRegistry, ContainerNotFoundError
from .element_repository import ElementRepository, RepositoryError

__version__ = "0.1.0"

__all__ = [
    "ValueType",
    "UnitType", 
    "UnitConverter",
    "UnitConversionError",
    "GenericElement",
    "ElementGeometry",
    "GeometryParameterDescriptor", 
    "ParameterDescriptor",
    "ParameterRegistry",
    "ParameterMapping",
    "HybridParameterInterface",
    "ParameterConfigurationError",
    "ContainerExtension",
    "ContainerRegistry",
    "ContainerNotFoundError",
    "ElementRepository",
    "RepositoryError"
]