"""
Integration tests for Railway Elements.

Tests the complete integration of PyM Application Layer with Core components,
demonstrating ENUM-based parameter access and repository operations.
"""

import pytest
from pymapp import Pole, Foundation, Track, Cantilever, Sleeper, RailwayParameters
from pymcore import ElementRepository, ContainerRegistry
from pymcore.types import Unit


class TestRailwayElementsIntegration:
    """Integration tests for railway infrastructure elements."""

    def test_pole_creation_and_properties(self):
        """Test pole creation with ENUM-based parameter access."""
        pole = Pole("pole_001")

        # Test property access
        pole.set_height(12000.0)
        pole.set_diameter(300.0)
        pole.set_material("steel")
        pole.set_foundation_depth(2000.0)

        assert pole.height == 12000.0
        assert pole.diameter == 300.0
        assert pole.material == "steel"
        assert pole.foundation_depth == 2000.0
        assert pole.element_type == "pole"
        assert pole.element_id == "pole_001"

    def test_foundation_creation_and_properties(self):
        """Test foundation creation with all parameters."""
        foundation = Foundation("foundation_001")

        foundation.set_width(2000.0)
        foundation.set_length(3000.0)
        foundation.set_depth(1500.0)
        foundation.set_concrete_grade("C30/37")

        assert foundation.width == 2000.0
        assert foundation.length == 3000.0
        assert foundation.depth == 1500.0
        assert foundation.concrete_grade == "C30/37"
        assert foundation.element_type == "foundation"

    def test_track_creation_and_properties(self):
        """Test track creation with railway-specific parameters."""
        track = Track("track_001")

        track.set_length(25000.0)  # 25m section
        track.set_gauge(1435.0)  # Standard gauge
        track.set_rail_profile("UIC60")
        track.set_curve_radius(1200000.0)  # 1200m curve

        assert track.length == 25000.0
        assert track.gauge == 1435.0
        assert track.rail_profile == "UIC60"
        assert track.curve_radius == 1200000.0
        assert track.element_type == "track"

    def test_cantilever_creation_and_properties(self):
        """Test cantilever creation with load specifications."""
        cantilever = Cantilever("cantilever_001")

        cantilever.set_length(8000.0)  # 8m length
        cantilever.set_height(1200.0)
        cantilever.set_load_capacity(500.0)  # 500kN load capacity
        cantilever.set_pole_connection("bolted")

        assert cantilever.length == 8000.0
        assert cantilever.height == 1200.0
        assert cantilever.load_capacity == 500.0
        assert cantilever.pole_connection == "bolted"
        assert cantilever.element_type == "cantilever"

    def test_sleeper_creation_and_properties(self):
        """Test sleeper creation with material specifications."""
        sleeper = Sleeper("sleeper_001")

        sleeper.set_length(2600.0)  # 2.6m length
        sleeper.set_width(300.0)  # 300mm width
        sleeper.set_height(220.0)  # 220mm height
        sleeper.set_material("concrete")
        sleeper.set_spacing(600.0)  # 600mm spacing

        assert sleeper.length == 2600.0
        assert sleeper.width == 300.0
        assert sleeper.height == 220.0
        assert sleeper.material == "concrete"
        assert sleeper.spacing == 600.0
        assert sleeper.element_type == "sleeper"

    def test_railway_elements_with_repository(self):
        """Test railway elements integration with ElementRepository."""
        # Setup repository
        container_registry = ContainerRegistry()
        repo = ElementRepository(container_registry)

        # Create railway infrastructure
        pole = Pole("pole_main_001")
        pole.set_height(15000.0)  # 15m height
        pole.set_diameter(400.0)  # 400mm diameter
        pole.set_material("aluminum")
        pole.set_foundation_depth(2500.0)  # 2.5m foundation depth

        foundation = Foundation("foundation_main_001")
        foundation.set_width(2500.0)
        foundation.set_length(3500.0)
        foundation.set_depth(2000.0)
        foundation.set_concrete_grade("C35/45")

        track = Track("track_main_001")
        track.set_length(30000.0)  # 30m track section
        track.set_gauge(1435.0)  # Standard gauge
        track.set_rail_profile("UIC54")
        track.set_curve_radius(1000000.0)  # 1000m curve

        # Save elements using their core elements
        repo.save(pole.get_core_element())
        repo.save(foundation.get_core_element())
        repo.save(track.get_core_element())

        # Load and verify elements
        loaded_pole_core = repo.load("pole_main_001")
        loaded_foundation_core = repo.load("foundation_main_001")
        loaded_track_core = repo.load("track_main_001")

        assert loaded_pole_core is not None
        assert loaded_foundation_core is not None
        assert loaded_track_core is not None

        # Verify element types
        assert loaded_pole_core.element_type == "pole"
        assert loaded_foundation_core.element_type == "foundation"
        assert loaded_track_core.element_type == "track"

        # Verify parameter access through core element
        param = loaded_pole_core.value_by("height")
        assert param is not None
        assert param.value == 15000.0
        param = loaded_foundation_core.value_by("concrete_grade")
        assert param is not None
        assert param.value == "C35/45"
        track_gauge = loaded_track_core.value_by("gauge")
        assert track_gauge is not None
        assert track_gauge.value == 1435.0

    def test_complete_railway_scene(self):
        """Test complete railway scene with all element types."""
        # Create a complete railway installation
        pole = Pole("pole_scene_001")
        pole.set_height(12000.0, Unit.METER)  # 12m height
        pole.set_diameter(300.0, Unit.MILLIMETER)  # 300mm diameter
        pole.set_material("steel")
        pole.set_foundation_depth(2500.0, Unit.MILLIMETER)  # 2.5m foundation depth

        foundation = Foundation("foundation_scene_001")
        foundation.set_width(2000.0, Unit.MILLIMETER)
        foundation.set_length(3000.0, Unit.MILLIMETER)
        foundation.set_depth(1500.0, Unit.MILLIMETER)
        foundation.set_concrete_grade("C30/37")

        cantilever = Cantilever("cantilever_scene_001")
        cantilever.set_length(8000.0, Unit.MILLIMETER)  # 8m length
        cantilever.set_height(1000.0, Unit.METER)
        cantilever.set_load_capacity(400.0, Unit.KILOGRAM)  # 400kN load capacity
        cantilever.set_pole_connection("bolted")

        track = Track("track_scene_001")
        track.set_length(25000.0, Unit.MILLIMETER)  # 25m section
        track.set_gauge(1435.0, Unit.MILLIMETER)  # Standard gauge
        track.set_rail_profile("UIC60")
        track.set_curve_radius(800000.0, Unit.MILLIMETER)  # 800m curve

        sleeper = Sleeper("sleeper_scene_001")
        sleeper.set_length(2600.0, Unit.MILLIMETER)  # 2.6m length
        sleeper.set_width(300.0, Unit.MILLIMETER)  # 300mm width
        sleeper.set_height(220.0, Unit.MILLIMETER)  # 220mm height
        sleeper.set_material("concrete")
        sleeper.set_spacing(600.0, Unit.MILLIMETER)  # 600mm spacing

        # Verify all elements are properly configured
        elements = [pole, foundation, cantilever, track, sleeper]

        for element in elements:
            assert element.element_id.startswith(f"{element.element_type}_scene_001")
            assert hasattr(element, "_interface")
            assert hasattr(element, "_core_element")

        # Test parameter access consistency
        pole.set_height(12000.0, Unit.MILLIMETER)
        assert pole.height == 12000.0
        assert foundation.concrete_grade == "C30/37"
        assert cantilever.load_capacity == 400.0
        assert track.curve_radius == 800000.0
        assert sleeper.spacing == 600.0

    def test_railway_parameters_enum_values(self):
        """Test RailwayParameters enum string representation."""
        # Test that enum values match expected parameter names
        assert str(RailwayParameters.HEIGHT) == "height"
        assert str(RailwayParameters.WIDTH) == "width"
        assert str(RailwayParameters.GAUGE) == "gauge"
        assert str(RailwayParameters.CONCRETE_GRADE) == "concrete_grade"
        assert str(RailwayParameters.LOAD_CAPACITY) == "load_capacity"

        # Test enum value access
        assert RailwayParameters.HEIGHT.value == "height"
        assert RailwayParameters.FOUNDATION_DEPTH.value == "foundation_depth"
        assert RailwayParameters.POLE_CONNECTION.value == "pole_connection"
