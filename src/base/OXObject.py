from dataclasses import dataclass, field
from uuid import UUID, uuid4

from utilities.class_loaders import get_fully_qualified_name


@dataclass
class OXObject:
    """Base class for all objects in the OptiX library.

    This class provides a unique identifier and class name for all objects,
    as well as basic string representation and hash functionality.

    Attributes:
        id (UUID): A unique identifier for the object, automatically generated.
        class_name (str): The fully qualified name of the object's class.
            This is automatically set in __post_init__.

    Examples:
        >>> obj = OXObject()
        >>> print(obj)
        base.OXObject(12345678-1234-5678-1234-567812345678)

    Note:
        All classes in the OptiX library should inherit from this class
        to ensure consistent object identity and serialization.
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
