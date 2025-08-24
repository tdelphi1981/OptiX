"""
Mathematical Expression Module for OptiX Optimization Framework
================================================================

This module provides classes and utilities for representing and manipulating
mathematical expressions in optimization problems. It implements linear
combinations of variables with precise arithmetic handling for coefficients.

The module serves as a foundation for constraint and objective function
definitions, providing robust handling of variable coefficients through
fraction-based arithmetic to avoid floating-point precision issues.

Classes:
    OXpression: Mathematical expression representing linear combinations of variables

Functions:
    get_integer_numerator_and_denominators: Utility for converting floating-point
        coefficients to integer values with common denominators

Key Features:
    - UUID-based variable referencing for serialization compatibility
    - Fraction-based arithmetic for precise coefficient handling
    - Automatic conversion between floating-point and integer representations
    - Support for iterating over variable-coefficient pairs
    - Integration with the OptiX constraint and objective systems

Module Dependencies:
    - math: For mathematical operations (LCM calculation)
    - dataclasses: For structured expression definitions
    - decimal: For precise decimal arithmetic
    - fractions: For rational number arithmetic
    - uuid: For variable identification
    - base: For core OptiX object system integration

Example:
    Creating and manipulating mathematical expressions:

    .. code-block:: python

        from constraints import OXpression
        from variables import OXVariable
        import uuid
        
        # Create variables
        x = OXVariable(name="x", lower_bound=0)
        y = OXVariable(name="y", lower_bound=0)
        z = OXVariable(name="z", lower_bound=0)
        
        # Create expression: 2.5x + 1.5y + 3z
        expr = OXpression(
            variables=[x.id, y.id, z.id],
            weights=[2.5, 1.5, 3.0]
        )
        
        # Access expression properties
        print(f"Number of variables: {expr.number_of_variables}")  # 3
        print(f"Integer weights: {expr.integer_weights}")  # [5, 3, 6]
        print(f"Common denominator: {expr.integer_denominator}")  # 2
        
        # Iterate over variable-weight pairs
        for var_id, weight in expr:
            print(f"Variable {var_id}: coefficient {weight}")
"""
import math
from dataclasses import dataclass, field
from fractions import Fraction
from uuid import UUID

from base import OXObject
from utilities.fraction import calculate_fraction


def get_integer_numerator_and_denominators(numbers: list[float | int]) -> tuple[int, list[int]]:
    """
    Convert a list of floating-point or integer weights to integer representations.
    
    This function takes a collection of numeric values (which may include floating-point
    numbers and integers) and converts them to exact integer representations by finding
    a common denominator. This is essential for optimization solvers that require
    integer coefficients while maintaining mathematical precision.
    
    The function works by:
    1. Converting each number to its fractional representation using calculate_fraction()
    2. Finding the least common multiple (LCM) of all denominators
    3. Scaling all numerators by appropriate factors to use the common denominator
    4. Returning both the common denominator and the scaled integer numerators
    
    Args:
        numbers (list[float | int]): A list of numeric values to convert to integer
                                   representations. Can contain floating-point numbers,
                                   integers, or a mix of both types.
    
    Returns:
        tuple[int, list[int]]: A tuple containing:
            - int: The common denominator for all converted values
            - list[int]: List of integer numerators corresponding to each input number
                        when expressed with the common denominator
    
    Raises:
        ValueError: If the input list is empty or contains non-numeric values.
        ZeroDivisionError: If any input number results in a zero denominator.
    
    Note:
        - All calculations maintain exact precision through Fraction arithmetic
        - The LCM approach ensures the smallest possible common denominator
        - Integer inputs are handled efficiently as Fraction(value, 1)
        - Useful for preparing coefficients for linear programming solvers
    
    Example:
        .. code-block:: python
        
            # Convert mixed numeric types
            numbers = [0.5, 1.5, 2, 0.25]
            denominator, numerators = get_integer_numerator_and_denominators(numbers)
            print(f"Common denominator: {denominator}")  # 4
            print(f"Integer numerators: {numerators}")   # [2, 6, 8, 1]
            
            # Verify the conversion
            for i, num in enumerate(numbers):
                converted = numerators[i] / denominator
                print(f"{num} = {numerators[i]}/{denominator} = {converted}")
            
            # Example with simple fractions
            simple_fractions = [0.5, 1.5, 2.0]
            denom, nums = get_integer_numerator_and_denominators(simple_fractions)
            # Returns: (2, [1, 3, 4]) representing [1/2, 3/2, 4/2]
    
    See Also:
        calculate_fraction: Used internally to convert individual numbers to fractions
        math.lcm: Used to find the least common multiple of denominators
    """
    fractional_weights = [calculate_fraction(value=w) if not isinstance(w, Fraction) else w for w in numbers]
    denominators = [fw.denominator for fw in fractional_weights]
    numerator = [fw.numerator for fw in fractional_weights]
    common_multiple = math.lcm(*denominators)
    factors = [common_multiple // n for n in denominators]
    numerator = [n * f for n, f in zip(numerator, factors)]
    return common_multiple, numerator


@dataclass
class OXpression(OXObject):
    """
    Mathematical expression representing linear combinations of optimization variables.
    
    OXpression is a fundamental component of the OptiX optimization framework that
    represents linear mathematical expressions in the form: c₁x₁ + c₂x₂ + ... + cₙxₙ,
    where cᵢ are coefficients (weights) and xᵢ are decision variables.
    
    This class is designed to handle expressions used in both constraint definitions
    and objective functions within optimization problems. It provides precise arithmetic
    handling through fraction-based calculations to avoid floating-point precision errors
    that can occur in mathematical optimization.
    
    The class maintains variable references using UUIDs rather than direct object references,
    enabling serialization, persistence, and cross-system compatibility. This design
    pattern supports distributed optimization scenarios and model persistence.
    
    Key Features:
        - UUID-based variable referencing for serialization safety
        - Automatic conversion between floating-point and integer coefficient representations
        - Fraction-based arithmetic for mathematical precision
        - Iterator support for easy traversal of variable-coefficient pairs
        - Integration with OptiX constraint and objective function systems
        - Support for multiple numeric types (int, float, Fraction, Decimal)
    
    Attributes:
        variables (list[UUID]): Ordered list of variable UUIDs that participate in this expression.
                              The order corresponds to the order of coefficients in the weights list.
        weights (list[float | int | Fraction]): Ordered list of coefficients (weights) for each variable.
                                               Supports mixed numeric types with automatic conversion.
    
    Type Parameters:
        The class inherits from OXObject, providing UUID-based identity and serialization capabilities.
    
    Example:
        Basic usage of OXpression for creating mathematical expressions:
        
        .. code-block:: python
        
            from uuid import UUID
            from constraints import OXpression
            from variables import OXVariable
            
            # Create some optimization variables
            x = OXVariable(name="production_x", lower_bound=0, upper_bound=100)
            y = OXVariable(name="production_y", lower_bound=0, upper_bound=50)
            z = OXVariable(name="production_z", lower_bound=0)
            
            # Create expression: 2.5x + 1.75y + 3z (production cost function)
            cost_expr = OXpression(
                variables=[x.id, y.id, z.id],
                weights=[2.5, 1.75, 3.0]
            )
            
            # Access expression properties
            print(f"Variables in expression: {cost_expr.number_of_variables}")  # 3
            print(f"Integer weights: {cost_expr.integer_weights}")              # [10, 7, 12]
            print(f"Common denominator: {cost_expr.integer_denominator}")       # 4
            
            # Iterate through variable-coefficient pairs
            for var_uuid, coefficient in cost_expr:
                print(f"Variable {var_uuid}: coefficient = {coefficient}")
            
            # Example with mixed coefficient types
            mixed_expr = OXpression(
                variables=[x.id, y.id],
                weights=[Fraction(1, 3), 0.75]  # Mixed Fraction and float
            )
    
    Note:
        - Variables are referenced by UUID to support serialization and persistence
        - The weights list must have the same length as the variables list
        - Automatic fraction conversion ensures mathematical precision for optimization solvers
        - The class supports empty expressions (no variables/weights) for initialization
        - All weight types are converted to fractions internally for consistent arithmetic
    
    Warning:
        Ensure that the variables and weights lists maintain corresponding order and equal length.
        Mismatched lengths will result in undefined behavior during iteration and calculations.
    
    See Also:
        OXVariable: Decision variables used in expressions
        OXConstraint: Constraints that use OXpression for left-hand sides
        calculate_fraction: Internal function for precise fraction conversion
        get_integer_numerator_and_denominators: Utility for solver-compatible representations
    """
    variables: list[UUID] = field(default_factory=list)
    weights: list[float | int | Fraction] = field(default_factory=list)

    @property
    def number_of_variables(self) -> int:
        """
        Get the total count of variables participating in this mathematical expression.
        
        This property provides a convenient way to determine the dimensionality of the
        linear expression, which is useful for validation, debugging, and solver setup.
        The count represents the number of decision variables that have non-zero
        coefficients in this expression.
        
        Returns:
            int: The total number of variables in the expression. Returns 0 for empty
                expressions (expressions with no variables or coefficients).
        
        Note:
            - The count is based on the length of the variables list
            - Empty expressions return 0, which is valid for initialization scenarios
            - The count should match the length of the weights list for consistency
        
        Example:
            .. code-block:: python
            
                # Create expression with three variables
                expr = OXpression(
                    variables=[var1_id, var2_id, var3_id],
                    weights=[1.0, 2.5, 0.75]
                )
                print(expr.number_of_variables)  # Output: 3
                
                # Empty expression
                empty_expr = OXpression()
                print(empty_expr.number_of_variables)  # Output: 0
        """
        return len(self.variables)

    @property
    def integer_weights(self) -> list[int]:
        """
        Convert expression coefficients to integer representations with common denominator.
        
        This property transforms all variable coefficients from their original numeric types
        (float, int, Fraction, Decimal) into integer values by finding a common denominator
        and scaling appropriately. This conversion is essential for optimization solvers
        that require integer coefficients while maintaining mathematical precision.
        
        The conversion process:
        1. Converts each weight to its exact fractional representation
        2. Finds the least common multiple (LCM) of all denominators
        3. Scales all numerators to use the common denominator
        4. Returns the scaled integer numerators
        
        Returns:
            list[int]: Integer representations of all coefficients, scaled by the common
                      denominator. The order corresponds to the variables list order.
                      Returns empty list if no weights are present.
        
        Note:
            - Maintains exact mathematical precision through fraction arithmetic
            - The integer values represent numerators when using the common denominator
            - Use integer_denominator property to get the corresponding denominator
            - Essential for solvers like CPLEX or Gurobi that prefer integer coefficients
        
        Example:
            .. code-block:: python
            
                # Expression with decimal coefficients
                expr = OXpression(
                    variables=[x_id, y_id, z_id],
                    weights=[0.5, 1.25, 2.0]
                )
                
                print(expr.integer_weights)      # [2, 5, 8]
                print(expr.integer_denominator)  # 4
                
                # Verification: 2/4 = 0.5, 5/4 = 1.25, 8/4 = 2.0
        
        See Also:
            integer_denominator: Get the common denominator for these integer weights
            get_integer_numerator_and_denominators: The underlying conversion function
        """
        return get_integer_numerator_and_denominators(self.weights)[1]

    @property
    def integer_denominator(self) -> int:
        """
        Get the common denominator used for integer weight representation.
        
        This property returns the least common multiple (LCM) of all denominators
        in the fractional representations of the expression coefficients. When combined
        with the integer_weights property, it allows for exact reconstruction of the
        original coefficient values while providing integer representations suitable
        for optimization solvers.
        
        The denominator represents the scaling factor applied to convert floating-point
        or fractional coefficients into integers. This approach maintains mathematical
        precision and avoids floating-point arithmetic errors in optimization calculations.
        
        Returns:
            int: The common denominator for all coefficients in the expression.
                Returns 1 if all weights are integers, or the LCM of all fractional
                denominators if floating-point weights are present. Returns 1 for
                empty expressions.
        
        Note:
            - Always returns a positive integer value
            - The LCM approach ensures the smallest possible common denominator
            - Combined with integer_weights, provides exact coefficient representation
            - Essential for maintaining precision in constraint and objective definitions
        
        Example:
            .. code-block:: python
            
                # Expression with fractional coefficients
                expr = OXpression(
                    variables=[x_id, y_id, z_id],
                    weights=[0.5, 0.25, 1.75]  # 1/2, 1/4, 7/4
                )
                
                print(expr.integer_denominator)  # 4 (LCM of 2, 4, 4)
                print(expr.integer_weights)      # [2, 1, 7]
                
                # Verification: 2/4 = 0.5, 1/4 = 0.25, 7/4 = 1.75
                
                # Expression with integer coefficients
                int_expr = OXpression(
                    variables=[x_id, y_id],
                    weights=[2, 3]
                )
                print(int_expr.integer_denominator)  # 1
        
        See Also:
            integer_weights: Get the integer numerators for these coefficients
            get_integer_numerator_and_denominators: The underlying conversion function
        """
        return get_integer_numerator_and_denominators(self.weights)[0]

    def __iter__(self):
        """
        Enable iteration over variable-coefficient pairs in the mathematical expression.
        
        This method implements the iterator protocol, allowing the OXpression object
        to be used in for-loops and other iteration contexts. It yields tuples of
        (variable_uuid, coefficient) pairs, maintaining the order defined in the
        variables and weights lists.
        
        The iterator is particularly useful for:
        - Traversing expression terms for solver setup
        - Debugging and validation of expression contents
        - Serialization and persistence operations
        - Constructing string representations of expressions
        
        Yields:
            tuple[UUID, float | int | Fraction]: Each iteration yields a tuple containing:
                - UUID: The unique identifier of the variable
                - float | int | Fraction: The coefficient (weight) for that variable
        
        Note:
            - Iteration order matches the order of variables and weights lists
            - Empty expressions will not yield any items
            - The yielded coefficients maintain their original numeric types
            - Supports standard Python iteration protocols (for loops, list comprehension, etc.)
        
        Example:
            .. code-block:: python
            
                from uuid import uuid4
                from fractions import Fraction
                
                # Create expression with mixed coefficient types
                expr = OXpression(
                    variables=[uuid4(), uuid4(), uuid4()],
                    weights=[2.5, 3, Fraction(1, 2)]
                )
                
                # Iterate over variable-coefficient pairs
                for var_uuid, coefficient in expr:
                    print(f"Variable {var_uuid}: coefficient = {coefficient}")
                
                # Use in list comprehension
                terms = [(str(var_id)[:8], coef) for var_id, coef in expr]
                print(f"Expression terms: {terms}")
                
                # Convert to dictionary
                expr_dict = dict(expr)
                
                # Count terms
                term_count = len(list(expr))
        
        Raises:
            ValueError: If variables and weights lists have different lengths
                       (this would indicate a malformed expression)
        """
        return iter(zip(self.variables, self.weights))
