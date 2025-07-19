import pytest
from hypothesis import given
from hypothesis import strategies as st
from pymcore import models as mdl


class TestIsTypeFunctions:
    """Tests für die mdl.is_* Funktionen."""

    def test_is_int(self):
        assert mdl.is_int(42)
        assert mdl.is_int("42")
        assert mdl.is_int("3.0")
        assert not mdl.is_int(3.14)
        assert not mdl.is_int("abc")

    def test_is_float(self):
        assert mdl.is_float(3.14)
        assert mdl.is_float("3.14")
        assert not mdl.is_float(42)
        assert not mdl.is_float("abc")

    def test_is_str(self):
        assert mdl.is_str("hello")
        assert not mdl.is_str(42)
        assert not mdl.is_str(3.14)

    def test_is_bool(self):
        assert mdl.is_bool(True)
        assert mdl.is_bool(False)
        assert not mdl.is_bool(1)
        assert not mdl.is_bool("true")

    def test_is_list(self):
        assert mdl.is_list([1, 2, 3])
        assert not mdl.is_list("abc")
        assert not mdl.is_list(42)

    def test_is_dict(self):
        assert mdl.is_dict({"a": 1})
        assert mdl.is_dict([1, 2, 3])
        assert not mdl.is_dict("abc")


class TestAsTypeFunctions:
    """Tests für die mdl.as_* Funktionen."""

    def test_as_int(self):
        assert mdl.as_int("42") == 42
        assert mdl.as_int(3.14) == 3
        assert mdl.as_int("3.0") == 3
        with pytest.raises((ValueError, TypeError)):
            mdl.as_int("abc")

    def test_as_float(self):
        assert mdl.as_float("3.14") == 3.14
        assert mdl.as_float(42) == 42.0
        with pytest.raises((ValueError, TypeError)):
            mdl.as_float("abc")

    def test_as_str(self):
        assert mdl.as_str(42) == "42"
        assert mdl.as_str(3.14) == "3.14"
        assert mdl.as_str(True) == "True"

    def test_as_bool(self):
        assert mdl.as_bool("true")
        assert mdl.as_bool("1")
        assert mdl.as_bool("yes")
        assert mdl.as_bool("on")
        assert not mdl.as_bool("false")
        assert not mdl.as_bool("0")
        assert not mdl.as_bool(1)
        assert not mdl.as_bool(0)


class TestConvertValue:
    """Tests für die Hauptkonvertierungsfunktion."""

    def test_convert_to_int(self):
        assert mdl.convert_value("42", mdl.ValueType.INTEGER) == 42
        assert mdl.convert_value(3.14, mdl.ValueType.INTEGER) == 3
        assert mdl.convert_value("3.0", mdl.ValueType.INTEGER) == 3

    def test_convert_to_float(self):
        assert mdl.convert_value("3.14", mdl.ValueType.FLOAT) == 3.14
        assert mdl.convert_value(42, mdl.ValueType.FLOAT) == 42.0

    def test_convert_to_str(self):
        assert mdl.convert_value(42, mdl.ValueType.STRING) == "42"
        assert mdl.convert_value(3.14, mdl.ValueType.STRING) == "3.14"

    def test_convert_to_bool(self):
        assert mdl.convert_value("true", mdl.ValueType.BOOLEAN) == True
        assert mdl.convert_value(1, mdl.ValueType.BOOLEAN) == True
        assert mdl.convert_value("false", mdl.ValueType.BOOLEAN) == False
        assert mdl.convert_value(0, mdl.ValueType.BOOLEAN) == False

    def test_convert_to_none(self):
        # NONE wird als STRING behandelt
        assert mdl.convert_value(42, mdl.ValueType.NONE) == "42"
        assert mdl.convert_value("test", mdl.ValueType.NONE) == "test"

    def test_convert_invalid_type(self):
        with pytest.raises(TypeError, match="Cannot convert to"):
            mdl.convert_value("test", mdl.ValueType.LIST)
        with pytest.raises(TypeError, match="Cannot convert to"):
            mdl.convert_value("test", mdl.ValueType.DICT)
        with pytest.raises(TypeError, match="Cannot convert to"):
            mdl.convert_value("test", mdl.ValueType.OBJECT)

    def test_convert_invalid_value(self):
        with pytest.raises((ValueError, TypeError)):
            mdl.convert_value("not_a_number", mdl.ValueType.INTEGER)


class TestValueType:
    """Tests für mdl.ValueType Enum."""

    def test_python_type_mapping(self):
        assert mdl.ValueType.STRING.python_type is str
        assert mdl.ValueType.INTEGER.python_type is int
        assert mdl.ValueType.FLOAT.python_type is float
        assert mdl.ValueType.BOOLEAN.python_type is bool
        assert mdl.ValueType.LIST.python_type is list
        assert mdl.ValueType.DICT.python_type is dict
        assert mdl.ValueType.OBJECT.python_type is object
        assert mdl.ValueType.NONE.python_type is type(None)

    def test_enum_values(self):
        assert mdl.ValueType.STRING == "string"
        assert mdl.ValueType.INTEGER == "integer"
        assert mdl.ValueType.FLOAT == "float"
        assert mdl.ValueType.BOOLEAN == "boolean"


@given(st.integers())
def test_int_conversion_roundtrip(value):
    """Property-based test: int -> str -> int sollte identisch sein."""
    converted = mdl.convert_value(str(value), mdl.ValueType.INTEGER)
    assert converted == value


@given(st.floats(allow_nan=False, allow_infinity=False))
def test_float_conversion_roundtrip(value):
    """Property-based test: float -> str -> float sollte nahezu identisch sein."""
    converted = mdl.convert_value(str(value), mdl.ValueType.FLOAT)
    assert abs(converted - value) < 1e-10
