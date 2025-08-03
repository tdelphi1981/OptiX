Constraints Module
=================

The constraints module provides comprehensive constraint definition capabilities for optimization problems.
It includes linear constraints, goal programming constraints, special non-linear constraints, and mathematical expressions.

.. currentmodule:: constraints

Constraint Classes
------------------

Linear Constraints
~~~~~~~~~~~~~~~~~~

.. autoclass:: OXConstraint
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: OXGoalConstraint
   :members:
   :undoc-members:
   :show-inheritance:

Constraint Collections
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: OXConstraintSet
   :members:
   :undoc-members:
   :show-inheritance:

Mathematical Expressions
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: OXpression
   :members:
   :undoc-members:
   :show-inheritance:

.. autofunction:: get_integer_numerator_and_denominators

Special Constraints
~~~~~~~~~~~~~~~~~~

.. autoclass:: OXSpecialConstraint
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: OXNonLinearEqualityConstraint
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: OXMultiplicativeEqualityConstraint
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: OXDivisionEqualityConstraint
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: OXModuloEqualityConstraint
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: OXSummationEqualityConstraint
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: OXConditionalConstraint
   :members:
   :undoc-members:
   :show-inheritance:

Enumerations
------------

.. autoclass:: RelationalOperators
   :members:
   :undoc-members:

   Available operators:

   * ``GREATER_THAN`` - Greater than (>)
   * ``GREATER_THAN_EQUAL`` - Greater than or equal (>=)
   * ``EQUAL`` - Equal (=)
   * ``LESS_THAN`` - Less than (<)
   * ``LESS_THAN_EQUAL`` - Less than or equal (<=)

Examples
--------

Basic Linear Constraints
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from constraints import OXConstraint, OXpression, RelationalOperators
   from variables import OXVariable

   # Create variables
   x = OXVariable(name="x", lower_bound=0, upper_bound=100)
   y = OXVariable(name="y", lower_bound=0, upper_bound=100)

   # Create expression: 2x + 3y
   expr = OXpression(variables=[x.id, y.id], weights=[2, 3])

   # Create constraint: 2x + 3y <= 500
   constraint = OXConstraint(
       expression=expr,
       relational_operator=RelationalOperators.LESS_THAN_EQUAL,
       rhs=500,
       name="Resource capacity constraint"
   )

   print(f"Constraint: {constraint}")

Goal Programming Constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from constraints import OXConstraint, RelationalOperators

   # Create a regular constraint
   constraint = OXConstraint(
       expression=expr,
       relational_operator=RelationalOperators.LESS_THAN_EQUAL,
       rhs=100,
       name="Production target"
   )

   # Convert to goal constraint
   goal_constraint = constraint.to_goal()

   # Check deviation variables
   print(f"Positive deviation desired: {goal_constraint.positive_deviation_variable.desired}")
   print(f"Negative deviation desired: {goal_constraint.negative_deviation_variable.desired}")

Constraint Sets
~~~~~~~~~~~~~~

.. code-block:: python

   from constraints import OXConstraintSet, OXConstraint

   # Create constraint set
   constraint_set = OXConstraintSet(name="Production Constraints")

   # Add constraints to the set
   for i, constraint in enumerate(production_constraints):
       # Add metadata for querying
       constraint.related_data["category"] = "production"
       constraint.related_data["priority"] = "high" if i < 3 else "medium"
       constraint_set.add_object(constraint)

   print(f"Total constraints: {len(constraint_set)}")

   # Query constraints by metadata
   high_priority = constraint_set.query(priority="high")
   production_constraints = constraint_set.query(category="production")

Mathematical Expressions
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from constraints import OXpression
   from variables import OXVariable

   # Create variables
   x = OXVariable(name="x", lower_bound=0)
   y = OXVariable(name="y", lower_bound=0)
   z = OXVariable(name="z", lower_bound=0)

   # Create expression: 2.5x + 1.5y + 3z
   expr = OXpression(
       variables=[x.id, y.id, z.id],
       weights=[2.5, 1.5, 3]
   )

   # Access variable coefficients
   for var_id, weight in zip(expr.variables, expr.weights):
       print(f"Variable {var_id}: coefficient {weight}")

   # Convert to integer coefficients
   int_weights, denominator = expr.get_integer_weights()
   print(f"Integer weights: {int_weights}, common denominator: {denominator}")

Special Constraints
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from constraints import OXMultiplicativeEqualityConstraint, OXDivisionEqualityConstraint
   from variables import OXVariable

   # Create variables for multiplication
   x = OXVariable(name="x", lower_bound=0, upper_bound=50)
   y = OXVariable(name="y", lower_bound=0, upper_bound=50)
   product = OXVariable(name="product", lower_bound=0, upper_bound=2500)

   # Multiplication constraint: x * y = product
   mult_constraint = OXMultiplicativeEqualityConstraint(
       left_variable_id=x.id,
       right_variable_id=y.id,
       result_variable_id=product.id,
       name="Product calculation"
   )

   # Division constraint: x / y = quotient (integer division)
   quotient = OXVariable(name="quotient", lower_bound=0, upper_bound=100)
   div_constraint = OXDivisionEqualityConstraint(
       left_variable_id=x.id,
       right_variable_id=y.id,
       result_variable_id=quotient.id,
       name="Division calculation"
   )

Conditional Constraints
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from constraints import OXConditionalConstraint
   from variables import OXVariable

   # Create binary variables
   condition = OXVariable(name="use_machine", lower_bound=0, upper_bound=1, variable_type="binary")
   production = OXVariable(name="production", lower_bound=0, upper_bound=100)
   cost = OXVariable(name="cost", lower_bound=0, upper_bound=1000)

   # Conditional constraint: if use_machine then production >= 10
   conditional = OXConditionalConstraint(
       condition_variable_id=condition.id,
       implication_variable_id=production.id,
       threshold_value=10,
       name="Minimum production when machine is used"
   )

Constraint Validation
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def validate_constraint_satisfaction(constraint, variable_values):
       """Check if a constraint is satisfied by given variable values."""
       
       # Calculate left-hand side value
       lhs_value = 0
       for var_id, weight in zip(constraint.expression.variables, constraint.expression.weights):
           lhs_value += weight * variable_values.get(var_id, 0)
       
       # Check constraint satisfaction
       tolerance = 1e-6
       
       if constraint.relational_operator == RelationalOperators.LESS_THAN_EQUAL:
           return lhs_value <= constraint.rhs + tolerance
       elif constraint.relational_operator == RelationalOperators.GREATER_THAN_EQUAL:
           return lhs_value >= constraint.rhs - tolerance
       elif constraint.relational_operator == RelationalOperators.EQUAL:
           return abs(lhs_value - constraint.rhs) <= tolerance
       elif constraint.relational_operator == RelationalOperators.LESS_THAN:
           return lhs_value < constraint.rhs + tolerance
       elif constraint.relational_operator == RelationalOperators.GREATER_THAN:
           return lhs_value > constraint.rhs - tolerance
       
       return False

   # Usage
   is_satisfied = validate_constraint_satisfaction(constraint, solution_values)
   print(f"Constraint satisfied: {is_satisfied}")

Precise Arithmetic with Fractions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from constraints import OXpression, get_integer_numerator_and_denominators

   # Create expression with decimal coefficients
   expr = OXpression(
       variables=[x.id, y.id, z.id],
       weights=[0.333, 0.667, 1.5]  # These will be converted to fractions
   )

   # Convert to integer representation for solver compatibility
   int_weights, common_denom = get_integer_numerator_and_denominators(expr.weights)
   print(f"Integer weights: {int_weights}")
   print(f"Common denominator: {common_denom}")

   # Access fraction properties
   for i, weight in enumerate(expr.weights):
       frac_weight = expr.get_fraction_weight(i)
       print(f"Weight {i}: {frac_weight.numerator}/{frac_weight.denominator}")

See Also
--------

* :doc:`problem` - Problem classes that use constraints
* :doc:`variables` - Variable definitions and management  
* :doc:`solvers` - Solver implementations that handle constraints
* :doc:`../user_guide/constraints` - Advanced constraint modeling guide