"""
OptiX Problem Classes Test Suite
================================

This module provides comprehensive test coverage for the OptiX problem classes,
including Constraint Satisfaction Problems (CSP), Linear Programming (LP), and
Goal Programming (GP) problems. It validates the core functionality of problem
creation, variable management, constraint handling, and objective function setup.

The test suite covers three main problem types in the OptiX optimization framework:
- OXCSPProblem: Constraint Satisfaction Problems with special constraint support
- OXLPProblem: Linear Programming problems with objective function optimization
- OXGPProblem: Goal Programming problems with goal constraints and deviation variables

Example:
    Running the test suite for problem classes:

    .. code-block:: bash

        # Run all problem tests
        poetry run python -m pytest tests/test_OXProblem.py -v
        
        # Run specific test patterns
        poetry run python -m pytest tests/test_OXProblem.py -k "test_create_constraint" -v
        
        # Run CSP-specific tests
        poetry run python -m pytest tests/test_OXProblem.py -k "oxcspproblem" -v

Module Dependencies:
    - uuid: For generating unique identifiers for variables and constraints
    - pytest: Testing framework for assertion handling and test fixtures
    - base.OXception: Custom exception handling for OptiX operations
    - constraints: Constraint classes for linear and special constraint types
    - data.OXDatabase: Database management for problem data storage
    - problem.OXProblem: Core problem class definitions and enumerations

Test Coverage:
    - Problem initialization and default value validation
    - Decision variable creation with bounds and metadata
    - Linear constraint creation with various parameter combinations
    - Special constraint handling (multiplication, division, modulo, summation)
    - Objective function setup for optimization problems
    - Goal constraint management for goal programming
    - Parameter validation and error handling
    - Database integration and variable/constraint storage
"""

from uuid import UUID

import pytest

from base import OXception
from constraints.OXConstraint import OXConstraint, RelationalOperators
from constraints.OXSpecialConstraints import (
    OXMultiplicativeEqualityConstraint,
    OXDivisionEqualityConstraint,
    OXModuloEqualityConstraint,
    OXSummationEqualityConstraint
)
from constraints.OXpression import OXpression
from data.OXDatabase import OXDatabase
from problem.OXProblem import (
    OXCSPProblem, OXLPProblem, OXGPProblem,
    SpecialConstraintType, ObjectiveType
)


def test_oxcspproblem_initialization():
    """Test default initialization of OXCSPProblem."""
    problem = OXCSPProblem()

    # Check default values
    assert isinstance(problem.db, OXDatabase)
    assert len(problem.variables) == 0
    assert len(problem.constraints) == 0
    assert len(problem.specials) == 0


def test_create_decision_variable():
    """Test creating a decision variable in OXCSPProblem."""
    problem = OXCSPProblem()

    # Create a decision variable
    problem.create_decision_variable(
        var_name="test_var",
        description="Test variable",
        upper_bound=100,
        lower_bound=0
    )

    # Check that the variable was created correctly
    assert len(problem.variables) == 1
    var = problem.variables.last_object
    assert var.name == "test_var"
    assert var.description == "Test variable"
    assert var.upper_bound == 100
    assert var.lower_bound == 0


def test_create_constraint():
    """Test creating a constraint in OXCSPProblem."""
    problem = OXCSPProblem()

    # Create variables
    problem.create_decision_variable(var_name="var1", upper_bound=10)
    problem.create_decision_variable(var_name="var2", upper_bound=20)

    # Get variable IDs
    var_ids = [var.id for var in problem.variables]

    # Create a constraint
    problem.create_constraint(
        variables=var_ids,
        weights=[1, 2],
        operator=RelationalOperators.LESS_THAN_EQUAL,
        value=30
    )

    # Check that the constraint was created correctly
    assert len(problem.constraints) == 1
    constraint = problem.constraints.last_object
    assert isinstance(constraint, OXConstraint)
    assert constraint.expression.variables == var_ids
    assert constraint.expression.weights == [1, 2]
    assert constraint.relational_operator == RelationalOperators.LESS_THAN_EQUAL
    assert constraint.rhs == 30


def test_create_constraint_with_search_function():
    """Test creating a constraint using search and weight calculation functions."""
    problem = OXCSPProblem()

    # Create variables
    problem.create_decision_variable(var_name="var1", upper_bound=10)
    problem.create_decision_variable(var_name="var2", upper_bound=20)

    # Define search and weight calculation functions
    def search_func(var):
        return True  # Include all variables

    def weight_func(var_id:UUID, prob):
        return prob.variables[var_id].upper_bound  # Weight by upper bound

    # Create a constraint
    problem.create_constraint(
        variable_search_function=search_func,
        weight_calculation_function=weight_func,
        operator=RelationalOperators.LESS_THAN_EQUAL,
        value=30
    )

    # Check that the constraint was created correctly
    assert len(problem.constraints) == 1
    constraint = problem.constraints.last_object
    assert isinstance(constraint, OXConstraint)
    assert len(constraint.expression.variables) == 2
    assert constraint.expression.weights == [10, 20]
    assert constraint.relational_operator == RelationalOperators.LESS_THAN_EQUAL
    assert constraint.rhs == 30


def test_create_multiplicative_equality_constraint():
    """Test creating a multiplicative equality constraint."""
    problem = OXCSPProblem()

    # Create variables
    problem.create_decision_variable(var_name="var1", lower_bound=2, upper_bound=4)
    problem.create_decision_variable(var_name="var2", lower_bound=3, upper_bound=5)

    # Create a multiplicative equality constraint
    constraint = problem.create_special_constraint(
        constraint_type=SpecialConstraintType.MultiplicativeEquality,
        input_variables=list(problem.variables)
    )

    # Check that the constraint was created correctly
    assert isinstance(constraint, OXMultiplicativeEqualityConstraint)
    assert len(problem.specials) == 1
    assert len(problem.variables) == 3  # Original 2 variables + 1 new variable

    # Check the new variable's bounds (2*3=6 to 4*5=20)
    new_var = problem.variables.last_object
    assert new_var.lower_bound == 6
    assert new_var.upper_bound == 20


def test_create_division_equality_constraint():
    """Test creating a division equality constraint."""
    problem = OXCSPProblem()

    # Create a variable
    problem.create_decision_variable(var_name="var1", lower_bound=10, upper_bound=20)

    # Create a division equality constraint
    constraint = problem.create_special_constraint(
        constraint_type=SpecialConstraintType.DivisionEquality,
        input_variable=[problem.variables.last_object],
        divisor=5
    )

    # Check that the constraint was created correctly
    assert isinstance(constraint, OXDivisionEqualityConstraint)
    assert len(problem.specials) == 1
    assert len(problem.variables) == 2  # Original variable + 1 new variable

    # Check the new variable's bounds (10/5=2 to 20/5=4)
    new_var = problem.variables.last_object
    assert new_var.lower_bound == 2
    assert new_var.upper_bound == 4


def test_create_modulus_equality_constraint():
    """Test creating a modulus equality constraint."""
    problem = OXCSPProblem()

    # Create a variable
    problem.create_decision_variable(var_name="var1", lower_bound=10, upper_bound=20)

    # Create a modulus equality constraint
    constraint = problem.create_special_constraint(
        constraint_type=SpecialConstraintType.ModulusEquality,
        input_variable=[problem.variables.last_object],
        divisor=5
    )

    # Check that the constraint was created correctly
    assert isinstance(constraint, OXModuloEqualityConstraint)
    assert len(problem.specials) == 1
    assert len(problem.variables) == 2  # Original variable + 1 new variable

    # Check the new variable's bounds (0 to divisor-1)
    new_var = problem.variables.last_object
    assert new_var.lower_bound == 0
    assert new_var.upper_bound == 4


def test_create_summation_equality_constraint():
    """Test creating a summation equality constraint."""
    problem = OXCSPProblem()

    # Create variables
    problem.create_decision_variable(var_name="var1", lower_bound=2, upper_bound=4)
    problem.create_decision_variable(var_name="var2", lower_bound=3, upper_bound=5)

    # Create a summation equality constraint
    constraint = problem.create_special_constraint(
        constraint_type=SpecialConstraintType.SummationEquality,
        input_variables=list(problem.variables)
    )

    # Check that the constraint was created correctly
    assert isinstance(constraint, OXSummationEqualityConstraint)
    assert len(problem.specials) == 1
    assert len(problem.variables) == 3  # Original 2 variables + 1 new variable

    # Check the new variable's bounds (2+3=5 to 4+5=9)
    new_var = problem.variables.last_object
    assert new_var.lower_bound == 5
    assert new_var.upper_bound == 9


def test_oxlpproblem_initialization():
    """Test default initialization of OXLPProblem."""
    problem = OXLPProblem()

    # Check default values
    assert isinstance(problem.db, OXDatabase)
    assert len(problem.variables) == 0
    assert len(problem.constraints) == 0
    assert len(problem.specials) == 0
    assert isinstance(problem.objective_function, OXpression)
    assert problem.objective_type == ObjectiveType.MINIMIZE


def test_create_objective_function():
    """Test creating an objective function in OXLPProblem."""
    problem = OXLPProblem()

    # Create variables
    problem.create_decision_variable(var_name="var1", upper_bound=10)
    problem.create_decision_variable(var_name="var2", upper_bound=20)

    # Get variable IDs
    var_ids = [var.id for var in problem.variables]

    # Create an objective function
    problem.create_objective_function(
        variables=var_ids,
        weights=[1, 2],
        objective_type=ObjectiveType.MAXIMIZE
    )

    # Check that the objective function was created correctly
    assert problem.objective_function.variables == var_ids
    assert problem.objective_function.weights == [1, 2]
    assert problem.objective_type == ObjectiveType.MAXIMIZE


def test_oxgpproblem_initialization():
    """Test default initialization of OXGPProblem."""
    problem = OXGPProblem()

    # Check default values
    assert isinstance(problem.db, OXDatabase)
    assert len(problem.variables) == 0
    assert len(problem.constraints) == 0
    assert len(problem.specials) == 0
    assert isinstance(problem.objective_function, OXpression)
    assert problem.objective_type == ObjectiveType.MINIMIZE
    assert len(problem.goal_constraints) == 0


def test_create_goal_constraint():
    """Test creating a goal constraint in OXGPProblem."""
    problem = OXGPProblem()

    # Create variables
    problem.create_decision_variable(var_name="var1", upper_bound=10)
    problem.create_decision_variable(var_name="var2", upper_bound=20)

    # Get variable IDs
    var_ids = [var.id for var in problem.variables]

    # Create a goal constraint
    problem.create_goal_constraint(
        variables=var_ids,
        weights=[1, 2],
        operator=RelationalOperators.LESS_THAN_EQUAL,
        value=30
    )

    # Check that the goal constraint was created correctly
    assert len(problem.goal_constraints) == 1
    assert len(problem.constraints) == 0  # The constraint is moved to goal_constraints

    goal = problem.goal_constraints.last_object
    assert goal.expression.variables == var_ids
    assert goal.expression.weights == [1, 2]
    assert goal.relational_operator == RelationalOperators.EQUAL
    assert goal.rhs == 30


def test_oxgpproblem_create_objective_function():
    """Test creating an objective function in OXGPProblem."""
    problem = OXGPProblem()

    # Create variables
    problem.create_decision_variable(var_name="var1", upper_bound=10)
    problem.create_decision_variable(var_name="var2", upper_bound=20)

    # Create goal constraints
    var_ids = [var.id for var in problem.variables]
    problem.create_goal_constraint(
        variables=var_ids,
        weights=[1, 2],
        operator=RelationalOperators.LESS_THAN_EQUAL,
        value=30
    )

    # Create an objective function
    problem.create_objective_function()

    # Check that the objective function was created correctly
    # It should include the undesired deviation variables from the goal constraints
    assert len(problem.objective_function.variables) > 0
    assert all(weight == 1.0 for weight in problem.objective_function.weights)
    assert problem.objective_type == ObjectiveType.MINIMIZE


def test_parameter_validation():
    """Test parameter validation in create_constraint method."""
    problem = OXCSPProblem()

    # Create a variable
    problem.create_decision_variable(var_name="var1")
    var_id = problem.variables.last_object.id

    # Test missing both variable_search_function and variables
    with pytest.raises(OXception):
        problem.create_constraint(value=10)

    # Test providing both variable_search_function and variables
    with pytest.raises(OXception):
        problem.create_constraint(
            variable_search_function=lambda x: True,
            variables=[var_id],
            weights=[1],
            value=10
        )

    # Test missing both weight_calculation_function and weights
    with pytest.raises(OXception):
        problem.create_constraint(variables=[var_id], value=10)

    # Test providing both weight_calculation_function and weights
    with pytest.raises(OXception):
        problem.create_constraint(
            variables=[var_id],
            weight_calculation_function=lambda x, y: 1,
            weights=[1],
            value=10
        )

    # Test providing variable_search_function without weight_calculation_function
    with pytest.raises(OXception):
        problem.create_constraint(
            variable_search_function=lambda x: True,
            value=10
        )

    # Test mismatched lengths of variables and weights
    with pytest.raises(OXception):
        problem.create_constraint(
            variables=[var_id],
            weights=[1, 2],
            value=10
        )
