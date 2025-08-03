from uuid import UUID

from constraints.OXConstraint import OXConstraint, OXGoalConstraint, RelationalOperators
from constraints.OXpression import OXpression
from variables.OXDeviationVar import OXDeviationVar


def test_relational_operators_enum():
    """Test the RelationalOperators enum values."""
    assert RelationalOperators.GREATER_THAN == ">"
    assert RelationalOperators.GREATER_THAN_EQUAL == ">="
    assert RelationalOperators.EQUAL == "="
    assert RelationalOperators.LESS_THAN == "<"
    assert RelationalOperators.LESS_THAN_EQUAL == "<="


def test_constraint_default_initialization():
    """Test default initialization of OXConstraint."""
    constraint = OXConstraint()

    # Check default values
    assert isinstance(constraint.expression, OXpression)
    assert len(constraint.expression.variables) == 0
    assert len(constraint.expression.weights) == 0
    assert constraint.relational_operator == RelationalOperators.EQUAL
    assert constraint.rhs == 0


def test_constraint_custom_initialization():
    """Test custom initialization of OXConstraint."""
    # Create an expression for the constraint
    var_id1 = UUID("12345678-1234-5678-1234-567812345678")
    var_id2 = UUID("87654321-4321-8765-4321-876543210987")
    expr = OXpression(variables=[var_id1, var_id2], weights=[2, 3])

    # Create the constraint
    constraint = OXConstraint(
        expression=expr,
        relational_operator=RelationalOperators.LESS_THAN_EQUAL,
        rhs=10
    )

    # Check values
    assert constraint.expression == expr
    assert constraint.relational_operator == RelationalOperators.LESS_THAN_EQUAL
    assert constraint.rhs == 10


def test_rhs_fraction_properties():
    """Test the rhs_numerator and rhs_denominator properties."""
    # Test with integer RHS
    constraint = OXConstraint(rhs=10)
    assert constraint.rhs_numerator == 10
    assert constraint.rhs_denominator == 1

    # Test with fractional RHS
    constraint = OXConstraint(rhs=2.5)
    assert constraint.rhs_numerator == 5
    assert constraint.rhs_denominator == 2


def test_to_goal_with_less_than():
    """Test converting a less-than constraint to a goal constraint."""
    constraint = OXConstraint(
        relational_operator=RelationalOperators.LESS_THAN,
        rhs=10
    )

    goal = constraint.to_goal()

    # Check that the goal constraint has the correct properties
    assert isinstance(goal, OXGoalConstraint)
    assert goal.relational_operator == RelationalOperators.EQUAL
    assert goal.rhs == 10
    assert goal.negative_deviation_variable.desired is True
    assert goal.positive_deviation_variable.desired is False


def test_to_goal_with_less_than_equal():
    """Test converting a less-than-equal constraint to a goal constraint."""
    constraint = OXConstraint(
        relational_operator=RelationalOperators.LESS_THAN_EQUAL,
        rhs=10
    )

    goal = constraint.to_goal()

    # Check that the goal constraint has the correct properties
    assert isinstance(goal, OXGoalConstraint)
    assert goal.relational_operator == RelationalOperators.EQUAL
    assert goal.rhs == 10
    assert goal.negative_deviation_variable.desired is True
    assert goal.positive_deviation_variable.desired is False


def test_to_goal_with_greater_than():
    """Test converting a greater-than constraint to a goal constraint."""
    constraint = OXConstraint(
        relational_operator=RelationalOperators.GREATER_THAN,
        rhs=10
    )

    goal = constraint.to_goal()

    # Check that the goal constraint has the correct properties
    assert isinstance(goal, OXGoalConstraint)
    assert goal.relational_operator == RelationalOperators.EQUAL
    assert goal.rhs == 10
    assert goal.negative_deviation_variable.desired is False
    assert goal.positive_deviation_variable.desired is True


def test_to_goal_with_greater_than_equal():
    """Test converting a greater-than-equal constraint to a goal constraint."""
    constraint = OXConstraint(
        relational_operator=RelationalOperators.GREATER_THAN_EQUAL,
        rhs=10
    )

    goal = constraint.to_goal()

    # Check that the goal constraint has the correct properties
    assert isinstance(goal, OXGoalConstraint)
    assert goal.relational_operator == RelationalOperators.EQUAL
    assert goal.rhs == 10
    assert goal.negative_deviation_variable.desired is False
    assert goal.positive_deviation_variable.desired is True


def test_to_goal_with_equal():
    """Test converting an equal constraint to a goal constraint."""
    constraint = OXConstraint(
        relational_operator=RelationalOperators.EQUAL,
        rhs=10
    )

    goal = constraint.to_goal()

    # Check that the goal constraint has the correct properties
    assert isinstance(goal, OXGoalConstraint)
    assert goal.relational_operator == RelationalOperators.EQUAL
    assert goal.rhs == 10
    assert goal.negative_deviation_variable.desired is False
    assert goal.positive_deviation_variable.desired is False


def test_goal_constraint_default_initialization():
    """Test default initialization of OXGoalConstraint."""
    goal = OXGoalConstraint()

    # Check default values
    assert isinstance(goal.expression, OXpression)
    assert goal.relational_operator == RelationalOperators.EQUAL
    assert goal.rhs == 0
    assert isinstance(goal.positive_deviation_variable, OXDeviationVar)
    assert isinstance(goal.negative_deviation_variable, OXDeviationVar)
    assert goal.positive_deviation_variable.desired is False
    assert goal.negative_deviation_variable.desired is False


def test_goal_constraint_desired_variables():
    """Test the desired_variables property of OXGoalConstraint."""
    goal = OXGoalConstraint()

    # Initially, no variables are desired
    assert len(goal.desired_variables) == 0

    # Set positive deviation as desired
    goal.positive_deviation_variable.desired = True
    assert len(goal.desired_variables) == 1
    assert goal.positive_deviation_variable in goal.desired_variables

    # Set negative deviation as desired
    goal.negative_deviation_variable.desired = True
    assert len(goal.desired_variables) == 2
    assert goal.positive_deviation_variable in goal.desired_variables
    assert goal.negative_deviation_variable in goal.desired_variables

    # Set positive deviation as not desired
    goal.positive_deviation_variable.desired = False
    assert len(goal.desired_variables) == 1
    assert goal.negative_deviation_variable in goal.desired_variables


def test_goal_constraint_undesired_variables():
    """Test the undesired_variables property of OXGoalConstraint."""
    goal = OXGoalConstraint()

    # Initially, all variables are undesired
    assert len(goal.undesired_variables) == 2
    assert goal.positive_deviation_variable in goal.undesired_variables
    assert goal.negative_deviation_variable in goal.undesired_variables

    # Set positive deviation as desired
    goal.positive_deviation_variable.desired = True
    assert len(goal.undesired_variables) == 1
    assert goal.negative_deviation_variable in goal.undesired_variables

    # Set negative deviation as desired
    goal.negative_deviation_variable.desired = True
    assert len(goal.undesired_variables) == 0

    # Set positive deviation as not desired
    goal.positive_deviation_variable.desired = False
    assert len(goal.undesired_variables) == 1
    assert goal.positive_deviation_variable in goal.undesired_variables
