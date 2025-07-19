# BIM Core Package - Implementation Specification

TARGET-PATH: /src/pymcore/...

## Principles

**LESS IS MORE**: 
- Do NOT invent fantasy parameters or elements
- Use only the examples provided (Railway infrastructure elements)
- No additional business logic beyond basic geometry and railway-specific calculations
- Keep it minimal and extensible

**Domain Focus: Railway Infrastructure**
- **Pole** (Mast): height, diameter, material, foundation_depth
- **Foundation** (Fundament): width, length, depth, concrete_grade  
- **Cantilever** (Ausleger): length, height, load_capacity, pole_connection
- **Track** (Gleis): length, gauge, rail_profile, curve_radius
- **Sleeper** (Schwelle): length, width, height, material, spacing
- **Future Extensions**: Pipes (Rohre), Manholes (Schächte) with gradient systems

## Architecture Overview

The BIM Core Package provides a universal container system with hybrid parameter management:

```
Core Package (src/pymcore/):
├── GenericElement          # Universal container
├── HybridParameterInterface # ENUM + Plugin parameter access  
├── ParameterRegistry       # Plugin system
├── ElementRepository       # Load/save operations
└── ContainerExtensions     # Dynamic container system

Application (src/pymapp/):
├── Pole, Foundation, Cantilever, Track, Sleeper  # Railway elements
├── RailwayParameters       # ENUM definitions
└── RailwayPlugin          # Parameter registration

Future (/src/pymsys/):
├── Pipe, Manhole          # Drainage elements  
├── GradientNormalization  # Slope calculation system
└── DrainagePlugin         # Parameter registration
```

## Core Components

### 1. GenericElement (Core)

```python
class GenericElement:
    """Universal container - parameter-agnostic"""
    
    def __init__(self, element_id: str, element_type: str):
        self.element_id = element_id
        self.element_type = element_type
        self._parameters: Dict[str, Any] = {}
        self._containers: Dict[str, Any] = {}  # NEW: Extension containers
    
    # Basic parameter operations
    def set_parameter(self, name: str, value: Any)
    def get_parameter(self, name: str, default: Any = None) -> Any
    def has_parameter(self, name: str) -> bool
    
    # NEW: Container extension system
    def add_container(self, container_type: str, container_data: Any)
    def get_container(self, container_type: str) -> Optional[Any]
    def has_container(self, container_type: str) -> bool
```

**Key Point**: GenericElement knows NOTHING about specific parameters or containers.

### 2. Hybrid Parameter System

#### ENUM Phase (Start)
```python
class ParameterRole(Enum):
    """Railway infrastructure parameter roles - keep minimal"""
    # Geometric dimensions
    PRIMARY_HEIGHT = "primary_height"      # Pole height, Foundation depth
    PRIMARY_LENGTH = "primary_length"      # Track length, Cantilever length  
    PRIMARY_WIDTH = "primary_width"        # Foundation width, Sleeper width
    DIAMETER = "diameter"                  # Pole diameter
    
    # Railway-specific
    GAUGE = "gauge"                        # Track gauge (1435mm standard)
    RAIL_PROFILE = "rail_profile"          # Rail type (UIC60, etc.)
    CURVE_RADIUS = "curve_radius"          # Track curvature
    LOAD_CAPACITY = "load_capacity"        # Cantilever load rating
    FOUNDATION_DEPTH = "foundation_depth"  # Pole foundation depth
    SLEEPER_SPACING = "sleeper_spacing"    # Distance between sleepers
    
    # Materials
    MATERIAL_TYPE = "material_type"        # Steel, concrete, wood
    CONCRETE_GRADE = "concrete_grade"      # C25/30, C30/37, etc.
    
    # Future: Drainage (do not implement yet)
    # GRADIENT = "gradient"                # Pipe gradient in %
    # INVERT_LEVEL = "invert_level"        # Bottom level of pipe/manhole
    # DO NOT ADD MORE without justification
```

#### Plugin Phase (Extension)
```python
@dataclass(frozen=True)
class ParameterDescriptor:
    semantic_key: str  # Must match ENUM values for migration
    data_type: Type
    unit: Optional[str] = None
    required: bool = True
```

#### **INTEGRATION POINT: ENUM ↔ Plugin**
```python
class ParameterRegistry:
    """Bridges ENUM and Plugin systems"""
    
    def register_from_enum(self, parameter_roles: Type[Enum]):
        """AUTO-CONVERTS ENUM to Plugin descriptors"""
        for role in parameter_roles:
            descriptor = ParameterDescriptor(
                semantic_key=role.value,  # SAME string as ENUM
                data_type=float,          # Default assumption
                unit="mm",               # Default assumption
                required=True
            )
            self.register_parameter(descriptor)
    
    def register_enum_mapping(self, mapping_name: str, enum_mapping: ParameterMapping):
        """Supports legacy ENUM mappings"""
        # Convert ENUM mapping to Plugin format automatically
```

### 3. HybridParameterInterface

```python
class HybridParameterInterface:
    """Unified interface for ENUM and Plugin access"""
    
    def __init__(self, element: GenericElement, mapping_name: str,
                 enum_mapping: Optional[ParameterMapping] = None,
                 registry: Optional[ParameterRegistry] = None):
        # Supports both ENUM and Plugin modes
    
    def get_value(self, role_or_key: Union[ParameterRole, str], default: Any = None):
        """Smart dispatcher: ENUM or string key"""
        if isinstance(role_or_key, ParameterRole):
            # ENUM mode
            return self._get_enum_value(role_or_key, default)
        else:
            # Plugin mode  
            return self._get_string_value(role_or_key, default)
```

**INTEGRATION POINT: The interface automatically detects ENUM vs Plugin mode**

### 4. Container Extension System

```python
class ContainerExtension(ABC):
    """Base for extending GenericElement with new data types"""
    
    @abstractmethod
    def get_container_type(self) -> str:
        """Unique identifier for this container type"""
        pass
    
    @abstractmethod
    def serialize(self) -> Dict[str, Any]:
        """Convert to JSON-serializable format"""
        pass
    
    @classmethod
    @abstractmethod  
    def deserialize(cls, data: Dict[str, Any]) -> 'ContainerExtension':
        """Create from JSON data"""
        pass

class ContainerRegistry:
    """Registry for container extensions - Core doesn't need to know specifics"""
    
    def __init__(self):
        self._container_types: Dict[str, Type[ContainerExtension]] = {}
    
    def register_container_type(self, container_class: Type[ContainerExtension]):
        """Register new container type"""
        container_type = container_class().get_container_type()
        self._container_types[container_type] = container_class
    
    def create_container(self, container_type: str, data: Dict[str, Any]) -> Optional[ContainerExtension]:
        """Factory method - Core can create without knowing specifics"""
        container_class = self._container_types.get(container_type)
        if container_class:
            return container_class.deserialize(data)
        return None
```

### 5. Repository Pattern (Core)

```python
class ElementRepository:
    """Core repository - handles ANY GenericElement regardless of content"""
    
    def __init__(self, container_registry: ContainerRegistry):
        self._elements: Dict[str, GenericElement] = {}
        self._container_registry = container_registry
    
    def save(self, element: GenericElement):
        """Saves element with all parameters and containers"""
        self._elements[element.element_id] = element
    
    def load(self, element_id: str) -> Optional[GenericElement]:
        """Loads element and reconstructs containers automatically"""
        # Core handles serialization/deserialization generically
    
    def save_to_file(self, filepath: str, format: str = "json"):
        """Streams to file - format agnostic"""
    
    def load_from_file(self, filepath: str, format: str = "json") -> List[GenericElement]:
        """Loads from file - auto-detects container types"""
```

**Key Point**: Repository serializes containers generically without knowing their specifics.

## **INTEGRATION POINT: Pydantic ↔ SQLModel Migration**

### JSON Phase (Now)
```python
class ElementDataJSON(BaseModel):
    """Pydantic model for JSON serialization"""
    element_id: str
    element_type: str
    parameters: Dict[str, Any]
    containers: Dict[str, Dict[str, Any]]  # Generic container storage

class ElementStream:
    def to_json(self, elements: List[GenericElement]) -> str:
        """Uses Pydantic for validation and serialization"""
        data = [ElementDataJSON(...) for element in elements]
        return json.dumps([item.dict() for item in data])
```

### DB Phase (Later)  
```python
class ElementDataDB(SQLModel, table=True):
    """SQLModel table - SAME structure as Pydantic"""
    __tablename__ = "elements"
    
    element_id: str = Field(primary_key=True)
    element_type: str
    parameters: Dict[str, Any] = Field(sa_column=JSON)
    containers: Dict[str, Any] = Field(sa_column=JSON)
    
    # Later: Can add relationships, indexes, etc.
```

**Migration Path**: Change only the persistence layer, not the business logic.

## Application Layer Examples

### Standard Elements
```python
class Pole:
    """Railway pole/mast implementation (Mast)"""
    
    def __init__(self, element: GenericElement, mapping_name: str, interface_config):
        self._element = element
        self._interface = element.get_hybrid_interface(mapping_name, interface_config)
    
    @property
    def height(self) -> float:
        return self._interface.get_value(ParameterRole.PRIMARY_HEIGHT, 0.0)
    
    @property
    def diameter(self) -> float:
        return self._interface.get_value(ParameterRole.DIAMETER, 0.0)
    
    @property
    def foundation_depth(self) -> float:
        return self._interface.get_value(ParameterRole.FOUNDATION_DEPTH, 0.0)
    
    def calculate_volume(self) -> float:
        """Basic cylindrical volume calculation"""
        radius = self.diameter / 2
        return 3.14159 * radius * radius * self.height
    
    def calculate_foundation_volume(self) -> float:
        """Foundation concrete volume (simplified cubic)"""
        # Simplified: foundation width = 3 * diameter
        foundation_width = self.diameter * 3
        return foundation_width * foundation_width * self.foundation_depth

class Foundation:
    """Railway foundation implementation (Fundament)"""
    
    @property
    def width(self) -> float:
        return self._interface.get_value(ParameterRole.PRIMARY_WIDTH, 0.0)
    
    @property  
    def length(self) -> float:
        return self._interface.get_value(ParameterRole.PRIMARY_LENGTH, 0.0)
    
    @property
    def depth(self) -> float:
        return self._interface.get_value(ParameterRole.PRIMARY_HEIGHT, 0.0)  # Reuse HEIGHT for depth
    
    def calculate_concrete_volume(self) -> float:
        """Concrete volume calculation"""
        return self.width * self.length * self.depth

class Cantilever:
    """Railway cantilever implementation (Ausleger)"""
    
    @property
    def length(self) -> float:
        return self._interface.get_value(ParameterRole.PRIMARY_LENGTH, 0.0)
    
    @property
    def load_capacity(self) -> float:
        return self._interface.get_value(ParameterRole.LOAD_CAPACITY, 0.0)
    
    def calculate_moment(self, load: float) -> float:
        """Maximum bending moment calculation"""
        return load * self.length

class Track:
    """Railway track implementation (Gleis)"""
    
    @property
    def length(self) -> float:
        return self._interface.get_value(ParameterRole.PRIMARY_LENGTH, 0.0)
    
    @property
    def gauge(self) -> float:
        return self._interface.get_value(ParameterRole.GAUGE, 1435.0)  # Standard gauge
    
    @property
    def curve_radius(self) -> float:
        return self._interface.get_value(ParameterRole.CURVE_RADIUS, 0.0)  # 0 = straight
    
    def is_curved(self) -> bool:
        """Check if track section is curved"""
        return self.curve_radius > 0
    
    def calculate_rail_length(self) -> float:
        """Total rail length (2 rails per track)"""
        if self.is_curved():
            # Arc length calculation: s = r * θ, where θ = length / radius
            angle = self.length / self.curve_radius
            arc_length = self.curve_radius * angle
            return arc_length * 2  # Two rails
        return self.length * 2

class Sleeper:
    """Railway sleeper implementation (Schwelle)"""
    
    @property
    def length(self) -> float:
        return self._interface.get_value(ParameterRole.PRIMARY_LENGTH, 0.0)
    
    @property
    def width(self) -> float:
        return self._interface.get_value(ParameterRole.PRIMARY_WIDTH, 0.0)
    
    @property
    def height(self) -> float:
        return self._interface.get_value(ParameterRole.PRIMARY_HEIGHT, 0.0)
    
    @property
    def spacing(self) -> float:
        return self._interface.get_value(ParameterRole.SLEEPER_SPACING, 600.0)  # Standard 60cm
    
    def calculate_volume(self) -> float:
        """Sleeper volume calculation"""
        return self.length * self.width * self.height
    
    @staticmethod
    def calculate_sleepers_needed(track_length: float, spacing: float = 600.0) -> int:
        """Calculate number of sleepers for track length"""
        return int(track_length / spacing) + 1
```

### Future Drainage Elements (Specification Only)
```python
# DO NOT IMPLEMENT YET - Specification for future development

class Pipe:
    """Drainage pipe implementation (Rohr/Leitung)"""
    
    # Parameters: diameter, length, material, gradient, invert_level_start, invert_level_end
    # Methods: calculate_flow_capacity(), normalize_gradient(), get_slope_percentage()

class Manhole:
    """Drainage manhole implementation (Schacht)"""
    
    # Parameters: diameter, depth, cover_level, invert_level
    # Methods: calculate_volume(), connect_pipes(), validate_levels()

class GradientNormalization:
    """System for normalizing pipe gradients"""
    
    # Methods: 
    # - normalize_gradient(start_level, end_level, length) -> gradient_percentage
    # - validate_minimum_slope(diameter, gradient) -> bool  
    # - calculate_invert_levels(cover_levels, depths) -> invert_levels
    # - save_gradient_system(elements) -> serialized_data
    # - load_gradient_system(serialized_data) -> elements
```

### Container Extensions Example
```python
class GeometryContainer(ContainerExtension):
    """Example: 3D geometry data container"""
    
    def __init__(self, vertices: List[Tuple[float, float, float]]):
        self.vertices = vertices
    
    def get_container_type(self) -> str:
        return "geometry"
    
    def serialize(self) -> Dict[str, Any]:
        return {"vertices": self.vertices}
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'GeometryContainer':
        return cls(data["vertices"])

# Usage in application
geometry = GeometryContainer([(0,0,0), (5000,0,0), (5000,300,0)])
element.add_container("geometry", geometry.serialize())
```

## Implementation Guidelines

### Phase 1: ENUM-based Start
1. Implement GenericElement with basic parameter operations
2. Create RailwayParameters ENUM with minimal roles
3. Implement HybridParameterInterface with ENUM support
4. Create Pole/Foundation/Track/Cantilever/Sleeper with ENUM-based properties
5. Implement JSON-based Repository

### Phase 2: Plugin System Addition  
1. Add ParameterRegistry and ParameterDescriptor
2. Extend HybridParameterInterface for Plugin support
3. Add migration helpers (ENUM → Plugin conversion)
4. Keep ENUM code working (backwards compatibility)

### Phase 3: Container Extensions
1. Implement ContainerExtension base class
2. Add ContainerRegistry to Core
3. Extend GenericElement with container operations
4. Update Repository for container serialization

### Phase 4: Railway-specific Containers
1. Create TrackGeometryContainer for curve data
2. Create LoadAnalysisContainer for cantilever stress data
3. Create MaterialContainer for pole/foundation specifications

### Phase 5: SQLModel Migration
1. Create SQLModel versions of Pydantic models
2. Update Repository to support both JSON and DB
3. Add relationship support for references (pole ↔ foundation, track ↔ sleepers)
4. Migrate data using same business logic

### Phase 6: Drainage Extension (Future)
1. Add drainage-specific ParameterRoles (GRADIENT, INVERT_LEVEL)
2. Implement Pipe/Manhole classes
3. Create GradientNormalization system
4. Add drainage-specific container types

## Critical Integration Points

**🔄 ENUM ↔ Plugin**: Same semantic keys, automatic conversion
**🔄 Pydantic ↔ SQLModel**: Same field structure, only persistence changes  
**🔄 Core ↔ Extensions**: Generic serialization, no specific knowledge required
**🔄 JSON ↔ DB**: Repository pattern abstracts storage details

## Testing Strategy

Focus on integration points:
- ENUM parameter access works identically to Plugin parameter access
- Container serialization/deserialization round-trips correctly
- Repository can save/load elements regardless of their container types
- Migration from ENUM to Plugin preserves data integrity
- Railway-specific calculations (pole volumes, track curves, cantilever moments)
- Future: Gradient normalization and drainage system integrity

## Error Handling

- Invalid parameter mappings: Clear error messages with migration hints
- Unknown container types: Graceful degradation (store as generic data)
- Missing required parameters: Fail fast with descriptive errors
- Type mismatches: Auto-conversion where possible, error otherwise

---

**Remember: Build the minimal viable system first, then extend thoughtfully. Each integration point should be seamless and maintain backwards compatibility.**
