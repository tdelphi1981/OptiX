"""
Base Object Module
==================

This module provides the fundamental base class for all objects in the OptiX mathematical
optimization framework. It implements a standardized object identity system using UUID-based
identification and provides consistent object representation patterns across the entire library.

The module serves as the foundation for all OptiX objects, ensuring they have unique identifiers,
proper string representations, and hash functionality for use in collections and data structures.

Key Features:
    - **UUID-based Identity**: Every object gets a unique identifier for tracking and relationships
    - **Automatic Class Naming**: Objects automatically capture their fully qualified class name
    - **Consistent Representation**: Standardized string representation across all OptiX objects
    - **Hash Support**: Objects can be used as dictionary keys and in sets
    - **Inheritance Foundation**: Provides common functionality for all specialized OptiX classes

Architecture:
    The OXObject class uses Python's dataclass decorator for automatic initialization and
    the __post_init__ hook to set up class metadata. This ensures minimal overhead while
    providing rich object identity features.

Usage:
    This class is not typically instantiated directly but serves as a base class:

    .. code-block:: python

        from base.OXObject import OXObject
        
        class MyOptimizationObject(OXObject):
            name: str = "default"
            
        obj = MyOptimizationObject(name="example")
        print(obj.id)  # UUID automatically generated
        print(obj.class_name)  # Fully qualified class name

Module Dependencies:
    - dataclasses: For automatic initialization and field management
    - uuid: For unique identifier generation
    - utilities.class_loaders: For fully qualified class name resolution
"""

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class OXObject:
    """
    Base class for all objects in the OptiX mathematical optimization framework.
    
    This class provides the fundamental infrastructure for object identity, representation,
    and hashing that is used throughout the OptiX library. Every OptiX object inherits
    from this class to ensure consistent behavior and unique identification.
    
    The class automatically generates a unique UUID for each instance and captures the
    fully qualified class name for debugging and serialization purposes. This enables
    proper object tracking in complex optimization problems with many variables,
    constraints, and objectives.
    
    Attributes:
        id (UUID): A unique identifier for the object, automatically generated using uuid4().
                  This ID is immutable and serves as the primary key for object relationships.
        class_name (str): The fully qualified name of the object's class, automatically
                         populated in __post_init__. Used for debugging and serialization.
    
    Key Features:
        - **Unique Identity**: Each object gets a UUID that remains constant throughout its lifetime
        - **Type Information**: Automatic capture of fully qualified class names for debugging
        - **Hash Support**: Objects can be used in sets and as dictionary keys
        - **String Representation**: Consistent, informative string representation
        - **Dataclass Integration**: Leverages Python dataclasses for efficient initialization
    
    Example:
        Basic usage as a base class:
        
        .. code-block:: python
        
            from base.OXObject import OXObject
            from dataclasses import dataclass
            
            @dataclass
            class OptimizationVariable(OXObject):
                name: str
                lower_bound: float = 0.0
                upper_bound: float = float('inf')
            
            # Create an instance
            var = OptimizationVariable(name="x1", lower_bound=0.0, upper_bound=10.0)
            
            # Access inherited properties
            print(f"Variable ID: {var.id}")
            print(f"Class: {var.class_name}")
            print(f"String representation: {var}")
            
            # Use in collections
            variable_set = {var}  # Works because of __hash__
            variable_dict = {var: "some_value"}  # Works as dictionary key
    
    Note:
        - All OptiX classes should inherit from this class for consistency
        - The UUID is generated once during object creation and never changes
        - Class name is captured automatically and reflects the actual runtime type
        - Objects are hashable and can be used in sets and as dictionary keys
    """
    id: UUID = field(default_factory=uuid4)
    class_name: str = ""

    def __post_init__(self):
        """Initialize the class_name attribute.

        This method is automatically called after the object is initialized.
        It sets the class_name attribute to the fully qualified name of the object's class.

        See Also:
            :func:`utilities.class_loaders.get_fully_qualified_name`
        """
        from utilities.class_loaders import get_fully_qualified_name
        self.class_name = get_fully_qualified_name(type(self))

    def __str__(self):
        """Return a string representation of the object.

        Returns:
            str: A string in the format "class_name(id)".
        """
        return f"{self.class_name}({self.id})"

    def __repr__(self):
        """Return a string representation of the object for debugging.

        Returns:
            str: The same string as __str__.
        """
        return self.__str__()

    def __hash__(self):
        """Return a hash value for the object based on its id.

        This allows OXObject instances to be used as dictionary keys and in sets.

        Returns:
            int: A hash value based on the object's id.
        """
        return hash(self.id)
