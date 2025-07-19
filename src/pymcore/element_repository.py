"""
Element repository system for PyM Core.

Provides persistent storage for GenericElements with JSON serialization,
object reference management, and container reconstruction capabilities.
"""
from __future__ import annotations
import json
import logging
from typing import Any

from .generic_element import GenericElement
from .container_extension import ContainerRegistry, ContainerExtension, ContainerNotFoundError

logger = logging.getLogger(__name__)


class RepositoryError(Exception):
    """Raised when repository operations fail."""
    pass


class ElementRepository:
    """
    Repository for persistent storage and retrieval of GenericElements.
    
    Handles JSON serialization, object references with relative UUID paths,
    and automatic container reconstruction through the container registry.
    """
    
    def __init__(self, container_registry: ContainerRegistry):
        """
        Initialize element repository.
        
        Parameters
        ----------
        container_registry : ContainerRegistry
            Registry for container type management and reconstruction
        """
        self._container_registry = container_registry
        self._elements: dict[str, GenericElement] = {}
        self._object_references: dict[str, dict[str, str]] = {}  # element_id -> {ref_name: target_path}
        
    def save(self, element: GenericElement) -> None:
        """
        Save element to repository.
        
        Parameters
        ----------
        element : GenericElement
            Element to save
        """
        self._elements[element.element_id] = element
        logger.debug(f"Saved element {element.element_id} of type {element.element_type}")
    
    def save_all(self, elements: list[GenericElement]) -> None:
        """
        Save multiple elements to repository.
        
        Parameters
        ----------
        elements : list[GenericElement]
            Elements to save
        """
        for element in elements:
            self.save(element)
        logger.info(f"Saved {len(elements)} elements to repository")
    
    def load(self, element_id: str) -> GenericElement | None:
        """
        Load element from repository by ID.
        
        Parameters
        ----------
        element_id : str
            ID of element to load
            
        Returns
        -------
        GenericElement | None
            Loaded element or None if not found
        """
        element = self._elements.get(element_id)
        if element:
            logger.debug(f"Loaded element {element_id}")
        return element
    
    def get_all(self) -> list[GenericElement]:
        """
        Get all elements from repository.
        
        Returns
        -------
        list[GenericElement]
            All elements in repository
        """
        return list(self._elements.values())
    
    def get_by_type(self, element_type: str) -> list[GenericElement]:
        """
        Get all elements of a specific type.
        
        Parameters
        ----------
        element_type : str
            Type of elements to retrieve
            
        Returns
        -------
        list[GenericElement]
            Elements of the specified type
        """
        return [elem for elem in self._elements.values() if elem.element_type == element_type]
    
    def exists(self, element_id: str) -> bool:
        """
        Check if element exists in repository.
        
        Parameters
        ----------
        element_id : str
            ID of element to check
            
        Returns
        -------
        bool
            True if element exists
        """
        return element_id in self._elements
    
    def delete(self, element_id: str) -> bool:
        """
        Delete element from repository.
        
        Parameters
        ----------
        element_id : str
            ID of element to delete
            
        Returns
        -------
        bool
            True if element was deleted, False if not found
        """
        if element_id in self._elements:
            del self._elements[element_id]
            # Clean up any object references to/from this element
            if element_id in self._object_references:
                del self._object_references[element_id]
            logger.debug(f"Deleted element {element_id}")
            return True
        return False
    
    def add_object_reference(
        self, 
        source_element: GenericElement, 
        reference_name: str, 
        target_element: GenericElement
    ) -> None:
        """
        Add object reference between elements.
        
        Uses relative UUID paths for portability when repository is moved.
        
        Parameters
        ----------
        source_element : GenericElement
            Element that contains the reference
        reference_name : str
            Name of the reference
        target_element : GenericElement
            Element being referenced
        """
        # Create relative reference path: target_id:target_type
        reference_path = f"{target_element.element_id}:{target_element.element_type}"
        
        if source_element.element_id not in self._object_references:
            self._object_references[source_element.element_id] = {}
        
        self._object_references[source_element.element_id][reference_name] = reference_path
        
        logger.debug(
            f"Added object reference '{reference_name}' from {source_element.element_id} "
            f"to {target_element.element_id}"
        )
    
    def get_object_reference_info(
        self, 
        element: GenericElement, 
        reference_name: str
    ) -> dict[str, str] | None:
        """
        Get information about an object reference.
        
        Parameters
        ----------
        element : GenericElement
            Element containing the reference
        reference_name : str
            Name of the reference
            
        Returns
        -------
        dict[str, str] | None
            Reference info with target_id and target_type, or None if not found
        """
        element_refs = self._object_references.get(element.element_id, {})
        reference_path = element_refs.get(reference_name)
        
        if reference_path:
            # Parse reference path: target_id:target_type
            parts = reference_path.split(":", 1)
            if len(parts) == 2:
                return {"target_id": parts[0], "target_type": parts[1]}
        
        return None
    
    def resolve_object_reference(
        self, 
        element: GenericElement, 
        reference_name: str
    ) -> GenericElement | None:
        """
        Resolve object reference to actual element.
        
        Parameters
        ----------
        element : GenericElement
            Element containing the reference
        reference_name : str
            Name of the reference
            
        Returns
        -------
        GenericElement | None
            Referenced element or None if not found
        """
        ref_info = self.get_object_reference_info(element, reference_name)
        if ref_info:
            return self.load(ref_info["target_id"])
        return None
    
    def reconstruct_container(
        self, 
        element: GenericElement, 
        container_type: str
    ) -> ContainerExtension | None:
        """
        Reconstruct container from element data using registry.
        
        Parameters
        ----------
        element : GenericElement
            Element containing container data
        container_type : str
            Type of container to reconstruct
            
        Returns
        -------
        ContainerExtension | None
            Reconstructed container or None if type not registered
        """
        container_data = element.get_container(container_type)
        if container_data is None:
            return None
        
        try:
            return self._container_registry.create_container(container_type, container_data)
        except ContainerNotFoundError:
            logger.warning(
                f"Container type '{container_type}' not registered. "
                f"Data preserved as raw dict for element {element.element_id}"
            )
            return None
    
    def save_to_file(self, filepath: str, format: str = "json") -> None:
        """
        Save repository contents to file.
        
        Parameters
        ----------
        filepath : str
            Path to save file
        format : str
            File format ("json" currently supported)
            
        Raises
        ------
        RepositoryError
            If save operation fails
        """
        if format != "json":
            raise RepositoryError(f"Unsupported format: {format}")
        
        try:
            # Serialize all elements and references
            data = {
                "elements": [elem.to_dict(for_json=True) for elem in self._elements.values()],
                "object_references": self._object_references,
                "metadata": {
                    "format_version": "1.0",
                    "total_elements": len(self._elements),
                    "container_types": self._container_registry.get_registered_types()
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved repository with {len(self._elements)} elements to {filepath}")
            
        except Exception as e:
            raise RepositoryError(f"Failed to save repository to {filepath}: {e}")
    
    def load_from_file(self, filepath: str, format: str = "json") -> list[GenericElement]:
        """
        Load repository contents from file.
        
        Parameters
        ----------
        filepath : str
            Path to load file
        format : str
            File format ("json" currently supported)
            
        Returns
        -------
        list[GenericElement]
            Loaded elements
            
        Raises
        ------
        RepositoryError
            If load operation fails
        """
        if format != "json":
            raise RepositoryError(f"Unsupported format: {format}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Clear current repository
            self._elements.clear()
            self._object_references.clear()
            
            # Load elements
            elements = []
            for elem_data in data.get("elements", []):
                element = GenericElement.from_dict(elem_data)
                self.save(element)
                elements.append(element)
            
            # Load object references
            self._object_references = data.get("object_references", {})
            
            logger.info(f"Loaded repository with {len(elements)} elements from {filepath}")
            return elements
            
        except FileNotFoundError:
            raise RepositoryError(f"Repository file not found: {filepath}")
        except json.JSONDecodeError as e:
            raise RepositoryError(f"Invalid JSON in repository file {filepath}: {e}")
        except Exception as e:
            raise RepositoryError(f"Failed to load repository from {filepath}: {e}")
    
    def get_statistics(self) -> dict[str, Any]:
        """
        Get repository statistics.
        
        Returns
        -------
        dict[str, Any]
            Statistics about repository contents
        """
        # Count elements by type
        type_counts: dict[str, int] = {}
        for element in self._elements.values():
            type_counts[element.element_type] = type_counts.get(element.element_type, 0) + 1
        
        # Count containers by type
        container_counts: dict[str, int] = {}
        for element in self._elements.values():
            for container_type in element.get_container_types():
                container_counts[container_type] = container_counts.get(container_type, 0) + 1
        
        return {
            "total_elements": len(self._elements),
            "element_types": type_counts,
            "container_types": container_counts,
            "total_object_references": sum(len(refs) for refs in self._object_references.values()),
            "registered_container_types": len(self._container_registry.get_registered_types())
        }
    
    def get_repository_info(self) -> dict[str, Any]:
        """
        Get general repository information.
        
        Returns
        -------
        dict[str, Any]
            Repository configuration and status information
        """
        return {
            "total_elements": len(self._elements),
            "storage_format": "memory",
            "container_registry": self._container_registry.get_registry_info(),
            "object_references_enabled": True,
            "supported_formats": ["json"]
        }