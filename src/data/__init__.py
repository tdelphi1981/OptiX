"""
Data Management Module
======================

This module provides comprehensive data management capabilities for the OptiX optimization
framework. It implements scenario-based data objects and type-safe container classes that
enable sophisticated data modeling for optimization problems with multiple parameter sets.

The module is designed around the following key components:

Architecture:
    - **Data Objects**: Base data classes with scenario support for parameter variations
    - **Container Management**: Specialized database containers with type safety enforcement
    - **Scenario System**: Multi-scenario support for sensitivity analysis and what-if modeling
    - **Type Safety**: Strong typing and validation throughout the data management layer

Key Features:
    - Scenario-based parameter management for optimization problems
    - Type-safe container classes for organizing and accessing data objects
    - UUID-based object identification and relationship management
    - Integration with the broader OptiX framework architecture
    - Support for dynamic attribute access with scenario fallback mechanisms

Data Objects:
    - **OXData**: Base class for data objects with multi-scenario support and dynamic attribute access
    - **OXDatabase**: Specialized container for OXData objects with enforced type safety

Usage:
    Import data management classes for optimization problem modeling:

    .. code-block:: python

        from data import OXData, OXDatabase, NON_SCENARIO_FIELDS
        
        # Create data objects with scenario support
        demand_data = OXData()
        demand_data.quantity = 100
        demand_data.cost = 50.0
        
        # Create scenarios for sensitivity analysis
        demand_data.create_scenario("High_Demand", quantity=150, cost=55.0)
        demand_data.create_scenario("Low_Demand", quantity=75, cost=45.0)
        
        # Organize data objects in a database
        db = OXDatabase()
        db.add_object(demand_data)
        
        # Switch scenarios for different optimization runs
        demand_data.active_scenario = "High_Demand"
        # Run optimization with high demand parameters
        
        demand_data.active_scenario = "Low_Demand" 
        # Run optimization with low demand parameters

Notes:
    - All data objects inherit UUID-based identity from the OXObject base class
    - Scenario switching affects all attributes except those in NON_SCENARIO_FIELDS
    - Type validation in OXDatabase ensures data integrity and framework consistency
    - The scenario system enables Monte Carlo analysis and robust optimization approaches
"""

from .OXData import OXData, NON_SCENARIO_FIELDS
from .OXDatabase import OXDatabase

__all__ = [
    # Core data management classes
    "OXData",
    "OXDatabase",
    
    # Constants and configuration
    "NON_SCENARIO_FIELDS",
]