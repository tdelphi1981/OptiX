"""
Object Serialization Package for OptiX Optimization Framework
==============================================================

This package provides comprehensive serialization and deserialization capabilities for the OptiX
optimization framework, enabling persistent storage, data transfer, and object reconstruction
across different execution contexts. The package implements a robust dictionary-based serialization
format that preserves complete object fidelity and supports complex optimization model hierarchies.

The serialization system is designed to handle the full spectrum of OptiX framework components
including optimization problems, variables, constraints, objectives, and solver configurations.
It maintains complete fidelity of object relationships and supports cross-platform compatibility
for distributed optimization scenarios.

Architecture:
    - **Core Serialization**: Dictionary-based format with metadata preservation
    - **Recursive Processing**: Automatic handling of nested objects and collections
    - **Dynamic Class Loading**: Runtime class resolution for object reconstruction
    - **Error Recovery**: Graceful handling of malformed data and missing dependencies
    - **Identity Preservation**: UUID-based object identity maintenance

Key Components:
    - **Serialization Functions**: Convert OptiX objects to dictionary representations
    - **Deserialization Functions**: Reconstruct OptiX objects from dictionary data
    - **Format Specifications**: Standardized dictionary structure for interoperability
    - **Error Handling**: Comprehensive exception management for data integrity

Key Features:
    - Complete object state preservation including attributes, relationships, and metadata
    - Recursive serialization of nested object hierarchies and collections
    - Dynamic class loading for robust object reconstruction across environments
    - UUID-based identity preservation for object tracking and relationship maintenance
    - JSON-compatible dictionary format for cross-platform data exchange
    - Graceful error handling with partial recovery for corrupted serializations
    - Support for all OptiX object types including problems, variables, and constraints

Serialization Entities:
    - **Optimization Problems**: LP, GP, and CSP problem instances with complete model state
    - **Decision Variables**: Variable definitions with bounds, types, and constraints
    - **Mathematical Expressions**: Linear combinations and coefficient representations
    - **Constraint Systems**: Constraint definitions with relationships and bounds
    - **Objective Functions**: Optimization objectives with direction and expressions
    - **Solver Configurations**: Solver settings and parameter specifications

Use Cases:
    - **Model Persistence**: Save and restore optimization models to/from files or databases
    - **Distributed Computing**: Transfer optimization problems between different processes or machines
    - **API Integration**: Serialize objects for REST API requests and responses
    - **Debugging and Analysis**: Create human-readable representations of complex optimization models
    - **Backup and Recovery**: Implement comprehensive backup systems for optimization workflows
    - **Version Control**: Track changes in optimization models over time

Usage:
    Import serialization functions for converting between objects and dictionaries:

    .. code-block:: python

        from serialization import serialize_to_python_dict, deserialize_from_python_dict
        from problem import OXLPProblem
        from variables import OXVariable
        import json
        
        # Create a complex optimization problem
        problem = OXLPProblem(name="Production Planning")
        x = problem.create_decision_variable("production_x", 0, 1000)
        y = problem.create_decision_variable("production_y", 0, 500)
        
        # Add constraints and objectives
        problem.create_constraint(x + 2*y, "<=", 1500)
        problem.create_objective_function(3*x + 2*y, direction="maximize")
        
        # Serialize the complete problem
        problem_dict = serialize_to_python_dict(problem)
        
        # Save to JSON file
        with open("optimization_model.json", "w") as f:
            json.dump(problem_dict, f, indent=2)
        
        # Later: load and deserialize
        with open("optimization_model.json", "r") as f:
            loaded_dict = json.load(f)
        
        restored_problem = deserialize_from_python_dict(loaded_dict)
        assert restored_problem.name == "Production Planning"
        assert len(restored_problem.variables) == 2

Format Specifications:
    The serialization format uses a standardized dictionary structure:
    
    - ``class_name`` (str): Fully qualified class name for dynamic loading
    - ``id`` (str): UUID string for object identity preservation  
    - Additional fields: Object attributes serialized recursively
    
    This format ensures cross-platform compatibility and enables reliable object reconstruction.

Notes:
    - All serialization operations preserve exact object state and relationships
    - Large optimization models may require significant memory during serialization
    - Dynamic class loading requires all necessary modules to be available
    - Consider security implications when deserializing data from untrusted sources
    - The package supports both simple objects and complex optimization model hierarchies

Performance Considerations:
    - Serialization time scales with object hierarchy complexity
    - Memory usage increases with model size and nesting depth
    - Class loading overhead occurs on first deserialization of each type
    - Consider caching mechanisms for frequently serialized/deserialized objects

Security Considerations:
    - Dynamic class loading can execute code during import operations
    - Validate data sources and implement appropriate security measures
    - Consider class whitelisting for production environments
    - Be cautious with deserialization of data from external sources
"""

from .serializers import (
    deserialize_from_python_dict,
    serialize_to_python_dict,
)

__all__ = [
    # Core serialization functions
    "serialize_to_python_dict",
    "deserialize_from_python_dict",
]