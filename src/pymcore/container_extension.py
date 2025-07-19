"""
Container extension system for PyM Core.

Provides base classes and registry for extending GenericElement with
new data types without Core knowing the specifics.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any


class ContainerNotFoundError(Exception):
    """Raised when a container type is not found in the registry."""

    pass


class ContainerExtension(ABC):
    """
    Base class for extending GenericElement with new data types.

    Containers are serializable extensions that can store complex data
    while maintaining generic serialization capabilities in the Core.
    """

    @abstractmethod
    def get_container_type(self) -> str:
        """
        Get unique identifier for this container type.

        Returns
        -------
        str
            Unique container type identifier
        """
        pass

    @abstractmethod
    def serialize(self) -> dict[str, Any]:
        """
        Convert container to JSON-serializable format.

        Returns
        -------
        dict[str, Any]
            JSON-serializable dictionary representation
        """
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, data: dict[str, Any]) -> ContainerExtension:
        """
        Create container instance from JSON data.

        Parameters
        ----------
        data : dict[str, Any]
            JSON data to deserialize

        Returns
        -------
        ContainerExtension
            Restored container instance
        """
        pass


class ContainerRegistry:
    """
    Registry for container extensions.

    Provides factory methods and type management without Core needing
    to know about specific container implementations.
    """

    def __init__(self):
        """Initialize empty container registry."""
        self._container_types: dict[str, type[ContainerExtension]] = {}

    def register_container_type(self, container_class: type[ContainerExtension]) -> None:
        """
        Register a container type in the registry.

        Parameters
        ----------
        container_class : type[ContainerExtension]
            Container class to register
        """
        # Create temporary instance to get container type
        temp_instance = container_class()
        container_type = temp_instance.get_container_type()

        # Register the class (idempotent - multiple registrations are safe)
        self._container_types[container_type] = container_class

    def is_registered(self, container_type: str) -> bool:
        """
        Check if a container type is registered.

        Parameters
        ----------
        container_type : str
            Container type identifier

        Returns
        -------
        bool
            True if container type is registered
        """
        return container_type in self._container_types

    def get_registered_types(self) -> list[str]:
        """
        Get list of all registered container types.

        Returns
        -------
        list[str]
            List of registered container type identifiers
        """
        return list(self._container_types.keys())

    def create_container(self, container_type: str, data: dict[str, Any]) -> ContainerExtension:
        """
        Factory method to create container instance from data.

        Core can use this method without knowing specific container types.

        Parameters
        ----------
        container_type : str
            Type of container to create
        data : dict[str, Any]
            Data to deserialize into container

        Returns
        -------
        ContainerExtension
            Created container instance

        Raises
        ------
        ContainerNotFoundError
            If container type is not registered
        """
        container_class = self._container_types.get(container_type)

        if container_class is None:
            raise ContainerNotFoundError(
                f"Container type '{container_type}' not registered. "
                f"Available types: {list(self._container_types.keys())}"
            )

        return container_class.deserialize(data)

    def get_container_class(self, container_type: str) -> type[ContainerExtension] | None:
        """
        Get the container class for a given type.

        Parameters
        ----------
        container_type : str
            Container type identifier

        Returns
        -------
        type[ContainerExtension] | None
            Container class if registered, None otherwise
        """
        return self._container_types.get(container_type)

    def unregister_container_type(self, container_type: str) -> bool:
        """
        Unregister a container type.

        Parameters
        ----------
        container_type : str
            Container type to unregister

        Returns
        -------
        bool
            True if container was unregistered, False if not found
        """
        if container_type in self._container_types:
            del self._container_types[container_type]
            return True
        return False

    def clear(self) -> None:
        """Clear all registered container types."""
        self._container_types.clear()

    def get_registry_info(self) -> dict[str, Any]:
        """
        Get information about the registry state.

        Returns
        -------
        dict[str, Any]
            Registry information including registered types and counts
        """
        return {
            "registered_types": list(self._container_types.keys()),
            "type_count": len(self._container_types),
            "registry_id": id(self),
        }
