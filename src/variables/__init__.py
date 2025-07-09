"""Variables package for OptiX optimization framework.

This package contains classes for representing decision variables in optimization
problems. It provides a hierarchical structure of variable types, starting with
the base :class:`OXVariable` class and specialized subclasses for specific use cases.

Classes:
    OXVariable: Base class for decision variables
    OXVariableSet: Container for managing collections of variables
    OXDeviationVar: Specialized variable for goal programming

The variables in this package are designed to work seamlessly with the constraint
and solver components of the OptiX framework.

Example:
    >>> from variables import OXVariable, OXVariableSet
    >>> var = OXVariable(name="x1", lower_bound=0, upper_bound=10)
    >>> var_set = OXVariableSet()
    >>> var_set.add_object(var)
"""

from .OXVariable import OXVariable
from .OXVariableSet import OXVariableSet
from .OXDeviationVar import OXDeviationVar

__all__ = [
    "OXVariable",
    "OXVariableSet", 
    "OXDeviationVar"
]