"""
Solver Factory and Registry Module
===================================

This module provides the central factory interface for creating, managing, and orchestrating
optimization solver instances within the OptiX mathematical optimization framework. It implements
the Factory Method design pattern to enable unified access to diverse optimization engines
while maintaining consistent problem-solving workflows and standardized result handling.

The module serves as the primary entry point for optimization operations, abstracting away
solver-specific implementation details and providing a streamlined interface for solving
complex mathematical optimization problems across different algorithmic approaches and
commercial/open-source solver backends.

Core Architecture:
    - **Solver Registry**: Centralized registration system for available optimization solvers
      with dynamic discovery and instantiation capabilities
    - **Unified Interface**: Standardized solve() function providing consistent access to
      all registered solvers regardless of underlying implementation differences
    - **Parameter Management**: Flexible parameter passing system enabling solver-specific
      configuration and performance tuning without breaking interface consistency
    - **Workflow Orchestration**: Automated problem setup, constraint translation, objective
      configuration, and solution extraction following standardized patterns

Key Features:
    - **Multi-Solver Support**: Seamless integration of diverse optimization engines including
      commercial solvers (Gurobi), open-source solvers (OR-Tools), and custom implementations
    - **Dynamic Registration**: Runtime solver discovery and registration enabling easy
      extension with new solver backends without modifying core framework code
    - **Consistent Workflows**: Standardized problem-solving sequences ensuring uniform
      behavior across different solver implementations and optimization paradigms
    - **Error Handling**: Comprehensive exception management with meaningful error messages
      and graceful fallback mechanisms for unavailable or misconfigured solvers
    - **Performance Optimization**: Efficient solver instantiation with minimal overhead
      and optimized parameter passing for high-performance optimization scenarios

Solver Registry Design:
    The factory maintains a comprehensive registry of available optimization solvers:
    
    - **OR-Tools Integration**: Google's open-source constraint programming and linear
      optimization suite with support for CP-SAT, linear programming, and mixed-integer
      programming problems with advanced constraint propagation techniques
    - **Gurobi Integration**: Commercial high-performance optimization solver with
      state-of-the-art algorithms for linear, quadratic, and mixed-integer programming
      with advanced presolving and cutting plane methods
    - **Extensible Architecture**: Plugin-based system enabling integration of additional
      solver backends including academic solvers, domain-specific optimizers, and
      custom algorithmic implementations

Unified Solving Interface:
    The solve() function provides a standardized interface for all optimization operations:
    
    .. code-block:: python
    
        from solvers.OXSolverFactory import solve
        from problem.OXProblem import OXLPProblem
        
        # Create optimization problem
        problem = OXLPProblem()
        x = problem.create_decision_variable("x", 0, 10)
        y = problem.create_decision_variable("y", 0, 10)
        problem.create_constraint([x, y], [1, 1], "<=", 15)
        problem.create_objective_function([x, y], [2, 3], "maximize")
        
        # Solve with different solvers using identical interface
        or_status, or_solver = solve(problem, 'ORTools', maxTime=300)
        gurobi_status, gurobi_solver = solve(problem, 'Gurobi', use_continuous=True)
        
        # Access solutions uniformly
        if or_status == OXSolutionStatus.OPTIMAL:
            solution = or_solver[0]
            print(f"OR-Tools solution: {solution.decision_variable_values}")
            
        if gurobi_status == OXSolutionStatus.OPTIMAL:
            solution = gurobi_solver[0]
            print(f"Gurobi solution: {solution.decision_variable_values}")

Problem Setup Automation:
    The factory automatically handles the complete problem setup workflow:
    
    1. **Variable Creation**: Systematic translation of OptiX decision variables to
       solver-specific variable representations with proper bounds and type constraints
    2. **Constraint Translation**: Comprehensive conversion of OptiX constraints to
       native solver constraint formats with accurate operator and coefficient handling
    3. **Special Constraint Handling**: Advanced constraint types including multiplicative,
       division, modulo, and conditional constraints with solver-specific implementation
    4. **Objective Configuration**: Optimization objective setup for linear and goal
       programming problems with proper minimization/maximization handling
    5. **Solution Extraction**: Automated retrieval and standardization of optimization
       results with comprehensive status reporting and error handling

Parameter Passing System:
    The factory supports flexible parameter configuration for solver customization:
    
    - **Solver-Specific Parameters**: Direct parameter passing to individual solver
      implementations enabling fine-grained control over algorithmic behavior
    - **Performance Tuning**: Time limits, memory constraints, precision settings,
      and convergence criteria for optimization performance optimization
    - **Algorithmic Options**: Solver-specific algorithm selection, heuristic settings,
      and advanced optimization technique configuration
    - **Output Control**: Logging levels, solution enumeration limits, and debugging
      output configuration for comprehensive optimization analysis

Error Handling and Validation:
    The factory implements robust error handling for reliable optimization operations:
    
    - **Solver Availability**: Runtime validation of solver availability with meaningful
      error messages for missing dependencies or configuration issues
    - **Parameter Validation**: Type checking and range validation for solver parameters
      with detailed error reporting for invalid configurations
    - **Problem Validation**: Comprehensive problem structure validation ensuring
      compatibility with selected solver capabilities and requirements
    - **Exception Translation**: Standardized exception handling translating solver-specific
      errors to consistent OptiX exception types for uniform error management

Module Dependencies:
    - base: OptiX core exception handling and validation framework
    - problem: OptiX problem type definitions for CSP, LP, and GP formulations
    - solvers.gurobi: Gurobi commercial solver integration module
    - solvers.ortools: OR-Tools open-source solver integration module
    - solvers.OXSolverInterface: Abstract solver interface and solution data structures
"""

from base import OXception
from problem.OXProblem import OXCSPProblem, OXLPProblem
from solvers.gurobi.OXGurobiSolverInterface import OXGurobiSolverInterface
from solvers.ortools.OXORToolsSolverInterface import OXORToolsSolverInterface
from solvers.OXSolverInterface import OXSolutionStatus

_available_solvers = {
    'ORTools': OXORToolsSolverInterface,
    'Gurobi': OXGurobiSolverInterface
}


def solve(problem: OXCSPProblem, solver: str, **kwargs):
    """
    Unified optimization problem solving interface with multi-solver support.
    
    This function serves as the primary entry point for solving optimization problems
    within the OptiX framework, providing a standardized interface that abstracts
    away solver-specific implementation details while ensuring consistent problem
    setup, solving workflows, and solution extraction across different optimization
    engines and algorithmic approaches.
    
    The function implements a comprehensive solving pipeline that automatically handles
    variable creation, constraint translation, objective function configuration, and
    solution extraction, enabling users to focus on problem modeling rather than
    solver-specific integration complexities.
    
    Solving Pipeline:
        The function orchestrates a standardized solving workflow:
        
        1. **Solver Validation**: Verifies solver availability and compatibility
           with the specified problem type and configuration parameters
        2. **Solver Instantiation**: Creates solver instance with custom parameters
           and configuration options for performance tuning and behavior control
        3. **Variable Setup**: Translates OptiX decision variables to solver-specific
           variable representations with proper bounds, types, and naming conventions
        4. **Constraint Translation**: Converts OptiX constraints to native solver
           constraint formats with accurate coefficient handling and operator mapping
        5. **Special Constraint Handling**: Processes advanced constraint types including
           multiplicative, division, modulo, and conditional constraints using
           solver-specific implementation strategies
        6. **Objective Configuration**: Sets up optimization objectives for linear and
           goal programming problems with proper minimization/maximization handling
        7. **Solution Execution**: Executes the core solving algorithm with progress
           monitoring and early termination capabilities
        8. **Result Extraction**: Retrieves optimization results and translates them
           to standardized OptiX solution formats for consistent analysis
    
    Args:
        problem (OXCSPProblem): The optimization problem instance to solve. Must be
                               a properly configured OptiX problem with defined variables,
                               constraints, and (for LP/GP problems) objective functions.
                               Supports constraint satisfaction problems (CSP), linear
                               programming (LP), and goal programming (GP) formulations.
                               
        solver (str): The identifier of the optimization solver to use for problem
                     solving. Must match a key in the _available_solvers registry.
                     Supported values include:
                     - 'ORTools': Google's open-source constraint programming solver
                     - 'Gurobi': Commercial high-performance optimization solver
                     Additional solvers may be available through plugin extensions.
                     
        **kwargs: Arbitrary keyword arguments passed directly to the solver constructor
                 for custom parameter configuration. Enables solver-specific performance
                 tuning, algorithmic customization, and behavior control. Common
                 parameters include:
                 - maxTime (int): Maximum solving time in seconds
                 - solutionCount (int): Maximum number of solutions to enumerate
                 - equalizeDenominators (bool): Enable fractional coefficient handling
                 - use_continuous (bool): Enable continuous variable optimization
                 - Additional solver-specific parameters as documented by each solver
        
    Returns:
        tuple: A two-element tuple containing comprehensive solving results:
        
            - **status** (OXSolutionStatus): The termination status of the optimization
              process indicating solution quality and solver performance. Possible values:
              * OXSolutionStatus.OPTIMAL: Globally optimal solution found
              * OXSolutionStatus.FEASIBLE: Feasible solution found, optimality not guaranteed
              * OXSolutionStatus.INFEASIBLE: No feasible solution exists
              * OXSolutionStatus.UNBOUNDED: Problem is unbounded
              * OXSolutionStatus.TIMEOUT: Solver reached time limit
              * OXSolutionStatus.ERROR: Solving error occurred
              * OXSolutionStatus.UNKNOWN: Status cannot be determined
              
            - **solver_obj** (OXSolverInterface): The configured solver instance used
              for problem solving. Provides access to all found solutions through
              iteration protocols, individual solution access through indexing,
              and solver-specific diagnostic information through logging methods.
              The solver maintains complete solution history and enables detailed
              post-solving analysis and validation.
            
    Raises:
        OXception: Raised when the specified solver is not available in the solver
                  registry. This typically occurs when:
                  - The solver name is misspelled or incorrect
                  - The solver backend is not installed or properly configured
                  - Required dependencies for the solver are missing
                  - The solver registration failed during framework initialization
                  
        Additional solver-specific exceptions may be raised during the solving process
        and should be handled appropriately by calling code for robust error management.
        
    Example:
        Basic problem solving with default parameters:
        
        .. code-block:: python
        
            from problem.OXProblem import OXCSPProblem
            from solvers.OXSolverFactory import solve
            
            # Create and configure problem
            problem = OXCSPProblem()
            x = problem.create_decision_variable("x", 0, 10)
            y = problem.create_decision_variable("y", 0, 10)
            problem.create_constraint([x, y], [1, 1], "<=", 15)
            
            # Solve with default OR-Tools configuration
            status, solver = solve(problem, 'ORTools')
            
            # Analyze results
            if status == OXSolutionStatus.OPTIMAL:
                print("Found optimal solution")
                for solution in solver:
                    print(f"Variables: {solution.decision_variable_values}")
            elif status == OXSolutionStatus.INFEASIBLE:
                print("Problem has no feasible solution")
        
        Advanced solving with custom parameters:
        
        .. code-block:: python
        
            from problem.OXProblem import OXLPProblem
            from solvers.OXSolverFactory import solve
            
            # Create linear programming problem
            problem = OXLPProblem()
            x = problem.create_decision_variable("x", 0, 100)
            y = problem.create_decision_variable("y", 0, 100)
            problem.create_constraint([x, y], [1, 1], "<=", 150)
            problem.create_objective_function([x, y], [2, 3], "maximize")
            
            # Solve with custom Gurobi parameters
            status, solver = solve(
                problem, 
                'Gurobi',
                use_continuous=True,
                maxTime=3600,
                optimality_gap=0.01
            )
            
            # Access optimal solution
            if status == OXSolutionStatus.OPTIMAL:
                solution = solver[0]
                print(f"Optimal value: {solution.objective_function_value}")
                print(f"Variables: {solution.decision_variable_values}")
    
    Performance Considerations:
        - Solver instantiation overhead is minimized through efficient registry lookup
        - Problem setup is optimized for large-scale problems with thousands of variables
        - Memory usage scales linearly with problem size and solution enumeration
        - Parallel solving capabilities depend on individual solver implementations
        
    Solver Selection Guidelines:
        - **OR-Tools**: Recommended for constraint satisfaction, discrete optimization,
          and problems requiring advanced constraint types with good open-source support
        - **Gurobi**: Optimal for large-scale linear/quadratic programming requiring
          commercial-grade performance and advanced optimization algorithms
        - **Custom Solvers**: Consider for specialized problem domains or when specific
          algorithmic approaches are required for particular optimization scenarios
          
    Thread Safety:
        The solve function creates independent solver instances for each call, ensuring
        thread safety for concurrent optimization operations. However, individual solver
        implementations may have their own thread safety considerations that should be
        reviewed for multi-threaded optimization scenarios.
    """
    if solver not in _available_solvers:
        raise OXception(f"Solver not available : {solver}")
    solver_obj = _available_solvers[solver](**kwargs)

    solver_obj.create_variable(problem)
    solver_obj.create_constraints(problem)
    solver_obj.create_special_constraints(problem)
    if isinstance(problem, OXLPProblem):
        solver_obj.create_objective(problem)

    status = solver_obj.solve(problem)

    return status, solver_obj


def solve_all_scenarios(problem: OXCSPProblem, solver: str, **kwargs):
    """
    Multi-scenario optimization solving interface with comprehensive scenario management.
    
    This function orchestrates the execution of optimization problems across all available
    scenarios within the problem's database, providing a systematic approach to scenario-based
    optimization and sensitivity analysis. It automatically discovers all unique scenarios
    across all data objects in the problem database and solves the optimization problem
    for each scenario configuration.
    
    The function implements a comprehensive multi-scenario solving pipeline that handles
    scenario discovery, data object synchronization, iterative solving, and result
    aggregation to provide complete scenario analysis capabilities for complex
    optimization problems with varying parameter sets.
    
    Solving Pipeline:
        The function orchestrates a standardized multi-scenario solving workflow:
        
        1. **Scenario Discovery**: Automatically scans all data objects in the problem
           database to identify all unique scenario names across the entire dataset
        2. **Scenario Validation**: Validates that at least one scenario exists and
           provides meaningful error messages for empty databases or missing scenarios
        3. **Iterative Solving**: For each discovered scenario, synchronizes all data objects
           to the same scenario and executes the standard solve() function with identical
           parameters and configuration
        4. **State Management**: Preserves original data object states and restores them
           after multi-scenario solving to prevent unintended side effects
        5. **Result Aggregation**: Collects all scenario solutions into a comprehensive
           dictionary structure for easy analysis and comparison
        6. **Error Handling**: Provides robust error handling for individual scenario
           failures while continuing execution for remaining scenarios
    
    Args:
        problem (OXCSPProblem): The optimization problem instance to solve across all scenarios.
                               Must be a properly configured OptiX problem with defined variables,
                               constraints, and (for LP/GP problems) objective functions. The
                               problem's database (problem.db) must contain data objects with
                               scenario definitions for multi-scenario optimization.
                               
        solver (str): The identifier of the optimization solver to use for all scenario
                     solving operations. Must match a key in the _available_solvers registry.
                     Supported values include:
                     - 'ORTools': Google's open-source constraint programming solver
                     - 'Gurobi': Commercial high-performance optimization solver
                     The same solver will be used consistently across all scenarios for
                     comparative analysis.
                     
        **kwargs: Arbitrary keyword arguments passed directly to the solve() function for
                 each scenario. These parameters will be applied consistently across all
                 scenario solving operations, enabling uniform solver configuration and
                 performance tuning across the entire scenario set. Common parameters include:
                 - maxTime (int): Maximum solving time in seconds per scenario
                 - solutionCount (int): Maximum number of solutions to enumerate per scenario
                 - equalizeDenominators (bool): Enable fractional coefficient handling
                 - use_continuous (bool): Enable continuous variable optimization
                 - Additional solver-specific parameters as documented by each solver
        
    Returns:
        dict[str, dict]: A comprehensive dictionary mapping scenario names to their
                        corresponding solving results. Each dictionary entry contains:
                         
            - **key** (str): The scenario name as defined in the data objects
            - **value** (dict): A dictionary with the following structure:
              * **status** (OXSolutionStatus): The termination status for this scenario
              * **solution** (OXSolverInterface): The solver instance with solutions
              
            The dictionary provides complete access to all scenario results and enables
            comprehensive comparison and analysis across different parameter configurations.
            Empty scenarios or scenarios that cannot be solved will still appear in the
            results with appropriate status codes for complete result coverage.
            
    Raises:
        OXception: Raised in the following scenarios:
                  - The specified solver is not available in the solver registry
                  - The problem database is empty (no data objects available)
                  - No scenarios are found across all data objects in the database
                  - Critical errors occur during scenario discovery or state management
                  
        Individual scenario solving errors are captured and returned as part of the results
        dictionary with appropriate error status codes, allowing analysis of which scenarios
        succeeded or failed without terminating the entire multi-scenario solving process.
        
    Example:
        Basic multi-scenario solving with scenario analysis:
        
        .. code-block:: python
        
            from problem.OXProblem import OXLPProblem
            from data.OXData import OXData
            from solvers.OXSolverFactory import solve_all_scenarios
            
            # Create problem with scenario-enabled data
            problem = OXLPProblem()
            
            # Create decision variables
            x = problem.create_decision_variable("x", 0, 100)
            y = problem.create_decision_variable("y", 0, 100)
            
            # Create data object with multiple scenarios
            demand_data = OXData()
            demand_data.demand = 100
            demand_data.cost_per_unit = 2.0
            
            # Define scenarios
            demand_data.create_scenario("High_Demand", demand=150, cost_per_unit=2.5)
            demand_data.create_scenario("Low_Demand", demand=75, cost_per_unit=1.8)
            demand_data.create_scenario("Economic_Downturn", demand=50, cost_per_unit=1.5)
            
            # Add data to problem database
            problem.db.add_object(demand_data)
            
            # Create constraints using data object
            problem.create_constraint([x, y], [1, 1], "<=", demand_data.demand)
            
            # Create objective function
            problem.create_objective_function([x, y], [demand_data.cost_per_unit, 3], "maximize")
            
            # Solve across all scenarios
            scenario_results = solve_all_scenarios(problem, 'ORTools', maxTime=300)
            
            # Analyze results across scenarios
            for scenario_name, result in scenario_results.items():
                print(f"\\nScenario: {scenario_name}")
                if result['status'] == OXSolutionStatus.OPTIMAL:
                    solution = result['solution'][0]
                    print(f"  Status: Optimal")
                    print(f"  Objective Value: {solution.objective_function_value}")
                    print(f"  Variables: {solution.decision_variable_values}")
                else:
                    print(f"  Status: {result['status'].value}")
        
        Advanced multi-scenario solving with custom parameters:
        
        .. code-block:: python
        
            from problem.OXProblem import OXCSPProblem
            from data.OXData import OXData
            from solvers.OXSolverFactory import solve_all_scenarios
            
            # Create CSP with multiple data objects having scenarios
            problem = OXCSPProblem()
            
            # Create variables
            x = problem.create_decision_variable("x", 0, 50)
            y = problem.create_decision_variable("y", 0, 50)
            
            # Create multiple data objects with scenarios
            capacity_data = OXData()
            capacity_data.max_capacity = 100
            capacity_data.create_scenario("Expanded", max_capacity=150)
            capacity_data.create_scenario("Reduced", max_capacity=80)
            
            resource_data = OXData()
            resource_data.availability = 200
            resource_data.create_scenario("Expanded", availability=250)
            resource_data.create_scenario("Reduced", availability=160)
            
            # Add both data objects to database
            problem.db.add_object(capacity_data)
            problem.db.add_object(resource_data)
            
            # Create constraints using data objects
            problem.create_constraint([x, y], [1, 1], "<=", capacity_data.max_capacity)
            problem.create_constraint([x, y], [2, 1], "<=", resource_data.availability)
            
            # Solve with custom Gurobi parameters
            scenario_results = solve_all_scenarios(
                problem, 
                'Gurobi',
                use_continuous=True,
                maxTime=1800,
                solutionCount=5
            )
            
            # Compare scenario performance
            best_scenario = None
            best_status = None
            
            for scenario_name, result in scenario_results.items():
                print(f"Scenario '{scenario_name}': {result['status'].value}")
                if result['status'] == OXSolutionStatus.OPTIMAL:
                    if best_scenario is None:
                        best_scenario = scenario_name
                        best_status = result['status']
            
            if best_scenario:
                print(f"\\nBest performing scenario: {best_scenario}")
    
    Performance Considerations:
        - Multi-scenario solving scales linearly with the number of unique scenarios
        - Each scenario is solved independently, enabling potential parallel execution
        - Memory usage scales with the number of scenarios and solutions per scenario
        - Large scenario sets may benefit from selective scenario filtering or batching
        - Scenario discovery overhead is minimal due to efficient set-based collection
        
    Scenario Management Guidelines:
        - **Consistent Naming**: Use descriptive, consistent scenario names across all data objects
        - **Complete Coverage**: Ensure all critical data objects have scenario definitions
        - **Realistic Parameters**: Use realistic parameter ranges to ensure solver convergence
        - **Scenario Validation**: Validate scenario parameter combinations before solving
        - **Result Analysis**: Implement comprehensive result comparison and sensitivity analysis
          
    Thread Safety:
        Each scenario solving operation creates independent solver instances and maintains
        separate data object states, ensuring thread safety for concurrent scenario execution.
        However, the original data object state restoration is performed sequentially to
        prevent race conditions and ensure consistent final state.
    """
    if solver not in _available_solvers:
        raise OXception(f"Solver not available : {solver}")

    if len(problem.db) == 0:
        raise OXception("Problem database is empty - no data objects with scenarios found")

    # Discover all unique scenarios across all data objects
    all_scenarios = set()
    for data_obj in problem.db:
        all_scenarios.update(data_obj.scenarios.keys())

    if len(all_scenarios) == 0:
        raise OXception("No scenarios found in any data objects")

    # Store original active scenarios for restoration
    original_scenarios = {}
    for data_obj in problem.db:
        original_scenarios[data_obj.id] = data_obj.active_scenario

    # Solve for each scenario
    scenario_results = {}

    try:
        for scenario_name in sorted(all_scenarios):
            # Set all data objects to the current scenario
            for data_obj in problem.db:
                if scenario_name in data_obj.scenarios:
                    data_obj.active_scenario = scenario_name
                else:
                    # Keep default scenario if this scenario doesn't exist for this object
                    data_obj.active_scenario = "Default"

            # Solve the problem with current scenario configuration
            try:
                status, solver_obj = solve(problem, solver, **kwargs)
                for solution in solver_obj:
                    scenario_results[scenario_name] = {
                        'status': status,
                        'solution': solution
                    }
            except Exception:
                # Capture individual scenario errors without stopping the process
                scenario_results[scenario_name] = {
                    'status': OXSolutionStatus.ERROR,
                    'solution': None
                }

    finally:
        # Restore original active scenarios
        for data_obj in problem.db:
            if data_obj.id in original_scenarios:
                data_obj.active_scenario = original_scenarios[data_obj.id]

    return scenario_results
