Problem Types
=============

OptiX supports three main types of optimization problems with increasing complexity:
Constraint Satisfaction Problems (CSP), Linear Programming (LP), and Goal Programming (GP).
This guide explains when and how to use each type.

.. raw:: html

   <div class="problem-type-section csp">

Constraint Satisfaction Problems (CSP)
--------------------------------------

CSPs focus on finding any solution that satisfies all constraints without optimizing
any particular objective. They are the foundation for more complex problem types.

When to Use CSP
~~~~~~~~~~~~~~~

* Finding feasible solutions to complex constraint systems
* Scheduling problems where any valid schedule is acceptable
* Configuration problems with multiple requirements
* Preprocessing to check problem feasibility

Key Characteristics
~~~~~~~~~~~~~~~~~~

* **Variables**: Decision variables with bounds and types
* **Constraints**: Linear and special constraints that must be satisfied
* **No Objective**: Focus on feasibility, not optimality
* **Solution**: Any point that satisfies all constraints

.. code-block:: python

   from problem import OXCSPProblem
   from constraints import RelationalOperators

   # Create CSP for employee scheduling
   csp = OXCSPProblem()

   # Variables: work assignments (binary)
   days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
   shifts = ['Morning', 'Evening']
   employees = ['Alice', 'Bob', 'Carol']

   for employee in employees:
       for day in days:
           for shift in shifts:
               csp.create_decision_variable(
                   var_name=f"{employee}_{day}_{shift}",
                   description=f"{employee} works {shift} on {day}",
                   lower_bound=0,
                   upper_bound=1,
                   variable_type="binary"
               )

   # Constraint: Each shift must be covered
   for day in days:
       for shift in shifts:
           shift_vars = [
               var.id for var in csp.variables 
               if f"{day}_{shift}" in var.name
           ]
           csp.create_constraint(
               variables=shift_vars,
               weights=[1] * len(shift_vars),
               operator=RelationalOperators.GREATER_THAN_EQUAL,
               value=1,
               description=f"Cover {shift} shift on {day}"
           )

   # Constraint: No employee works both shifts same day
   for employee in employees:
       for day in days:
           morning_var = next(v for v in csp.variables if f"{employee}_{day}_Morning" in v.name)
           evening_var = next(v for v in csp.variables if f"{employee}_{day}_Evening" in v.name)
           
           csp.create_constraint(
               variables=[morning_var.id, evening_var.id],
               weights=[1, 1],
               operator=RelationalOperators.LESS_THAN_EQUAL,
               value=1,
               description=f"{employee} works at most one shift on {day}"
           )

.. raw:: html

   </div>

.. raw:: html

   <div class="problem-type-section lp">

Linear Programming (LP)
-----------------------

Linear Programming extends CSP by adding an objective function to optimize.
LP problems seek to maximize or minimize a linear objective subject to linear constraints.

When to Use LP
~~~~~~~~~~~~~~

* Resource allocation with clear optimization goals
* Production planning to maximize profit or minimize cost
* Transportation problems minimizing shipping costs
* Portfolio optimization with linear objectives

Key Characteristics
~~~~~~~~~~~~~~~~~~

* **Variables**: Continuous, integer, or binary decision variables
* **Constraints**: Linear equality and inequality constraints
* **Objective**: Single linear objective function (minimize or maximize)
* **Solution**: Optimal point that maximizes/minimizes the objective

Mathematical Form
~~~~~~~~~~~~~~~~

.. math::

   \begin{align}
   \text{minimize/maximize} \quad & \sum_{i=1}^{n} c_i x_i \\
   \text{subject to} \quad & \sum_{i=1}^{n} a_{ji} x_i \leq b_j, \quad j = 1, \ldots, m \\
   & x_i \geq 0, \quad i = 1, \ldots, n
   \end{align}

Where:
- :math:`x_i` are decision variables
- :math:`c_i` are objective coefficients  
- :math:`a_{ji}` are constraint coefficients
- :math:`b_j` are constraint bounds

.. code-block:: python

   from problem import OXLPProblem, ObjectiveType
   from constraints import RelationalOperators

   # Create LP for production planning
   lp = OXLPProblem()

   # Products to manufacture
   products = [
       {'name': 'Product_A', 'profit': 50, 'labor': 2, 'material': 1},
       {'name': 'Product_B', 'profit': 40, 'labor': 3, 'material': 2},
       {'name': 'Product_C', 'profit': 60, 'labor': 1, 'material': 3}
   ]

   # Create production variables
   for product in products:
       lp.create_decision_variable(
           var_name=f"production_{product['name']}",
           description=f"Units of {product['name']} to produce",
           lower_bound=0,
           upper_bound=1000,
           variable_type="continuous"
       )

   # Resource constraints
   # Labor constraint: total labor <= 1000 hours
   labor_vars = [var.id for var in lp.variables]
   labor_weights = [product['labor'] for product in products]
   
   lp.create_constraint(
       variables=labor_vars,
       weights=labor_weights,
       operator=RelationalOperators.LESS_THAN_EQUAL,
       value=1000,
       description="Labor hours constraint"
   )

   # Material constraint: total material <= 800 units
   material_weights = [product['material'] for product in products]
   
   lp.create_constraint(
       variables=labor_vars,  # Same variables
       weights=material_weights,
       operator=RelationalOperators.LESS_THAN_EQUAL,
       value=800,
       description="Material constraint"
   )

   # Objective: maximize total profit
   profit_weights = [product['profit'] for product in products]
   
   lp.create_objective_function(
       variables=labor_vars,
       weights=profit_weights,
       objective_type=ObjectiveType.MAXIMIZE
   )

   # Solve the problem
   from solvers import solve
   status, solution = solve(lp, 'ORTools')

.. raw:: html

   </div>

.. raw:: html

   <div class="problem-type-section gp">

Goal Programming (GP)
---------------------

Goal Programming handles multiple, often conflicting objectives by formulating
them as goals with associated deviation variables and priorities.

When to Use GP
~~~~~~~~~~~~~~

* Multi-criteria decision making
* Problems with conflicting objectives
* Situations where trade-offs are necessary
* When exact goal achievement is less important than minimizing deviations

Key Characteristics
~~~~~~~~~~~~~~~~~

* **Variables**: Decision variables plus deviation variables
* **Constraints**: Regular constraints plus goal constraints
* **Objectives**: Multiple goals with priorities or weights
* **Solution**: Minimize weighted deviations from goals

Mathematical Form
~~~~~~~~~~~~~~~~

.. math::

   \begin{align}
   \text{minimize} \quad & \sum_{i=1}^{k} w_i^+ d_i^+ + w_i^- d_i^- \\
   \text{subject to} \quad & \sum_{j=1}^{n} a_{ij} x_j + d_i^- - d_i^+ = g_i, \quad i = 1, \ldots, k \\
   & \text{regular constraints} \\
   & x_j, d_i^+, d_i^- \geq 0
   \end{align}

Where:
- :math:`d_i^+, d_i^-` are positive and negative deviation variables
- :math:`w_i^+, w_i^-` are weights for deviations
- :math:`g_i` are goal targets

.. code-block:: python

   from problem import OXGPProblem
   from constraints import RelationalOperators

   # Create GP for workforce planning
   gp = OXGPProblem()

   # Decision variables: number of employees to hire
   departments = ['Engineering', 'Sales', 'Support']
   
   for dept in departments:
       gp.create_decision_variable(
           var_name=f"hire_{dept}",
           description=f"Employees to hire in {dept}",
           lower_bound=0,
           upper_bound=50,
           variable_type="integer"
       )

   # Goal constraints with priorities
   goals = [
       {
           'description': 'Total workforce target of 100 employees',
           'variables': [var.id for var in gp.variables],
           'weights': [1, 1, 1],
           'target': 100,
           'priority': 1
       },
       {
           'description': 'Engineering should be 40% of workforce',
           'variables': [gp.variables[0].id],  # Engineering
           'weights': [1],
           'target': 40,
           'priority': 2
       },
       {
           'description': 'Balance between Sales and Support',
           'variables': [gp.variables[1].id, gp.variables[2].id],  # Sales, Support
           'weights': [1, -1],
           'target': 0,  # Equal hiring
           'priority': 3
       }
   ]

   # Add goal constraints
   for goal in goals:
       gp.create_goal_constraint(
           variables=goal['variables'],
           weights=goal['weights'],
           target_value=goal['target'],
           description=goal['description']
       )

   # Additional regular constraints
   # Budget constraint: hiring costs <= $500,000
   hiring_costs = [80000, 60000, 50000]  # Cost per hire by department
   
   gp.create_constraint(
       variables=[var.id for var in gp.variables],
       weights=hiring_costs,
       operator=RelationalOperators.LESS_THAN_EQUAL,
       value=500000,
       description="Budget constraint"
   )

.. raw:: html

   </div>

Problem Type Comparison
----------------------

.. raw:: html

   <table class="performance-table">
     <thead>
       <tr>
         <th>Aspect</th>
         <th>CSP</th>
         <th>LP</th>
         <th>GP</th>
       </tr>
     </thead>
     <tbody>
       <tr>
         <td><strong>Primary Goal</strong></td>
         <td>Find feasible solution</td>
         <td>Optimize single objective</td>
         <td>Balance multiple objectives</td>
       </tr>
       <tr>
         <td><strong>Objective Function</strong></td>
         <td>None</td>
         <td>Single linear objective</td>
         <td>Multiple goals with priorities</td>
       </tr>
       <tr>
         <td><strong>Solution Type</strong></td>
         <td>Any feasible point</td>
         <td>Optimal point</td>
         <td>Best compromise point</td>
       </tr>
       <tr>
         <td><strong>Complexity</strong></td>
         <td>Low</td>
         <td>Medium</td>
         <td>High</td>
       </tr>
       <tr>
         <td><strong>Use Cases</strong></td>
         <td>Scheduling, Configuration</td>
         <td>Resource allocation, Planning</td>
         <td>Multi-criteria decisions</td>
       </tr>
     </tbody>
   </table>

Advanced Problem Features
------------------------

Special Constraints
~~~~~~~~~~~~~~~~~

All problem types support special constraints for non-linear operations:

.. code-block:: python

   from problem import SpecialConstraintType

   # Multiplication constraint: production * price = revenue
   problem.create_special_constraint(
       constraint_type=SpecialConstraintType.MULTIPLICATION,
       left_variable_id=production_var.id,
       right_variable_id=price_var.id,
       result_variable_id=revenue_var.id
   )

   # Conditional constraint: if condition then action
   problem.create_special_constraint(
       constraint_type=SpecialConstraintType.CONDITIONAL,
       left_variable_id=condition_var.id,
       right_variable_id=action_var.id,
       result_variable_id=result_var.id
   )

Database Integration
~~~~~~~~~~~~~~~~~~

Create variables and constraints from data objects:

.. code-block:: python

   from data import OXData, OXDatabase

   # Create data structure
   facilities = OXDatabase([
       OXData(name="Plant_A", capacity=500, cost=1000),
       OXData(name="Plant_B", capacity=300, cost=800)
   ])

   customers = OXDatabase([
       OXData(name="Customer_1", demand=200, location="NY"),
       OXData(name="Customer_2", demand=150, location="CA")
   ])

   # Create variables from Cartesian product
   problem.create_variables_from_database_objects(
       database_objects=[facilities, customers],
       variable_name_template="ship_{0}_{1}",
       variable_description_template="Shipment from {0} to {1}",
       lower_bound=0,
       upper_bound=1000
   )

Problem Selection Guide
----------------------

Choosing the Right Problem Type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. raw:: html

   <div class="feature-grid">
     <div class="feature-card">
       <h3>Choose CSP When:</h3>
       <ul>
         <li>Any feasible solution is acceptable</li>
         <li>Checking if constraints can be satisfied</li>
         <li>Constraint complexity is the main challenge</li>
         <li>No clear optimization criterion exists</li>
       </ul>
     </div>
     <div class="feature-card">
       <h3>Choose LP When:</h3>
       <ul>
         <li>Clear single objective exists</li>
         <li>Linear relationships dominate</li>
         <li>Optimal solution is required</li>
         <li>Resource allocation is the focus</li>
       </ul>
     </div>
     <div class="feature-card">
       <h3>Choose GP When:</h3>
       <ul>
         <li>Multiple conflicting objectives</li>
         <li>Trade-offs are necessary</li>
         <li>Stakeholder preferences vary</li>
         <li>Compromise solutions are acceptable</li>
       </ul>
     </div>
   </div>

Migration Between Problem Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can easily migrate between problem types as requirements evolve:

.. code-block:: python

   # Start with CSP to check feasibility
   csp = OXCSPProblem()
   # ... add variables and constraints

   # Convert to LP when objective becomes clear
   lp = OXLPProblem()
   # Copy variables and constraints from CSP
   for variable in csp.variables:
       lp.add_variable(variable)
   for constraint in csp.constraints:
       lp.add_constraint(constraint)
   
   # Add objective function
   lp.create_objective_function(variables, weights, ObjectiveType.MAXIMIZE)

   # Evolve to GP when multiple objectives emerge
   gp = OXGPProblem()
   # Copy from LP and add goal constraints

Best Practices
--------------

Problem Modeling
~~~~~~~~~~~~~~~

1. **Start Simple**: Begin with CSP to ensure feasibility
2. **Add Gradually**: Introduce objectives and goals incrementally
3. **Validate Early**: Check constraints before adding complexity
4. **Use Data**: Leverage database integration for complex scenarios

Performance Tips
~~~~~~~~~~~~~~~

1. **Variable Bounds**: Tighten bounds to reduce search space
2. **Constraint Order**: Place restrictive constraints first
3. **Problem Size**: Monitor variable and constraint counts
4. **Solver Selection**: Choose appropriate solver for problem type

Common Pitfalls
~~~~~~~~~~~~~~

1. **Infeasible Problems**: Over-constraining the solution space
2. **Unbounded Objectives**: Missing constraints on decision variables
3. **Numerical Issues**: Very large or very small coefficients
4. **Goal Conflicts**: Incompatible goals in GP problems

.. tip::
   **Development Workflow**: Start with CSP to validate your constraint model,
   then add objectives to create LP, and finally introduce multiple goals for GP.

See Also
--------

* :doc:`../quickstart` - Get started with your first problem
* :doc:`constraints` - Advanced constraint modeling
* :doc:`../examples/index` - Real-world problem examples
* :doc:`../api/problem` - Complete API reference