"""Data package for the OptiX optimization framework.

This package contains classes for representing and managing data objects
in optimization problems. It provides support for scenario-based data
management and database containers for organizing data objects.

Classes:
    OXData: Base class for data objects with scenario support. Allows storing
        different attribute values for different scenarios (e.g., optimistic,
        pessimistic, realistic).
    OXDatabase: A specialized container for OXData objects that enforces type
        safety and provides database-like functionality.

Constants:
    NON_SCENARIO_FIELDS: List of field names that are not part of scenarios.

Examples:
    >>> from data import OXData, OXDatabase
    >>> # Create a data object with scenarios
    >>> data = OXData()
    >>> data.value = 10
    >>> data.create_scenario("Optimistic", value=20)
    >>> data.create_scenario("Pessimistic", value=5)
    >>> 
    >>> # Switch between scenarios
    >>> data.active_scenario = "Optimistic"
    >>> print(data.value)  # 20
    >>> data.active_scenario = "Pessimistic"
    >>> print(data.value)  # 5
    >>> 
    >>> # Store data objects in a database
    >>> db = OXDatabase()
    >>> db.add_object(data)
    >>> print(len(db))  # 1

The scenario system allows for sensitivity analysis and what-if scenarios
in optimization problems by maintaining multiple versions of data values
while using the same optimization model structure.
"""

from .OXData import OXData, NON_SCENARIO_FIELDS
from .OXDatabase import OXDatabase