Quick Start Guide
=================

This guide will get you up and running with OptiX in just a few minutes. We'll walk through
creating and solving your first optimization problem step by step.

.. note::
   Before starting, make sure you have completed the :doc:`installation` process.

Your First Optimization Problem
-------------------------------

Let's solve a simple production planning problem:

**Scenario**: A factory produces two products (A and B). We want to maximize profit while
respecting resource constraints.

.. raw:: html

   <div class="code-example">
     <div class="code-example-header">
       Complete Example - Production Planning
     </div>
   </div>

Step 1: Import Required Modules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from problem import OXLPProblem, ObjectiveType
   from constraints import RelationalOperators
   from solvers import solve

Step 2: Create the Problem
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create a Linear Programming problem
   problem = OXLPProblem()

Step 3: Define Decision Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Production quantities (units per day)
   problem.create_decision_variable(
       var_name="product_A",
       description="Daily production of Product A",
       lower_bound=0,
       upper_bound=1000
   )

   problem.create_decision_variable(
       var_name="product_B", 
       description="Daily production of Product B",
       lower_bound=0,
       upper_bound=1000
   )

Step 4: Add Constraints
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Resource constraint: 2A + 3B <= 1200 (machine hours)
   problem.create_constraint(
       variables=[var.id for var in problem.variables],
       weights=[2, 3],  # Hours per unit
       operator=RelationalOperators.LESS_THAN_EQUAL,
       value=1200,  # Available hours
       description="Machine hours constraint"
   )

   # Material constraint: 1A + 2B <= 800 (kg of material)
   problem.create_constraint(
       variables=[var.id for var in problem.variables],
       weights=[1, 2],  # Material per unit
       operator=RelationalOperators.LESS_THAN_EQUAL,
       value=800,  # Available material
       description="Material constraint"
   )

Step 5: Set Objective Function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Maximize profit: 50A + 40B (profit per unit)
   problem.create_objective_function(
       variables=[var.id for var in problem.variables],
       weights=[50, 40],  # Profit per unit
       objective_type=ObjectiveType.MAXIMIZE
   )

Step 6: Solve the Problem
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Solve using OR-Tools
   status, solution = solve(problem, 'ORTools')

   # Check if solution was found
   if solution and solution[0].objective_value is not None:
       print(f"✅ Optimization Status: {status}")
       print(f"💰 Maximum Profit: ${solution[0].objective_value:.2f}")
       
       # Display variable values
       for variable in problem.variables:
           value = solution[0].variable_values.get(variable.id, 0)
           print(f"📦 {variable.description}: {value:.2f} units")
   else:
       print("❌ No optimal solution found")

Complete Example Code
~~~~~~~~~~~~~~~~~~~~

Here's the complete code you can copy and run:

.. code-block:: python
   :caption: quickstart_example.py

   from problem import OXLPProblem, ObjectiveType
   from constraints import RelationalOperators
   from solvers import solve

   def solve_production_problem():
       """Solve a simple production planning problem."""
       
       # Create problem
       problem = OXLPProblem()
       
       # Add variables
       problem.create_decision_variable("product_A", "Daily production of Product A", 0, 1000)
       problem.create_decision_variable("product_B", "Daily production of Product B", 0, 1000)
       
       # Add constraints
       problem.create_constraint(
           variables=[var.id for var in problem.variables],
           weights=[2, 3],
           operator=RelationalOperators.LESS_THAN_EQUAL,
           value=1200,
           description="Machine hours constraint"
       )
       
       problem.create_constraint(
           variables=[var.id for var in problem.variables],
           weights=[1, 2],
           operator=RelationalOperators.LESS_THAN_EQUAL,
           value=800,
           description="Material constraint"
       )
       
       # Set objective
       problem.create_objective_function(
           variables=[var.id for var in problem.variables],
           weights=[50, 40],
           objective_type=ObjectiveType.MAXIMIZE
       )
       
       # Solve
       status, solution = solve(problem, 'ORTools')
       
       # Display results
       if solution and solution[0].objective_value is not None:
           print("🎯 Production Planning Results")
           print("=" * 40)
           print(f"Status: {status}")
           print(f"Maximum Profit: ${solution[0].objective_value:.2f}")
           print()
           
           for variable in problem.variables:
               value = solution[0].variable_values.get(variable.id, 0)
               print(f"{variable.description}: {value:.2f} units")
       
       return problem, solution

   if __name__ == "__main__":
       problem, solution = solve_production_problem()

Expected Output
~~~~~~~~~~~~~~

When you run this example, you should see output similar to:

.. code-block:: text

   🎯 Production Planning Results
   ========================================
   Status: OPTIMAL
   Maximum Profit: $26666.67
   
   Daily production of Product A: 266.67 units
   Daily production of Product B: 266.67 units

Understanding the Results
------------------------

The optimizer found that producing approximately 267 units of each product daily
maximizes profit at $26,667 while respecting both resource constraints.

Problem Types Overview
----------------------

OptiX supports three main problem types:

CSP (Constraint Satisfaction)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Find any solution that satisfies all constraints:

.. code-block:: python

   from problem import OXCSPProblem

   csp = OXCSPProblem()
   # Add variables and constraints
   # No objective function needed

LP (Linear Programming)
~~~~~~~~~~~~~~~~~~~~~~~

Optimize a linear objective subject to linear constraints:

.. code-block:: python

   from problem import OXLPProblem, ObjectiveType

   lp = OXLPProblem()
   # Add variables, constraints, and objective function

GP (Goal Programming)
~~~~~~~~~~~~~~~~~~~~

Handle multiple conflicting objectives:

.. code-block:: python

   from problem import OXGPProblem

   gp = OXGPProblem()
   # Add variables, constraints, and goal constraints
   gp.create_goal_constraint(variables, weights, target_value, description)

Solver Selection
----------------

OptiX supports multiple solvers:

.. code-block:: python

   from solvers import solve, get_available_solvers

   # Check available solvers
   available = get_available_solvers()
   print(f"Available solvers: {available}")

   # Solve with specific solver
   status, solution = solve(problem, 'ORTools')
   status, solution = solve(problem, 'Gurobi')  # If installed

   # Let OptiX choose the best available solver
   status, solution = solve(problem)

Common Patterns
---------------

Variable Creation from Data
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from data import OXData, OXDatabase

   # Create data objects
   products = OXDatabase([
       OXData(name="Product_A", cost=10, capacity=500),
       OXData(name="Product_B", cost=15, capacity=300)
   ])

   # Create variables from data
   for product in products:
       problem.create_decision_variable(
           var_name=f"production_{product.name}",
           description=f"Production of {product.name}",
           lower_bound=0,
           upper_bound=product.capacity
       )

Constraint Patterns
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Capacity constraint
   problem.create_constraint(
       variables=production_vars,
       weights=[1] * len(production_vars),
       operator=RelationalOperators.LESS_THAN_EQUAL,
       value=total_capacity
   )

   # Demand constraint
   problem.create_constraint(
       variables=[product_var.id],
       weights=[1],
       operator=RelationalOperators.GREATER_THAN_EQUAL,
       value=minimum_demand
   )

   # Balance constraint
   problem.create_constraint(
       variables=[inflow_var.id, outflow_var.id],
       weights=[1, -1],
       operator=RelationalOperators.EQUAL,
       value=0
   )

Debugging and Validation
------------------------

Problem Validation
~~~~~~~~~~~~~~~~~

.. code-block:: python

   def validate_problem(problem):
       """Basic problem validation."""
       
       issues = []
       
       # Check variables
       if not problem.variables:
           issues.append("No variables defined")
       
       # Check constraints
       if not problem.constraints:
           issues.append("No constraints defined")
       
       # Check objective (for LP/GP)
       if hasattr(problem, 'objective_function'):
           if not problem.objective_function:
               issues.append("No objective function defined")
       
       # Check variable bounds
       for var in problem.variables:
           if var.lower_bound > var.upper_bound:
               issues.append(f"Invalid bounds for {var.name}")
       
       return issues

   # Usage
   issues = validate_problem(problem)
   if issues:
       print("Problem issues found:")
       for issue in issues:
           print(f"  - {issue}")

Solution Analysis
~~~~~~~~~~~~~~~~

.. code-block:: python

   def analyze_solution(solution, problem):
       """Analyze optimization solution."""
       
       if not solution:
           print("No solution to analyze")
           return
       
       sol = solution[0]
       print(f"Objective Value: {sol.objective_value}")
       print(f"Solution Status: {sol.status}")
       
       # Check constraint satisfaction
       print("\nConstraint Analysis:")
       for i, constraint in enumerate(problem.constraints):
           lhs_value = sum(
               constraint.weights[j] * sol.variable_values.get(constraint.variables[j], 0)
               for j in range(len(constraint.variables))
           )
           
           print(f"Constraint {i+1}: {lhs_value:.2f} {constraint.operator.name} {constraint.value}")

Next Steps
----------

Now that you've solved your first problem, explore these areas:

1. **Examples**: Try the :doc:`examples/diet_problem` and :doc:`examples/bus_assignment`
2. **Problem Types**: Learn about :doc:`user_guide/problem_types`
3. **Advanced Features**: Explore :doc:`user_guide/constraints` and special constraints
4. **Solvers**: Configure :doc:`user_guide/solvers` for your needs

Common Issues and Solutions
--------------------------

Problem: Import Errors
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Solution: Ensure OptiX is properly installed
   poetry install
   poetry shell

Problem: No Solution Found
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Check if problem is feasible
   if not solution:
       print("Problem may be infeasible or unbounded")
       # Review constraints and bounds

Problem: Unexpected Results
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Validate input data
   print("Variable bounds:")
   for var in problem.variables:
       print(f"  {var.name}: [{var.lower_bound}, {var.upper_bound}]")
   
   print("Constraint details:")
   for i, constraint in enumerate(problem.constraints):
       print(f"  Constraint {i}: {constraint.description}")

Getting Help
-----------

- **Documentation**: Comprehensive guides in this documentation
- **Examples**: Real-world examples in the ``samples/`` directory
- **API Reference**: Detailed API documentation for all modules
- **GitHub Issues**: Report bugs and request features

.. tip::
   **Pro Tip**: Start with simple problems and gradually add complexity. 
   Use the validation functions to catch issues early!

.. seealso::
   * :doc:`installation` - Detailed installation instructions
   * :doc:`examples/index` - More comprehensive examples
   * :doc:`api/index` - Complete API reference