from dataclasses import dataclass

from base import OXObjectPot, OXObject, OXception
from data.OXData import OXData


@dataclass
class OXDatabase(OXObjectPot):
    """A container for OXData objects.

    This class extends OXObjectPot to provide a container specifically for
    OXData objects. It enforces type safety by ensuring that only OXData
    objects can be added to or removed from the database.

    Examples:
        >>> db = OXDatabase()
        >>> data1 = OXData()
        >>> data2 = OXData()
        >>> db.add_object(data1)
        >>> db.add_object(data2)
        >>> len(db)
        2
        >>> for data in db:
        ...     print(data.id)
        12345678-1234-5678-1234-567812345678
        87654321-4321-8765-4321-876543210987

    See Also:
        :class:`base.OXObjectPot.OXObjectPot`
        :class:`data.OXData.OXData`
    """

    def add_object(self, obj: OXObject):
        """Add an OXData object to the database.

        Args:
            obj (OXObject): The object to add. Must be an instance of OXData.

        Raises:
            OXception: If the object is not an instance of OXData.
        """
        if not isinstance(obj, OXData):
            raise OXception("Only OXData can be added to OXDatabase")
        super().add_object(obj)

    def remove_object(self, obj: OXObject):
        """Remove an OXData object from the database.

        Args:
            obj (OXObject): The object to remove. Must be an instance of OXData.

        Raises:
            OXception: If the object is not an instance of OXData.
            ValueError: If the object is not in the database.
        """
        if not isinstance(obj, OXData):
            raise OXception("Only OXData can be removed from OXDatabase")
        super().remove_object(obj)
