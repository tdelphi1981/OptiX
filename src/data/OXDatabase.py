"""
OXDatabase Module
=================

This module provides a specialized container class for managing collections of OXData objects
in the OptiX optimization framework. It implements type-safe storage and retrieval operations
specifically designed for data objects with scenario support.

The OXDatabase class extends OXObjectPot to provide enhanced data management capabilities
including filtering, searching, and batch operations on data objects while maintaining
strict type safety to ensure only OXData instances are stored.

Key Features:
    - **Type Safety**: Enforces that only OXData objects can be added or removed
    - **Container Operations**: Full iterator and length support for data collections
    - **Object Management**: UUID-based object identification and relationship tracking
    - **Scenario Integration**: Works seamlessly with OXData scenario management

Architecture:
    The OXDatabase class inherits from OXObjectPot but adds specific validation to ensure
    that only OXData objects are managed. This provides both the flexibility of the base
    container class and the type safety required for data object management.

Example:
    Basic usage of OXDatabase for managing data objects:

    .. code-block:: python

        from data.OXDatabase import OXDatabase
        from data.OXData import OXData
        
        # Create a database and data objects
        db = OXDatabase()
        
        # Create demand data with scenarios
        demand1 = OXData()
        demand1.location = "Factory_A"
        demand1.quantity = 100
        demand1.create_scenario("High_Season", quantity=150)
        
        demand2 = OXData()
        demand2.location = "Factory_B" 
        demand2.quantity = 80
        demand2.create_scenario("High_Season", quantity=120)
        
        # Add objects to database
        db.add_object(demand1)
        db.add_object(demand2)
        
        # Iterate through all data objects
        for data in db:
            print(f"Location: {data.location}, Quantity: {data.quantity}")
        
        # Access by UUID
        found_data = db.get_object_by_id(demand1.id)

Module Dependencies:
    - dataclasses: For structured data class definitions
    - base: For OXObjectPot container base class and exception handling
    - data.OXData: For OXData type validation and integration

Notes:
    - Only OXData instances can be added to or removed from the database
    - The database maintains all OXObjectPot functionality including UUID-based lookups
    - Type validation occurs at runtime during add/remove operations
    - The database works transparently with OXData scenario switching
"""

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
