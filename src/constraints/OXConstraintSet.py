"""
Constraint Set Module for OptiX Optimization Framework
=======================================================

This module provides a specialized container class for managing collections of
constraints in optimization problems. It extends the base OXObjectPot functionality
to create type-safe constraint collections with enhanced query capabilities.

The module implements a container pattern specifically designed for OXConstraint
objects, ensuring type safety while providing efficient storage, retrieval, and
organization of constraints in optimization models.

Classes:
    OXConstraintSet: Type-safe container for managing collections of OXConstraint objects

Key Features:
    - Type-safe constraint management with runtime validation
    - Metadata-based constraint querying and filtering
    - Integration with the OXObjectPot container system
    - Support for constraint categorization and organization
    - Efficient iteration and manipulation of constraint collections

Module Dependencies:
    - dataclasses: For structured container definitions
    - base: For core OptiX object system and container patterns
    - constraints: For OXConstraint class integration

Example:
    Basic constraint set usage for organizing constraints by category:

    .. code-block:: python

        from constraints import OXConstraint, OXConstraintSet, OXpression, RelationalOperators
        
        # Create a constraint set for capacity constraints
        capacity_set = OXConstraintSet(name="Production Capacity Constraints")
        
        # Create and categorize constraints
        for i, constraint in enumerate(production_constraints):
            constraint.related_data["category"] = "capacity"
            constraint.related_data["priority"] = "high" if i < 5 else "medium"
            constraint.related_data["department"] = f"dept_{i % 3}"
            capacity_set.add_object(constraint)
        
        # Query constraints by metadata
        high_priority = capacity_set.query(priority="high")
        dept_constraints = capacity_set.query(department="dept_0")
        capacity_constraints = capacity_set.query(category="capacity")
        
        # Iterate through all constraints
        for constraint in capacity_set:
            print(f"Constraint: {constraint.name} - Priority: {constraint.related_data.get('priority')}")
"""

from dataclasses import dataclass

from ..base import OXObjectPot, OXObject, OXception
from .OXConstraint import OXConstraint


@dataclass
class OXConstraintSet(OXObjectPot):
    """A specialized container for managing OXConstraint objects.

    OXConstraintSet extends OXObjectPot to provide a type-safe container specifically
    designed for managing collections of OXConstraint objects. It ensures that only
    OXConstraint instances can be added or removed from the set, and provides
    specialized query functionality for finding constraints based on their metadata.

    This class is particularly useful for organizing constraints in optimization
    problems by category, type, or other metadata attributes stored in the
    constraint's related_data dictionary.

    Attributes:
        Inherits all attributes from OXObjectPot:
        - objects (list[OXObject]): List of constraint objects in the set
        - id (str): Unique identifier for the constraint set
        - name (str): Human-readable name for the constraint set

    Methods:
        add_object(obj): Add an OXConstraint to the set
        remove_object(obj): Remove an OXConstraint from the set
        query(**kwargs): Find constraints by metadata attributes

    Raises:
        OXception: When attempting to add/remove non-OXConstraint objects

    Examples:
        >>> # Create a constraint set for capacity constraints
        >>> capacity_set = OXConstraintSet(name="Capacity Constraints")
        >>> 
        >>> # Add constraints with metadata
        >>> for i, constraint in enumerate(capacity_constraints):
        ...     constraint.related_data["category"] = "capacity"
        ...     constraint.related_data["priority"] = "high"
        ...     capacity_set.add_object(constraint)
        >>> 
        >>> # Query by metadata
        >>> high_priority = capacity_set.query(priority="high")
        >>> capacity_constraints = capacity_set.query(category="capacity")
        >>> 
        >>> # Check set size
        >>> print(f"Total constraints: {len(capacity_set)}")
        >>> 
        >>> # Iterate through constraints
        >>> for constraint in capacity_set:
        ...     print(f"Constraint: {constraint.name}")
    """

    def add_object(self, obj: OXObject):
        """Add an OXConstraint object to the constraint set.

        This method provides type-safe addition of constraint objects to the set.
        Only OXConstraint instances are allowed to be added to maintain the
        integrity of the constraint set.

        Args:
            obj (OXObject): The constraint object to add. Must be an instance of OXConstraint.

        Raises:
            OXception: If the object is not an instance of OXConstraint.

        Examples:
            >>> constraint_set = OXConstraintSet()
            >>> constraint = OXConstraint(...)
            >>> constraint_set.add_object(constraint)
            >>> print(len(constraint_set))  # 1
        """
        if not isinstance(obj, OXConstraint):
            raise OXception("Only OXConstraint can be added to OXConstraintSet")
        super().add_object(obj)

    def remove_object(self, obj: OXObject):
        """Remove an OXConstraint object from the constraint set.

        This method provides type-safe removal of constraint objects from the set.
        Only OXConstraint instances are allowed to be removed to maintain the
        integrity of the constraint set.

        Args:
            obj (OXObject): The constraint object to remove. Must be an instance of OXConstraint.

        Raises:
            OXception: If the object is not an instance of OXConstraint.

        Examples:
            >>> constraint_set = OXConstraintSet()
            >>> constraint = OXConstraint(...)
            >>> constraint_set.add_object(constraint)
            >>> constraint_set.remove_object(constraint)
            >>> print(len(constraint_set))  # 0
        """
        if not isinstance(obj, OXConstraint):
            raise OXception("Only OXConstraint can be removed from OXConstraintSet")
        super().remove_object(obj)

