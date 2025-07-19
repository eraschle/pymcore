"""
Value conversion and validation utilities for PyM Core.

Provides type guards and safe conversion functions for common data types.
"""

from typing import Any, TypeGuard


class ValueConversionError(Exception):
    """Raised when value conversion is not possible."""

    pass


def is_int(value: Any) -> TypeGuard[int]:
    """
    Type guard to check if a value can be treated as an integer.

    Parameters
    ----------
    value : Any
        Value to check

    Returns
    -------
    TypeGuard[int]
        True if value is or can be converted to int
    """
    if isinstance(value, int):
        return True

    if isinstance(value, float):
        return value.is_integer()

    if isinstance(value, str):
        try:
            int(value)
            return True
        except ValueError:
            return False

    if isinstance(value, bool):
        return True

    return False


def as_int(value: Any) -> int:
    """
    Convert a value to integer.

    Parameters
    ----------
    value : Any
        Value to convert

    Returns
    -------
    int
        Converted integer value

    Raises
    ------
    ValueConversionError
        If conversion is not possible
    """
    if isinstance(value, int):
        return value

    if isinstance(value, float):
        if not is_int(value):
            raise ValueConversionError(f"Float value {value} is not a whole number")
        return int(value)

    if not isinstance(value, str):
        value = str(value).strip()
        try:
            return int(value)
        except ValueError as e:
            raise ValueConversionError(f"Cannot convert string '{value}' to int") from e

    if isinstance(value, bool):
        return int(value)

    raise ValueConversionError(f"Cannot convert {type(value).__name__} to int")


def is_str(value: Any) -> TypeGuard[str]:
    """
    Type guard to check if a value can be treated as a string.

    Parameters
    ----------
    value : Any
        Value to check

    Returns
    -------
    TypeGuard[str]
        True if value is or can be converted to str
    """
    # Almost everything can be converted to string
    return value is not None


def as_str(value: Any) -> str:
    """
    Convert a value to string.

    Parameters
    ----------
    value : Any
        Value to convert

    Returns
    -------
    str
        Converted string value

    Raises
    ------
    ValueConversionError
        If conversion is not possible
    """
    if value is None:
        raise ValueConversionError("Cannot convert None to string")

    return str(value)


def is_float(value: Any) -> TypeGuard[float]:
    """
    Type guard to check if a value can be treated as a float.

    Parameters
    ----------
    value : Any
        Value to check

    Returns
    -------
    TypeGuard[float]
        True if value is or can be converted to float
    """
    if isinstance(value, (int | float)):
        return True

    if isinstance(value, str):
        try:
            float(value)
            return True
        except ValueError:
            return False

    if isinstance(value, bool):
        return True

    return False


def as_float(value: Any) -> float:
    """
    Convert a value to float.

    Parameters
    ----------
    value : Any
        Value to convert

    Returns
    -------
    float
        Converted float value

    Raises
    ------
    ValueConversionError
        If conversion is not possible
    """

    if isinstance(value, bool):
        return float(value)

    if isinstance(value, (int | float)):
        return float(value)

    if not isinstance(value, str):
        value = str(value).strip()
    try:
        return float(value)
    except ValueError as e:
        raise ValueConversionError(f"Cannot convert string '{value}' to float") from e


def is_bool(value: Any) -> TypeGuard[bool]:
    """
    Type guard to check if a value can be treated as a boolean.

    Parameters
    ----------
    value : Any
        Value to check

    Returns
    -------
    TypeGuard[bool]
        True if value is or can be converted to bool
    """
    if isinstance(value, bool):
        return True

    if isinstance(value, (int | float)):
        return value in (0, 1, 0.0, 1.0)

    if isinstance(value, str):
        return value.lower() in ("true", "false", "1", "0", "yes", "no", "on", "off")

    return False


def as_bool(value: Any) -> bool:
    """
    Convert a value to boolean.

    Parameters
    ----------
    value : Any
        Value to convert

    Returns
    -------
    bool
        Converted boolean value

    Raises
    ------
    ValueConversionError
        If conversion is not possible
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, (int | float)):
        if value == 0 or value == 0.0:
            return False
        elif value == 1 or value == 1.0:
            return True
        else:
            raise ValueConversionError(f"Cannot convert numeric value {value} to bool (only 0/1 allowed)")

    if isinstance(value, str):
        lower_value = value.lower()
        if lower_value in ("true", "1", "yes", "on"):
            return True
        elif lower_value in ("false", "0", "no", "off"):
            return False
        else:
            raise ValueConversionError(f"Cannot convert string '{value}' to bool")

    raise ValueConversionError(f"Cannot convert {type(value).__name__} to bool")
