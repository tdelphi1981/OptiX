from dataclasses import dataclass

from base import OXObjectPot, OXObject, OXception
from variables.OXVariable import OXVariable


@dataclass
class OXVariableSet(OXObjectPot):
    """A container for OXVariable objects.

    This class extends OXObjectPot to provide a container specifically for
    OXVariable objects. It enforces type safety by ensuring that only OXVariable
    objects can be added to or removed from the set. It also provides a query
    method for finding variables based on their related_data attributes.

    Examples:
        >>> var_set = OXVariableSet()
        >>> var1 = OXVariable(name="x1")
        >>> var2 = OXVariable(name="x2")
        >>> var_set.add_object(var1)
        >>> var_set.add_object(var2)
        >>> len(var_set)
        2
        >>> for var in var_set:
        ...     print(var.name)
        x1
        x2

    See Also:
        :class:`base.OXObjectPot.OXObjectPot`
        :class:`variables.OXVariable.OXVariable`
    """

    def add_object(self, obj: OXObject):
        """Add an OXVariable object to the set.

        Args:
            obj (OXObject): The object to add. Must be an instance of OXVariable.

        Raises:
            OXception: If the object is not an instance of OXVariable.
        """
        if not isinstance(obj, OXVariable):
            raise OXception("Only OXVariable can be added to OXVariableSet")
        super().add_object(obj)

    def remove_object(self, obj: OXObject):
        """Remove an OXVariable object from the set.

        Args:
            obj (OXObject): The object to remove. Must be an instance of OXVariable.

        Raises:
            OXception: If the object is not an instance of OXVariable.
            ValueError: If the object is not in the set.
        """
        if not isinstance(obj, OXVariable):
            raise OXception("Only OXVariable can be removed from OXVariableSet")
        super().remove_object(obj)

    def query(self, **kwargs) -> list[OXObject]:
        """Search for variables based on their related_data attributes.

        This method searches for variables that have the specified key-value pairs
        in their related_data dictionary.

        Args:
            **kwargs: Key-value pairs to match against variables' related_data.
                A variable is included in the result if it has all the specified
                keys with the specified values.

        Returns:
            list[OXObject]: A list of variables that match the query.

        Raises:
            OXception: If a non-OXVariable object is found in the set (which
                should not happen).

        Examples:
            >>> var1.related_data["customer"] = customer1.id
            >>> var2.related_data["customer"] = customer2.id
            >>> result = var_set.query(customer=customer1.id)
            >>> len(result)
            1
            >>> result[0].name
            'x1'
        """

        def query_function(obj: OXObject):
            if isinstance(obj, OXVariable):
                number_of_keys_found = 0
                for key, value in kwargs.items():
                    if key in obj.related_data:
                        number_of_keys_found += 1
                        if obj.related_data[key] != value:
                            return False
                if number_of_keys_found == 0:
                    return False
                return True
            else:
                raise OXception("This should not happen.")

        return self.search_by_function(query_function)
