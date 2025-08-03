Solvers Module
==============

The solvers module provides solver interfaces and implementations for solving optimization problems.
OptiX supports multiple solvers through a unified interface, allowing easy switching between different
optimization engines.

.. currentmodule:: solvers

Solver Factory
--------------

.. autofunction:: solve

Solver Interfaces
-----------------

Base Interface
~~~~~~~~~~~~~~

.. autoclass:: OXSolverInterface
   :members:
   :undoc-members:
   :show-inheritance:

OR-Tools Solver
~~~~~~~~~~~~~~~

.. automodule:: solvers.ortools
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: solvers.ortools.OXORToolsSolverInterface
   :members:
   :undoc-members:
   :show-inheritance:

Gurobi Solver
~~~~~~~~~~~~~

.. automodule:: solvers.gurobi
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: solvers.gurobi.OXGurobiSolverInterface
   :members:
   :undoc-members:
   :show-inheritance:

Solution Management
-------------------

.. autoclass:: OXSolverSolution
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: OXSolutionStatus
   :members:
   :undoc-members:

Examples
--------

Basic Solving
~~~~~~~~~~~~~

.. code-block:: python

   from problem import OXLPProblem, ObjectiveType
   from constraints import RelationalOperators
   from solvers import solve

   # Create problem
   problem = OXLPProblem()
   problem.create_decision_variable("x", "Variable X", 0, 10)
   problem.create_decision_variable("y", "Variable Y", 0, 10)

   # Add constraint
   problem.create_constraint(
       variables=[var.id for var in problem.variables],
       weights=[1, 1],
       operator=RelationalOperators.LESS_THAN_EQUAL,
       value=15
   )

   # Set objective
   problem.create_objective_function(
       variables=[var.id for var in problem.variables],
       weights=[3, 2],
       objective_type=ObjectiveType.MAXIMIZE
   )

   # Solve with OR-Tools
   status, solution = solve(problem, 'ORTools')
   print(f"Status: {status}")
   
   if solution:
       for sol in solution:
           print(f"Objective value: {sol.objective_value}")
           sol.print_solution_for(problem)

   # Solve with Gurobi
   try:
       status, solution = solve(problem, 'Gurobi')
       print(f"Gurobi Status: {status}")
   except Exception as e:
       print(f"Gurobi not available: {e}")

Solver Comparison
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import time
   from solvers import solve

   def compare_solvers(problem, solvers=['ORTools', 'Gurobi']):
       """Compare performance of different solvers on the same problem."""
       results = {}
       
       for solver_name in solvers:
           try:
               start_time = time.time()
               status, solution = solve(problem, solver_name)
               solve_time = time.time() - start_time
               
               results[solver_name] = {
                   'status': status,
                   'solve_time': solve_time,
                   'objective_value': solution[0].objective_value if solution else None
               }
               
               print(f"{solver_name}:")
               print(f"  Status: {status}")
               print(f"  Time: {solve_time:.4f} seconds")
               if solution:
                   print(f"  Objective: {solution[0].objective_value}")
               print()
               
           except Exception as e:
               print(f"{solver_name} failed: {e}")
               results[solver_name] = {'error': str(e)}
       
       return results

   # Usage
   results = compare_solvers(problem)

Custom Solver Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from solvers import OXSolverInterface, OXSolverSolution, OXSolutionStatus
   import random

   class RandomSolverInterface(OXSolverInterface):
       """A simple random solver for demonstration purposes."""
       
       def __init__(self):
           super().__init__()
           self.solutions = []
       
       def solve(self, problem):
           """Solve the problem using random sampling."""
           self.solutions = []
           
           # Simple random search (not optimal, just for demo)
           best_objective = float('-inf') if problem.objective_function.objective_type == ObjectiveType.MAXIMIZE else float('inf')
           best_values = {}
           
           for _ in range(1000):  # 1000 random samples
               values = {}
               objective_value = 0
               
               # Generate random values for each variable
               for variable in problem.variables:
                   random_value = random.uniform(variable.lower_bound, variable.upper_bound)
                   values[variable.id] = random_value
               
               # Check constraints (simplified)
               feasible = True
               for constraint in problem.constraints:
                   constraint_value = sum(
                       constraint.weights[i] * values[constraint.variables[i]]
                       for i in range(len(constraint.variables))
                   )
                   
                   if constraint.operator == RelationalOperators.LESS_THAN_EQUAL:
                       if constraint_value > constraint.value:
                           feasible = False
                           break
                   elif constraint.operator == RelationalOperators.GREATER_THAN_EQUAL:
                       if constraint_value < constraint.value:
                           feasible = False
                           break
                   elif constraint.operator == RelationalOperators.EQUAL:
                       if abs(constraint_value - constraint.value) > 1e-6:
                           feasible = False
                           break
               
               if feasible:
                   # Calculate objective value
                   objective_value = sum(
                       problem.objective_function.weights[i] * values[problem.objective_function.variables[i]]
                       for i in range(len(problem.objective_function.variables))
                   )
                   
                   # Check if this is the best solution so far
                   is_better = False
                   if problem.objective_function.objective_type == ObjectiveType.MAXIMIZE:
                       is_better = objective_value > best_objective
                   else:
                       is_better = objective_value < best_objective
                   
                   if is_better:
                       best_objective = objective_value
                       best_values = values.copy()
           
           # Create solution
           if best_values:
               solution = OXSolverSolution(
                   objective_value=best_objective,
                   variable_values=best_values,
                   status=OXSolutionStatus.OPTIMAL
               )
               self.solutions = [solution]
               return OXSolutionStatus.OPTIMAL
           else:
               return OXSolutionStatus.INFEASIBLE
       
       def get_solution(self):
           """Return the best solution found."""
           return self.solutions

   # Custom solvers would need to be registered through the solver factory
   # This is an example of implementing a custom solver interface

Advanced Solver Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from solvers.ortools import OXORToolsSolverInterface
   from solvers.gurobi import OXGurobiSolverInterface

   # Configure OR-Tools solver
   ortools_solver = OXORToolsSolverInterface()
   ortools_solver.set_time_limit(300)  # 5 minutes
   ortools_solver.set_num_threads(4)
   
   # Configure Gurobi solver (if available)
   try:
       gurobi_solver = OXGurobiSolverInterface()
       gurobi_solver.set_parameter('TimeLimit', 300)
       gurobi_solver.set_parameter('Threads', 4)
       gurobi_solver.set_parameter('MIPGap', 0.01)  # 1% optimality gap
   except ImportError:
       print("Gurobi not available")

   # Solve with configured solvers
   status = ortools_solver.solve(problem)
   ortools_solutions = ortools_solver.get_solution()

Parallel Solving
~~~~~~~~~~~~~~~~

.. code-block:: python

   import concurrent.futures
   import time

   def solve_parallel(problem, solvers=['ORTools', 'Gurobi'], timeout=300):
       """Solve the same problem with multiple solvers in parallel."""
       
       def solve_with_solver(solver_name):
           try:
               start_time = time.time()
               status, solution = solve(problem, solver_name)
               solve_time = time.time() - start_time
               
               return {
                   'solver': solver_name,
                   'status': status,
                   'solution': solution,
                   'time': solve_time
               }
           except Exception as e:
               return {
                   'solver': solver_name,
                   'error': str(e),
                   'time': None
               }
       
       # Use ThreadPoolExecutor for parallel execution
       with concurrent.futures.ThreadPoolExecutor(max_workers=len(solvers)) as executor:
           # Submit all solver tasks
           future_to_solver = {
               executor.submit(solve_with_solver, solver): solver 
               for solver in solvers
           }
           
           results = []
           
           # Collect results as they complete
           for future in concurrent.futures.as_completed(future_to_solver, timeout=timeout):
               try:
                   result = future.result()
                   results.append(result)
                   print(f"Completed: {result['solver']} in {result.get('time', 'N/A')} seconds")
               except Exception as e:
                   solver = future_to_solver[future]
                   results.append({
                       'solver': solver,
                       'error': str(e),
                       'time': None
                   })
       
       return results

   # Usage
   parallel_results = solve_parallel(problem)
   
   # Find the best result
   best_result = None
   for result in parallel_results:
       if 'error' not in result and result['solution']:
           if best_result is None or result['time'] < best_result['time']:
               best_result = result
   
   if best_result:
       print(f"Best solver: {best_result['solver']} ({best_result['time']:.4f}s)")

Solution Analysis
~~~~~~~~~~~~~~~~~

.. code-block:: python

   def analyze_solution(solution, problem):
       """Analyze and validate a solution."""
       
       if not solution:
           print("No solution available")
           return
       
       sol = solution[0]  # Get first solution
       
       print("=== Solution Analysis ===")
       print(f"Objective Value: {sol.objective_value}")
       print(f"Status: {sol.status}")
       print()
       
       print("Variable Values:")
       for var_id, value in sol.variable_values.items():
           variable = next((v for v in problem.variables if v.id == var_id), None)
           if variable:
               print(f"  {variable.name}: {value:.6f}")
       print()
       
       # Validate constraints
       print("Constraint Validation:")
       all_satisfied = True
       
       for i, constraint in enumerate(problem.constraints):
           constraint_value = sum(
               constraint.weights[j] * sol.variable_values[constraint.variables[j]]
               for j in range(len(constraint.variables))
           )
           
           satisfied = False
           if constraint.operator == RelationalOperators.LESS_THAN_EQUAL:
               satisfied = constraint_value <= constraint.value + 1e-6
               op_str = "<="
           elif constraint.operator == RelationalOperators.GREATER_THAN_EQUAL:
               satisfied = constraint_value >= constraint.value - 1e-6
               op_str = ">="
           elif constraint.operator == RelationalOperators.EQUAL:
               satisfied = abs(constraint_value - constraint.value) <= 1e-6
               op_str = "=="
           
           status_icon = "✅" if satisfied else "❌"
           print(f"  Constraint {i+1}: {constraint_value:.6f} {op_str} {constraint.value} {status_icon}")
           
           if not satisfied:
               all_satisfied = False
       
       print(f"\nAll constraints satisfied: {'✅' if all_satisfied else '❌'}")
       
       # Calculate objective value manually to verify
       if hasattr(problem, 'objective_function') and problem.objective_function:
           manual_objective = sum(
               problem.objective_function.weights[i] * sol.variable_values[problem.objective_function.variables[i]]
               for i in range(len(problem.objective_function.variables))
           )
           print(f"Manual objective calculation: {manual_objective:.6f}")
           print(f"Solver objective value: {sol.objective_value:.6f}")
           print(f"Difference: {abs(manual_objective - sol.objective_value):.8f}")

   # Usage
   status, solution = solve(problem, 'ORTools')
   analyze_solution(solution, problem)

See Also
--------

* :doc:`problem` - Problem type definitions
* :doc:`../tutorials/custom_solvers` - Creating custom solver implementations
* :doc:`../user_guide/solvers` - Detailed solver configuration guide