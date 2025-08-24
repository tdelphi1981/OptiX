"""
Constraint Module for OptiX Optimization Framework
===================================================

This module provides constraint classes for representing and managing linear constraints
in optimization problems. It implements standard linear constraints and goal programming
constraints with support for multiple relational operators, deviation variables, and
comprehensive scenario management for sensitivity analysis.

The module is a core component of the OptiX framework's constraint system, enabling
the definition of mathematical relationships between variables that must be satisfied
by the optimization solver, with the ability to analyze these constraints under
different parameter scenarios.

Classes:
    RelationalOperators: Enumeration of comparison operators (>, >=, =, <, <=)
    OXConstraint: Standard linear constraint with expression, relational operator, and scenario support
    OXGoalConstraint: Goal programming constraint with positive and negative deviation variables

Key Features:
    - **Scenario-Based Constraint Management**: Support for multiple constraint scenarios
      with different RHS values, operators, and names for comprehensive sensitivity analysis
    - **Dynamic Attribute Access**: Transparent scenario switching for constraint parameters
      enabling seamless what-if analysis without constraint object duplication
    - Support for all standard relational operators
    - Automatic conversion from regular constraints to goal constraints
    - Fraction-based arithmetic for precise coefficient handling
    - Integration with OXpression for complex mathematical expressions
    - Deviation variable management for goal programming

Module Dependencies:
    - dataclasses: For structured constraint definitions
    - enum: For relational operator enumeration
    - fractions: For precise arithmetic operations
    - base: For core OptiX object system
    - constraints.OXpression: For mathematical expression handling
    - variables.OXDeviationVar: For goal programming deviation variables

Example:
    Basic constraint creation and scenario-based usage:

    .. code-block:: python

        from constraints import OXConstraint, OXpression, RelationalOperators
        from variables import OXVariable
        
        # Create variables
        x = OXVariable(name="x", lower_bound=0)
        y = OXVariable(name="y", lower_bound=0)
        
        # Create expression: 2x + 3y
        expr = OXpression(variables=[x.id, y.id], weights=[2, 3])
        
        # Create constraint with base scenario: 2x + 3y <= 10
        constraint = OXConstraint(
            expression=expr,
            relational_operator=RelationalOperators.LESS_THAN_EQUAL,
            rhs=10,
            name="Base capacity constraint"
        )
        
        # Create scenarios for sensitivity analysis
        constraint.create_scenario("High_Capacity", rhs=15, name="Expanded capacity")
        constraint.create_scenario("Low_Capacity", rhs=8, name="Reduced capacity")
        constraint.create_scenario("Equality", 
            relational_operator=RelationalOperators.EQUAL,
            rhs=12,
            name="Exact capacity requirement"
        )
        
        # Switch between scenarios
        print(f"Base: {constraint.rhs}")  # 10
        
        constraint.active_scenario = "High_Capacity"
        print(f"High: {constraint.rhs} - {constraint.name}")  # 15 - Expanded capacity
        
        constraint.active_scenario = "Equality"
        print(f"Equal: {constraint.rhs}, Op: {constraint.relational_operator}")  # 12, =
        
        # Convert to goal constraint for goal programming
        goal_constraint = constraint.to_goal()
        print(goal_constraint.negative_deviation_variable.desired)  # True
"""

from dataclasses import dataclass, field, fields
from enum import StrEnum
from fractions import Fraction
from typing import Any

from base import OXObject, OXception
from utilities.DynamicValue import DynamicFloat
from utilities.fraction import calculate_fraction
from variables.OXDeviationVar import OXDeviationVar
from .OXpression import OXpression

#: List of field names that are excluded from scenario management to prevent infinite loops
#: and maintain object integrity. These fields are always accessed from the base object.
NON_SCENARIO_FIELDS = ["active_scenario", "scenarios", "id", "class_name", "positive_deviation_variable",
                       "negative_deviation_variable", "expression"]


class RelationalOperators(StrEnum):
    """Enumeration of relational operators for constraints.

    These operators define the relationship between the left-hand side (expression)
    and right-hand side (rhs) of a constraint.

    Attributes:
        GREATER_THAN (str): The ">" operator.
        GREATER_THAN_EQUAL (str): The ">=" operator.
        EQUAL (str): The "=" operator.
        LESS_THAN (str): The "<" operator.
        LESS_THAN_EQUAL (str): The "<=" operator.
    """
    GREATER_THAN = ">"
    GREATER_THAN_EQUAL = ">="
    EQUAL = "="
    LESS_THAN = "<"
    LESS_THAN_EQUAL = "<="


@dataclass
class OXConstraint(OXObject):
    """A constraint in an optimization problem with scenario support.

    A constraint represents a relationship between an expression and a value,
    such as "2x + 3y <= 10". This class supports multiple scenarios, allowing
    different constraint parameters (RHS values, names, operators) to be defined
    for different optimization scenarios.

    The scenario system enables sensitivity analysis and what-if modeling by
    maintaining multiple constraint configurations within the same constraint object.

    Attributes:
        expression (OXpression): The left-hand side of the constraint.
        relational_operator (RelationalOperators): The operator (>, >=, =, <, <=).
        rhs (float | int): The right-hand side value.
        name (str): A descriptive name for the constraint.
        active_scenario (str): The name of the currently active scenario.
        scenarios (dict[str, dict[str, Any]]): Dictionary mapping scenario names
            to dictionaries of attribute values for that scenario.

    Examples:
        Basic constraint creation:
        
        >>> from constraints.OXpression import OXpression
        >>> expr = OXpression(variables=[x.id, y.id], weights=[2, 3])
        >>> constraint = OXConstraint(
        ...     expression=expr,
        ...     relational_operator=RelationalOperators.LESS_THAN_EQUAL,
        ...     rhs=10,
        ...     name="Capacity constraint"
        ... )
        
        Scenario-based constraint management:
        
        >>> # Create constraint with base values
        >>> constraint = OXConstraint(
        ...     expression=expr,
        ...     relational_operator=RelationalOperators.LESS_THAN_EQUAL,
        ...     rhs=100,
        ...     name="Production capacity"
        ... )
        >>> 
        >>> # Create scenarios with different RHS values
        >>> constraint.create_scenario("High_Capacity", rhs=150, name="High capacity scenario")
        >>> constraint.create_scenario("Low_Capacity", rhs=80, name="Reduced capacity scenario")
        >>> 
        >>> # Switch between scenarios
        >>> print(constraint.rhs)  # 100 (Default scenario)
        >>> 
        >>> constraint.active_scenario = "High_Capacity"
        >>> print(constraint.rhs)  # 150
        >>> print(constraint.name)  # "High capacity scenario"
        >>> 
        >>> constraint.active_scenario = "Low_Capacity"
        >>> print(constraint.rhs)  # 80
    """
    expression: OXpression = field(default_factory=OXpression)
    relational_operator: RelationalOperators = RelationalOperators.EQUAL
    rhs: float | int = 0
    name: str = ""
    active_scenario: str = "Default"
    scenarios: dict[str, dict[str, Any]] = field(default_factory=dict)

    def __getattribute__(self, item):
        """Custom attribute access that checks the active scenario first.

        When an attribute is accessed, this method first checks if it exists
        in the active scenario, and if not, falls back to the object's own attribute.
        This enables transparent scenario switching for constraint parameters.

        Args:
            item (str): The name of the attribute to access.

        Returns:
            Any: The value of the attribute in the active scenario, or the
                object's own attribute if not found in the active scenario.

        Examples:
            >>> constraint = OXConstraint(rhs=100)
            >>> constraint.create_scenario("High_RHS", rhs=150)
            >>> print(constraint.rhs)  # 100 (Default)
            >>> constraint.active_scenario = "High_RHS"
            >>> print(constraint.rhs)  # 150 (from scenario)
        """
        if item in NON_SCENARIO_FIELDS:  # Prevent Infinite Loop!
            return super().__getattribute__(item)

        # Check if item is a dataclass field
        obj_fields = super().__getattribute__('__dataclass_fields__')
        if item not in obj_fields:
            return super().__getattribute__(item)

        def get_current_value():
            current_scenarios = super(OXConstraint, self).__getattribute__('scenarios')
            current_active = super(OXConstraint, self).__getattribute__('active_scenario')
            current_scenario_values = current_scenarios.get(current_active, {})

            if current_scenario_values and item in current_scenario_values:
                return current_scenario_values[item]
            return super(OXConstraint, self).__getattribute__(item)

        current_value = get_current_value()
        if isinstance(current_value, (int, float)) and not isinstance(current_value, DynamicFloat):
            return DynamicFloat(get_current_value)
        return current_value


    def create_scenario(self, scenario_name: str, **kwargs):
        """Create a new scenario with the specified constraint attribute values.

        If the "Default" scenario doesn't exist yet, it is created first,
        capturing the constraint's current attribute values. This enables
        systematic scenario-based analysis while preserving the original
        constraint configuration.

        Args:
            scenario_name (str): The name of the new scenario.
            **kwargs: Constraint attribute-value pairs for the new scenario.
                     Common attributes include:
                     - rhs (float | int): Right-hand side value
                     - name (str): Constraint name for this scenario
                     - relational_operator (RelationalOperators): Constraint operator

        Raises:
            OXception: If an attribute in kwargs doesn't exist in the constraint object.

        Examples:
            Creating RHS scenarios for sensitivity analysis:
            
            >>> constraint = OXConstraint(
            ...     expression=expr,
            ...     relational_operator=RelationalOperators.LESS_THAN_EQUAL,
            ...     rhs=100,
            ...     name="Base capacity"
            ... )
            >>> 
            >>> # Create scenarios with different RHS values
            >>> constraint.create_scenario("High_Demand", rhs=150, name="Peak capacity")
            >>> constraint.create_scenario("Low_Demand", rhs=75, name="Reduced capacity")
            >>> constraint.create_scenario("Critical", rhs=200, name="Emergency capacity")
            >>> 
            >>> # Switch scenarios and access values
            >>> constraint.active_scenario = "High_Demand"
            >>> print(f"RHS: {constraint.rhs}, Name: {constraint.name}")
            >>> # Output: RHS: 150, Name: Peak capacity
            
            Creating operator scenarios for constraint type analysis:
            
            >>> constraint.create_scenario("Equality", 
            ...     relational_operator=RelationalOperators.EQUAL,
            ...     name="Exact capacity requirement"
            ... )
            >>> constraint.create_scenario("Lower_Bound",
            ...     relational_operator=RelationalOperators.GREATER_THAN_EQUAL,
            ...     name="Minimum capacity requirement"
            ... )
        """
        if 'Default' not in self.scenarios:
            self.scenarios['Default'] = {}
            obj_fields = fields(self)
            for field in obj_fields:
                if field.name not in NON_SCENARIO_FIELDS:
                    self.scenarios['Default'][field.name] = super().__getattribute__(field.name)
        self.scenarios[scenario_name] = {}
        for key, value in kwargs.items():
            if key not in NON_SCENARIO_FIELDS:
                if hasattr(self, key):
                    self.scenarios[scenario_name][key] = value
                else:
                    raise OXception(f"Constraint {self} has no attribute {key}")

    def reverse(self):
        """Reverse the relational operator of the constraint.

        This method changes the relational operator to its opposite:
        - GREATER_THAN becomes LESS_THAN
        - GREATER_THAN_EQUAL becomes LESS_THAN_EQUAL
        - EQUAL remains EQUAL
        - LESS_THAN becomes GREATER_THAN
        - LESS_THAN_EQUAL becomes GREATER_THAN_EQUAL

        Returns:
            OXConstraint: A new constraint with the reversed operator.
        """
        if self.relational_operator == RelationalOperators.EQUAL:
            raise OXception("Cannot reverse an equality constraint.")
        reversed_operator = {
            RelationalOperators.GREATER_THAN: RelationalOperators.LESS_THAN_EQUAL,
            RelationalOperators.GREATER_THAN_EQUAL: RelationalOperators.LESS_THAN,
            RelationalOperators.LESS_THAN: RelationalOperators.GREATER_THAN_EQUAL,
            RelationalOperators.LESS_THAN_EQUAL: RelationalOperators.GREATER_THAN
        }[self.relational_operator]

        return OXConstraint(
            expression=self.expression,
            relational_operator=reversed_operator,
            rhs=self.rhs,
            name=f"Inverse of {self.name}"
        )

    @property
    def rhs_numerator(self):
        """Get the numerator of the right-hand side as a fraction.

        Returns:
            int: The numerator of the right-hand side.
        """
        return calculate_fraction(self.rhs).numerator

    @property
    def rhs_denominator(self):
        """Get the denominator of the right-hand side as a fraction.

        Returns:
            int: The denominator of the right-hand side.
        """
        return calculate_fraction(self.rhs).denominator

    def to_goal(self, upper_bound: int | float | Fraction = 100) -> "OXGoalConstraint":
        """Convert this constraint to a goal constraint for goal programming.

        The conversion sets the relational operator to EQUAL and sets the
        desired deviation variables based on the original operator.

        Returns:
            OXGoalConstraint: A new goal constraint based on this constraint.

        See Also:
            :class:`OXGoalConstraint`
        """
        result = OXGoalConstraint()
        result.expression = self.expression
        result.relational_operator = RelationalOperators.EQUAL
        result.rhs = self.rhs
        result.name = self.name
        result.positive_deviation_variable.name = f"Positive deviation of {self.name}"
        result.negative_deviation_variable.name = f"Negative deviation of {self.name}"
        if self.relational_operator in [RelationalOperators.LESS_THAN, RelationalOperators.LESS_THAN_EQUAL]:
            result.negative_deviation_variable.desired = True
            result.negative_deviation_variable.upper_bound = upper_bound
            result.positive_deviation_variable.upper_bound = upper_bound
        elif self.relational_operator in [RelationalOperators.GREATER_THAN, RelationalOperators.GREATER_THAN_EQUAL]:
            result.positive_deviation_variable.desired = True
            result.positive_deviation_variable.upper_bound = upper_bound
            result.negative_deviation_variable.upper_bound = upper_bound
        return result


@dataclass
class OXGoalConstraint(OXConstraint):
    """A goal constraint for goal programming.

    A goal constraint extends a regular constraint by adding deviation variables
    that measure how much the constraint is violated. In goal programming, the
    objective is typically to minimize undesired deviations.

    Attributes:
        positive_deviation_variable (OXDeviationVar): The variable representing
            positive deviation from the goal.
        negative_deviation_variable (OXDeviationVar): The variable representing
            negative deviation from the goal.

    Examples:
        >>> goal = constraint.to_goal()
        >>> print(goal.positive_deviation_variable.desired)
        False
        >>> print(goal.negative_deviation_variable.desired)
        True

    See Also:
        :class:`OXConstraint`
        :class:`variables.OXDeviationVar.OXDeviationVar`
    """
    positive_deviation_variable: OXDeviationVar = field(default_factory=OXDeviationVar)
    negative_deviation_variable: OXDeviationVar = field(default_factory=OXDeviationVar)

    @property
    def desired_variables(self) -> list[OXDeviationVar]:
        """Get the list of desired deviation variables.

        Returns:
            list[OXDeviationVar]: A list of deviation variables marked as desired.
        """
        result = []
        if self.positive_deviation_variable.desired:
            result.append(self.positive_deviation_variable)
        if self.negative_deviation_variable.desired:
            result.append(self.negative_deviation_variable)
        return result

    @property
    def undesired_variables(self) -> list[OXDeviationVar]:
        """Get the list of undesired deviation variables.

        Returns:
            list[OXDeviationVar]: A list of deviation variables not marked as desired.
        """
        result = []
        if not self.positive_deviation_variable.desired:
            result.append(self.positive_deviation_variable)
        if not self.negative_deviation_variable.desired:
            result.append(self.negative_deviation_variable)
        return result
