from collections.abc import Callable
from dataclasses import dataclass, field
from uuid import UUID

from base.OXception import OXception
from base.OXObject import OXObject


@dataclass
class OXObjectPot(OXObject):
    """A container for OXObject instances.

    This class provides methods for storing, retrieving, and searching for OXObject instances.
    It serves as a base class for specialized containers like OXVariableSet and OXDatabase.

    Attributes:
        objects (list[OXObject]): The list of objects contained in this pot.

    Examples:
        >>> pot = OXObjectPot()
        >>> obj1 = OXObject()
        >>> obj2 = OXObject()
        >>> pot.add_object(obj1)
        >>> pot.add_object(obj2)
        >>> len(pot)
        2
        >>> for obj in pot:
        ...     print(obj.id)
        12345678-1234-5678-1234-567812345678
        87654321-4321-8765-4321-876543210987
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
                if not hasattr(object, key) and getattr(object, key) != value:
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
