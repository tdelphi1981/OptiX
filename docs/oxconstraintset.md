# OXConstraintSet Documentation

## Overview

The `OXConstraintSet` class is a specialized container for managing collections of `OXConstraint` objects in the OptiX optimization framework. It extends the `OXObjectPot` base class to provide type-safe operations specifically designed for constraint management.

## Class Hierarchy

```
OXObject
└── OXObjectPot
    └── OXConstraintSet
```

## Purpose and Use Cases

`OXConstraintSet` is designed to:

1. **Organize constraints by category**: Group related constraints together (e.g., capacity constraints, demand constraints)
2. **Enable metadata-based queries**: Find constraints based on their metadata attributes
3. **Maintain type safety**: Ensure only `OXConstraint` objects are stored in the set
4. **Facilitate constraint management**: Provide specialized operations for constraint collections

## Key Features

- **Type-safe operations**: Only `OXConstraint` objects can be added or removed
- **Metadata-based querying**: Search constraints by their `related_data` attributes
- **Inheritance from OXObjectPot**: Inherits all container functionality like iteration, indexing, and length operations
- **Exception handling**: Proper error handling for invalid operations

## Class Definition

```python
@dataclass
class OXConstraintSet(OXObjectPot):
    """A specialized container for managing OXConstraint objects."""
```

## Methods

### `add_object(obj: OXObject)`

Adds an `OXConstraint` object to the constraint set.

**Parameters:**
- `obj` (OXObject): The constraint object to add. Must be an instance of `OXConstraint`.

**Raises:**
- `OXception`: If the object is not an instance of `OXConstraint`.

**Example:**
```python
constraint_set = OXConstraintSet()
constraint = OXConstraint(...)
constraint_set.add_object(constraint)
```

### `remove_object(obj: OXObject)`

Removes an `OXConstraint` object from the constraint set.

**Parameters:**
- `obj` (OXObject): The constraint object to remove. Must be an instance of `OXConstraint`.

**Raises:**
- `OXception`: If the object is not an instance of `OXConstraint`.

**Example:**
```python
constraint_set.remove_object(constraint)
```

### `query(**kwargs) -> list[OXObject]`

Queries constraints in the set by their metadata attributes.

**Parameters:**
- `**kwargs`: Keyword arguments representing metadata key-value pairs to match.

**Returns:**
- `list[OXObject]`: A list of `OXConstraint` objects that match the query criteria.

**Query Logic:**
- Uses AND logic: all specified key-value pairs must match
- At least one matching key must be found in the constraint's `related_data`
- Returns empty list if no matches are found

**Example:**
```python
# Query by single attribute
high_priority = constraint_set.query(priority="high")

# Query by multiple attributes (AND logic)
high_capacity = constraint_set.query(category="capacity", priority="high")
```

## Inherited Methods

From `OXObjectPot`, `OXConstraintSet` inherits:

- `__len__()`: Get the number of constraints in the set
- `__iter__()`: Iterate through constraints
- `__getitem__()`: Access constraints by index
- `__contains__()`: Check if a constraint is in the set
- `search_by_attributes()`: Search by object attributes
- `search_by_function()`: Search using a custom function
- `first` and `last` properties: Access first and last constraints

## Usage Examples

### Basic Usage

```python
from constraints import OXConstraint, OXConstraintSet, OXpression, RelationalOperators

# Create a constraint set
constraint_set = OXConstraintSet(name="Production Constraints")

# Create some constraints
expr1 = OXpression(variables=[var1.id, var2.id], weights=[2, 3])
constraint1 = OXConstraint(
    expression=expr1,
    relational_operator=RelationalOperators.LESS_THAN_EQUAL,
    rhs=100,
    name="Capacity constraint"
)

# Add metadata to constraints
constraint1.related_data["category"] = "capacity"
constraint1.related_data["priority"] = "high"
constraint1.related_data["department"] = "production"

# Add to constraint set
constraint_set.add_object(constraint1)

# Check set size
print(f"Total constraints: {len(constraint_set)}")

# Iterate through constraints
for constraint in constraint_set:
    print(f"Constraint: {constraint.name}")
```

### Metadata-based Organization

```python
# Create constraints with different metadata
capacity_constraint = OXConstraint(...)
capacity_constraint.related_data["type"] = "capacity"
capacity_constraint.related_data["priority"] = "high"

demand_constraint = OXConstraint(...)
demand_constraint.related_data["type"] = "demand"
demand_constraint.related_data["priority"] = "medium"

balance_constraint = OXConstraint(...)
balance_constraint.related_data["type"] = "balance"
balance_constraint.related_data["priority"] = "low"

# Add all to constraint set
constraint_set.add_object(capacity_constraint)
constraint_set.add_object(demand_constraint)
constraint_set.add_object(balance_constraint)

# Query by type
capacity_constraints = constraint_set.query(type="capacity")
demand_constraints = constraint_set.query(type="demand")

# Query by priority
high_priority_constraints = constraint_set.query(priority="high")

# Query by multiple criteria
high_capacity_constraints = constraint_set.query(type="capacity", priority="high")
```

### Advanced Usage with Multiple Constraint Sets

```python
# Create specialized constraint sets
capacity_set = OXConstraintSet(name="Capacity Constraints")
demand_set = OXConstraintSet(name="Demand Constraints")
balance_set = OXConstraintSet(name="Balance Constraints")

# Organize constraints by type
for constraint in all_constraints:
    if constraint.related_data.get("type") == "capacity":
        capacity_set.add_object(constraint)
    elif constraint.related_data.get("type") == "demand":
        demand_set.add_object(constraint)
    elif constraint.related_data.get("type") == "balance":
        balance_set.add_object(constraint)

# Query within specific sets
critical_capacity = capacity_set.query(priority="critical")
seasonal_demand = demand_set.query(period="seasonal")
```

## Integration with OptiX Framework

### With OXProblem

```python
from problem import OXProblem

# Create problem and constraint set
problem = OXProblem(name="Production Planning")
constraint_set = OXConstraintSet(name="Production Constraints")

# Add constraints to set with metadata
for constraint in production_constraints:
    constraint.related_data["phase"] = "production"
    constraint.related_data["validated"] = True
    constraint_set.add_object(constraint)

# Add constraint set to problem
problem.add_constraint_set(constraint_set)

# Query constraints in problem context
validated_constraints = constraint_set.query(validated=True)
production_constraints = constraint_set.query(phase="production")
```

### With Solvers

```python
from solvers.ortools import OXORToolsSolverInterface

# Create solver and add constraint set
solver = OXORToolsSolverInterface()
problem = OXProblem()

# Add constraint set to problem
problem.add_constraint_set(constraint_set)

# Solver can access organized constraints
solver.solve(problem)

# Query specific constraint types for analysis
linear_constraints = constraint_set.query(type="linear")
nonlinear_constraints = constraint_set.query(type="nonlinear")
```

## Best Practices

### 1. Consistent Metadata Schema

```python
# Define a consistent metadata schema
METADATA_SCHEMA = {
    "type": ["capacity", "demand", "balance", "flow"],
    "priority": ["critical", "high", "medium", "low"],
    "department": ["production", "logistics", "finance"],
    "phase": ["planning", "execution", "monitoring"]
}

# Apply metadata consistently
def add_constraint_with_metadata(constraint_set, constraint, metadata):
    for key, value in metadata.items():
        constraint.related_data[key] = value
    constraint_set.add_object(constraint)
```

### 2. Validation Functions

```python
def validate_constraint_metadata(constraint):
    """Validate constraint metadata against schema."""
    required_fields = ["type", "priority"]
    
    for field in required_fields:
        if field not in constraint.related_data:
            raise OXception(f"Missing required metadata field: {field}")
    
    if constraint.related_data["type"] not in METADATA_SCHEMA["type"]:
        raise OXception(f"Invalid constraint type: {constraint.related_data['type']}")
```

### 3. Query Helper Functions

```python
def get_critical_constraints(constraint_set):
    """Get all critical priority constraints."""
    return constraint_set.query(priority="critical")

def get_constraints_by_department(constraint_set, department):
    """Get constraints for a specific department."""
    return constraint_set.query(department=department)

def get_production_constraints(constraint_set):
    """Get all production-related constraints."""
    return constraint_set.query(phase="production")
```

## Error Handling

### Common Exceptions

```python
try:
    # This will raise OXception
    constraint_set.add_object(some_variable)  # Not a constraint
except OXception as e:
    print(f"Error: {e}")

try:
    # This will raise OXception
    constraint_set.remove_object(some_variable)  # Not a constraint
except OXception as e:
    print(f"Error: {e}")
```

### Graceful Query Handling

```python
def safe_query(constraint_set, **kwargs):
    """Safely query constraints with error handling."""
    try:
        results = constraint_set.query(**kwargs)
        return results
    except Exception as e:
        print(f"Query failed: {e}")
        return []

# Usage
results = safe_query(constraint_set, priority="high", type="capacity")
```

## Performance Considerations

### Efficient Querying

```python
# Cache frequently used queries
class ConstraintSetManager:
    def __init__(self, constraint_set):
        self.constraint_set = constraint_set
        self._cache = {}
    
    def get_by_priority(self, priority):
        if priority not in self._cache:
            self._cache[priority] = self.constraint_set.query(priority=priority)
        return self._cache[priority]
    
    def clear_cache(self):
        self._cache.clear()
```

### Batch Operations

```python
def add_constraints_with_metadata(constraint_set, constraints_metadata_pairs):
    """Add multiple constraints with metadata in batch."""
    for constraint, metadata in constraints_metadata_pairs:
        for key, value in metadata.items():
            constraint.related_data[key] = value
        constraint_set.add_object(constraint)
```

## Testing

### Unit Tests Example

```python
import unittest

class TestOXConstraintSet(unittest.TestCase):
    def setUp(self):
        self.constraint_set = OXConstraintSet()
        self.constraint = OXConstraint(...)
        self.constraint.related_data["type"] = "capacity"
        self.constraint.related_data["priority"] = "high"
    
    def test_add_constraint(self):
        self.constraint_set.add_object(self.constraint)
        self.assertEqual(len(self.constraint_set), 1)
    
    def test_add_invalid_object(self):
        with self.assertRaises(OXception):
            self.constraint_set.add_object("not a constraint")
    
    def test_query_by_metadata(self):
        self.constraint_set.add_object(self.constraint)
        results = self.constraint_set.query(type="capacity")
        self.assertEqual(len(results), 1)
    
    def test_query_multiple_criteria(self):
        self.constraint_set.add_object(self.constraint)
        results = self.constraint_set.query(type="capacity", priority="high")
        self.assertEqual(len(results), 1)
```

## Related Classes

- **OXObjectPot**: Base container class providing core functionality
- **OXConstraint**: The constraint objects managed by this set
- **OXObject**: Base class for all OptiX objects
- **OXception**: Custom exception class for error handling

## File Location

- **Source**: `/Users/tolgaberber/Work/Okul/OptiX/src/constraints/OXConstraintSet.py`
- **Package**: `constraints`
- **Import**: `from constraints import OXConstraintSet`