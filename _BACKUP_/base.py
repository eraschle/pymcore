class Component:
    """Base class for all components."""

    def __init__(self, name: str, component_type: ComponentType):
        self.name = name
        self.component_type = component_type

    def to_dict(self) -> dict[str, Any]:
        """
        Convert component to a dictionary for serialization.

        Returns
        -------
        dict
            Dictionary representation of the component
        """
        return {
            "name": self.name,
            "component_type": self.component_type.value,
        }


class ProcessEnumComponent(Component):
    """Base class for all components."""

    def __init__(self, element: IComponent, name: str, component_type: ComponentType):
        """
        Initialize a component with an element, name, and type.

        Parameters
        ----------
        element: InfrastructureElement
            The element to which this component belongs
        name: str
            Name of the component
        component_type: ComponentType
            Type of the component
        """
        super().__init__(name=name, component_type=component_type)
        self.element = element

    def to_dict(self) -> dict[str, Any]:
        """
        Convert component to a dictionary for serialization.

        Returns
        -------
        dict
            Dictionary representation of the component
        """
        return {
            "name": self.name,
            "component_type": self.component_type.value,
        }
