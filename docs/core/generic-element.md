# GenericElement - Universal Container

> *"Mache eine Sache und mache sie gut"* - GenericElement ist der universelle Container für Infrastructure Modeling

## 🎯 Overview

`GenericElement` ist das Herzstück von PyM Core - ein parameter-agnostischer Container, der **jedes** Infrastructure-Element repräsentieren kann, ohne Domain-spezifisches Wissen zu benötigen.

## 🏗️ Design Philosophy

### Unix-Prinzip: Universelle Abstraktion

```python
# Ein Interface für alle Domains
railway_pole = GenericElement("pole_001", "pole")
drainage_pipe = GenericElement("pipe_001", "pipe")
building_beam = GenericElement("beam_001", "beam")

# Identische API, verschiedene Domänen
for element in [railway_pole, drainage_pipe, building_beam]:
    element.set_parameter("length", 5000.0)
    length = element.get_parameter("length", 0.0)
```

### Separation of Concerns

- **Parameter Definitions**: Schema ohne Werte
- **Parameter Values**: Instanz-Daten ohne Schema
- **Business Logic**: Gehört in Application Layer

## 📊 Core Architecture

```python
class GenericElement:
    def __init__(self, element_id: str, element_type: str):
        self.element_id = element_id           # Unique identifier
        self.element_type = element_type       # Type classification
        self.parameters = {}                   # Instance values
        self._parameter_definitions = {}       # Schema definitions
```

### Parameter Definition vs. Value

```python
# 1. Define parameter schema (without value)
element.define_parameter("height", ValueType.FLOAT, Unit.MILLIMETER)

# 2. Set parameter value (with automatic conversion)
element.set_parameter("height", 5000.0)

# 3. Get parameter value (type-safe)
height = element.get_parameter("height", 0.0)  # → 5000.0
```

## 🔧 Core Operations

### Parameter Definition

**Location**: `src/pymcore/generic_element.py:55`

```python
def define_parameter(self, name: str, value_type: ValueType, unit: Unit) -> None:
    """Define parameter schema without setting value."""
    descriptor = ParameterDescriptor(
        semantic_key=name,
        data_type=self._map_value_type(value_type),
        unit=unit
    )
    self._parameter_definitions[name] = descriptor
```

**Key Features**:

- Schema-first approach
- Type and unit constraints
- No value assignment
- Validation preparation

### Parameter Management

```python
# Setting values with validation
element.set_parameter("height", 5000.0)
element.set_parameter("material", "steel")
element.set_parameter("active", True)

# Getting values with defaults
height = element.get_parameter("height", 0.0)     # → 5000.0
width = element.get_parameter("width", 100.0)     # → 100.0 (default)
material = element.get_parameter("material", "")  # → "steel"

# Checking existence
has_height = element.has_parameter("height")      # → True
has_weight = element.has_parameter("weight")      # → False
```

### Parameter Introspection

```python
# Discover available parameters
definitions = element.get_parameter_definitions()
for name, descriptor in definitions.items():
    print(f"{name}: {descriptor.data_type.__name__} ({descriptor.unit})")

# Get all current values
values = element.get_all_parameters()
for key, value in values.items():
    print(f"{key} = {value}")
```

## 🔄 Data Flow Patterns

### Creation Pattern

```python
# 1. Create element
element = GenericElement("B001", "BEAM")

# 2. Define schema
element.define_parameter("length", ValueType.FLOAT, Unit.MILLIMETER)
element.define_parameter("width", ValueType.FLOAT, Unit.MILLIMETER)
element.define_parameter("height", ValueType.FLOAT, Unit.MILLIMETER)

# 3. Set values
element.set_parameter("length", 5000.0)
element.set_parameter("width", 300.0)
element.set_parameter("height", 400.0)
```

### Factory Pattern

```python
class ElementFactory:
    """Factory für standard Railway Elements"""

    def create_beam(self, element_id: str, length: float, width: float, height: float) -> GenericElement:
        beam = GenericElement(element_id, "BEAM")

        # Define standard beam parameters
        beam.define_parameter("length", ValueType.FLOAT, Unit.MILLIMETER)
        beam.define_parameter("width", ValueType.FLOAT, Unit.MILLIMETER)
        beam.define_parameter("height", ValueType.FLOAT, Unit.MILLIMETER)
        beam.define_parameter("material", ValueType.STRING, Unit.NONE)

        # Set initial values
        beam.set_parameter("length", length)
        beam.set_parameter("width", width)
        beam.set_parameter("height", height)
        beam.set_parameter("material", "steel")

        return beam
```

## 🧪 Type System Integration

### Value Type Mapping

```python
def _map_value_type(self, value_type: ValueType) -> type:
    """Maps ValueType enum to Python types."""
    mapping = {
        ValueType.FLOAT: float,
        ValueType.INT: int,
        ValueType.STRING: str,
        ValueType.BOOL: bool
    }
    return mapping.get(value_type, str)
```

### Type Validation

```python
# Automatic type validation during parameter setting
element.set_parameter("height", "5000.0")  # String → float conversion
element.set_parameter("active", "true")    # String → bool conversion
element.set_parameter("count", 42.5)       # Float → int (if whole number)
```

## 📁 Serialization & Persistence

### JSON Serialization

```python
def to_dict(self) -> Dict[str, Any]:
    """Serialize element to dictionary."""
    return {
        "element_id": self.element_id,
        "element_type": self.element_type,
        "parameters": self.parameters,
        "parameter_definitions": {
            name: {
                "semantic_key": desc.semantic_key,
                "data_type": desc.data_type.__name__,
                "unit": desc.unit.value,
                "description": desc.description
            }
            for name, desc in self._parameter_definitions.items()
        }
    }
```

### Deserialization

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'GenericElement':
    """Deserialize element from dictionary."""
    element = cls(data["element_id"], data["element_type"])

    # Restore parameter definitions
    for name, desc_data in data.get("parameter_definitions", {}).items():
        element._parameter_definitions[name] = ParameterDescriptor(
            semantic_key=desc_data["semantic_key"],
            data_type=eval(desc_data["data_type"]),  # TODO: Safer type restoration
            unit=Unit(desc_data["unit"]),
            description=desc_data.get("description", "")
        )

    # Restore parameter values
    element.parameters.update(data.get("parameters", {}))

    return element
```

## 🔧 Integration Patterns

### With HybridParameterInterface

```python
# GenericElement provides the data container
element = GenericElement("P001", "POLE")
element.define_parameter("height", ValueType.FLOAT, Unit.MILLIMETER)

# HybridParameterInterface provides the access patterns
interface = HybridParameterInterface(element, "pole_params", registry)
interface.set_value("height", 5.0, Unit.METER)  # → 5000.0 mm in element

# Both access the same underlying data
direct_access = element.get_parameter("height")      # → 5000.0
interface_access = interface.get_value("height")    # → 5000.0
assert direct_access == interface_access
```

### With Repository

```python
# GenericElement is storage-agnostic
repository = ElementRepository()
repository.save(element)  # Automatic serialization

# Retrieval with reconstruction
loaded_element = repository.get_by_id("P001")
assert loaded_element.element_type == element.element_type
assert loaded_element.parameters == element.parameters
```

### With ContainerExtension

```python
# GenericElement supports hierarchical relationships
parent_element = GenericElement("track_001", "TRACK")
child_element = GenericElement("pole_001", "POLE")

container = ContainerExtension(parent_element)
container.add_child(child_element)

# Child maintains its identity while being part of hierarchy
assert child_element.element_id == "pole_001"
assert container.get_children()[0] == child_element
```

## ⚡ Performance Characteristics

### Memory Efficiency

- Lazy parameter definition creation
- Dictionary-based parameter storage (O(1) access)
- No unnecessary object creation

### Access Performance

```python
# O(1) operations
element.get_parameter("height")        # Direct dict lookup
element.set_parameter("height", 5000)  # Direct dict assignment
element.has_parameter("height")        # Dict key check

# O(n) operations (where n = number of parameters)
element.get_all_parameters()           # Dict iteration
element.get_parameter_definitions()    # Dict iteration
```

### Conversion Performance

- Type conversion only when needed
- No automatic validation unless requested
- Minimal object creation during operations

## 🎯 Design Decisions

### Why Not Inheritance?

```python
# ❌ Inheritance-based approach
class Beam(InfrastructureElement):
    def __init__(self):
        self.length = 0.0
        self.width = 0.0
        # Fixed schema, no flexibility

# ✅ Composition-based approach
beam = GenericElement("B001", "BEAM")
beam.define_parameter("length", ValueType.FLOAT, Unit.MILLIMETER)
# Flexible schema, universal container
```

### Why Parameter Definitions?

- **Type Safety**: Prevents invalid value assignments
- **Unit Conversion**: Enables automatic unit transformations
- **Validation**: Provides schema-based validation rules
- **Introspection**: Allows runtime discovery of available parameters

### Why String-based Parameter Keys?

- **Flexibility**: Easy integration with external systems
- **Serialization**: Direct JSON mapping without conversion
- **Debugging**: Human-readable parameter names
- **Interoperability**: Works with any naming convention

## 🚀 Future Extensions

### Planned Features

1. **Parameter Validation Rules**: Custom validation logic in descriptors
2. **Parameter Dependencies**: Parameters that depend on other parameters
3. **Parameter Calculations**: Automatic derived parameter computation
4. **Parameter History**: Track parameter value changes over time

### Extension Points

```python
# Custom parameter types
class CustomParameterDescriptor(ParameterDescriptor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.custom_validation = kwargs.get('validation_func')

    def validate(self, value: Any) -> bool:
        return self.custom_validation(value) if self.custom_validation else True

# Plugin-based parameter processors
class ParameterProcessor(ABC):
    @abstractmethod
    def process_parameter(self, element: GenericElement, key: str, value: Any) -> Any:
        pass
```

## 📚 Related Documentation

- **[Parameter System](./parameter-system.md)** - Parameter definitions and values
- **[Registry System](./registry-system.md)** - Semantic parameter mapping
- **[Repository Patterns](./repository.md)** - Storage and persistence
- **[HybridParameterInterface](../interfaces/hybrid-parameter.md)** - Access patterns

---

**GenericElement verkörpert Unix-Weisheit: Ein einfaches, universelles Tool, das durch Komposition mächtig wird.** 🏗️⚡
