"""
Optimization Problem Types Module
==================================

This module provides classes for representing different types of optimization problems
in the OptiX framework. It implements a hierarchical structure supporting Constraint 
Satisfaction Problems (CSP), Linear Programming (LP), and Goal Programming (GP).

The module serves as the core problem definition layer in the OptiX optimization 
framework, providing the foundation for mathematical optimization problems across
various domains including resource allocation, scheduling, and multi-objective optimization.

The module implements a progressive complexity pattern where each problem type builds
upon the previous one, allowing users to choose the appropriate level of sophistication
for their optimization needs.

Example:
    Basic usage for different problem types:

    .. code-block:: python

        from problem import OXLPProblem, OXGPProblem, ObjectiveType
        from constraints import RelationalOperators
        
        # Linear Programming Problem
        lp_problem = OXLPProblem()
        lp_problem.create_decision_variable("x", lower_bound=0, upper_bound=10)
        lp_problem.create_decision_variable("y", lower_bound=0, upper_bound=10)
        
        # Add constraint: x + y <= 15
        lp_problem.create_constraint(
            variables=[lp_problem.variables[0].id, lp_problem.variables[1].id],
            weights=[1, 1],
            operator=RelationalOperators.LESS_THAN_EQUAL,
            value=15
        )
        
        # Set objective: maximize 3x + 2y
        lp_problem.create_objective_function(
            variables=[lp_problem.variables[0].id, lp_problem.variables[1].id],
            weights=[3, 2],
            objective_type=ObjectiveType.MAXIMIZE
        )

Module Dependencies:
    - base: For OXObject base class and exception handling
    - constraints: For constraint and expression classes
    - variables: For variable and variable set classes
    - data: For database management classes
"""

import dataclasses
import itertools
import operator
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from fractions import Fraction
from functools import reduce
from typing import Self
from uuid import UUID

from base import OXObject, OXception
from constraints import OXConstraintSet
from constraints.OXConstraint import OXConstraint, OXGoalConstraint, RelationalOperators
from constraints.OXSpecialConstraints import OXSpecialConstraint, OXMultiplicativeEqualityConstraint, \
    OXDivisionEqualityConstraint, OXModuloEqualityConstraint, OXSummationEqualityConstraint, OXConditionalConstraint
from constraints.OXpression import OXpression
from data.OXDatabase import OXDatabase
from variables.OXVariable import OXVariable
from variables.OXVariableSet import OXVariableSet


class SpecialConstraintType(StrEnum):
    """Enumeration of special constraint types supported by the framework.

    This enumeration defines the types of special (non-linear) constraints
    that can be created in optimization problems.

    Attributes:
        MultiplicativeEquality (str): Constraint for variable multiplication.
        DivisionEquality (str): Constraint for integer division operations.
        ModulusEquality (str): Constraint for modulo operations.
        SummationEquality (str): Constraint for variable summation.
        ConditionalConstraint (str): Constraint for conditional logic.
    """
    MultiplicativeEquality = "MultiplicativeEquality"
    DivisionEquality = "DivisionEquality"
    ModulusEquality = "ModulusEquality"
    SummationEquality = "SummationEquality"
    ConditionalConstraint = "ConditionalConstraint"


def _create_multiplicative_equality_constraint(problem: 'OXCSPProblem',
                                               input_variables: Callable[[OXObject], bool] | list[OXObject] = None
                                               ) -> OXMultiplicativeEqualityConstraint:
    """Create a multiplicative equality constraint for a problem.

    This function creates a special constraint that enforces the equality:
    output_variable = input_variable_1 * input_variable_2 * ... * input_variable_n

    The function automatically calculates the bounds for the output variable
    based on the Cartesian product of all input variable domains.

    Args:
        problem (OXCSPProblem): The problem instance to add the constraint to.
        input_variables (Callable[[OXObject], bool] | list[OXObject], optional):
            Either a function to search for variables or a list of variables
            to multiply. If a function is provided, it will be used to filter
            variables from the problem.

    Returns:
        OXMultiplicativeEqualityConstraint: The created constraint object.

    Raises:
        OXception: If fewer than 2 variables are provided.

    Examples:
        >>> # Using a list of variables
        >>> constraint = _create_multiplicative_equality_constraint(
        ...     problem, [var1, var2, var3]
        ... )
        >>> 
        >>> # Using a search function
        >>> constraint = _create_multiplicative_equality_constraint(
        ...     problem, lambda v: v.name.startswith("factor")
        ... )

    Note:
        This function automatically creates a new decision variable to store
        the multiplication result and adds it to the problem's variable set.
    """
    if isinstance(input_variables, Callable):
        input_variables = [var for var in problem.variables if input_variables(var)]
    variable_uuids = [var.id for var in input_variables]

    if len(variable_uuids) < 2:
        raise OXception("Multiplicative equality constraint requires at least 2 variables")

    domains = [(var.lower_bound, var.upper_bound) for var in input_variables]

    combinations = itertools.product(*domains)

    products = [reduce(operator.mul, combination) for combination in combinations]

    lower_bound, upper_bound = min(products), max(products)

    new_var_name = f"Multiplication of {'_'.join(var.name for var in input_variables)}"

    problem.create_decision_variable(var_name=new_var_name, lower_bound=lower_bound, upper_bound=upper_bound)

    result = OXMultiplicativeEqualityConstraint(
        input_variables=variable_uuids,
        output_variable=problem.variables.last_object.id,
    )

    problem.specials.append(result)

    return result


def _create_division_or_modulus_equality_constraint(problem: 'OXCSPProblem',
                                                    input_variable: Callable[[OXObject], bool] | OXObject,
                                                    divisor: int,
                                                    constraint_type: SpecialConstraintType) -> OXDivisionEqualityConstraint | OXModuloEqualityConstraint:
    """Create a division or modulus equality constraint for a problem.

    This function creates a special constraint that enforces either:
    - Division: output_variable = input_variable // divisor (integer division)
    - Modulus: output_variable = input_variable % divisor (remainder)

    The function automatically calculates the appropriate bounds for the output variable
    based on the constraint type and divisor value.

    Args:
        problem (OXCSPProblem): The problem instance to add the constraint to.
        input_variable (Callable[[OXObject], bool] | OXObject): Either a function
            to search for a variable or the variable object to operate on.
        divisor (int): The divisor value for the operation.
        constraint_type (SpecialConstraintType): The type of constraint to create
            (DivisionEquality or ModulusEquality).

    Returns:
        OXDivisionEqualityConstraint | OXModuloEqualityConstraint: The created
            constraint object.

    Raises:
        OXception: If the input_variable selection doesn't result in exactly one variable,
            or if the constraint_type is not DivisionEquality or ModulusEquality.

    Examples:
        >>> # Create a division constraint: z = x // 3
        >>> constraint = _create_division_or_modulus_equality_constraint(
        ...     problem, variable_x, 3, SpecialConstraintType.DivisionEquality
        ... )
        >>> 
        >>> # Create a modulus constraint: z = x % 5
        >>> constraint = _create_division_or_modulus_equality_constraint(
        ...     problem, variable_x, 5, SpecialConstraintType.ModulusEquality
        ... )

    Note:
        - For division constraints, the output bounds are calculated as 
          input_bounds / divisor
        - For modulus constraints, the output bounds are always [0, divisor-1]
        - This function automatically creates a new decision variable to store
          the operation result
    """
    if isinstance(input_variable, Callable):
        input_variable = [var for var in problem.variables if input_variable(var)]

    if len(input_variable) < 1 or len(input_variable) >= 2:
        raise OXception("Division/Modulus equality constraint requires exactly 1 variable")
    if constraint_type not in [SpecialConstraintType.DivisionEquality, SpecialConstraintType.ModulusEquality]:
        raise OXception("This function only works for Division/Modulus equality constraints")

    lower_bound, upper_bound = input_variable[0].lower_bound, input_variable[0].upper_bound

    if constraint_type == SpecialConstraintType.DivisionEquality:
        lb, ub = lower_bound / divisor, upper_bound / divisor
    else:
        lb, ub = 0, divisor - 1

    if constraint_type == SpecialConstraintType.DivisionEquality:
        new_var_name = f"{input_variable[0].name} / {divisor}"
    else:
        new_var_name = f"{input_variable[0].name} % {divisor}"

    problem.create_decision_variable(var_name=new_var_name, lower_bound=lb, upper_bound=ub)

    if constraint_type == SpecialConstraintType.DivisionEquality:
        result = OXDivisionEqualityConstraint(
            input_variable=input_variable[0].id,
            output_variable=problem.variables.last_object.id,
            denominator=divisor
        )
    else:
        result = OXModuloEqualityConstraint(
            input_variable=input_variable[0].id,
            output_variable=problem.variables.last_object.id,
            denominator=divisor
        )

    problem.specials.append(result)

    return result


def _create_summation_equality_constraint(problem: 'OXCSPProblem',
                                          input_variables: Callable[[OXObject], bool] | list[
                                              OXObject]) -> OXSummationEqualityConstraint:
    """Create a summation equality constraint for a problem.

    This function creates a special constraint that enforces the equality:
    output_variable = input_variable_1 + input_variable_2 + ... + input_variable_n

    The function automatically calculates the bounds for the output variable
    as the sum of the bounds of all input variables.

    Args:
        problem (OXCSPProblem): The problem instance to add the constraint to.
        input_variables (Callable[[OXObject], bool] | list[OXObject]): Either
            a function to search for variables or a list of variables to sum.
            If a function is provided, it will be used to filter variables
            from the problem.

    Returns:
        OXSummationEqualityConstraint: The created constraint object.

    Raises:
        OXception: If fewer than 2 variables are provided, or if input_variables
            is not a list of OXVariable objects.

    Examples:
        >>> # Using a list of variables
        >>> constraint = _create_summation_equality_constraint(
        ...     problem, [var1, var2, var3]
        ... )
        >>> 
        >>> # Using a search function
        >>> constraint = _create_summation_equality_constraint(
        ...     problem, lambda v: v.name.startswith("term")
        ... )

    Note:
        While summation could be expressed as a linear constraint, it's included
        as a special constraint for consistency and potential solver optimization.
        This function automatically creates a new decision variable to store
        the summation result.
    """
    if isinstance(input_variables, Callable):
        input_variables = [var for var in problem.variables if input_variables(var)]
    variable_uuids = [var.id for var in input_variables]
    if len(variable_uuids) < 2:
        raise OXception("Summation equality constraint requires at least 2 variables")
    if not isinstance(input_variables, list):
        raise OXception("input_variables must be a list of OXVariable objects")
    if not all(isinstance(var, OXVariable) for var in input_variables):
        raise OXception("All elements in input_variables must be OXVariable objects")
    lower_bound = sum(var.lower_bound for var in input_variables)
    upper_bound = sum(var.upper_bound for var in input_variables)
    new_var_name = f"Summation of {'_'.join(var.name for var in input_variables)}"
    problem.create_decision_variable(var_name=new_var_name, lower_bound=lower_bound, upper_bound=upper_bound)
    result = OXSummationEqualityConstraint(
        input_variables=variable_uuids,
        output_variable=problem.variables.last_object.id,
    )
    problem.specials.append(result)
    return result


def _create_conditional_constraint(problem: 'OXCSPProblem',
                                   input_constraint: Callable[[OXObject], bool] | OXObject,
                                   true_constraint: Callable[[OXObject], bool] | OXObject,
                                   false_constraint: Callable[[OXObject], bool] | OXObject) -> OXConditionalConstraint:
    """Create a conditional constraint for a problem.

    This function creates a special constraint that enforces conditional logic:
    if (indicator_variable == 1) then true_constraint else false_constraint

    The function creates an indicator variable that determines which constraint
    to enforce based on the input constraint evaluation.

    Args:
        problem (OXCSPProblem): The problem instance to add the constraint to.
        input_constraint (Callable[[OXObject], bool] | OXObject): Either a function
            to search for the input constraint or the constraint object itself.
        true_constraint (Callable[[OXObject], bool] | OXObject): Either a function
            to search for the constraint to enforce when condition is true, or
            the constraint object itself.
        false_constraint (Callable[[OXObject], bool] | OXObject): Either a function
            to search for the constraint to enforce when condition is false, or
            the constraint object itself.

    Returns:
        OXConditionalConstraint: The created conditional constraint object.

    Raises:
        OXception: If any of the constraint selections don't result in exactly
            one constraint, or if the constraints are not OXConstraint objects.

    Examples:
        >>> # Create a conditional constraint using constraint objects
        >>> constraint = _create_conditional_constraint(
        ...     problem, input_constraint, true_constraint, false_constraint
        ... )
        >>> 
        >>> # Using search functions
        >>> constraint = _create_conditional_constraint(
        ...     problem,
        ...     lambda c: c.id == input_id,
        ...     lambda c: c.id == true_id,
        ...     lambda c: c.id == false_id
        ... )

    Note:
        This function automatically creates a binary indicator variable (0 or 1)
        to represent the conditional logic. The input constraints are marked as
        used in special constraints to avoid duplication in the main constraint list.
    """
    if isinstance(input_constraint, Callable):
        input_constraint = [var for var in problem.constraints if input_constraint(var)]
    if isinstance(true_constraint, Callable):
        true_constraint = [var for var in problem.constraints if true_constraint(var)]
    if isinstance(false_constraint, Callable):
        false_constraint = [var for var in problem.constraints if false_constraint(var)]
    # if (isinstance(input_constraint, list) and len(input_constraint) != 1) or
    #    (isinstance(true_constraint, list) and len(true_constraint) != 1) or
    #    (isinstance(false_constraint, list) and len(false_constraint) != 1):
    if any(isinstance(obj, list) and len(obj) != 1 for obj in [input_constraint, true_constraint, false_constraint]):
        raise OXception("Conditional constraint requires exactly 1 input, true and false constraints")

    input_constraint = input_constraint[0]
    true_constraint = true_constraint[0]
    false_constraint = false_constraint[0]

    problem.constraints_in_special_constraints.append(input_constraint.id)
    problem.constraints_in_special_constraints.append(true_constraint.id)
    problem.constraints_in_special_constraints.append(false_constraint.id)

    # if not isinstance(input_constraint, OXConstraint) or not isinstance(true_constraint,
    #                                                                     OXConstraint) or not isinstance(
    #         false_constraint, OXConstraint):
    if not all(isinstance(obj, OXConstraint) for obj in [input_constraint, true_constraint, false_constraint]):
        raise OXception("All constraints must be OXConstraint objects")

    new_var_name = f"Conditional constraint: {input_constraint.id} ? {true_constraint.id} : {false_constraint.id}"
    problem.create_decision_variable(var_name=new_var_name, lower_bound=0, upper_bound=1)
    result = OXConditionalConstraint(
        indicator_variable=problem.variables.last_object.id,
        input_constraint=input_constraint.id,
        constraint_if_true=true_constraint.id,
        constraint_if_false=false_constraint.id
    )
    problem.specials.append(result)
    return result


@dataclass
class OXCSPProblem(OXObject):
    """Base class for Constraint Satisfaction Problems (CSP).

    This class represents a constraint satisfaction problem where the goal is to find
    values for variables that satisfy a set of constraints. It provides the fundamental
    structure for optimization problems in the OptiX framework.

    Attributes:
        db (OXDatabase): Database containing data objects used in the problem.
        variables (OXVariableSet): Set of decision variables in the problem.
        constraints (list[OXConstraint]): List of linear constraints.
        specials (list[OXSpecialConstraint]): List of special (non-linear) constraints.
        constraints_in_special_constraints (list[UUID]): List of constraint IDs used 
            in special constraints to avoid duplication.

    Examples:
        >>> problem = OXCSPProblem()
        >>> problem.create_decision_variable("x", lower_bound=0, upper_bound=10)
        >>> problem.create_decision_variable("y", lower_bound=0, upper_bound=10)
        >>> problem.create_constraint(
        ...     variables=[problem.variables[0].id, problem.variables[1].id],
        ...     weights=[1, 1],
        ...     operator=RelationalOperators.LESS_THAN_EQUAL,
        ...     value=15
        ... )

    See Also:
        :class:`OXLPProblem`: Linear Programming extension of CSP.
        :class:`OXGPProblem`: Goal Programming extension of LP.
    """
    db: OXDatabase = field(default_factory=OXDatabase)
    variables: OXVariableSet = field(default_factory=OXVariableSet)
    constraints: OXConstraintSet = field(default_factory=OXConstraintSet)
    specials: list[OXSpecialConstraint] = field(default_factory=list)
    constraints_in_special_constraints: list[UUID] = field(default_factory=list)

    def create_special_constraint(self, *,
                                  constraint_type: SpecialConstraintType = SpecialConstraintType.MultiplicativeEquality,
                                  **kwargs
                                  ):
        """Create a special (non-linear) constraint for the problem.

        This method creates various types of special constraints that handle
        non-linear operations such as multiplication, division, modulo, summation,
        and conditional logic.

        Args:
            constraint_type (SpecialConstraintType): The type of special constraint
                to create. Defaults to MultiplicativeEquality.
            **kwargs: Additional keyword arguments specific to the constraint type.
                See individual constraint creation functions for details.

        Returns:
            OXSpecialConstraint: The created special constraint object.

        Raises:
            OXception: If an unknown constraint type is provided.

        Examples:
            >>> # Create a multiplication constraint: z = x * y
            >>> constraint = problem.create_special_constraint(
            ...     constraint_type=SpecialConstraintType.MultiplicativeEquality,
            ...     input_variables=[var_x, var_y]
            ... )
            >>> 
            >>> # Create a division constraint: z = x // 3
            >>> constraint = problem.create_special_constraint(
            ...     constraint_type=SpecialConstraintType.DivisionEquality,
            ...     input_variable=var_x,
            ...     divisor=3
            ... )

        See Also:
            :func:`_create_multiplicative_equality_constraint`: For multiplication constraints.
            :func:`_create_division_or_modulus_equality_constraint`: For division/modulo constraints.
            :func:`_create_summation_equality_constraint`: For summation constraints.
            :func:`_create_conditional_constraint`: For conditional constraints.
        """
        match constraint_type:
            case SpecialConstraintType.MultiplicativeEquality:
                return _create_multiplicative_equality_constraint(self, **kwargs)
            case SpecialConstraintType.DivisionEquality:
                return _create_division_or_modulus_equality_constraint(self, **kwargs,
                                                                       constraint_type=SpecialConstraintType.DivisionEquality)
            case SpecialConstraintType.ModulusEquality:
                return _create_division_or_modulus_equality_constraint(self, **kwargs,
                                                                       constraint_type=SpecialConstraintType.ModulusEquality)
            case SpecialConstraintType.SummationEquality:
                return _create_summation_equality_constraint(self, **kwargs)
            case SpecialConstraintType.ConditionalConstraint:
                return _create_conditional_constraint(self, **kwargs)
        raise OXception(f"Unknown constraint type: {constraint_type}")

    def create_variables_from_db(self, *args,
                                 var_name_template: str = "",
                                 var_description_template: str = "",
                                 upper_bound: float | int = float("inf"),
                                 lower_bound: float | int = 0):
        """Create decision variables from database objects using Cartesian product.

        This method creates decision variables by taking the Cartesian product of
        specified database object types. For each combination of objects, a new
        variable is created with the specified bounds and template-based naming.

        Args:
            *args: Variable number of database object types to use for variable creation.
                Each argument should be a type that exists in the problem's database.
            var_name_template (str, optional): Template string for variable names.
                Can use database object type names as format keys, as well as
                individual field values with format "{type_name}_{field_name}".
                Defaults to "".
            var_description_template (str, optional): Template string for variable
                descriptions. Can use database object type names as format keys, as well as
                individual field values with format "{type_name}_{field_name}".
                Defaults to "".
            upper_bound (float | int, optional): Upper bound for all created variables.
                Defaults to positive infinity.
            lower_bound (float | int, optional): Lower bound for all created variables.
                Defaults to 0.

        Raises:
            OXception: If any of the provided argument types don't exist in the database.

        Examples:
            >>> # Create variables for all combinations of buses and routes
            >>> problem.create_variables_from_db(
            ...     Bus, Route,
            ...     var_name_template="bus_{bus_id}_route_{route_id}",
            ...     var_description_template="Assignment of bus {bus_name} to route {route_name}",
            ...     upper_bound=1,
            ...     lower_bound=0
            ... )
            >>> 
            >>> # Create variables for single object type using field values
            >>> problem.create_variables_from_db(
            ...     Driver,
            ...     var_name_template="driver_{driver_id}_active",
            ...     var_description_template="Driver {driver_name} is active",
            ...     upper_bound=1
            ... )

        Note:
            The method uses the Cartesian product of all specified object types,
            so the number of created variables equals the product of the counts
            of each object type. Template strings can now access both object type
            names and individual field values from dataclass objects.
        """
        available_object_type_set = set(self.db.get_object_types())
        argument_set = set(t.__name__.lower() for t in args)
        invalid_arguments = argument_set.difference(available_object_type_set)
        if len(invalid_arguments) > 0:
            raise OXception(f"Invalid db object type(s) detected : {invalid_arguments}")
        object_type_names = []
        object_instances = []
        for object_type in argument_set:
            object_type_names.append(object_type)
            object_instances.append(self.db.search_by_function(
                lambda x: x.class_name.lower().endswith(object_type.lower())))

        for instances_tuple in itertools.product(*object_instances):
            related_data = {}
            format_parameters = {}
            for i in range(len(object_type_names)):
                related_data[object_type_names[i]] = instances_tuple[i].id
                for field in dataclasses.fields(instances_tuple[i]):
                    format_parameters[f"{object_type_names[i]}_{field.name}"] = getattr(instances_tuple[i], field.name)
            var_name = var_name_template.format(**format_parameters)
            var_description = var_description_template.format(**format_parameters)
            self.create_decision_variable(var_name=var_name, description=var_description,
                                          upper_bound=upper_bound, lower_bound=lower_bound,
                                          **related_data)

    def create_decision_variable(self, var_name: str = "", description: str = "",
                                 upper_bound: float | int = float("inf"),
                                 lower_bound: float | int = 0,
                                 **kwargs):
        """Create a decision variable for the optimization problem.

        Creates a new decision variable with the specified bounds and properties,
        and adds it to the problem's variable set. The variable can be linked to
        database objects through keyword arguments.

        Args:
            var_name (str, optional): Name of the variable. Defaults to "".
            description (str, optional): Description of the variable. Defaults to "".
            upper_bound (float | int, optional): Upper bound for the variable.
                Defaults to positive infinity.
            lower_bound (float | int, optional): Lower bound for the variable.
                Defaults to 0.
            **kwargs: Additional keyword arguments linking the variable to database
                objects. Keys must match database object types.

        Raises:
            OXception: If any keyword argument key doesn't match a database object type.

        Examples:
            >>> # Create a simple bounded variable
            >>> problem.create_decision_variable(
            ...     var_name="x",
            ...     description="Production quantity",
            ...     upper_bound=100,
            ...     lower_bound=0
            ... )
            >>> 
            >>> # Create a variable linked to database objects
            >>> problem.create_decision_variable(
            ...     var_name="assignment_bus_1_route_2",
            ...     description="Bus 1 assigned to route 2",
            ...     upper_bound=1,
            ...     lower_bound=0,
            ...     bus=bus_1_id,
            ...     route=route_2_id
            ... )

        Note:
            The variable is automatically added to the problem's variable set
            and can be accessed through the variables attribute.
        """
        d_var = OXVariable(name=var_name, description=description, upper_bound=upper_bound, lower_bound=lower_bound)
        db_types = self.db.get_object_types()
        for key, value in kwargs.items():
            if key not in db_types:
                raise OXception(f"Invalid key {key} for decision variable.")
            d_var.related_data[key] = value
        self.variables.add_object(d_var)

    def create_constraint(self,
                          variable_search_function: Callable[[OXObject], bool] = None,
                          weight_calculation_function: Callable[[UUID, Self], float | int | Fraction] = None,
                          variables: list[UUID] = None,
                          weights: list[float | int | Fraction] = None,
                          operator: RelationalOperators = RelationalOperators.LESS_THAN_EQUAL,
                          value: float | int = None,
                          name: str = None):
        """Create a linear constraint for the optimization problem.

        Creates a linear constraint of the form:
        w1*x1 + w2*x2 + ... + wn*xn {operator} value

        Variables and weights can be specified either directly or through
        search and calculation functions.

        Args:
            variable_search_function (Callable[[OXObject], bool], optional): Function
                to search for variables in the problem. If provided, variables
                parameter must be None.
            weight_calculation_function (Callable[[UUID, Self], float | int], optional):
                Function to calculate weights for each variable. If provided,
                weights parameter must be None.
            variables (list[UUID], optional): List of variable IDs to include in
                the constraint. If provided, variable_search_function must be None.
            weights (list[float | int], optional): List of weights for each variable.
                If provided, weight_calculation_function must be None.
            operator (RelationalOperators, optional): Relational operator for the
                constraint. Defaults to LESS_THAN_EQUAL.
            value (float | int, optional): Right-hand side value of the constraint.
            name (str, optional): A descriptive name for the constraint. If None,
                an auto-generated name will be created based on the constraint terms.

        Raises:
            OXception: If parameter combinations are invalid (see _check_parameters).

        Examples:
            >>> # Using direct variable and weight specification
            >>> problem.create_constraint(
            ...     variables=[var1.id, var2.id, var3.id],
            ...     weights=[1, 2, 3],
            ...     operator=RelationalOperators.LESS_THAN_EQUAL,
            ...     value=100
            ... )
            >>> 
            >>> # Using search and calculation functions
            >>> problem.create_constraint(
            ...     variable_search_function=lambda v: v.name.startswith("x"),
            ...     weight_calculation_function=lambda v, p: 1.0,
            ...     operator=RelationalOperators.EQUAL,
            ...     value=1
            ... )

        Note:
            The constraint is automatically added to the problem's constraint list.
            Exactly one of variable_search_function/variables and one of
            weight_calculation_function/weights must be provided.
        """
        self._check_parameters(variable_search_function, variables, weight_calculation_function, weights)

        if variables is None:
            variables = [v.id for v in self.variables.search_by_function(variable_search_function)]

        if weights is None:
            weights = [weight_calculation_function(var, self) for var in variables]

        expr = OXpression(variables=variables, weights=weights)
        if name is None:
            vars = [self.variables[var_id] for var_id in variables]
            var_names = [f"{abs(w)}*{v.name}" for v, w in zip(vars, weights)]
            negative_weights = [True if w < 0 else False for w in weights]
            prefixes = [" - " if negative_weight else ' + ' for negative_weight in negative_weights]
            if prefixes[0] == ' + ':
                prefixes[0] = ''

            terms = [f"{pfx}{var_name}" for pfx, var_name in zip(prefixes, var_names)]
            name = "".join(terms).strip()
        constraint = OXConstraint(expression=expr, relational_operator=operator, rhs=value, name=name)
        self.constraints.add_object(constraint)

    def _check_parameters(self, variable_search_function, variables, weight_calculation_function, weights):
        """Validate parameter combinations for constraint creation.

        This private method ensures that the parameters for constraint creation
        are valid and mutually exclusive where required.

        Args:
            variable_search_function: Function to search for variables.
            variables: List of variable IDs.
            weight_calculation_function: Function to calculate weights.
            weights: List of weights.

        Raises:
            OXception: If parameter combinations are invalid, including:
                - Neither variable_search_function nor variables provided
                - Both variable_search_function and variables provided
                - Neither weight_calculation_function nor weights provided
                - Both weight_calculation_function and weights provided
                - variable_search_function without weight_calculation_function
                - variables without weights
                - variables and weights have different lengths

        Note:
            This method is used internally by create_constraint and related methods
            to ensure parameter consistency.
        """
        if variable_search_function is None and variables is None:
            raise OXception("Either variable_search_function or variables must be provided.")
        if variable_search_function is not None and variables is not None:
            raise OXception("Only one of variable_search_function or variables can be provided.")
        if weight_calculation_function is None and weights is None:
            raise OXception("Either weight_calculation_function or weights must be provided.")
        if weight_calculation_function is not None and weights is not None:
            raise OXception("Only one of weight_calculation_function or weights can be provided.")
        if variable_search_function is not None and weight_calculation_function is None:
            raise OXception("weight_calculation_function must be provided if variable_search_function is provided.")
        if variables is not None and weights is None:
            raise OXception("weights must be provided if variables is provided.")
        if variables is not None and len(variables) != len(weights):
            raise OXception("variables and weights must have the same length.")


class ObjectiveType(StrEnum):
    """Enumeration of objective types for optimization problems.

    Attributes:
        MINIMIZE (str): Minimize the objective function.
        MAXIMIZE (str): Maximize the objective function.
    """
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"


@dataclass
class OXLPProblem(OXCSPProblem):
    """Linear Programming Problem class.

    This class extends OXCSPProblem to add support for linear programming by
    introducing an objective function that can be minimized or maximized.

    Attributes:
        objective_function (OXpression): The objective function to optimize.
        objective_type (ObjectiveType): Whether to minimize or maximize the objective.
        db (OXDatabase): Inherited from OXCSPProblem.
        variables (OXVariableSet): Inherited from OXCSPProblem.
        constraints (list[OXConstraint]): Inherited from OXCSPProblem.
        specials (list[OXSpecialConstraint]): Inherited from OXCSPProblem.

    Examples:
        >>> problem = OXLPProblem()
        >>> problem.create_decision_variable("x", lower_bound=0, upper_bound=10)
        >>> problem.create_decision_variable("y", lower_bound=0, upper_bound=10)
        >>> problem.create_constraint(
        ...     variables=[problem.variables[0].id, problem.variables[1].id],
        ...     weights=[1, 1],
        ...     operator=RelationalOperators.LESS_THAN_EQUAL,
        ...     value=15
        ... )
        >>> problem.create_objective_function(
        ...     variables=[problem.variables[0].id, problem.variables[1].id],
        ...     weights=[3, 2],
        ...     objective_type=ObjectiveType.MAXIMIZE
        ... )

    See Also:
        :class:`OXCSPProblem`: Base constraint satisfaction problem class.
        :class:`OXGPProblem`: Goal Programming extension of LP.
    """
    objective_function: OXpression = field(default_factory=OXpression)
    objective_type: ObjectiveType = ObjectiveType.MINIMIZE

    def create_objective_function(self,
                                  variable_search_function: Callable[[OXObject], bool] = None,
                                  weight_calculation_function: Callable[[OXVariable, Self], float | int] = None,
                                  variables: list[UUID] = None,
                                  weights: list[float | int] = None,
                                  objective_type: ObjectiveType = ObjectiveType.MINIMIZE):
        """Create an objective function for the linear programming problem.

        Creates an objective function of the form:
        {minimize|maximize} w1*x1 + w2*x2 + ... + wn*xn

        Variables and weights can be specified either directly or through
        search and calculation functions.

        Args:
            variable_search_function (Callable[[OXObject], bool], optional): Function
                to search for variables in the problem. If provided, variables
                parameter must be None.
            weight_calculation_function (Callable[[OXVariable, Self], float | int], optional):
                Function to calculate weights for each variable. If provided,
                weights parameter must be None.
            variables (list[UUID], optional): List of variable IDs to include in
                the objective function. If provided, variable_search_function must be None.
            weights (list[float | int], optional): List of weights for each variable.
                If provided, weight_calculation_function must be None.
            objective_type (ObjectiveType, optional): Whether to minimize or maximize
                the objective function. Defaults to MINIMIZE.

        Examples:
            >>> # Maximize profit: 3*x + 2*y
            >>> problem.create_objective_function(
            ...     variables=[x_id, y_id],
            ...     weights=[3, 2],
            ...     objective_type=ObjectiveType.MAXIMIZE
            ... )
            >>> 
            >>> # Minimize cost using search function
            >>> problem.create_objective_function(
            ...     variable_search_function=lambda v: "cost" in v.name,
            ...     weight_calculation_function=lambda v, p: v.get_cost(),
            ...     objective_type=ObjectiveType.MINIMIZE
            ... )

        Note:
            This method sets both the objective_function and objective_type
            attributes of the problem.
        """
        self._check_parameters(variable_search_function, variables, weight_calculation_function, weights)

        if variable_search_function is not None:
            variables = [v.id for v in self.variables.search_by_function(variable_search_function)]
            weights = [weight_calculation_function(var, self) for var in variables]

        self.objective_function = OXpression(variables=variables, weights=weights)
        self.objective_type = objective_type


@dataclass
class OXGPProblem(OXLPProblem):
    """Goal Programming Problem class.

    This class extends OXLPProblem to add support for goal programming by
    introducing goal constraints with deviation variables. Goal programming
    is used when there are multiple conflicting objectives that cannot be
    simultaneously satisfied.

    Attributes:
        goal_constraints (list[OXGoalConstraint]): List of goal constraints with
            deviation variables.
        objective_function (OXpression): Inherited from OXLPProblem.
        objective_type (ObjectiveType): Inherited from OXLPProblem.
        db (OXDatabase): Inherited from OXCSPProblem.
        variables (OXVariableSet): Inherited from OXCSPProblem.
        constraints (list[OXConstraint]): Inherited from OXCSPProblem.
        specials (list[OXSpecialConstraint]): Inherited from OXCSPProblem.

    Examples:
        >>> problem = OXGPProblem()
        >>> problem.create_decision_variable("x", lower_bound=0, upper_bound=10)
        >>> problem.create_decision_variable("y", lower_bound=0, upper_bound=10)
        >>> # Create a goal constraint: aim for x + y = 8
        >>> problem.create_goal_constraint(
        ...     variables=[problem.variables[0].id, problem.variables[1].id],
        ...     weights=[1, 1],
        ...     operator=RelationalOperators.EQUAL,
        ...     value=8
        ... )
        >>> # The objective function minimizes undesired deviations
        >>> problem.create_objective_function()

    See Also:
        :class:`OXLPProblem`: Base linear programming problem class.
        :class:`OXCSPProblem`: Base constraint satisfaction problem class.
        :class:`constraints.OXConstraint.OXGoalConstraint`: Goal constraint with deviation variables.
    """
    goal_constraints: OXConstraintSet = field(default_factory=OXConstraintSet)

    def create_goal_constraint(self,
                               variable_search_function: Callable[[OXObject], bool] = None,
                               weight_calculation_function: Callable[[UUID, Self], float | int | Fraction] = None,
                               variables: list[UUID] = None,
                               weights: list[float | int] = None,
                               operator: RelationalOperators = RelationalOperators.LESS_THAN_EQUAL,
                               value: float | int = None,
                               name: str = None):
        """Create a goal constraint for the goal programming problem.

        Creates a goal constraint with associated positive and negative deviation
        variables. Goal constraints represent targets that the problem should try
        to achieve, but may not be strictly satisfied.

        The constraint is of the form:
        w1*x1 + w2*x2 + ... + wn*xn + d- - d+ {operator} value

        Where d- and d+ are negative and positive deviation variables respectively.

        Args:
            variable_search_function (Callable[[OXObject], bool], optional): Function
                to search for variables in the problem. If provided, variables
                parameter must be None.
            weight_calculation_function (Callable[[OXVariable, Self], float | int], optional):
                Function to calculate weights for each variable. If provided,
                weights parameter must be None.
            variables (list[UUID], optional): List of variable IDs to include in
                the constraint. If provided, variable_search_function must be None.
            weights (list[float | int], optional): List of weights for each variable.
                If provided, weight_calculation_function must be None.
            operator (RelationalOperators, optional): Relational operator for the
                constraint. Defaults to LESS_THAN_EQUAL.
            value (float | int, optional): Target value for the goal constraint.

        Examples:
            >>> # Goal: total production should be around 1000 units
            >>> problem.create_goal_constraint(
            ...     variables=[prod1_id, prod2_id, prod3_id],
            ...     weights=[1, 1, 1],
            ...     operator=RelationalOperators.EQUAL,
            ...     value=1000
            ... )
            >>> 
            >>> # Goal: minimize resource usage below 500
            >>> problem.create_goal_constraint(
            ...     variable_search_function=lambda v: "resource" in v.name,
            ...     weight_calculation_function=lambda v, p: v.usage_rate,
            ...     operator=RelationalOperators.LESS_THAN_EQUAL,
            ...     value=500
            ... )

        Note:
            This method creates a regular constraint first, then converts it to
            a goal constraint with deviation variables. The goal constraint is
            added to the goal_constraints list.
        """
        self.create_constraint(variable_search_function, weight_calculation_function, variables, weights, operator,
                               value, name=name)

        last_constraint = self.constraints.last_object
        self.constraints.remove_object(last_constraint)
        upper_bound = 0
        for var in last_constraint.expression.variables:
            if self.variables[var].upper_bound > upper_bound:
                upper_bound = self.variables[var].upper_bound
        upper_bound = round(upper_bound // 7)
        goal_constraint = last_constraint.to_goal(upper_bound=upper_bound)
        self.goal_constraints.add_object(goal_constraint)

    def create_objective_function(self,
                                  variable_search_function: Callable[[OXObject], bool] = None,
                                  weight_calculation_function: Callable[[OXVariable, Self], float | int] = None,
                                  variables: list[UUID] = None,
                                  weights: list[float | int] = None,
                                  objective_type: ObjectiveType = ObjectiveType.MINIMIZE):
        """Create an objective function for the goal programming problem.

        Creates an objective function that minimizes the sum of undesired deviation
        variables from all goal constraints. This is the standard approach in
        goal programming where the objective is to minimize deviations from goals.

        Args:
            variable_search_function (Callable[[OXObject], bool], optional): 
                Not used in goal programming. Included for interface consistency.
            weight_calculation_function (Callable[[OXVariable, Self], float | int], optional):
                Not used in goal programming. Included for interface consistency.
            variables (list[UUID], optional): Not used in goal programming.
                Included for interface consistency.
            weights (list[float | int], optional): Not used in goal programming.
                Included for interface consistency.
            objective_type (ObjectiveType, optional): Not used in goal programming.
                Always set to MINIMIZE. Included for interface consistency.

        Examples:
            >>> # Create goal constraints first
            >>> problem.create_goal_constraint(
            ...     variables=[x_id, y_id],
            ...     weights=[1, 1],
            ...     operator=RelationalOperators.EQUAL,
            ...     value=100
            ... )
            >>> 
            >>> # Create objective function to minimize deviations
            >>> problem.create_objective_function()

        Note:
            This method automatically collects all undesired deviation variables
            from existing goal constraints and creates an objective function
            that minimizes their sum. The objective is always set to MINIMIZE.
            Parameters are ignored as the objective is automatically determined
            from goal constraints.
        """
        variables = []
        desireds = []

        for constraint in self.goal_constraints:
            variables.extend(constraint.undesired_variables)
            desireds.extend(constraint.desired_variables)

        for var in variables:
            if not var in self.variables:
                self.variables.add_object(var)

        for var in desireds:
            if not var in self.variables:
                self.variables.add_object(var)

        all_vars = variables  # + desireds
        weights = [1.0] * len(all_vars)
        uuids = [var.id for var in all_vars]

        self.objective_function = OXpression(variables=uuids, weights=weights)
        self.objective_type = ObjectiveType.MINIMIZE
