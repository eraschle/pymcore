"""
Integration tests for ContainerExtension and Registry System.

Tests focus on generic container serialization, plugin registration,
and lazy loading capabilities without Core knowing container specifics.
"""

import pytest
from pymcore.container_extension import (
    ContainerExtension,
    ContainerRegistry,
    ContainerNotFoundError,
)
from pymcore.generic_element import GenericElement
from pymcore.types import Unit, ValueType


class GeometryContainer(ContainerExtension):
    """Example geometry container for testing."""

    def __init__(self, vertices: list[tuple[float, float, float]] | None = None):
        """Initialize geometry container with vertices."""
        self.vertices = vertices or []

    def get_container_type(self) -> str:
        """Return container type identifier."""
        return "geometry"

    def serialize(self) -> dict[str, object]:
        """Serialize container to dictionary."""
        return {"vertices": self.vertices, "vertex_count": len(self.vertices)}

    @classmethod
    def deserialize(cls, data: dict[str, object]) -> "GeometryContainer":
        """Deserialize container from dictionary."""
        vertices_data = data.get("vertices", [])
        # Convert back to list of tuples
        vertices = [tuple(vertex) for vertex in vertices_data] if vertices_data else []
        return cls(vertices)

    def add_vertex(self, x: float, y: float, z: float) -> None:
        """Add a vertex to the geometry."""
        self.vertices.append((x, y, z))

    def get_bounding_box(self) -> dict[str, float]:
        """Calculate bounding box from vertices."""
        if not self.vertices:
            return {"min_x": 0, "max_x": 0, "min_y": 0, "max_y": 0, "min_z": 0, "max_z": 0}

        xs, ys, zs = zip(*self.vertices)
        return {
            "min_x": min(xs),
            "max_x": max(xs),
            "min_y": min(ys),
            "max_y": max(ys),
            "min_z": min(zs),
            "max_z": max(zs),
        }


class MaterialContainer(ContainerExtension):
    """Example material properties container for testing."""

    def __init__(self, material_type: str = "unknown", properties: dict[str, float] | None = None):
        """Initialize material container."""
        self.material_type = material_type
        self.properties = properties or {}

    def get_container_type(self) -> str:
        """Return container type identifier."""
        return "material"

    def serialize(self) -> dict[str, object]:
        """Serialize container to dictionary."""
        return {"material_type": self.material_type, "properties": self.properties}

    @classmethod
    def deserialize(cls, data: dict[str, object]) -> "MaterialContainer":
        """Deserialize container from dictionary."""
        material_type = str(data.get("material_type", "unknown"))
        properties: dict = dict(data.get("properties", {}))
        return cls(material_type, properties)

    def set_property(self, name: str, value: float) -> None:
        """Set material property."""
        self.properties[name] = value

    def get_property(self, name: str, default: float = 0.0) -> float:
        """Get material property."""
        return self.properties.get(name, default)


class TestContainerExtensionIntegration:
    """Integration tests for container extension system."""

    def test_container_registry_registration(self):
        """Test container type registration in registry."""
        registry = ContainerRegistry()

        # Register container types
        registry.register_container_type(GeometryContainer)
        registry.register_container_type(MaterialContainer)

        # Verify registration
        assert registry.is_registered("geometry")
        assert registry.is_registered("material")
        assert not registry.is_registered("unknown")

        # Verify type listing
        registered_types = registry.get_registered_types()
        assert "geometry" in registered_types
        assert "material" in registered_types

    def test_container_factory_creation(self):
        """Test factory creation of containers without knowing specifics."""
        registry = ContainerRegistry()
        registry.register_container_type(GeometryContainer)
        registry.register_container_type(MaterialContainer)

        # Create geometry container from data
        geometry_data = {
            "vertices": [(0.0, 0.0, 0.0), (1000.0, 0.0, 0.0), (1000.0, 1000.0, 0.0)],
            "vertex_count": 3,
        }

        geometry_container = registry.create_container("geometry", geometry_data)
        assert geometry_container is not None
        assert isinstance(geometry_container, GeometryContainer)
        assert len(geometry_container.vertices) == 3

        # Create material container from data
        material_data = {
            "material_type": "steel",
            "properties": {"density": 7850.0, "yield_strength": 355.0},
        }

        material_container = registry.create_container("material", material_data)
        assert material_container is not None
        assert isinstance(material_container, MaterialContainer)
        assert material_container.material_type == "steel"
        assert material_container.get_property("density") == 7850.0

    def test_unknown_container_type_handling(self):
        """Test handling of unknown container types."""
        registry = ContainerRegistry()

        # Try to create unknown container type
        with pytest.raises(ContainerNotFoundError) as exc_info:
            registry.create_container("unknown", {})

        assert "Container type 'unknown' not registered" in str(exc_info.value)

    def test_generic_element_container_integration(self):
        """Test GenericElement integration with containers."""
        element = GenericElement("pole_001", "pole")
        element.define_parameter(name="height", unit=Unit.MILLIMETER, value_type=ValueType.FLOAT)
        element.define_parameter(name="diameter", unit=Unit.MILLIMETER, value_type=ValueType.FLOAT)

        # Set basic parameters
        element.set_value("height", 12000.0, Unit.MILLIMETER)
        element.set_value("diameter", 300.0, Unit.MILLIMETER)

        # Add geometry container
        geometry = GeometryContainer()
        geometry.add_vertex(0.0, 0.0, 0.0)
        geometry.add_vertex(150.0, 0.0, 0.0)  # radius from diameter
        geometry.add_vertex(150.0, 0.0, 12000.0)  # top of pole

        element.add_container("geometry", geometry.serialize())

        # Add material container
        material = MaterialContainer("steel")
        material.set_property("density", 7850.0)
        material.set_property("elastic_modulus", 210000.0)

        element.add_container("material", material.serialize())

        # Verify containers are stored
        assert element.has_container("geometry")
        assert element.has_container("material")

        # Retrieve containers
        geometry_data = element.get_container("geometry")
        material_data = element.get_container("material")

        assert geometry_data is not None
        assert material_data is not None
        assert geometry_data["vertex_count"] == 3
        assert material_data["material_type"] == "steel"

    def test_element_serialization_with_containers(self):
        """Test element serialization/deserialization with containers."""
        # Create element with containers
        original = GenericElement("foundation_001", "foundation")
        original.define_parameter(name="width", value_type=ValueType.FLOAT, unit=Unit.MILLIMETER)
        original.define_parameter(name="length", value_type=ValueType.FLOAT, unit=Unit.MILLIMETER)
        original.set_value("width", 2000.0, Unit.MILLIMETER)
        original.set_value("length", 3000.0, Unit.MILLIMETER)

        # Add containers
        geometry = GeometryContainer()
        geometry.add_vertex(0.0, 0.0, 0.0)
        geometry.add_vertex(2000.0, 3000.0, 1500.0)
        original.add_container("geometry", geometry.serialize())

        material = MaterialContainer("concrete")
        material.set_property("compressive_strength", 30.0)
        original.add_container("material", material.serialize())

        # Serialize
        data = original.to_dict()

        # Deserialize
        restored = GenericElement.from_dict(data)

        # Verify parameters preserved
        param_value = restored.value_by("width")
        assert param_value is not None
        assert param_value.value == 2000.0
        param_value = restored.value_by("length")
        assert param_value is not None
        assert param_value.value == 3000.0

        # Verify containers preserved
        assert restored.has_container("geometry")
        assert restored.has_container("material")

        geometry_data = restored.get_container("geometry")
        material_data = restored.get_container("material")

        assert geometry_data is not None
        assert geometry_data["vertex_count"] == 2
        assert material_data is not None
        assert material_data["material_type"] == "concrete"

    def test_container_registry_with_element_repository(self):
        """Test container registry integration with element repository."""
        # Setup registry with container types
        registry = ContainerRegistry()
        registry.register_container_type(GeometryContainer)
        registry.register_container_type(MaterialContainer)

        # Create element with containers
        element = GenericElement("pole_001", "pole")
        element.set_value("height", 15000.0, Unit.MILLIMETER)

        # Add containers
        geometry = GeometryContainer([(0.0, 0.0, 0.0), (0.0, 0.0, 15000.0)])
        element.add_container("geometry", geometry.serialize())

        # Simulate repository save/load cycle
        element_data = element.to_dict()

        # Load element and reconstruct containers
        loaded_element = GenericElement.from_dict(element_data)

        # Use registry to reconstruct container objects
        if loaded_element.has_container("geometry"):
            geometry_data = loaded_element.get_container("geometry")
            assert geometry_data is not None
            reconstructed_geometry = registry.create_container("geometry", geometry_data)

            assert isinstance(reconstructed_geometry, GeometryContainer)
            assert len(reconstructed_geometry.vertices) == 2

            # Test container functionality
            bbox = reconstructed_geometry.get_bounding_box()
            assert bbox["max_z"] == 15000.0

    def test_lazy_loading_container_scenario(self):
        """Test lazy loading of containers when type is registered later."""
        registry = ContainerRegistry()

        # Create element with container data but no registered type yet
        element = GenericElement("test_001", "test")

        # Store raw container data
        raw_data = {"material_type": "aluminum", "properties": {"density": 2700.0}}
        element.add_container("material", raw_data)

        # Later, register the container type
        registry.register_container_type(MaterialContainer)

        # Now we can create the proper container
        material_data = element.get_container("material")
        assert material_data is not None
        material_container = registry.create_container("material", material_data)

        assert isinstance(material_container, MaterialContainer)
        assert material_container.material_type == "aluminum"
        assert material_container.get_property("density") == 2700.0

    def test_container_type_validation(self):
        """Test container type validation and error handling."""
        registry = ContainerRegistry()

        # Register valid container
        registry.register_container_type(GeometryContainer)

        # Try to register same type again (should be idempotent)
        registry.register_container_type(GeometryContainer)
        assert registry.is_registered("geometry")

        # Verify only one registration
        registered_types = registry.get_registered_types()
        assert registered_types.count("geometry") == 1

    def test_container_serialization_roundtrip(self):
        """Test container serialization roundtrip preserves all data."""
        # Test geometry container
        original_geometry = GeometryContainer()
        original_geometry.add_vertex(100.0, 200.0, 300.0)
        original_geometry.add_vertex(400.0, 500.0, 600.0)

        # Serialize and deserialize
        serialized = original_geometry.serialize()
        restored_geometry = GeometryContainer.deserialize(serialized)

        assert len(restored_geometry.vertices) == 2
        assert restored_geometry.vertices[0] == (100.0, 200.0, 300.0)
        assert restored_geometry.vertices[1] == (400.0, 500.0, 600.0)

        # Test bounding box calculation
        bbox = restored_geometry.get_bounding_box()
        assert bbox["min_x"] == 100.0
        assert bbox["max_z"] == 600.0

        # Test material container
        original_material = MaterialContainer("titanium")
        original_material.set_property("density", 4500.0)
        original_material.set_property("melting_point", 1668.0)

        serialized = original_material.serialize()
        restored_material = MaterialContainer.deserialize(serialized)

        assert restored_material.material_type == "titanium"
        assert restored_material.get_property("density") == 4500.0
        assert restored_material.get_property("melting_point") == 1668.0
