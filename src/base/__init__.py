"""Base package for the OptiX optimization framework.

This package contains the fundamental classes and exceptions used throughout
the OptiX library. It provides the basic building blocks for object identity,
exception handling, and container management.

Classes:
    OXObject: Base class for all objects in the OptiX library with UUID-based identity.
    OXObjectPot: Container class for managing collections of OXObject instances.
    OXception: Custom exception class with detailed error context information.

Examples:
    >>> from base import OXObject, OXObjectPot, OXception
    >>> obj = OXObject()
    >>> pot = OXObjectPot()
    >>> pot.add_object(obj)
    >>> len(pot)
    1
"""

from .OXObject import OXObject
from .OXObjectPot import OXObjectPot
from .OXception import OXception
