Analysis Module
===============

The analysis module provides comprehensive analysis tools for OptiX optimization problems,
including sensitivity analysis, scenario comparison, and performance evaluation
capabilities that leverage the built-in scenario management system.

.. currentmodule:: analysis

Analysis Classes
----------------

Objective Function Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: OXObjectiveFunctionAnalysis
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: OXObjectiveFunctionAnalysisResult
   :members:
   :undoc-members:
   :show-inheritance:

Right-Hand Side Analysis
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: OXRightHandSideAnalysis
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: OXRightHandSideAnalysisResult
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: OXConstraintRHSAnalysis
   :members:
   :undoc-members:
   :show-inheritance:

Examples
--------

Basic Analysis Workflow
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from analysis import OXObjectiveFunctionAnalysis, OXRightHandSideAnalysis
   from problem import OXLPProblem
   
   # Create and configure your optimization problem
   problem = OXLPProblem(name="Production Planning")
   
   # Set up variables, constraints, objective function with scenario data
   # ... problem configuration code ...
   
   # Perform objective function analysis
   obj_analyzer = OXObjectiveFunctionAnalysis(problem, 'ORTools')
   obj_results = obj_analyzer.analyze()
   
   # Perform RHS constraint analysis
   rhs_analyzer = OXRightHandSideAnalysis(problem, 'ORTools')
   rhs_results = rhs_analyzer.analyze()
   
   # Access analysis results
   print(f"Best scenario: {obj_results.best_scenario}")
   print(f"Worst scenario: {obj_results.worst_scenario}")
   print(f"Success rate: {obj_results.success_rate:.1%}")
   print(f"Critical constraints: {len(rhs_results.critical_constraints)}")

Objective Function Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from analysis import OXObjectiveFunctionAnalysis
   from problem import OXLPProblem
   
   # Assume problem is already configured with multiple scenarios
   analyzer = OXObjectiveFunctionAnalysis(problem, solver_name='ORTools')
   
   # Run comprehensive analysis across all scenarios
   results = analyzer.analyze()
   
   # Access detailed results
   print(f"Total scenarios analyzed: {results.total_scenarios}")
   print(f"Successful solutions: {results.successful_scenarios}")
   print(f"Failed scenarios: {results.failed_scenarios}")
   
   # Best and worst case scenarios
   if results.best_scenario:
       print(f"Best objective value: {results.best_value}")
       print(f"Best scenario ID: {results.best_scenario}")
   
   if results.worst_scenario:
       print(f"Worst objective value: {results.worst_value}")
       print(f"Worst scenario ID: {results.worst_scenario}")
   
   # Statistical summary
   print(f"Average objective value: {results.average_value:.2f}")
   print(f"Standard deviation: {results.std_deviation:.2f}")
   print(f"Value range: [{results.min_value}, {results.max_value}]")

Right-Hand Side Analysis
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from analysis import OXRightHandSideAnalysis
   from problem import OXGPProblem
   
   # Create analyzer for goal programming problem
   analyzer = OXRightHandSideAnalysis(problem, solver_name='Gurobi')
   
   # Analyze constraint behavior across scenarios
   results = analyzer.analyze()
   
   # Check critical constraints
   for constraint_analysis in results.critical_constraints:
       constraint_id = constraint_analysis.constraint_id
       print(f"Critical constraint: {constraint_id}")
       print(f"  Binding frequency: {constraint_analysis.binding_frequency:.1%}")
       print(f"  Average slack: {constraint_analysis.average_slack:.2f}")
       print(f"  Never feasible in: {len(constraint_analysis.infeasible_scenarios)} scenarios")
   
   # Analyze specific constraint
   constraint_id = "resource_capacity_constraint_uuid"
   if constraint_id in results.constraint_analyses:
       analysis = results.constraint_analyses[constraint_id]
       print(f"Constraint {constraint_id} analysis:")
       print(f"  Min slack: {analysis.min_slack}")
       print(f"  Max slack: {analysis.max_slack}")
       print(f"  Binding scenarios: {analysis.binding_scenarios}")

Scenario Comparison
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from analysis import OXObjectiveFunctionAnalysis, OXRightHandSideAnalysis
   
   # Compare objective function performance
   obj_analyzer = OXObjectiveFunctionAnalysis(problem, 'ORTools')
   obj_results = obj_analyzer.analyze()
   
   # Identify performance outliers
   if obj_results.std_deviation > 0:
       z_scores = {}
       for scenario_id, value in obj_results.scenario_values.items():
           z_score = (value - obj_results.average_value) / obj_results.std_deviation
           if abs(z_score) > 2:  # Outlier threshold
               z_scores[scenario_id] = z_score
       
       print(f"Found {len(z_scores)} outlier scenarios")
       for scenario_id, z_score in sorted(z_scores.items(), key=lambda x: abs(x[1]), reverse=True):
           print(f"  Scenario {scenario_id}: Z-score = {z_score:.2f}")

Multi-Solver Analysis
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from analysis import OXObjectiveFunctionAnalysis
   
   # Compare solver performance
   solvers = ['ORTools', 'Gurobi']
   solver_results = {}
   
   for solver in solvers:
       try:
           analyzer = OXObjectiveFunctionAnalysis(problem, solver)
           results = analyzer.analyze()
           solver_results[solver] = results
           print(f"{solver}: Success rate = {results.success_rate:.1%}, "
                 f"Avg value = {results.average_value:.2f}")
       except Exception as e:
           print(f"{solver} failed: {e}")
   
   # Compare results
   if len(solver_results) > 1:
       values = [r.average_value for r in solver_results.values()]
       if max(values) - min(values) > 0.01:
           print("Warning: Significant difference in solver results detected")

Performance Analysis
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import time
   from analysis import OXObjectiveFunctionAnalysis, OXRightHandSideAnalysis
   
   # Time analysis operations
   start_time = time.time()
   
   # Run both analyses
   obj_analyzer = OXObjectiveFunctionAnalysis(problem, 'ORTools')
   obj_results = obj_analyzer.analyze()
   
   rhs_analyzer = OXRightHandSideAnalysis(problem, 'ORTools')
   rhs_results = rhs_analyzer.analyze()
   
   analysis_time = time.time() - start_time
   
   # Performance metrics
   scenarios_per_second = obj_results.total_scenarios / analysis_time
   print(f"Analysis completed in {analysis_time:.2f} seconds")
   print(f"Processing rate: {scenarios_per_second:.1f} scenarios/second")
   
   # Memory efficiency check
   total_constraints = len(problem.constraints)
   total_scenarios = obj_results.total_scenarios
   total_analyses = total_constraints * total_scenarios
   print(f"Analyzed {total_analyses:,} constraint-scenario combinations")

Integration with Problem Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from analysis import OXObjectiveFunctionAnalysis
   from problem import OXLPProblem, OXGPProblem, OXCSPProblem
   
   def analyze_problem(problem, solver='ORTools'):
       """Analyze any OptiX problem type."""
       
       # Objective function analysis (not applicable to CSP)
       if not isinstance(problem, OXCSPProblem):
           obj_analyzer = OXObjectiveFunctionAnalysis(problem, solver)
           obj_results = obj_analyzer.analyze()
           
           print(f"Problem: {problem.name}")
           print(f"Type: {type(problem).__name__}")
           print(f"Objective analysis:")
           print(f"  Success rate: {obj_results.success_rate:.1%}")
           print(f"  Value range: [{obj_results.min_value}, {obj_results.max_value}]")
           
           # Goal programming specific
           if isinstance(problem, OXGPProblem):
               print(f"  Note: Values represent weighted deviation sums")
       
       # RHS analysis (applicable to all problem types)
       rhs_analyzer = OXRightHandSideAnalysis(problem, solver)
       rhs_results = rhs_analyzer.analyze()
       
       print(f"Constraint analysis:")
       print(f"  Total constraints: {len(problem.constraints)}")
       print(f"  Critical constraints: {len(rhs_results.critical_constraints)}")
       print(f"  Always binding: {rhs_results.always_binding_count}")
       print(f"  Never binding: {rhs_results.never_binding_count}")
   
   # Usage with different problem types
   lp_problem = OXLPProblem(name="Linear Program")
   gp_problem = OXGPProblem(name="Goal Program")
   csp_problem = OXCSPProblem(name="Constraint Satisfaction")
   
   for problem in [lp_problem, gp_problem, csp_problem]:
       analyze_problem(problem)
       print("-" * 50)

See Also
--------

* :doc:`problem` - Problem classes that generate analysis data
* :doc:`constraints` - Constraint definitions analyzed by RHS analysis
* :doc:`solvers` - Solver implementations used in analysis
* :doc:`data` - Data management for scenario-based analysis
* :doc:`../user_guide/analysis` - Advanced analysis techniques guide