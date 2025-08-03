Solvers Module
==============

The solvers module provides solver interfaces and implementations for solving optimization problems.
OptiX supports multiple solvers through a unified interface, allowing easy switching between different
optimization engines.

.. currentmodule:: solvers

Solver Factory
--------------

.. autofunction:: solve

.. autofunction:: solve_all_scenarios

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

Multi-Scenario Solving
~~~~~~~~~~~~~~~~~~~~~~~

The ``solve_all_scenarios`` function enables comprehensive scenario-based optimization analysis:

.. code-block:: python

   from problem import OXLPProblem, ObjectiveType
   from constraints import RelationalOperators
   from data import OXData
   from solvers import solve_all_scenarios

   # Create problem with scenario-based data
   problem = OXLPProblem()
   
   # Create decision variables
   x = problem.create_decision_variable("production_x", "Production of X", 0, 100)
   y = problem.create_decision_variable("production_y", "Production of Y", 0, 100)
   
   # Create data object with scenarios
   demand_data = OXData()
   demand_data.demand = 100        # Default scenario
   demand_data.price = 5.0
   
   # Create scenarios for different market conditions
   demand_data.create_scenario("High_Demand", demand=150, price=6.0)
   demand_data.create_scenario("Low_Demand", demand=75, price=4.5)
   demand_data.create_scenario("Peak_Season", demand=200, price=7.0)
   
   # Add data to problem database
   problem.db.add_object(demand_data)
   
   # Create constraints using scenario data
   problem.create_constraint(
       variables=[x.id, y.id],
       weights=[1, 1], 
       operator=RelationalOperators.LESS_THAN_EQUAL,
       value=demand_data.demand,
       description="Total production must not exceed demand"
   )
   
   # Create objective function using scenario data
   problem.create_objective_function(
       variables=[x.id, y.id],
       weights=[demand_data.price, 3.0],
       objective_type=ObjectiveType.MAXIMIZE,
       description="Maximize revenue"
   )
   
   # Solve across all scenarios
   scenario_results = solve_all_scenarios(problem, 'ORTools', maxTime=300)
   
   print(f"Solved {len(scenario_results)} scenarios")
   print(f"Scenarios: {list(scenario_results.keys())}")
   
   # Analyze results across scenarios
   best_scenario = None
   best_value = float('-inf')
   
   for scenario_name, result in scenario_results.items():
       print(f"\n=== Scenario: {scenario_name} ===")
       
       if result['status'] == OXSolutionStatus.OPTIMAL:
           solution = result['solution']
           print(f"Status: Optimal")
           print(f"Objective Value: {solution.objective_value:.2f}")
           print(f"Production X: {solution.variable_values[x.id]:.2f}")
           print(f"Production Y: {solution.variable_values[y.id]:.2f}")
           
           # Track best scenario
           if solution.objective_value > best_value:
               best_value = solution.objective_value
               best_scenario = scenario_name
       else:
           print(f"Status: {result['status']}")
   
   if best_scenario:
       print(f"\nBest performing scenario: {best_scenario} (${best_value:.2f})")

Advanced Multi-Scenario Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from problem import OXLPProblem
   from data import OXData  
   from solvers import solve_all_scenarios
   import statistics

   def comprehensive_scenario_analysis(problem, solver='ORTools'):
       """Perform comprehensive multi-scenario optimization analysis."""
       
       # Solve all scenarios
       results = solve_all_scenarios(problem, solver, maxTime=600)
       
       # Collect statistics
       optimal_scenarios = []
       objective_values = []
       
       for scenario_name, result in results.items():
           if result['status'] == OXSolutionStatus.OPTIMAL:
               optimal_scenarios.append(scenario_name)
               objective_values.append(result['solution'].objective_value)
       
       if not objective_values:
           print("No optimal solutions found across scenarios")
           return
       
       # Statistical analysis
       print("=== Multi-Scenario Analysis ===")
       print(f"Total scenarios: {len(results)}")
       print(f"Optimal scenarios: {len(optimal_scenarios)}")
       print(f"Success rate: {len(optimal_scenarios)/len(results)*100:.1f}%")
       print()
       
       print("=== Objective Value Statistics ===")
       print(f"Best value: {max(objective_values):.2f}")
       print(f"Worst value: {min(objective_values):.2f}")
       print(f"Average value: {statistics.mean(objective_values):.2f}")
       print(f"Median value: {statistics.median(objective_values):.2f}")
       print(f"Standard deviation: {statistics.stdev(objective_values):.2f}")
       print()
       
       # Scenario ranking
       scenario_ranking = []
       for scenario_name, result in results.items():
           if result['status'] == OXSolutionStatus.OPTIMAL:
               scenario_ranking.append((scenario_name, result['solution'].objective_value))
       
       scenario_ranking.sort(key=lambda x: x[1], reverse=True)
       
       print("=== Scenario Ranking ===")
       for i, (scenario, value) in enumerate(scenario_ranking, 1):
           print(f"{i:2d}. {scenario:<20}: ${value:8.2f}")
       
       # Sensitivity analysis
       if len(objective_values) > 1:
           value_range = max(objective_values) - min(objective_values)
           cv = statistics.stdev(objective_values) / statistics.mean(objective_values)
           
           print(f"\n=== Sensitivity Analysis ===")
           print(f"Value range: ${value_range:.2f}")
           print(f"Coefficient of variation: {cv:.3f}")
           
           if cv > 0.2:
               print("⚠️  High sensitivity to scenario parameters")
           elif cv > 0.1:
               print("⚡ Moderate sensitivity to scenario parameters")  
           else:
               print("✅ Low sensitivity to scenario parameters")
       
       return results
   
   # Usage with complex multi-object scenarios
   problem = OXLPProblem()
   
   # Create variables
   x = problem.create_decision_variable("x", "Variable X", 0, 50)
   y = problem.create_decision_variable("y", "Variable Y", 0, 50)
   
   # Create multiple data objects with coordinated scenarios
   capacity_data = OXData()
   capacity_data.max_capacity = 100
   capacity_data.create_scenario("Expansion", max_capacity=150)
   capacity_data.create_scenario("Recession", max_capacity=80)
   capacity_data.create_scenario("Growth", max_capacity=120)
   
   cost_data = OXData()
   cost_data.unit_cost = 2.0
   cost_data.create_scenario("Expansion", unit_cost=1.8)    # Lower costs during expansion
   cost_data.create_scenario("Recession", unit_cost=2.5)   # Higher costs during recession
   cost_data.create_scenario("Growth", unit_cost=2.2)      # Moderate cost increase
   
   # Add to database
   problem.db.add_object(capacity_data)
   problem.db.add_object(cost_data)
   
   # Create constraints and objectives using scenario data
   problem.create_constraint([x.id, y.id], [1, 1], "<=", capacity_data.max_capacity)
   problem.create_objective_function([x.id, y.id], [cost_data.unit_cost, 3.0], "maximize")
   
   # Perform comprehensive analysis
   analysis_results = comprehensive_scenario_analysis(problem, 'Gurobi')

Constraint-Based Scenarios
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from constraints import RelationalOperators
   from solvers import solve_all_scenarios

   # Create problem with constraint scenarios
   problem = OXLPProblem()
   
   x = problem.create_decision_variable("x", "Production X", 0, 100)
   y = problem.create_decision_variable("y", "Production Y", 0, 100)
   
   # Create base constraint
   resource_constraint = problem.create_constraint(
       variables=[x.id, y.id],
       weights=[2, 1],
       operator=RelationalOperators.LESS_THAN_EQUAL,
       value=200,
       description="Resource availability constraint"
   )
   
   # Add constraint scenarios for different resource conditions
   resource_constraint.create_scenario(
       "Limited_Resources", 
       rhs=150, 
       description="Resource shortage scenario"
   )
   
   resource_constraint.create_scenario(
       "Abundant_Resources", 
       rhs=300,
       description="Resource abundance scenario"
   )
   
   resource_constraint.create_scenario(
       "Emergency_Resources",
       rhs=100,
       description="Emergency resource rationing"
   )
   
   # Create objective
   problem.create_objective_function(
       variables=[x.id, y.id],
       weights=[5, 4],
       objective_type=ObjectiveType.MAXIMIZE
   )
   
   # Solve across constraint scenarios
   constraint_results = solve_all_scenarios(problem, 'ORTools')
   
   # Analyze impact of resource availability
   print("=== Resource Scenario Analysis ===")
   for scenario_name, result in constraint_results.items():
       if result['status'] == OXSolutionStatus.OPTIMAL:
           solution = result['solution']
           total_production = solution.variable_values[x.id] + solution.variable_values[y.id]
           
           print(f"{scenario_name}:")
           print(f"  Objective: ${solution.objective_value:.2f}")
           print(f"  Total Production: {total_production:.2f} units")
           print(f"  X Production: {solution.variable_values[x.id]:.2f}")
           print(f"  Y Production: {solution.variable_values[y.id]:.2f}")
           print()

Mixed Data and Constraint Scenarios
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from data import OXData
   from solvers import solve_all_scenarios

   # Complex scenario setup with both data and constraint scenarios
   problem = OXLPProblem()
   
   # Variables
   x = problem.create_decision_variable("x", "Product X", 0, 100)
   y = problem.create_decision_variable("y", "Product Y", 0, 100)
   
   # Data object scenarios for market conditions
   market_data = OXData()
   market_data.price_x = 10.0
   market_data.price_y = 8.0
   market_data.create_scenario("Bull_Market", price_x=12.0, price_y=10.0)
   market_data.create_scenario("Bear_Market", price_x=8.0, price_y=6.0)
   
   problem.db.add_object(market_data)
   
   # Constraint scenarios for operational conditions
   capacity_constraint = problem.create_constraint(
       variables=[x.id, y.id],
       weights=[1, 1],
       operator=RelationalOperators.LESS_THAN_EQUAL,
       value=150,
       description="Production capacity"
   )
   capacity_constraint.create_scenario("Maintenance", rhs=100)
   capacity_constraint.create_scenario("Overtime", rhs=200)
   
   # Objective using data scenarios
   problem.create_objective_function(
       variables=[x.id, y.id],
       weights=[market_data.price_x, market_data.price_y],
       objective_type=ObjectiveType.MAXIMIZE
   )
   
   # This will solve all combinations:
   # - Default + Default, Bull_Market + Default, Bear_Market + Default
   # - Default + Maintenance, Bull_Market + Maintenance, Bear_Market + Maintenance  
   # - Default + Overtime, Bull_Market + Overtime, Bear_Market + Overtime
   mixed_results = solve_all_scenarios(problem, 'Gurobi', use_continuous=True)
   
   print(f"Total scenario combinations solved: {len(mixed_results)}")
   
   # Group results by data vs constraint scenarios
   market_scenarios = {}
   capacity_scenarios = {}
   
   for scenario_name, result in mixed_results.items():
       if result['status'] == OXSolutionStatus.OPTIMAL:
           solution = result['solution']
           
           # Categorize scenarios
           if 'Market' in scenario_name:
               market_scenarios[scenario_name] = solution.objective_value
           elif scenario_name in ['Maintenance', 'Overtime']:
               capacity_scenarios[scenario_name] = solution.objective_value
           else:
               print(f"Default scenario value: ${solution.objective_value:.2f}")
   
   print("\n=== Market Impact Analysis ===")
   for scenario, value in market_scenarios.items():
       print(f"{scenario}: ${value:.2f}")
   
   print("\n=== Capacity Impact Analysis ===")
   for scenario, value in capacity_scenarios.items():
       print(f"{scenario}: ${value:.2f}")

See Also
--------

* :doc:`problem` - Problem type definitions
* :doc:`../tutorials/custom_solvers` - Creating custom solver implementations
* :doc:`../user_guide/solvers` - Detailed solver configuration guide