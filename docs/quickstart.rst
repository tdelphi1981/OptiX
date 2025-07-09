Quick Start
===========

Installation
------------

OptiX can be installed using pip:

.. code-block:: bash

   pip install optix

Or if you're working with the source code:

.. code-block:: bash

   git clone <repository-url>
   cd OptiX
   pip install -e .

Basic Usage
-----------

Here's a simple example of how to use OptiX:

.. code-block:: python

   from optix.problem import OXProblem
   from optix.variables import OXVariable
   from optix.constraints import OXConstraint
   from optix.solvers import OXSolverFactory

   # Create a problem
   problem = OXProblem()

   # Define variables
   x = OXVariable("x", bounds=(0, 10))
   y = OXVariable("y", bounds=(0, 10))

   # Add variables to problem
   problem.add_variable(x)
   problem.add_variable(y)

   # Define constraints
   constraint = OXConstraint("x + y <= 5")
   problem.add_constraint(constraint)

   # Set objective
   problem.set_objective("maximize", "2*x + 3*y")

   # Create solver
   solver = OXSolverFactory.create_solver("ortools")

   # Solve the problem
   solution = solver.solve(problem)

   # Access results
   print(f"Solution: x = {solution.get_value('x')}, y = {solution.get_value('y')}")
   print(f"Objective value: {solution.objective_value}")

Next Steps
----------

* Read the :doc:`overview` to understand the framework architecture
* Explore the :doc:`api/index` for detailed API documentation
* Check out :doc:`examples` for more complex use cases