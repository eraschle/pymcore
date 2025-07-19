"""
PyM Core - Universal container system for infrastructure modeling.

Provides a flexible architecture for modeling infrastructure elements
with hybrid parameter management and extensible container system.
"""

from .types import ValueType, UnitType
from .unit_converter import UnitConverter, UnitConversionError

__version__ = "0.1.0"

__all__ = [
    "ValueType",
    "UnitType", 
    "UnitConverter",
    "UnitConversionError"
]