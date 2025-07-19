"""
Integration tests for ElementRepository System.

Tests focus on JSON serialization, object reference handling,
and container registry integration with file I/O operations.
"""

import pytest
import tempfile
import os
from pymcore.element_repository import ElementRepository, RepositoryError
from pymcore.generic_element import GenericElement
from pymcore.container_extension import ContainerRegistry, ContainerExtension
from pymcore.types import Unit, ValueType


class MockContainerForRepo(ContainerExtension):
    """Test container for repository integration."""

    def __init__(self, test_data: str = "test"):
        self.test_data = test_data

    def get_container_type(self) -> str:
        return "test_container"

    def serialize(self) -> dict[str, object]:
        return {"test_data": self.test_data}

    @classmethod
    def deserialize(cls, data: dict[str, object]) -> "MockContainerForRepo":
        return cls(str(data.get("test_data", "test")))


class TestElementRepositoryIntegration:
    """Integration tests for element repository system."""

    def test_repository_save_and_load_single_element(self):
        """Test basic save and load operations for single element."""
        # Setup
        container_registry = ContainerRegistry()
        container_registry.register_container_type(MockContainerForRepo)

        repo = ElementRepository(container_registry)

        # Create element with parameters and containers
        element = GenericElement("pole_001", "pole")
        element.define_parameter(
            "height", unit=Unit.MILLIMETER, value_type=ValueType.FLOAT
        )
        element.define_parameter(
            "material", unit=Unit.NONE, value_type=ValueType.STRING
        )
        element.set_value("height", 12000.0, Unit.MILLIMETER)
        element.set_value("material", "steel", Unit.NONE)

        # Add container
        test_container = MockContainerForRepo("pole_geometry")
        element.add_container("test_container", test_container.serialize())

        # Save element
        repo.save(element)

        # Load element
        loaded_element = repo.load("pole_001")

        assert loaded_element is not None
        assert loaded_element.element_id == "pole_001"
        assert loaded_element.element_type == "pole"
        param_value = loaded_element.value_by("height")
        assert param_value is not None
        assert param_value.value == 12000.0

        param_value = loaded_element.value_by("material")
        assert param_value is not None
        assert param_value.value == "steel"

        param_value = loaded_element.value_by("height")
        assert param_value is not None
        assert param_value.value == 12000.0
        assert element.has_container("test_container")

    def test_repository_save_and_load_multiple_elements(self):
        """Test save and load operations for multiple elements."""
        container_registry = ContainerRegistry()
        repo = ElementRepository(container_registry)

        # Create multiple elements
        pole = GenericElement("pole_001", "pole")
        pole.define_parameter(
            "height", unit=Unit.MILLIMETER, value_type=ValueType.FLOAT
        )
        pole.set_value("height", 12000.0, unit=Unit.MILLIMETER)

        foundation = GenericElement("foundation_001", "foundation")
        foundation.define_parameter(
            "width", unit=Unit.MILLIMETER, value_type=ValueType.FLOAT
        )
        foundation.define_parameter(
            "length", unit=Unit.MILLIMETER, value_type=ValueType.FLOAT
        )
        foundation.set_value("width", 2000.0, unit=Unit.MILLIMETER)
        foundation.set_value("length", 3000.0, unit=Unit.MILLIMETER)

        track = GenericElement("track_001", "track")
        track.define_parameter(
            "length", unit=Unit.MILLIMETER, value_type=ValueType.FLOAT
        )
        track.define_parameter(
            "gauge", unit=Unit.MILLIMETER, value_type=ValueType.FLOAT
        )
        track.set_value("length", 25000.0, unit=Unit.MILLIMETER)
        track.set_value("gauge", 1435.0, unit=Unit.MILLIMETER)

        # Save all elements
        repo.save_all([pole, foundation, track])

        # Load all elements
        all_elements = repo.get_all()

        assert len(all_elements) == 3
        element_ids = {elem.element_id for elem in all_elements}
        assert element_ids == {"pole_001", "foundation_001", "track_001"}

        # Load by type
        pole_elements = repo.get_by_type("pole")
        assert len(pole_elements) == 1
        assert pole_elements[0].element_id == "pole_001"

    def test_repository_object_references_system(self):
        """Test object reference system with relative UUID paths."""
        container_registry = ContainerRegistry()
        repo = ElementRepository(container_registry)

        # Create pole and foundation with reference
        pole = GenericElement("pole_123", "pole")
        pole.define_parameter("height", ValueType.FLOAT, Unit.MILLIMETER)
        pole.set_value("height", 15000.0, Unit.MILLIMETER)

        foundation = GenericElement("foundation_456", "foundation")
        foundation.define_parameter("width", ValueType.FLOAT, Unit.MILLIMETER)
        foundation.set_value("width", 2500.0, Unit.MILLIMETER)

        # Add object reference from pole to foundation
        repo.add_object_reference(pole, "foundation_connection", foundation)

        # Save both elements
        repo.save_all([pole, foundation])

        # Load pole and verify reference
        loaded_pole = repo.load("pole_123")
        assert loaded_pole is not None

        # Get reference information
        ref_info = repo.get_object_reference_info(loaded_pole, "foundation_connection")
        assert ref_info is not None
        assert ref_info["target_id"] == "foundation_456"
        assert ref_info["target_type"] == "foundation"

        # Resolve reference to actual object
        referenced_foundation = repo.resolve_object_reference(
            loaded_pole, "foundation_connection"
        )
        assert referenced_foundation is not None
        assert referenced_foundation.element_id == "foundation_456"

        ref_element = repo.resolve_object_reference(loaded_pole, "foundation_connection")  
        assert ref_element is not None
        param_value = ref_element.value_by("width")
        assert param_value is not None
        assert param_value.value == 2500.0

    def test_repository_file_save_and_load_json(self):
        """Test file-based save and load operations with JSON format."""
        container_registry = ContainerRegistry()
        container_registry.register_container_type(MockContainerForRepo)

        repo = ElementRepository(container_registry)

        # Create elements with various data
        elements = []

        # Pole with container
        pole = GenericElement("pole_001", "pole")
        pole.define_parameter("height", ValueType.FLOAT, Unit.MILLIMETER)
        pole.set_value("height", 12000.0, Unit.MILLIMETER)
        test_container = MockContainerForRepo("pole_data")
        pole.add_container("test_container", test_container.serialize())
        elements.append(pole)

        # Foundation
        foundation = GenericElement("foundation_001", "foundation")
        foundation.define_parameter("width", ValueType.FLOAT, Unit.MILLIMETER)
        foundation.define_parameter("concrete_grade", ValueType.STRING, Unit.NONE)
        foundation.set_value("width", 2000.0, Unit.MILLIMETER)
        foundation.set_value("concrete_grade", "C30/37", Unit.NONE)
        elements.append(foundation)

        # Save all to repository
        repo.save_all(elements)

        # Save to file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_file = f.name

        try:
            repo.save_to_file(temp_file, format="json")

            # Create new repository and load from file
            new_repo = ElementRepository(container_registry)
            loaded_elements = new_repo.load_from_file(temp_file, format="json")

            assert len(loaded_elements) == 2

            # Verify pole
            loaded_pole = next(e for e in loaded_elements if e.element_id == "pole_001")
            pole_height = loaded_pole.value_by("height")
            assert pole_height is not None
            assert pole_height.value == 12000.0
            assert loaded_pole.has_container("test_container")

            # Verify foundation
            loaded_foundation = next(
                e for e in loaded_elements if e.element_id == "foundation_001"
            )
            foundation_width = loaded_foundation.value_by("width")
            assert foundation_width is not None
            assert foundation_width.value == 2000.0
            foundation_grade = loaded_foundation.value_by("concrete_grade")
            assert foundation_grade is not None  
            assert foundation_grade.value == "C30/37"

        finally:
            os.unlink(temp_file)

    def test_repository_container_reconstruction(self):
        """Test container reconstruction through registry during load."""
        container_registry = ContainerRegistry()
        container_registry.register_container_type(MockContainerForRepo)

        repo = ElementRepository(container_registry)

        # Create element with container
        element = GenericElement("test_001", "test")
        test_container = MockContainerForRepo("important_data")
        element.add_container("test_container", test_container.serialize())

        repo.save(element)

        # Load element and reconstruct container
        loaded_element = repo.load("test_001")
        assert loaded_element is not None

        # Use repository method to reconstruct container
        reconstructed_container = repo.reconstruct_container(
            loaded_element, "test_container"
        )

        assert reconstructed_container is not None
        assert isinstance(reconstructed_container, MockContainerForRepo)
        assert reconstructed_container.test_data == "important_data"

    def test_repository_missing_container_type_handling(self):
        """Test graceful handling of missing container types."""
        container_registry = ContainerRegistry()
        repo = ElementRepository(container_registry)

        # Create element with container data but no registered type
        element = GenericElement("test_001", "test")
        unknown_container_data = {"unknown": "data", "type": "mystery"}
        element.add_container("mystery_container", unknown_container_data)

        repo.save(element)

        # Load element - should work even without container type registered
        loaded_element = repo.load("test_001")
        assert loaded_element is not None
        assert loaded_element.has_container("mystery_container")

        # Container data should be preserved as raw data
        raw_data = loaded_element.get_container("mystery_container")
        assert raw_data == unknown_container_data

        # Trying to reconstruct should log warning but not fail
        reconstructed = repo.reconstruct_container(loaded_element, "mystery_container")
        assert reconstructed is None  # Cannot reconstruct without registered type

    def test_repository_element_deletion(self):
        """Test element deletion operations."""
        container_registry = ContainerRegistry()
        repo = ElementRepository(container_registry)

        # Create and save elements
        element1 = GenericElement("delete_me", "test")
        element2 = GenericElement("keep_me", "test")

        repo.save_all([element1, element2])

        # Verify both exist
        assert repo.load("delete_me") is not None
        assert repo.load("keep_me") is not None

        # Delete one element
        deleted = repo.delete("delete_me")
        assert deleted

        # Verify deletion
        assert repo.load("delete_me") is None
        assert repo.load("keep_me") is not None

        # Try to delete non-existent element
        deleted = repo.delete("not_exists")
        assert not deleted

    def test_repository_query_operations(self):
        """Test various query operations on the repository."""
        container_registry = ContainerRegistry()
        repo = ElementRepository(container_registry)

        # Create elements of different types
        elements = [
            GenericElement("pole_1", "pole"),
            GenericElement("pole_2", "pole"),
            GenericElement("foundation_1", "foundation"),
            GenericElement("track_1", "track"),
            GenericElement("track_2", "track"),
            GenericElement("track_3", "track"),
        ]

        # Add some parameters
        for i, elem in enumerate(elements):
            elem.set_value("sequence", i, Unit.NONE)

        repo.save_all(elements)

        # Test get by type
        poles = repo.get_by_type("pole")
        assert len(poles) == 2

        tracks = repo.get_by_type("track")
        assert len(tracks) == 3

        foundations = repo.get_by_type("foundation")
        assert len(foundations) == 1

        # Test get all
        all_elements = repo.get_all()
        assert len(all_elements) == 6

        # Test element existence
        assert repo.exists("pole_1")
        assert repo.exists("track_3")
        assert not repo.exists("non_existent")

    def test_repository_error_handling(self):
        """Test error handling in repository operations."""
        container_registry = ContainerRegistry()
        repo = ElementRepository(container_registry)

        # Test loading non-existent element
        result = repo.load("non_existent")
        assert result is None

        # Test invalid file operations
        with pytest.raises(RepositoryError):
            repo.save_to_file("/invalid/path/file.json")

        with pytest.raises(RepositoryError):
            repo.load_from_file("non_existent_file.json")

    def test_repository_concurrent_access_simulation(self):
        """Test repository behavior under simulated concurrent access."""
        container_registry = ContainerRegistry()
        repo = ElementRepository(container_registry)

        # Simulate concurrent saves (repository should handle gracefully)
        elements_batch_1 = [
            GenericElement("concurrent_1", "test"),
            GenericElement("concurrent_2", "test"),
        ]

        elements_batch_2 = [
            GenericElement("concurrent_3", "test"),
            GenericElement("concurrent_4", "test"),
        ]

        # Save batches
        repo.save_all(elements_batch_1)
        repo.save_all(elements_batch_2)

        # Verify all elements are accessible
        all_elements = repo.get_all()
        assert len(all_elements) == 4

        concurrent_ids = {elem.element_id for elem in all_elements}
        expected_ids = {"concurrent_1", "concurrent_2", "concurrent_3", "concurrent_4"}
        assert concurrent_ids == expected_ids

    def test_repository_metadata_and_statistics(self):
        """Test repository metadata and statistics functionality."""
        container_registry = ContainerRegistry()
        repo = ElementRepository(container_registry)

        # Add various elements
        elements = [
            GenericElement("meta_1", "pole"),
            GenericElement("meta_2", "pole"),
            GenericElement("meta_3", "foundation"),
            GenericElement("meta_4", "track"),
        ]

        repo.save_all(elements)

        # Get repository statistics
        stats = repo.get_statistics()

        assert stats["total_elements"] == 4
        assert stats["element_types"]["pole"] == 2
        assert stats["element_types"]["foundation"] == 1
        assert stats["element_types"]["track"] == 1

        # Get repository info
        info = repo.get_repository_info()
        assert "container_registry" in info
        assert "total_elements" in info
        assert info["storage_format"] == "memory"
