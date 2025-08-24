"""
Object Container Module
=======================

This module provides a flexible container class for managing collections of OXObject instances
in the OptiX mathematical optimization framework. The OXObjectPot class serves as the foundation
for specialized containers used throughout the library for organizing variables, constraints,
objectives, and data objects.

The module implements advanced collection functionality including search capabilities, iteration
support, and type-safe object retrieval. It provides both attribute-based and predicate-based
search functionality to efficiently locate objects within large optimization problems.

Key Features:
    - **Object Storage**: Efficient storage and retrieval of OXObject instances
    - **Search Functionality**: Multiple search methods for finding objects by attributes or predicates
    - **Collection Interface**: Full Python collection protocol support (iteration, indexing, length)
    - **Type Safety**: UUID-based indexing with proper error handling
    - **Metadata Extraction**: Automatic extraction of object type information
    - **Base Container**: Foundation for specialized containers like OXVariableSet and OXDatabase

Architecture:
    The OXObjectPot extends OXObject to inherit UUID-based identity while providing collection
    functionality. It maintains an internal list of objects and provides various access patterns
    optimized for optimization problem construction and solving.

Usage:
    The class can be used directly or as a base for specialized containers:

    .. code-block:: python

        from base.OXObjectPot import OXObjectPot
        from base.OXObject import OXObject
        
        # Create a container
        pot = OXObjectPot()
        
        # Add objects
        obj1 = OXObject()
        obj2 = OXObject()
        pot.add_object(obj1)
        pot.add_object(obj2)
        
        # Search and retrieve
        found_objects = pot.search(name="variable1")
        specific_obj = pot[obj1.id]  # UUID-based access

Module Dependencies:
    - collections.abc: For callable type hints and abstract base classes
    - dataclasses: For dataclass functionality and field definitions
    - uuid: For UUID type annotations and handling
    - base.OXception: For custom exception handling
    - base.OXObject: For base object functionality
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from uuid import UUID

from base.OXObject import OXObject
from base.OXception import OXception


@dataclass
class OXObjectPot(OXObject):
    """
    A flexible container class for managing collections of OXObject instances.
    
    This class provides comprehensive functionality for storing, retrieving, and searching
    collections of OXObject instances in the OptiX optimization framework. It serves as
    the foundation for specialized containers like OXVariableSet, OXConstraintSet, and
    OXDatabase that manage specific types of optimization objects.
    
    The container supports multiple access patterns including direct UUID-based lookup,
    attribute-based searching, and predicate-based filtering. It implements the full
    Python collection protocol, making it integrate seamlessly with standard Python
    iteration and collection operations.
    
    Attributes:
        objects (list[OXObject]): The internal list of objects contained in this pot.
                                 Objects maintain their insertion order and can be
                                 accessed by index or UUID.
    
    Key Features:
        - **Flexible Search**: Search by attributes, predicates, or UUID
        - **Collection Protocol**: Full support for len(), iter(), contains(), and indexing
        - **Type Analysis**: Automatic extraction of contained object types
        - **Memory Efficient**: Stores objects by reference, not copy
        - **Thread Safe**: Basic operations are atomic (though concurrent modification requires external synchronization)
    
    Search Methods:
        - ``search(**kwargs)``: Find objects matching specific attribute values
        - ``search_by_function(func)``: Find objects satisfying a custom predicate
        - ``__getitem__(uuid)``: Direct UUID-based lookup
        - ``__contains__(obj)``: Check if object or UUID exists in container
    
    Example:
        Basic container operations:
        
        .. code-block:: python
        
            from base.OXObjectPot import OXObjectPot
            from base.OXObject import OXObject
            from dataclasses import dataclass
            
            # Create a specialized object type
            @dataclass
            class Variable(OXObject):
                name: str
                value: float = 0.0
                is_integer: bool = False
            
            # Create container and add objects
            pot = OXObjectPot()
            var1 = Variable(name="x1", value=10.5)
            var2 = Variable(name="x2", value=20.0, is_integer=True)
            
            pot.add_object(var1)
            pot.add_object(var2)
            
            # Various access methods
            print(f"Container size: {len(pot)}")  # 2
            
            # Search by attributes
            integer_vars = pot.search(is_integer=True)
            named_vars = pot.search(name="x1")
            
            # Search by predicate
            high_value_vars = pot.search_by_function(lambda x: x.value > 15.0)
            
            # Direct UUID access
            retrieved_var = pot[var1.id]
            
            # Iteration
            for var in pot:
                print(f"Variable: {var.name} = {var.value}")
    
    Inheritance:
        This class is designed to be extended by specialized containers:
        
        .. code-block:: python
        
            class VariableSet(OXObjectPot):
                def add_variable(self, name: str, **kwargs) -> Variable:
                    var = Variable(name=name, **kwargs)
                    self.add_object(var)
                    return var
                    
                def get_by_name(self, name: str) -> Variable:
                    results = self.search(name=name)
                    return results[0] if results else None
    
    Note:
        - Objects are stored by reference, so modifications to objects affect the container
        - UUID-based access is O(n) as it performs linear search
        - For large collections, consider maintaining additional index structures
        - The container does not enforce uniqueness - duplicate objects can be added
    """
    objects: list[OXObject] = field(default_factory=list)

    def search(self, **kwargs) -> list[OXObject]:
        """Search for objects with matching attribute values.

        Args:
            **kwargs: Attribute-value pairs to match against objects.
                An object is included in the result if it has all the specified
                attributes with the specified values.

        Returns:
            list[OXObject]: A list of objects that match the search criteria.

        Examples:
            >>> pot.search(name="variable1", lower_bound=0)
            [OXVariable(12345678-1234-5678-1234-567812345678)]
        """
        result = []
        for object in self.objects:
            should_include = True
            for key, value in kwargs.items():
                if not hasattr(object, key) or getattr(object, key) != value:
                    should_include = False
                    break
            if should_include:
                result.append(object)
        return result

    def search_by_function(self, function: Callable[[OXObject], bool]) -> list[OXObject]:
        """Search for objects that satisfy a given predicate function.

        Args:
            function (Callable[[OXObject], bool]): A function that takes an OXObject
                and returns True if the object should be included in the result.

        Returns:
            list[OXObject]: A list of objects for which the function returns True.

        Examples:
            >>> pot.search_by_function(lambda x: x.name.startswith("var"))
            [OXVariable(12345678-1234-5678-1234-567812345678)]
        """
        result = []
        for object in self.objects:
            if function(object):
                result.append(object)
        return result

    def add_object(self, obj: OXObject):
        """Add an object to the pot.

        Args:
            obj (OXObject): The object to add.
        """
        self.objects.append(obj)

    def remove_object(self, obj: OXObject):
        """Remove an object from the pot.

        Args:
            obj (OXObject): The object to remove.

        Raises:
            ValueError: If the object is not in the pot.
        """
        self.objects.remove(obj)

    def __getitem__(self, item):
        """Get an object by its UUID.

        Args:
            item (UUID): The UUID of the object to retrieve.

        Returns:
            OXObject: The object with the specified UUID.

        Raises:
            OXception: If the item is not a UUID or if no object with the given UUID is found.

        Examples:
            >>> pot = OXObjectPot()
            >>> obj = OXObject()
            >>> pot.add_object(obj)
            >>> retrieved = pot[obj.id]
            >>> retrieved == obj
            True
        """
        if not isinstance(item, UUID):
            raise OXception("Only UUID indices are accepted")
        for object in self.objects:
            if object.id == item:
                return object
        raise OXception("Object not found")

    def __iter__(self):
        """Return an iterator over the objects in the pot.

        Returns:
            iterator: An iterator over the objects.
        """
        return iter(self.objects)

    def __len__(self):
        """Return the number of objects in the pot.

        Returns:
            int: The number of objects.
        """
        return len(self.objects)

    def __contains__(self, obj: OXObject) -> bool:
        """Check if an object is in the pot.

        Args:
            obj (OXObject): The object to check.

        Returns:
            bool: True if the object is in the pot, False otherwise.
        """
        if isinstance(obj, UUID):
            for object in self.objects:
                if object.id == obj:
                    return True
        else:
            for object in self.objects:
                if object.id == obj.id:
                    return True
        return False

    @property
    def last_object(self):
        """Get the last object from the list of objects.

        Returns:
            OXObject: The last object in the objects list.

        Raises:
            IndexError: If the objects list is empty.

        Examples:
            >>> pot = OXObjectPot()
            >>> obj = OXObject()
            >>> pot.add_object(obj)
            >>> pot.last_object == obj
            True
        """
        return self.objects[-1]

    @property
    def first_object(self):
        """Get the first object from the list of objects.

        Returns:
            OXObject: The first object in the objects list.

        Raises:
            IndexError: If the objects list is empty.

        Examples:
            >>> pot = OXObjectPot()
            >>> obj = OXObject()
            >>> pot.add_object(obj)
            >>> pot.first_object == obj
            True
        """
        return self.objects[0]

    def get_object_types(self) -> list[str]:
        """Get a list of the types of objects in the pot.

        The type names are derived from the class_name attribute of each object,
        with the "OX" prefix removed and converted to lowercase.

        Returns:
            list[str]: A list of unique object type names.

        Examples:
            >>> pot.get_object_types()
            ['variable', 'constraint']
        """
        result = set()
        for obj in self.objects:
            temp_class_name = obj.class_name[(obj.class_name.rfind(".") + 1):].lower()
            if temp_class_name[:2] == "ox":
                temp_class_name = temp_class_name[2:]
            result.add(temp_class_name)
        return list(result)
