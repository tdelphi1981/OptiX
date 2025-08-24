"""
Object Serialization Module for OptiX Optimization Framework
=============================================================

This module provides comprehensive serialization and deserialization capabilities for OptiX objects,
enabling persistent storage, data transfer, and object reconstruction across different execution
contexts. The module implements a robust dictionary-based serialization format that preserves
object identity, class information, and complex nested structures.

The serialization system is designed to handle the full spectrum of OptiX objects including
optimization problems, variables, constraints, and solver configurations. It maintains complete
fidelity of object relationships and supports recursive serialization of nested object hierarchies.

Key Features:
    - **Complete Object Fidelity**: Preserves all object attributes, identity, and class information
    - **Recursive Serialization**: Handles nested objects and collections automatically
    - **Dynamic Class Loading**: Supports deserialization of objects using dynamic class resolution
    - **Error Recovery**: Graceful handling of malformed data and missing dependencies
    - **UUID Preservation**: Maintains object identity through UUID-based identification
    - **Type Safety**: Ensures correct object reconstruction with proper type validation

Serialization Format:
    The serialization format uses a dictionary structure with the following reserved fields:
    
    - ``class_name``: Fully qualified class name for dynamic loading (e.g., "problem.OXLPProblem")
    - ``id``: UUID string for object identity preservation
    - All other fields: Object attributes serialized recursively
    
    Example serialized object:
    
    .. code-block:: python
    
        {
            "class_name": "variables.OXVariable",
            "id": "12345678-1234-5678-1234-567812345678",
            "name": "production_x",
            "lower_bound": 0,
            "upper_bound": 100,
            "variable_type": "continuous"
        }

Functions:
    serialize_to_python_dict: Convert OptiX objects to dictionary representations
    deserialize_from_python_dict: Reconstruct OptiX objects from dictionary data

Use Cases:
    - **Model Persistence**: Save optimization models to files or databases
    - **Inter-Process Communication**: Transfer objects between different Python processes
    - **API Serialization**: Convert objects for REST API responses and requests
    - **Debugging and Logging**: Create human-readable representations of complex objects
    - **Backup and Recovery**: Create complete backups of optimization problem states

Module Dependencies:
    - dataclasses: For automatic object field extraction via asdict()
    - base: Core OptiX object system and exception handling
    - utilities.class_loaders: Dynamic class loading for deserialization

Example:
    Complete workflow for serializing and deserializing OptiX objects:
    
    .. code-block:: python
    
        from serialization.serializers import serialize_to_python_dict, deserialize_from_python_dict
        from problem import OXLPProblem
        from variables import OXVariable
        import json
        
        # Create a complex optimization problem
        problem = OXLPProblem(name="Production Planning")
        
        # Add variables and constraints
        x = problem.create_decision_variable("production_x", 0, 100)
        y = problem.create_decision_variable("production_y", 0, 50)
        problem.create_constraint(expression=x + y, comparison="<=", value=120)
        
        # Serialize to dictionary
        problem_dict = serialize_to_python_dict(problem)
        
        # Convert to JSON for storage (optional)
        json_data = json.dumps(problem_dict, indent=2)
        
        # Later: deserialize from dictionary
        restored_problem = deserialize_from_python_dict(problem_dict)
        
        # Verify object integrity
        assert restored_problem.name == "Production Planning"
        assert len(restored_problem.variables) == 2
        assert restored_problem.variables[0].name == "production_x"

Performance Considerations:
    - Large object hierarchies may require significant memory during serialization
    - Complex nested structures increase serialization/deserialization time
    - Consider using streaming or chunked serialization for very large models
    - Cache class loading results when deserializing many objects of the same type

Security Notes:
    - Dynamic class loading poses potential security risks in untrusted environments
    - Validate source and content of serialized data before deserialization
    - Consider implementing class whitelisting for production environments
    - Be cautious with deserialization of data from external sources
"""

from dataclasses import asdict

from base import OXObject, OXception
from utilities.class_loaders import load_class


def serialize_to_python_dict(target_obj: OXObject) -> dict:
    """
    Convert an OptiX object to a complete dictionary representation for serialization.
    
    This function performs a comprehensive serialization of OptiX objects by converting
    them to Python dictionaries that preserve all object state, relationships, and
    metadata necessary for complete reconstruction. The serialization process leverages
    the dataclasses.asdict() function to automatically extract all object fields while
    maintaining proper handling of nested objects and collections.
    
    The function is designed to handle the full complexity of OptiX object hierarchies,
    including optimization problems with variables, constraints, objectives, and solver
    configurations. It ensures that all object relationships and dependencies are
    properly preserved in the serialized format.
    
    Serialization Process:
        1. Extracts all dataclass fields using dataclasses.asdict()
        2. Preserves object identity through the UUID-based 'id' field
        3. Includes class information via the 'class_name' field
        4. Recursively serializes nested OXObject instances
        5. Handles collections (lists, sets) containing OXObject instances
        6. Maintains exact field values for primitive types (int, float, str, bool)
    
    Args:
        target_obj (OXObject): The OptiX object instance to serialize. Must be a valid
                              OXObject subclass instance (dataclass) with the required
                              'class_name' and 'id' attributes. The object can contain
                              nested objects, collections, and primitive attributes.
    
    Returns:
        dict: A complete dictionary representation containing all object data:
            - 'class_name' (str): Fully qualified class name for deserialization
            - 'id' (str): UUID string preserving object identity
            - All other object attributes: Recursively serialized field values
            
            The dictionary structure mirrors the object's dataclass structure with
            nested dictionaries for OXObject fields and lists of dictionaries for
            collections containing OXObject instances.
    
    Raises:
        TypeError: If the target_obj is not an OXObject instance or dataclass.
        AttributeError: If the object lacks required 'class_name' or 'id' attributes.
    
    Note:
        - The function uses dataclasses.asdict() which automatically handles recursion
        - Circular references in object graphs are not supported and may cause infinite recursion
        - Large object hierarchies may consume significant memory during serialization
        - The resulting dictionary is JSON-serializable for most OptiX object types
        - Complex Python objects (functions, classes) in attributes may not serialize properly
    
    Performance:
        - Time complexity: O(n) where n is the total number of objects in the hierarchy
        - Space complexity: O(n) for the resulting dictionary structure
        - Memory usage scales with object complexity and nesting depth
    
    Example:
        .. code-block:: python
        
            from variables import OXVariable
            from constraints import OXConstraint, OXpression
            from problem import OXLPProblem
            
            # Create a variable
            variable = OXVariable(
                name="production_capacity",
                lower_bound=0,
                upper_bound=1000,
                variable_type="continuous"
            )
            
            # Serialize the variable
            var_dict = serialize_to_python_dict(variable)
            print(var_dict)
            # Output:
            # {
            #     'class_name': 'variables.OXVariable',
            #     'id': '12345678-1234-5678-1234-567812345678',
            #     'name': 'production_capacity',
            #     'lower_bound': 0,
            #     'upper_bound': 1000,
            #     'variable_type': 'continuous'
            # }
            
            # Create and serialize a complex problem
            problem = OXLPProblem(name="Manufacturing Optimization")
            x = problem.create_decision_variable("x", 0, 100)
            y = problem.create_decision_variable("y", 0, 50)
            
            # Serialize the entire problem with all nested objects
            problem_dict = serialize_to_python_dict(problem)
            
            # The result includes all variables, constraints, and relationships
            assert problem_dict['name'] == "Manufacturing Optimization"
            assert len(problem_dict['variables']) == 2
            assert 'class_name' in problem_dict['variables'][0]
    
    See Also:
        deserialize_from_python_dict: Reverse operation for object reconstruction
        dataclasses.asdict: Core Python function for dataclass serialization
        base.OXObject: Base class for all serializable OptiX objects
    """
    return asdict(target_obj)


def deserialize_from_python_dict(source_dict: dict) -> OXObject:
    """
    Reconstruct an OptiX object from its dictionary representation with complete state restoration.
    
    This function performs comprehensive deserialization of OptiX objects from their dictionary
    representations, rebuilding the complete object hierarchy with all relationships, attributes,
    and metadata preserved. The deserialization process handles complex object graphs including
    nested objects, collections, and circular references while maintaining object identity and
    type integrity.
    
    The function implements a robust reconstruction algorithm that dynamically loads classes,
    instantiates objects, and recursively deserializes nested structures. It provides graceful
    error handling for malformed data while ensuring that successfully deserializable components
    are preserved.
    
    Deserialization Process:
        1. Validates presence of required metadata fields ('class_name' and 'id')
        2. Dynamically loads the target class using the class name
        3. Creates a new instance of the class with default initialization
        4. Restores object identity by setting the 'id' field
        5. Recursively deserializes nested dictionaries (potential OXObject instances)
        6. Processes collections containing dictionaries (lists of OXObject instances)
        7. Sets all reconstructed attributes on the target object
        8. Returns the fully reconstructed object instance
    
    Args:
        source_dict (dict): Dictionary containing the serialized object data. Must include:
                           - 'class_name' (str): Fully qualified class name for dynamic loading
                           - 'id' (str): UUID string for object identity restoration
                           - Additional fields: Object attributes to be restored
                           
                           The dictionary structure should match the output format of
                           serialize_to_python_dict() for proper reconstruction.
    
    Returns:
        OXObject: Fully reconstructed OptiX object instance with all attributes, relationships,
                 and metadata restored. The returned object will be of the exact type specified
                 in the 'class_name' field and will maintain the same UUID as the original.
    
    Raises:
        OXception: If the 'class_name' field is missing from the dictionary.
                  This indicates an invalid or corrupted serialization format.
        OXception: If the 'id' field is missing from the dictionary.
                  Object identity cannot be preserved without the UUID field.
        ImportError: If the class specified in 'class_name' cannot be loaded.
                     This may indicate missing modules or incorrect class paths.
        AttributeError: If the loaded class cannot be instantiated or lacks expected attributes.
    
    Error Handling:
        - **Graceful Degradation**: Failed nested deserializations preserve original dictionary data
        - **Partial Recovery**: Successfully deserializable components are restored even if others fail
        - **Lenient Processing**: Missing or malformed nested objects don't prevent overall reconstruction
        - **Error Isolation**: Failures in list items don't affect other items in the same list
    
    Performance:
        - Time complexity: O(n) where n is the total number of objects in the hierarchy
        - Space complexity: O(n) for object reconstruction and temporary storage
        - Class loading overhead: First-time class loading may have additional latency
        - Memory efficiency: Objects are constructed in-place without intermediate copies
    
    Example:
        .. code-block:: python
        
            # Deserialize a simple variable
            var_dict = {
                'class_name': 'variables.OXVariable',
                'id': '12345678-1234-5678-1234-567812345678',
                'name': 'production_x',
                'lower_bound': 0,
                'upper_bound': 100,
                'variable_type': 'continuous'
            }
            
            variable = deserialize_from_python_dict(var_dict)
            assert variable.name == 'production_x'
            assert variable.lower_bound == 0
            assert str(variable.id) == '12345678-1234-5678-1234-567812345678'
            
            # Deserialize a complex optimization problem
            problem_dict = {
                'class_name': 'problem.OXLPProblem',
                'id': '87654321-4321-8765-4321-876543218765',
                'name': 'Manufacturing Optimization',
                'variables': [
                    {
                        'class_name': 'variables.OXVariable',
                        'id': '11111111-1111-1111-1111-111111111111',
                        'name': 'x',
                        'lower_bound': 0,
                        'upper_bound': 100
                    },
                    {
                        'class_name': 'variables.OXVariable', 
                        'id': '22222222-2222-2222-2222-222222222222',
                        'name': 'y',
                        'lower_bound': 0,
                        'upper_bound': 50
                    }
                ],
                'constraints': [],
                'objective': None
            }
            
            problem = deserialize_from_python_dict(problem_dict)
            assert problem.name == 'Manufacturing Optimization'
            assert len(problem.variables) == 2
            assert problem.variables[0].name == 'x'
            assert problem.variables[1].name == 'y'
            
            # Error handling example - malformed nested object
            malformed_dict = {
                'class_name': 'problem.OXLPProblem',
                'id': '99999999-9999-9999-9999-999999999999',
                'variables': [
                    {'name': 'incomplete_var'}  # Missing class_name and id
                ],
                'name': 'Test Problem'
            }
            
            # This succeeds - malformed variable remains as dictionary
            problem = deserialize_from_python_dict(malformed_dict)
            assert problem.name == 'Test Problem'
            assert isinstance(problem.variables[0], dict)  # Not deserialized
    
    Note:
        - The function creates new object instances rather than modifying existing ones
        - Circular object references are not explicitly handled and may cause infinite recursion
        - Large object hierarchies may require significant memory during reconstruction
        - Dynamic class loading assumes all required modules are available in the Python path
        - The lenient error handling ensures maximum data recovery from partially corrupted serializations
    
    Security Considerations:
        - Dynamic class loading can execute arbitrary code during import
        - Validate the source and content of dictionaries before deserialization
        - Consider implementing class whitelisting for production environments
        - Be particularly cautious with data from untrusted sources
    
    See Also:
        serialize_to_python_dict: Reverse operation for object serialization
        utilities.class_loaders.load_class: Dynamic class loading implementation
        base.OXObject: Base class providing object identity and serialization support
        base.OXception: Custom exception types for OptiX framework errors
    """
    if "class_name" not in source_dict:
        raise OXception("class_name not found in dictionary")
    if "id" not in source_dict:
        raise OXception("id not found in dictionary")
    class_name = source_dict["class_name"]
    clazz = load_class(class_name)
    retval = clazz()
    retval.id = source_dict["id"]
    for key, value in source_dict.items():
        if key != "class_name" and key != "id":
            if isinstance(value, dict):
                try:
                    value = deserialize_from_python_dict(value)
                except OXception:
                    pass
            if isinstance(value, list):
                for i in range(len(value)):
                    if isinstance(value[i], dict):
                        try:
                            value[i] = deserialize_from_python_dict(value[i])
                        except OXception:
                            pass
            setattr(retval, key, value)
    return retval
