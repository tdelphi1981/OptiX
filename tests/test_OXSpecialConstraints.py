from uuid import UUID

from src.constraints.OXSpecialConstraints import (
    OXSpecialConstraint,
    OXNonLinearEqualityConstraint,
    OXMultiplicativeEqualityConstraint,
    OXDivisionEqualityConstraint,
    OXModuloEqualityConstraint,
    OXSummationEqualityConstraint,
    OXConditionalConstraint
)


def test_special_constraint_initialization():
    """Test initialization of the base OXSpecialConstraint class."""
    constraint = OXSpecialConstraint()
    assert constraint.class_name == "constraints.OXSpecialConstraint"


def test_non_linear_equality_constraint_initialization():
    """Test initialization of OXNonLinearEqualityConstraint."""
    # Default initialization
    constraint = OXNonLinearEqualityConstraint()
    assert constraint.class_name == "constraints.OXNonLinearEqualityConstraint"
    assert isinstance(constraint.output_variable, UUID)
    
    # Custom initialization
    output_var_id = UUID("12345678-1234-5678-1234-567812345678")
    constraint = OXNonLinearEqualityConstraint(output_variable=output_var_id)
    assert constraint.output_variable == output_var_id


def test_multiplicative_equality_constraint_initialization():
    """Test initialization of OXMultiplicativeEqualityConstraint."""
    # Default initialization
    constraint = OXMultiplicativeEqualityConstraint()
    assert constraint.class_name == "constraints.OXMultiplicativeEqualityConstraint"
    assert isinstance(constraint.output_variable, UUID)
    assert isinstance(constraint.input_variables, list)
    assert len(constraint.input_variables) == 0
    
    # Custom initialization
    output_var_id = UUID("12345678-1234-5678-1234-567812345678")
    input_var_id1 = UUID("87654321-4321-8765-4321-876543210987")
    input_var_id2 = UUID("11111111-1111-1111-1111-111111111111")
    
    constraint = OXMultiplicativeEqualityConstraint(
        output_variable=output_var_id,
        input_variables=[input_var_id1, input_var_id2]
    )
    
    assert constraint.output_variable == output_var_id
    assert len(constraint.input_variables) == 2
    assert input_var_id1 in constraint.input_variables
    assert input_var_id2 in constraint.input_variables


def test_division_equality_constraint_initialization():
    """Test initialization of OXDivisionEqualityConstraint."""
    # Default initialization
    constraint = OXDivisionEqualityConstraint()
    assert constraint.class_name == "constraints.OXDivisionEqualityConstraint"
    assert isinstance(constraint.output_variable, UUID)
    assert isinstance(constraint.input_variable, UUID)
    assert constraint.denominator == 1
    
    # Custom initialization
    output_var_id = UUID("12345678-1234-5678-1234-567812345678")
    input_var_id = UUID("87654321-4321-8765-4321-876543210987")
    
    constraint = OXDivisionEqualityConstraint(
        output_variable=output_var_id,
        input_variable=input_var_id,
        denominator=5
    )
    
    assert constraint.output_variable == output_var_id
    assert constraint.input_variable == input_var_id
    assert constraint.denominator == 5


def test_modulo_equality_constraint_initialization():
    """Test initialization of OXModuloEqualityConstraint."""
    # Default initialization
    constraint = OXModuloEqualityConstraint()
    assert constraint.class_name == "constraints.OXModuloEqualityConstraint"
    assert isinstance(constraint.output_variable, UUID)
    assert isinstance(constraint.input_variable, UUID)
    assert constraint.denominator == 1
    
    # Custom initialization
    output_var_id = UUID("12345678-1234-5678-1234-567812345678")
    input_var_id = UUID("87654321-4321-8765-4321-876543210987")
    
    constraint = OXModuloEqualityConstraint(
        output_variable=output_var_id,
        input_variable=input_var_id,
        denominator=7
    )
    
    assert constraint.output_variable == output_var_id
    assert constraint.input_variable == input_var_id
    assert constraint.denominator == 7


def test_summation_equality_constraint_initialization():
    """Test initialization of OXSummationEqualityConstraint."""
    # Default initialization
    constraint = OXSummationEqualityConstraint()
    assert constraint.class_name == "constraints.OXSummationEqualityConstraint"
    assert isinstance(constraint.output_variable, UUID)
    assert isinstance(constraint.input_variables, list)
    assert len(constraint.input_variables) == 0
    
    # Custom initialization
    output_var_id = UUID("12345678-1234-5678-1234-567812345678")
    input_var_id1 = UUID("87654321-4321-8765-4321-876543210987")
    input_var_id2 = UUID("11111111-1111-1111-1111-111111111111")
    
    constraint = OXSummationEqualityConstraint(
        output_variable=output_var_id,
        input_variables=[input_var_id1, input_var_id2]
    )
    
    assert constraint.output_variable == output_var_id
    assert len(constraint.input_variables) == 2
    assert input_var_id1 in constraint.input_variables
    assert input_var_id2 in constraint.input_variables


def test_conditional_constraint_initialization():
    """Test initialization of OXConditionalConstraint."""
    # Default initialization
    constraint = OXConditionalConstraint()
    assert constraint.class_name == "constraints.OXConditionalConstraint"
    assert isinstance(constraint.indicator_variable, UUID)
    assert isinstance(constraint.input_constraint, UUID)
    assert isinstance(constraint.constraint_if_true, UUID)
    assert isinstance(constraint.constraint_if_false, UUID)
    
    # Custom initialization
    indicator_var_id = UUID("12345678-1234-5678-1234-567812345678")
    input_constraint_id = UUID("87654321-4321-8765-4321-876543210987")
    constraint_if_true_id = UUID("11111111-1111-1111-1111-111111111111")
    constraint_if_false_id = UUID("22222222-2222-2222-2222-222222222222")
    
    constraint = OXConditionalConstraint(
        indicator_variable=indicator_var_id,
        input_constraint=input_constraint_id,
        constraint_if_true=constraint_if_true_id,
        constraint_if_false=constraint_if_false_id
    )
    
    assert constraint.indicator_variable == indicator_var_id
    assert constraint.input_constraint == input_constraint_id
    assert constraint.constraint_if_true == constraint_if_true_id
    assert constraint.constraint_if_false == constraint_if_false_id


def test_inheritance_hierarchy():
    """Test the inheritance hierarchy of special constraint classes."""
    # Test that all special constraints inherit from OXSpecialConstraint
    assert issubclass(OXNonLinearEqualityConstraint, OXSpecialConstraint)
    assert issubclass(OXMultiplicativeEqualityConstraint, OXNonLinearEqualityConstraint)
    assert issubclass(OXDivisionEqualityConstraint, OXNonLinearEqualityConstraint)
    assert issubclass(OXModuloEqualityConstraint, OXNonLinearEqualityConstraint)
    assert issubclass(OXSummationEqualityConstraint, OXSpecialConstraint)
    assert issubclass(OXConditionalConstraint, OXSpecialConstraint)
    
    # Test instance relationships
    assert isinstance(OXMultiplicativeEqualityConstraint(), OXNonLinearEqualityConstraint)
    assert isinstance(OXDivisionEqualityConstraint(), OXNonLinearEqualityConstraint)
    assert isinstance(OXModuloEqualityConstraint(), OXNonLinearEqualityConstraint)
    assert isinstance(OXNonLinearEqualityConstraint(), OXSpecialConstraint)
    assert isinstance(OXSummationEqualityConstraint(), OXSpecialConstraint)
    assert isinstance(OXConditionalConstraint(), OXSpecialConstraint)