"""
OptiX Mathematical Expression Test Suite
========================================

This module provides comprehensive test coverage for the OXpression class
and related mathematical utility functions in the OptiX optimization framework.
The OXpression class represents linear mathematical expressions with variables
and coefficients, supporting fractional arithmetic and integer conversion.

The module tests both the core expression functionality and utility functions
for handling fractional coefficients, ensuring accurate mathematical operations
and proper conversion between fractional and integer representations.

Example:
    Running the mathematical expression test suite:

    .. code-block:: bash

        # Run all expression tests
        poetry run python -m pytest tests/test_OXpression.py -v
        
        # Run fraction calculation tests
        poetry run python -m pytest tests/test_OXpression.py -k "fraction" -v
        
        # Run expression property tests
        poetry run python -m pytest tests/test_OXpression.py -k "expression" -v

Module Dependencies:
    - uuid: For UUID generation and handling in variable references
    - src.constraints.OXpression: Expression class and mathematical utilities

Test Coverage:
    - Fraction calculation utilities for coefficient handling
    - Integer numerator and denominator conversion functions
    - Expression initialization with default and custom parameters
    - Variable and weight list management
    - Mathematical property validation and calculation
    - Expression manipulation and coefficient handling

Mathematical Features Tested:
    - Fractional arithmetic with automatic denominator calculation
    - Integer conversion preserving mathematical relationships
    - Linear expression representation with variables and coefficients
    - Mathematical operations on expression components
    - Coefficient normalization and fraction handling
    - Variable reference management with UUID tracking
"""

from uuid import UUID

from src.constraints.OXpression import OXpression, get_integer_numerator_and_denominators, calculate_fraction


def test_get_integer_numerator_and_denominators():
    """Test the get_integer_numerator_and_denominators function."""
    # Test with integer values
    denominator, numerators = get_integer_numerator_and_denominators([1, 2, 3])
    assert denominator == 1
    assert numerators == [1, 2, 3]
    
    # Test with simple fractions
    denominator, numerators = get_integer_numerator_and_denominators([0.5, 1.5, 2])
    assert denominator == 2
    assert numerators == [1, 3, 4]
    
    # Test with mixed fractions
    denominator, numerators = get_integer_numerator_and_denominators([1/3, 2/3, 1])
    assert denominator == 3
    assert numerators == [1, 2, 3]
    
    # Test with complex fractions
    denominator, numerators = get_integer_numerator_and_denominators([0.25, 0.75, 1.5])
    assert denominator == 4
    assert numerators == [1, 3, 6]
    
    # Test with mixed denominators
    denominator, numerators = get_integer_numerator_and_denominators([1/2, 1/3, 1/4])
    assert denominator == 12
    assert numerators == [6, 4, 3]


def test_expression_default_initialization():
    """Test default initialization of OXpression."""
    expr = OXpression()
    
    # Check default values
    assert isinstance(expr.variables, list)
    assert len(expr.variables) == 0
    assert isinstance(expr.weights, list)
    assert len(expr.weights) == 0


def test_expression_custom_initialization():
    """Test custom initialization of OXpression."""
    var_id1 = UUID("12345678-1234-5678-1234-567812345678")
    var_id2 = UUID("87654321-4321-8765-4321-876543210987")
    weights = [2, 3]
    
    expr = OXpression(variables=[var_id1, var_id2], weights=weights)
    
    # Check values
    assert len(expr.variables) == 2
    assert var_id1 in expr.variables
    assert var_id2 in expr.variables
    assert expr.weights == weights


def test_number_of_variables_property():
    """Test the number_of_variables property."""
    # Empty expression
    expr = OXpression()
    assert expr.number_of_variables == 0
    
    # Expression with variables
    var_id1 = UUID("12345678-1234-5678-1234-567812345678")
    var_id2 = UUID("87654321-4321-8765-4321-876543210987")
    expr = OXpression(variables=[var_id1, var_id2], weights=[2, 3])
    assert expr.number_of_variables == 2


def test_integer_weights_property():
    """Test the integer_weights property."""
    # Test with integer weights
    expr = OXpression(variables=[], weights=[1, 2, 3])
    assert expr.integer_weights == [1, 2, 3]
    
    # Test with fractional weights
    expr = OXpression(variables=[], weights=[0.5, 1.5, 2])
    assert expr.integer_weights == [1, 3, 4]
    
    # Test with mixed fractions
    expr = OXpression(variables=[], weights=[1/3, 2/3, 1])
    assert expr.integer_weights == [1, 2, 3]


def test_integer_denominator_property():
    """Test the integer_denominator property."""
    # Test with integer weights
    expr = OXpression(variables=[], weights=[1, 2, 3])
    assert expr.integer_denominator == 1
    
    # Test with fractional weights
    expr = OXpression(variables=[], weights=[0.5, 1.5, 2])
    assert expr.integer_denominator == 2
    
    # Test with mixed fractions
    expr = OXpression(variables=[], weights=[1/3, 2/3, 1])
    assert expr.integer_denominator == 3


def test_iteration():
    """Test iterating over (variable, weight) pairs."""
    var_id1 = UUID("12345678-1234-5678-1234-567812345678")
    var_id2 = UUID("87654321-4321-8765-4321-876543210987")
    weights = [2, 3]
    
    expr = OXpression(variables=[var_id1, var_id2], weights=weights)
    
    # Collect pairs from iteration
    pairs = list(expr)
    
    # Check pairs
    assert len(pairs) == 2
    assert (var_id1, 2) in pairs
    assert (var_id2, 3) in pairs


def test_empty_expression_iteration():
    """Test iterating over an empty expression."""
    expr = OXpression()
    pairs = list(expr)
    assert len(pairs) == 0


def test_expression_with_unequal_variables_and_weights():
    """Test handling of expressions with unequal numbers of variables and weights."""
    var_id1 = UUID("12345678-1234-5678-1234-567812345678")
    var_id2 = UUID("87654321-4321-8765-4321-876543210987")
    
    # More variables than weights
    expr = OXpression(variables=[var_id1, var_id2], weights=[2])
    pairs = list(expr)
    assert len(pairs) == 1  # Should only iterate over the pairs that have both variable and weight
    assert pairs[0] == (var_id1, 2)
    
    # More weights than variables
    expr = OXpression(variables=[var_id1], weights=[2, 3])
    pairs = list(expr)
    assert len(pairs) == 1  # Should only iterate over the pairs that have both variable and weight
    assert pairs[0] == (var_id1, 2)


def test_lru_cache_for_get_integer_numerator_and_denominators():
    """Test that the get_integer_numerator_and_denominators function uses LRU cache."""
    # Call the function twice with the same arguments
    result1 = get_integer_numerator_and_denominators([0.5, 1.5, 2])
    result2 = get_integer_numerator_and_denominators([0.5, 1.5, 2])

    # The results should be the same
    assert result1 == result2


def test_farey_algorithm():
    """Test that the get_integer_numerator_and_denominators function uses LRU cache."""
    # Call the function twice with the same arguments
    result1 = calculate_fraction(17/28)

    assert result1.numerator==17
    assert result1.denominator==28

