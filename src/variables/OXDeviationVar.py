"""
Deviation Variable Module
=========================

This module provides the OXDeviationVar class, a specialized decision variable 
designed for goal programming optimization problems within the OptiX framework. 
It extends the base OXVariable class to include goal programming-specific features 
such as deviation direction tracking and desirability indicators.

Goal programming is a multi-objective optimization technique that focuses on 
minimizing deviations from target goals rather than optimizing a single objective. 
Deviation variables measure the extent to which goals are over-achieved or under-achieved, 
providing the foundation for goal programming constraint formulations.

Key Features:
    - **Goal Programming Support**: Specialized variables for deviation measurement
    - **Desirability Tracking**: Boolean flags to indicate whether deviations are desired
    - **Direction Semantics**: Clear distinction between positive and negative deviations
    - **Inheritance Benefits**: Full OXVariable functionality with goal programming extensions

Core Components:
    - **OXDeviationVar**: Specialized variable class for goal programming deviations
    - **Desirability Flag**: Boolean indicator for optimization preference direction
    - **Variable Integration**: Seamless integration with standard optimization variables
    - **String Representation**: Enhanced display showing deviation characteristics

Use Cases:
    - Goal programming problems with multiple objectives and target values
    - Multi-criteria decision making with conflicting objectives
    - Soft constraint implementation where violations are penalized rather than forbidden
    - Priority-based optimization where different goals have varying importance levels
    - Resource allocation problems with multiple performance targets

Example:
    Creating deviation variables for goal programming models:

    .. code-block:: python

        from variables.OXDeviationVar import OXDeviationVar
        
        # Positive deviation (over-achievement) - typically undesired
        positive_deviation = OXDeviationVar(
            name="budget_overrun",
            description="Amount by which budget is exceeded",
            lower_bound=0,
            upper_bound=float('inf'),
            desired=False  # Over-spending is undesirable
        )
        
        # Negative deviation (under-achievement) - may be desired or undesired
        negative_deviation = OXDeviationVar(
            name="production_shortfall", 
            description="Amount by which production falls short of target",
            lower_bound=0,
            upper_bound=float('inf'),
            desired=False  # Under-production is undesirable
        )
        
        # Sometimes negative deviations might be desired (e.g., cost savings)
        cost_savings = OXDeviationVar(
            name="cost_under_budget",
            description="Amount by which actual cost is below budget",
            lower_bound=0,
            upper_bound=float('inf'), 
            desired=True  # Spending less than budget is desirable
        )

Module Dependencies:
    - dataclasses: For structured class definitions with automatic method generation
    - variables.OXVariable: For base decision variable functionality and inheritance
"""

from dataclasses import dataclass

from variables.OXVariable import OXVariable


@dataclass
class OXDeviationVar(OXVariable):
    """
    Specialized decision variable for goal programming deviation measurement.
    
    This class extends the base OXVariable to provide goal programming-specific
    functionality for measuring and tracking deviations from target goals. 
    Deviation variables are essential components of goal programming models where
    multiple objectives are balanced through the minimization of unwanted deviations.
    
    In goal programming, deviation variables come in pairs (positive and negative)
    to measure over-achievement and under-achievement relative to goal targets.
    The desirability flag helps optimization algorithms prioritize which deviations
    to minimize, supporting complex multi-objective decision making scenarios.
    
    Key Capabilities:
        - Goal programming deviation measurement with directional semantics
        - Desirability tracking for optimization objective formulation
        - Full integration with standard optimization variable operations
        - Enhanced string representation showing goal programming characteristics
        - Seamless compatibility with OXVariable-based constraint systems

    Mathematical Context:
        In goal programming, a typical goal constraint has the form:
        achievement_level + negative_deviation - positive_deviation = target_value
        
        Where:
        - achievement_level: actual performance or resource usage
        - negative_deviation: shortfall below target (under-achievement)
        - positive_deviation: excess above target (over-achievement)
        - target_value: desired goal level

    Attributes:
        desired (bool): Flag indicating whether this deviation is desirable in the
                       optimization context. False (default) means the deviation
                       should be minimized, while True means it may be acceptable
                       or even beneficial. This flag influences objective function
                       formulation in goal programming models.

    Performance:
        - Inherits all performance characteristics from OXVariable
        - Minimal overhead for the additional boolean flag
        - String representation includes desirability information with minimal cost

    Thread Safety:
        - Same thread safety characteristics as OXVariable
        - The desired flag is immutable after initialization for consistency

    Examples:
        Create deviation variables for different goal programming scenarios:
        
        .. code-block:: python
        
            from variables.OXDeviationVar import OXDeviationVar
            
            # Budget constraint - over-spending is undesirable
            budget_overrun = OXDeviationVar(
                name="budget_positive_deviation",
                description="Amount by which spending exceeds budget",
                lower_bound=0,
                upper_bound=float('inf'),
                desired=False  # Minimize over-spending
            )
            
            # Production target - under-production is undesirable  
            production_shortfall = OXDeviationVar(
                name="production_negative_deviation",
                description="Amount by which production falls short of target",
                lower_bound=0,
                upper_bound=float('inf'),
                desired=False  # Minimize under-production
            )
            
            # Quality improvement - exceeding quality targets may be desired
            quality_improvement = OXDeviationVar(
                name="quality_positive_deviation", 
                description="Amount by which quality exceeds minimum standards",
                lower_bound=0,
                upper_bound=float('inf'),
                desired=True  # Exceeding quality standards is good
            )
            
            # Capacity utilization - some under-utilization might be acceptable
            capacity_slack = OXDeviationVar(
                name="capacity_negative_deviation",
                description="Unused capacity below target utilization",
                lower_bound=0,
                upper_bound=100,  # Maximum 100% under-utilization
                desired=False  # Generally want to minimize unused capacity
            )
            
            # Display deviation characteristics
            print(budget_overrun)  # Shows desired status in string representation
            
            # Goal programming objective formulation example
            undesired_deviations = [budget_overrun, production_shortfall, capacity_slack]
            objective_terms = [dev for dev in undesired_deviations if not dev.desired]

    Note:
        - Deviation variables are typically non-negative in goal programming models
        - Pairs of positive/negative deviation variables are common for each goal
        - The desired flag influences objective function coefficient assignment
        - String representation clearly shows both variable name and desirability status

    See Also:
        :class:`variables.OXVariable.OXVariable`: Base variable class with bounds and relationships.
        :class:`constraints.OXConstraint.OXGoalConstraint`: Goal constraints that use deviation variables.
        :class:`variables.OXVariableSet.OXVariableSet`: Container for managing deviation variable collections.
    """
    desired: bool = False

    def __str__(self):
        """
        Return enhanced string representation including desirability status.
        
        Provides a comprehensive string representation that includes both the
        variable name from the parent class and the goal programming-specific
        desirability flag. This enhanced representation is useful for debugging,
        model visualization, and optimization solver interfaces.

        Returns:
            str: String in format "variable_name (desired: boolean_value)" that
                 clearly indicates both the variable identifier and its role
                 in the goal programming objective function.

        Examples:
            .. code-block:: python
            
                desired_dev = OXDeviationVar(name="quality_surplus", desired=True)
                undesired_dev = OXDeviationVar(name="cost_overrun", desired=False)
                
                print(desired_dev)    # Output: "quality_surplus (desired: True)"
                print(undesired_dev)  # Output: "cost_overrun (desired: False)"
        """
        return f"{super().__str__()} (desired: {self.desired})"
