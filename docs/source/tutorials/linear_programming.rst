Linear Programming Tutorial
===========================

This tutorial provides a comprehensive introduction to Linear Programming (LP) using OptiX.
You'll learn the theory behind LP, how to formulate problems, and implement solutions step by step.

What is Linear Programming?
---------------------------

Linear Programming is a mathematical optimization technique for finding the best outcome
(maximum or minimum value) in a mathematical model with linear relationships.

Key Components
~~~~~~~~~~~~~

1. **Decision Variables**: Variables you can control
2. **Objective Function**: What you want to optimize (linear combination of variables)
3. **Constraints**: Linear inequalities or equalities that limit feasible solutions
4. **Feasible Region**: Set of all points satisfying constraints
5. **Optimal Solution**: Best feasible point according to objective function

Mathematical Form
~~~~~~~~~~~~~~~~

Standard LP formulation:

.. math::

   \begin{align}
   \text{minimize/maximize} \quad & c^T x \\
   \text{subject to} \quad & Ax \leq b \\
   & x \geq 0
   \end{align}

Where:
- :math:`x` is the vector of decision variables
- :math:`c` is the vector of objective coefficients
- :math:`A` is the constraint coefficient matrix
- :math:`b` is the vector of constraint bounds

Tutorial 1: Basic LP Problem
----------------------------

Let's start with a simple two-variable problem that can be visualized graphically.

Problem Statement
~~~~~~~~~~~~~~~~

A furniture company makes chairs and tables. Each chair requires 1 hour of labor and 2 units of wood,
earning $3 profit. Each table requires 2 hours of labor and 1 unit of wood, earning $2 profit.
The company has 100 hours of labor and 80 units of wood available. How many chairs and tables
should they make to maximize profit?

Mathematical Formulation
~~~~~~~~~~~~~~~~~~~~~~~

**Decision Variables:**
- :math:`x_1` = number of chairs to make
- :math:`x_2` = number of tables to make

**Objective Function:**
Maximize profit: :math:`3x_1 + 2x_2`

**Constraints:**
- Labor: :math:`1x_1 + 2x_2 \leq 100`
- Wood: :math:`2x_1 + 1x_2 \leq 80`
- Non-negativity: :math:`x_1, x_2 \geq 0`

Implementation
~~~~~~~~~~~~~

.. code-block:: python

   from problem import OXLPProblem, ObjectiveType
   from constraints import RelationalOperators
   from solvers import solve

   def solve_furniture_problem():
       """Solve the furniture production problem."""
       
       # Step 1: Create LP problem
       problem = OXLPProblem()
       
       # Step 2: Define decision variables
       problem.create_decision_variable(
           var_name="chairs",
           description="Number of chairs to produce",
           lower_bound=0,
           upper_bound=1000,  # Reasonable upper bound
           variable_type="continuous"
       )
       
       problem.create_decision_variable(
           var_name="tables", 
           description="Number of tables to produce",
           lower_bound=0,
           upper_bound=1000,
           variable_type="continuous"
       )
       
       # Step 3: Add constraints
       # Labor constraint: 1*chairs + 2*tables <= 100
       problem.create_constraint(
           variables=[var.id for var in problem.variables],
           weights=[1, 2],  # Labor hours per unit
           operator=RelationalOperators.LESS_THAN_EQUAL,
           value=100,  # Available labor hours
           description="Labor hours constraint"
       )
       
       # Wood constraint: 2*chairs + 1*tables <= 80
       problem.create_constraint(
           variables=[var.id for var in problem.variables],
           weights=[2, 1],  # Wood units per unit
           operator=RelationalOperators.LESS_THAN_EQUAL,
           value=80,  # Available wood units
           description="Wood units constraint"
       )
       
       # Step 4: Set objective function
       # Maximize: 3*chairs + 2*tables
       problem.create_objective_function(
           variables=[var.id for var in problem.variables],
           weights=[3, 2],  # Profit per unit
           objective_type=ObjectiveType.MAXIMIZE
       )
       
       # Step 5: Solve the problem
       status, solution = solve(problem, 'ORTools')
       
       # Step 6: Analyze results
       if solution and solution[0].objective_value is not None:
           print("🪑 Furniture Production Optimization")
           print("=" * 40)
           print(f"Status: {status}")
           print(f"Maximum Profit: ${solution[0].objective_value:.2f}")
           print()
           
           for variable in problem.variables:
               value = solution[0].variable_values.get(variable.id, 0)
               print(f"{variable.description}: {value:.2f}")
           
           return problem, solution[0]
       else:
           print("No optimal solution found")
           return problem, None

   # Run the example
   problem, solution = solve_furniture_problem()

Understanding the Solution
~~~~~~~~~~~~~~~~~~~~~~~~~

The optimal solution typically produces approximately:
- **20 chairs** and **40 tables**
- **Maximum profit: $140**

This solution is found at the intersection of the two constraint lines, demonstrating
a key LP property: optimal solutions occur at vertices of the feasible region.

Tutorial 2: Multi-Resource Problem
----------------------------------

Let's expand to a more complex problem with multiple resources and products.

Problem Statement
~~~~~~~~~~~~~~~~

A factory produces three products (A, B, C) using three resources (labor, material, machine time).
We want to maximize profit while respecting resource limitations.

.. code-block:: python

   def solve_multi_resource_problem():
       """Solve a multi-resource production problem."""
       
       # Problem data
       products = [
           {'name': 'Product_A', 'profit': 40, 'labor': 1, 'material': 3, 'machine': 1},
           {'name': 'Product_B', 'profit': 30, 'labor': 2, 'material': 1, 'machine': 2}, 
           {'name': 'Product_C', 'profit': 20, 'labor': 1, 'material': 2, 'machine': 1}
       ]
       
       resources = {
           'labor': 100,      # Available labor hours
           'material': 150,   # Available material units
           'machine': 80      # Available machine hours
       }
       
       # Create problem
       problem = OXLPProblem()
       
       # Create variables
       for product in products:
           problem.create_decision_variable(
               var_name=f"produce_{product['name']}",
               description=f"Units of {product['name']} to produce",
               lower_bound=0,
               upper_bound=1000,
               variable_type="continuous"
           )
       
       # Resource constraints
       for resource, capacity in resources.items():
           resource_usage = [product[resource] for product in products]
           
           problem.create_constraint(
               variables=[var.id for var in problem.variables],
               weights=resource_usage,
               operator=RelationalOperators.LESS_THAN_EQUAL,
               value=capacity,
               description=f"{resource.title()} capacity constraint"
           )
       
       # Objective function: maximize profit
       profit_coefficients = [product['profit'] for product in products]
       
       problem.create_objective_function(
           variables=[var.id for var in problem.variables],
           weights=profit_coefficients,
           objective_type=ObjectiveType.MAXIMIZE
       )
       
       # Solve and analyze
       status, solution = solve(problem, 'ORTools')
       
       if solution and solution[0].objective_value is not None:
           print("🏭 Multi-Resource Production Optimization")
           print("=" * 50)
           print(f"Maximum Profit: ${solution[0].objective_value:.2f}")
           print()
           
           # Production plan
           print("Production Plan:")
           total_profit = 0
           for i, (variable, product) in enumerate(zip(problem.variables, products)):
               quantity = solution[0].variable_values.get(variable.id, 0)
               profit = quantity * product['profit']
               total_profit += profit
               
               print(f"  {product['name']}: {quantity:.2f} units (${profit:.2f})")
           
           print(f"\nTotal Profit: ${total_profit:.2f}")
           
           # Resource utilization
           print("\nResource Utilization:")
           for resource, capacity in resources.items():
               used = sum(
                   solution[0].variable_values.get(problem.variables[i].id, 0) * products[i][resource]
                   for i in range(len(products))
               )
               utilization = (used / capacity) * 100
               print(f"  {resource.title()}: {used:.1f}/{capacity} ({utilization:.1f}%)")
       
       return problem, solution[0] if solution else None

Tutorial 3: Advanced LP Concepts
--------------------------------

Sensitivity Analysis
~~~~~~~~~~~~~~~~~~~

Understanding how changes in parameters affect the optimal solution:

.. code-block:: python

   def perform_sensitivity_analysis(base_problem, base_solution):
       """Perform sensitivity analysis on problem parameters."""
       
       print("\n📊 Sensitivity Analysis")
       print("=" * 30)
       
       # Test profit coefficient changes
       print("Profit Coefficient Sensitivity:")
       original_profits = [40, 30, 20]  # Original profit coefficients
       
       for i, product_name in enumerate(['Product_A', 'Product_B', 'Product_C']):
           print(f"\n{product_name} profit sensitivity:")
           
           for change in [-20, -10, 0, 10, 20]:  # Percentage changes
               new_profit = original_profits[i] * (1 + change/100)
               print(f"  {change:+3d}% change (${new_profit:.1f}): ", end="")
               
               # Create modified problem
               modified_problem = create_modified_problem(base_problem, i, new_profit)
               status, solution = solve(modified_problem, 'ORTools')
               
               if solution:
                   obj_change = ((solution[0].objective_value - base_solution.objective_value) 
                               / base_solution.objective_value) * 100
                   print(f"Objective {obj_change:+5.1f}%")
               else:
                   print("No solution")

   def create_modified_problem(base_problem, product_index, new_profit):
       """Create a modified problem with changed profit coefficient."""
       # Implementation would copy base problem and modify specific coefficient
       # This is a simplified version for demonstration
       pass

Shadow Prices and Dual Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Understanding the value of additional resources:

.. code-block:: python

   def analyze_shadow_prices(problem, solution):
       """Analyze shadow prices for resource constraints."""
       
       print("\n💰 Shadow Price Analysis")
       print("=" * 30)
       
       # Shadow prices indicate the value of one additional unit of each resource
       # In practice, these would be extracted from the solver's dual solution
       
       print("Resource shadow prices (value per additional unit):")
       print("  Labor: $X.XX per hour")
       print("  Material: $X.XX per unit") 
       print("  Machine: $X.XX per hour")
       print("\nNote: Shadow prices available from solver dual solution")

Integer and Binary Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Handling discrete decisions:

.. code-block:: python

   def solve_integer_problem():
       """Solve problem with integer variables."""
       
       problem = OXLPProblem()
       
       # Integer variables (can't produce fractional units)
       problem.create_decision_variable(
           var_name="machines_type_A",
           description="Number of Type A machines to buy",
           lower_bound=0,
           upper_bound=10,
           variable_type="integer"  # Must be whole number
       )
       
       problem.create_decision_variable(
           var_name="machines_type_B", 
           description="Number of Type B machines to buy",
           lower_bound=0,
           upper_bound=10,
           variable_type="integer"
       )
       
       # Binary variables (yes/no decisions)
       problem.create_decision_variable(
           var_name="open_facility",
           description="Whether to open new facility",
           lower_bound=0,
           upper_bound=1,
           variable_type="binary"  # 0 or 1 only
       )
       
       # Budget constraint
       machine_costs = [50000, 30000]  # Cost per machine
       facility_cost = 100000  # Fixed cost to open facility
       
       problem.create_constraint(
           variables=[var.id for var in problem.variables],
           weights=machine_costs + [facility_cost],
           operator=RelationalOperators.LESS_THAN_EQUAL,
           value=200000,  # Budget limit
           description="Budget constraint"
       )
       
       # Logical constraint: need facility open to buy machines
       # machines_type_A <= 10 * open_facility
       problem.create_constraint(
           variables=[problem.variables[0].id, problem.variables[2].id],
           weights=[1, -10],
           operator=RelationalOperators.LESS_THAN_EQUAL,
           value=0,
           description="Facility requirement for Type A"
       )
       
       # Similar constraint for Type B machines
       problem.create_constraint(
           variables=[problem.variables[1].id, problem.variables[2].id],
           weights=[1, -10],
           operator=RelationalOperators.LESS_THAN_EQUAL,
           value=0,
           description="Facility requirement for Type B"
       )
       
       # Objective: maximize production capacity
       capacity_per_machine = [100, 80]  # Units per day per machine
       facility_capacity = 50  # Additional capacity from facility
       
       problem.create_objective_function(
           variables=[var.id for var in problem.variables],
           weights=capacity_per_machine + [facility_capacity],
           objective_type=ObjectiveType.MAXIMIZE
       )
       
       # Solve
       status, solution = solve(problem, 'ORTools')
       
       if solution:
           print("🏗️ Facility and Equipment Planning")
           print("=" * 40)
           print(f"Maximum Capacity: {solution[0].objective_value:.0f} units/day")
           print()
           
           for variable in problem.variables:
               value = solution[0].variable_values.get(variable.id, 0)
               print(f"{variable.description}: {value:.0f}")

Tutorial 4: Common LP Patterns
------------------------------

Diet/Nutrition Problems
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def solve_nutrition_problem():
       """Standard diet problem pattern."""
       
       foods = [
           {'name': 'Bread', 'cost': 2.0, 'protein': 4, 'fat': 1, 'carbs': 15},
           {'name': 'Milk', 'cost': 3.5, 'protein': 8, 'fat': 5, 'carbs': 12},
           {'name': 'Cheese', 'cost': 8.0, 'protein': 25, 'fat': 25, 'carbs': 1},
           {'name': 'Potato', 'cost': 1.5, 'protein': 2, 'fat': 0, 'carbs': 17}
       ]
       
       requirements = {
           'protein': {'min': 55, 'max': 200},
           'fat': {'min': 20, 'max': 100},
           'carbs': {'min': 130, 'max': 300}
       }
       
       # Implementation pattern for diet problems
       problem = OXLPProblem()
       
       # Variables: quantity of each food
       for food in foods:
           problem.create_decision_variable(
               var_name=f"quantity_{food['name']}",
               description=f"Quantity of {food['name']} (servings)",
               lower_bound=0,
               upper_bound=10,  # Reasonable upper limit
               variable_type="continuous"
           )
       
       # Nutritional constraints
       for nutrient, limits in requirements.items():
           nutrient_content = [food[nutrient] for food in foods]
           
           # Minimum requirement
           problem.create_constraint(
               variables=[var.id for var in problem.variables],
               weights=nutrient_content,
               operator=RelationalOperators.GREATER_THAN_EQUAL,
               value=limits['min'],
               description=f"Minimum {nutrient} requirement"
           )
           
           # Maximum limit
           problem.create_constraint(
               variables=[var.id for var in problem.variables], 
               weights=nutrient_content,
               operator=RelationalOperators.LESS_THAN_EQUAL,
               value=limits['max'],
               description=f"Maximum {nutrient} limit"
           )
       
       # Objective: minimize cost
       costs = [food['cost'] for food in foods]
       problem.create_objective_function(
           variables=[var.id for var in problem.variables],
           weights=costs,
           objective_type=ObjectiveType.MINIMIZE
       )
       
       return problem

Transportation Problems
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def solve_transportation_problem():
       """Standard transportation problem pattern."""
       
       # Supply and demand data
       suppliers = [
           {'name': 'Plant_A', 'supply': 300},
           {'name': 'Plant_B', 'supply': 400},
           {'name': 'Plant_C', 'supply': 500}
       ]
       
       customers = [
           {'name': 'Customer_1', 'demand': 250},
           {'name': 'Customer_2', 'demand': 350},
           {'name': 'Customer_3', 'demand': 400},
           {'name': 'Customer_4', 'demand': 200}
       ]
       
       # Transportation costs (supplier x customer)
       costs = [
           [8, 6, 10, 9],   # Plant_A to customers
           [9, 12, 13, 7],  # Plant_B to customers  
           [14, 9, 16, 5]   # Plant_C to customers
       ]
       
       problem = OXLPProblem()
       
       # Variables: shipment quantities
       for i, supplier in enumerate(suppliers):
           for j, customer in enumerate(customers):
               problem.create_decision_variable(
                   var_name=f"ship_{supplier['name']}_{customer['name']}",
                   description=f"Shipment from {supplier['name']} to {customer['name']}",
                   lower_bound=0,
                   upper_bound=min(supplier['supply'], customer['demand']),
                   variable_type="continuous"
               )
       
       # Supply constraints
       var_index = 0
       for i, supplier in enumerate(suppliers):
           supplier_vars = []
           for j in range(len(customers)):
               supplier_vars.append(problem.variables[var_index].id)
               var_index += 1
           
           problem.create_constraint(
               variables=supplier_vars,
               weights=[1] * len(customers),
               operator=RelationalOperators.LESS_THAN_EQUAL,
               value=supplier['supply'],
               description=f"Supply constraint for {supplier['name']}"
           )
       
       # Demand constraints  
       for j, customer in enumerate(customers):
           customer_vars = []
           for i in range(len(suppliers)):
               var_idx = i * len(customers) + j
               customer_vars.append(problem.variables[var_idx].id)
           
           problem.create_constraint(
               variables=customer_vars,
               weights=[1] * len(suppliers),
               operator=RelationalOperators.GREATER_THAN_EQUAL,
               value=customer['demand'],
               description=f"Demand constraint for {customer['name']}"
           )
       
       # Objective: minimize transportation cost
       flat_costs = [cost for row in costs for cost in row]
       problem.create_objective_function(
           variables=[var.id for var in problem.variables],
           weights=flat_costs,
           objective_type=ObjectiveType.MINIMIZE
       )
       
       return problem

Tutorial 5: Debugging and Validation
------------------------------------

Common Issues and Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def debug_lp_problem(problem):
       """Debug common LP problem issues."""
       
       print("🔍 LP Problem Debugging")
       print("=" * 30)
       
       issues = []
       
       # Check for variables
       if not problem.variables:
           issues.append("No decision variables defined")
       
       # Check for constraints
       if not problem.constraints:
           issues.append("No constraints defined")
       
       # Check for objective
       if not hasattr(problem, 'objective_function') or not problem.objective_function:
           issues.append("No objective function defined")
       
       # Check variable bounds
       for var in problem.variables:
           if var.lower_bound > var.upper_bound:
               issues.append(f"Invalid bounds for {var.name}: [{var.lower_bound}, {var.upper_bound}]")
           
           if var.lower_bound == var.upper_bound:
               issues.append(f"Variable {var.name} is fixed to {var.lower_bound}")
       
       # Check constraint feasibility (basic checks)
       for i, constraint in enumerate(problem.constraints):
           if len(constraint.variables) != len(constraint.weights):
               issues.append(f"Constraint {i}: variables and weights length mismatch")
           
           if constraint.value < 0 and constraint.operator in [
               RelationalOperators.GREATER_THAN_EQUAL, 
               RelationalOperators.GREATER_THAN
           ]:
               issues.append(f"Constraint {i}: may be infeasible (negative RHS with >=)")
       
       # Report issues
       if issues:
           print("Issues found:")
           for issue in issues:
               print(f"  ❌ {issue}")
       else:
           print("✅ No obvious issues detected")
       
       # Problem statistics
       print(f"\nProblem Statistics:")
       print(f"  Variables: {len(problem.variables)}")
       print(f"  Constraints: {len(problem.constraints)}")
       
       if hasattr(problem, 'objective_function') and problem.objective_function:
           print(f"  Objective: {problem.objective_function.objective_type.name}")
       
       return issues

   def validate_solution(problem, solution):
       """Validate solution satisfies all constraints."""
       
       if not solution:
           print("❌ No solution to validate")
           return False
       
       print("\n✅ Solution Validation")
       print("=" * 25)
       
       violations = []
       
       for i, constraint in enumerate(problem.constraints):
           # Calculate left-hand side
           lhs = sum(
               constraint.weights[j] * solution.variable_values.get(constraint.variables[j], 0)
               for j in range(len(constraint.variables))
           )
           
           # Check constraint satisfaction
           satisfied = False
           tolerance = 1e-6
           
           if constraint.operator == RelationalOperators.LESS_THAN_EQUAL:
               satisfied = lhs <= constraint.value + tolerance
           elif constraint.operator == RelationalOperators.GREATER_THAN_EQUAL:
               satisfied = lhs >= constraint.value - tolerance
           elif constraint.operator == RelationalOperators.EQUAL:
               satisfied = abs(lhs - constraint.value) <= tolerance
           
           if not satisfied:
               violations.append({
                   'constraint': i,
                   'description': constraint.description,
                   'lhs': lhs,
                   'operator': constraint.operator.name,
                   'rhs': constraint.value,
                   'violation': abs(lhs - constraint.value)
               })
       
       if violations:
           print(f"❌ Found {len(violations)} constraint violations:")
           for v in violations:
               print(f"  Constraint {v['constraint']}: {v['lhs']:.6f} {v['operator']} {v['rhs']}")
           return False
       else:
           print("✅ All constraints satisfied")
           return True

Best Practices Summary
---------------------

**Problem Formulation**
  1. Clearly define decision variables
  2. Write objective function first
  3. Add constraints systematically
  4. Use meaningful names and descriptions
  5. Validate mathematical formulation

**Implementation Tips**
  1. Start with simple problems
  2. Add constraints incrementally
  3. Test with known solutions
  4. Use debugging functions
  5. Validate all solutions

**Performance Optimization**
  1. Tighten variable bounds
  2. Remove redundant constraints
  3. Use appropriate variable types
  4. Monitor problem size
  5. Choose optimal solver

**Common Pitfalls to Avoid**
  1. Infeasible constraint combinations
  2. Unbounded objectives
  3. Numerical precision issues
  4. Missing non-negativity constraints
  5. Incorrect constraint directions

Next Steps
----------

After mastering these LP concepts:

1. **Practice**: Implement various LP problems from different domains
2. **Advanced Topics**: Explore integer programming and mixed-integer LP
3. **Goal Programming**: Learn multi-objective optimization techniques
4. **Sensitivity Analysis**: Understand parameter changes and their effects
5. **Large-Scale Problems**: Handle real-world problem sizes and complexity

.. seealso::
   * :doc:`../examples/diet_problem` - Complete LP implementation
   * :doc:`../examples/production_planning` - Advanced LP example
   * :doc:`goal_programming` - Multi-objective optimization
   * :doc:`../user_guide/problem_types` - Problem type selection guide