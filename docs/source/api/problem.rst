Problem Module
==============

The problem module provides the core problem type classes for representing different types of 
optimization problems in the OptiX framework. It implements a hierarchical structure supporting 
Constraint Satisfaction Problems (CSP), Linear Programming (LP), and Goal Programming (GP).

.. currentmodule:: problem

Problem Types
-------------

.. autoclass:: OXCSPProblem
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: OXLPProblem
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: OXGPProblem
   :members:
   :undoc-members:
   :show-inheritance:

Enumerations
------------

.. autoclass:: ObjectiveType
   :members:
   :undoc-members:

   Available objective types:

   * ``MINIMIZE`` - Minimize the objective function
   * ``MAXIMIZE`` - Maximize the objective function

.. autoclass:: SpecialConstraintType
   :members:
   :undoc-members:

   Available special constraint types:

   * ``MultiplicativeEquality`` - Multiplication: result = var1 * var2 * ... * varN
   * ``DivisionEquality`` - Integer division: result = var // divisor
   * ``ModulusEquality`` - Modulo operation: result = var % divisor
   * ``SummationEquality`` - Summation: result = var1 + var2 + ... + varN
   * ``ConditionalConstraint`` - Conditional logic: if condition then constraint1 else constraint2

Examples
--------

Creating a Constraint Satisfaction Problem
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from problem import OXCSPProblem
   from constraints import RelationalOperators

   # Create CSP
   csp = OXCSPProblem()

   # Add variables
   csp.create_decision_variable("x1", lower_bound=0, upper_bound=10)
   csp.create_decision_variable("x2", lower_bound=0, upper_bound=10)

   # Add constraint: x1 + x2 <= 15
   csp.create_constraint(
       variables=[csp.variables[0].id, csp.variables[1].id],
       weights=[1, 1],
       operator=RelationalOperators.LESS_THAN_EQUAL,
       value=15
   )

Creating a Linear Programming Problem
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from problem import OXLPProblem, ObjectiveType
   from constraints import RelationalOperators

   # Create LP problem
   lp = OXLPProblem()

   # Add variables
   lp.create_decision_variable("production_a", lower_bound=0, upper_bound=1000)
   lp.create_decision_variable("production_b", lower_bound=0, upper_bound=1000)

   # Add resource constraint
   lp.create_constraint(
       variables=[lp.variables[0].id, lp.variables[1].id],
       weights=[2, 3],  # Resource consumption per unit
       operator=RelationalOperators.LESS_THAN_EQUAL,
       value=500,  # Available resources
       name="Resource limitation"
   )

   # Set objective: maximize profit
   lp.create_objective_function(
       variables=[lp.variables[0].id, lp.variables[1].id],
       weights=[10, 15],  # Profit per unit
       objective_type=ObjectiveType.MAXIMIZE
   )

Creating a Goal Programming Problem
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from problem import OXGPProblem
   from constraints import RelationalOperators

   # Create GP problem
   gp = OXGPProblem()

   # Add variables
   gp.create_decision_variable("workers_day", lower_bound=0, upper_bound=100)
   gp.create_decision_variable("workers_night", lower_bound=0, upper_bound=100)

   # Add goal constraint: target 80 total workers
   gp.create_goal_constraint(
       variables=[gp.variables[0].id, gp.variables[1].id],
       weights=[1, 1],
       operator=RelationalOperators.EQUAL,
       value=80,
       name="Target workforce size"
   )

   # Add goal constraint: prefer balanced shifts
   gp.create_goal_constraint(
       variables=[gp.variables[0].id, gp.variables[1].id],
       weights=[1, -1],  # Difference between shifts
       operator=RelationalOperators.EQUAL,
       value=0,   # Equal shifts
       name="Balanced shift allocation"
   )

   # Create objective function to minimize deviations
   gp.create_objective_function()

Working with Database Objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from problem import OXLPProblem
   from data import OXData, OXDatabase

   # Create data objects
   bus1 = OXData()
   bus1.capacity = 50
   bus1.cost_per_km = 2.5

   bus2 = OXData()
   bus2.capacity = 40
   bus2.cost_per_km = 2.0

   route1 = OXData()
   route1.distance = 25
   route1.demand = 35

   route2 = OXData()
   route2.distance = 30
   route2.demand = 45

   # Create problem
   problem = OXLPProblem()
   
   # Add data to database
   problem.db.add_object(bus1)
   problem.db.add_object(bus2)
   problem.db.add_object(route1)
   problem.db.add_object(route2)

   # Create variables from database objects using custom types
   class Bus:
       pass
   
   class Route:
       pass

   # Create variables for all bus-route combinations
   problem.create_variables_from_db(
       Bus, Route,
       var_name_template="assign_{bus_id}_{route_id}",
       var_description_template="Assign bus {bus_id} to route {route_id}",
       upper_bound=1,
       lower_bound=0
   )

Special Constraints
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from problem import OXLPProblem, SpecialConstraintType

   problem = OXLPProblem()

   # Create variables
   problem.create_decision_variable("x", lower_bound=0, upper_bound=100)
   problem.create_decision_variable("y", lower_bound=0, upper_bound=100)

   # Create multiplication constraint: z = x * y
   mult_constraint = problem.create_special_constraint(
       constraint_type=SpecialConstraintType.MultiplicativeEquality,
       input_variables=[problem.variables[0], problem.variables[1]]
   )

   # Create division constraint: w = x // 5
   div_constraint = problem.create_special_constraint(
       constraint_type=SpecialConstraintType.DivisionEquality,
       input_variable=[problem.variables[0]],
       divisor=5
   )

   # Create modulo constraint: r = x % 7
   mod_constraint = problem.create_special_constraint(
       constraint_type=SpecialConstraintType.ModulusEquality,
       input_variable=[problem.variables[0]],
       divisor=7
   )

Functional Constraint Creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from problem import OXLPProblem
   from constraints import RelationalOperators

   problem = OXLPProblem()

   # Create variables with meaningful names
   for i in range(5):
       problem.create_decision_variable(
           f"production_{i}",
           lower_bound=0,
           upper_bound=100
       )

   # Create constraint using search function
   problem.create_constraint(
       variable_search_function=lambda v: v.name.startswith("production"),
       weight_calculation_function=lambda var_id, prob: 1.0,  # Equal weights
       operator=RelationalOperators.LESS_THAN_EQUAL,
       value=300,
       name="Total production capacity"
   )

   # Create objective using search function
   problem.create_objective_function(
       variable_search_function=lambda v: v.name.startswith("production"),
       weight_calculation_function=lambda var_id, prob: 10.0,  # Profit per unit
       objective_type=ObjectiveType.MAXIMIZE
   )

Advanced Goal Programming
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from problem import OXGPProblem
   from constraints import RelationalOperators

   # Multi-criteria optimization problem
   problem = OXGPProblem()

   # Create variables for different departments
   problem.create_decision_variable("dept_a_budget", lower_bound=0, upper_bound=1000000)
   problem.create_decision_variable("dept_b_budget", lower_bound=0, upper_bound=1000000)
   problem.create_decision_variable("dept_c_budget", lower_bound=0, upper_bound=1000000)

   # Goal 1: Total budget should be around $2M
   problem.create_goal_constraint(
       variables=[v.id for v in problem.variables],
       weights=[1, 1, 1],
       operator=RelationalOperators.EQUAL,
       value=2000000,
       name="Total budget target"
   )

   # Goal 2: Department A should get at least 40% of total budget
   problem.create_goal_constraint(
       variables=[v.id for v in problem.variables],
       weights=[1, -0.4, -0.4],  # dept_a - 0.4*(dept_b + dept_c)
       operator=RelationalOperators.GREATER_THAN_EQUAL,
       value=0,
       name="Department A minimum share"
   )

   # Goal 3: Departments B and C should have similar budgets
   problem.create_goal_constraint(
       variables=[problem.variables[1].id, problem.variables[2].id],
       weights=[1, -1],  # dept_b - dept_c
       operator=RelationalOperators.EQUAL,
       value=0,
       name="Balanced B and C budgets"
   )

   # Create objective to minimize undesired deviations
   problem.create_objective_function()

Complex Special Constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from problem import OXCSPProblem, SpecialConstraintType

   problem = OXCSPProblem()

   # Create variables for a scheduling problem
   problem.create_decision_variable("task_duration", lower_bound=1, upper_bound=10)
   problem.create_decision_variable("num_workers", lower_bound=1, upper_bound=5)
   problem.create_decision_variable("efficiency_factor", lower_bound=1, upper_bound=3)

   # Total work = duration * workers * efficiency
   work_constraint = problem.create_special_constraint(
       constraint_type=SpecialConstraintType.MultiplicativeEquality,
       input_variables=problem.variables.objects  # All variables
   )

   # Create summation constraint for resource allocation
   for i in range(3):
       problem.create_decision_variable(f"resource_{i}", lower_bound=0, upper_bound=100)

   # Total resources used
   resource_sum = problem.create_special_constraint(
       constraint_type=SpecialConstraintType.SummationEquality,
       input_variables=lambda v: v.name.startswith("resource")
   )

Working with Variable Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from problem import OXLPProblem
   from data import OXData, OXDatabase

   # Create a transportation problem
   problem = OXLPProblem()

   # Create supply and demand data
   supply_points = []
   for i in range(3):
       point = OXData()
       point.location = f"Factory_{i}"
       point.supply_capacity = (i + 1) * 100
       problem.db.add_object(point)
       supply_points.append(point)

   demand_points = []
   for i in range(4):
       point = OXData()
       point.location = f"Customer_{i}"
       point.demand = (i + 1) * 50
       problem.db.add_object(point)
       demand_points.append(point)

   # Create classes for database query
   class SupplyPoint:
       pass

   class DemandPoint:
       pass

   # Create transportation variables
   problem.create_variables_from_db(
       SupplyPoint, DemandPoint,
       var_name_template="ship_{supplypoint_location}_{demandpoint_location}",
       var_description_template="Shipment from {supplypoint_location} to {demandpoint_location}",
       upper_bound=1000,
       lower_bound=0
   )

   print(f"Created {len(problem.variables)} transportation variables")

See Also
--------

* :doc:`constraints` - Constraint definitions and operators
* :doc:`variables` - Variable management and types
* :doc:`data` - Database objects and scenario management
* :doc:`solvers` - Solver interfaces and implementations
* :doc:`../examples/index` - Complete example problems