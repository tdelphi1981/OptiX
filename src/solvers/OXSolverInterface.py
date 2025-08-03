"""
Core Solver Interface Module
=============================

This module provides the fundamental architecture for solver integration within the OptiX
mathematical optimization framework. It defines abstract base classes, common data structures,
and standardized interfaces that all solver implementations must adhere to, ensuring
consistent behavior and interoperability across different optimization engines.

The module serves as the foundational layer for OptiX's multi-solver architecture, providing
a unified abstraction that enables seamless switching between different optimization solvers
while maintaining consistent problem formulation and solution handling patterns.

Key Components:
    - **OXSolverInterface**: Abstract base class defining the standard interface that all
      concrete solver implementations must implement, including variable creation, constraint
      handling, objective setup, and solution extraction capabilities
    - **OXSolverSolution**: Comprehensive data structure for representing optimization solutions
      with variable values, constraint evaluations, objective function values, and metadata
    - **OXSolutionStatus**: Enumeration defining standardized solution status codes across
      all solver implementations for consistent status reporting and error handling

Architecture Principles:
    - **Abstraction**: Clean separation between high-level problem modeling and low-level
      solver implementation details through well-defined interfaces
    - **Extensibility**: Modular design enabling easy addition of new solver backends
      without modifying existing code or breaking compatibility
    - **Consistency**: Standardized data structures and method signatures ensuring
      uniform behavior across different solver implementations
    - **Type Safety**: Comprehensive type annotations and generic programming patterns
      for compile-time error detection and improved code reliability

Solution Data Model:
    The module implements a comprehensive solution representation that captures:
    
    - **Variable Values**: Complete mapping of decision variable assignments with UUID-based
      identification for efficient lookup and cross-referencing
    - **Constraint Evaluations**: Detailed constraint satisfaction analysis including
      left-hand side values, operators, and right-hand side bounds
    - **Objective Function**: Optimization objective value for linear and goal programming
      problems with support for minimization and maximization scenarios
    - **Special Constraints**: Advanced constraint types including multiplicative, division,
      modulo, and conditional constraints with specialized value representations
    - **Solution Metadata**: Status information, solver statistics, and diagnostic data
      for comprehensive solution analysis and debugging

Interface Design Patterns:
    The solver interface follows established design patterns for optimization software:
    
    - **Factory Method**: Centralized solver instantiation through the solver factory
    - **Template Method**: Standardized solving workflow with customizable implementation
    - **Strategy Pattern**: Interchangeable solver algorithms with common interface
    - **Observer Pattern**: Solution callback mechanisms for multi-solution enumeration

Example:
    Basic usage pattern for implementing a new solver:

    .. code-block:: python

        from solvers.OXSolverInterface import OXSolverInterface, OXSolutionStatus
        
        class CustomSolverInterface(OXSolverInterface):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                # Initialize solver-specific components
                
            def _create_single_variable(self, var: OXVariable):
                # Implement variable creation in solver
                pass
                
            def _create_single_constraint(self, constraint: OXConstraint):
                # Implement constraint creation in solver  
                pass
                
            def create_special_constraints(self, prb: OXCSPProblem):
                # Handle special constraint types
                pass
                
            def solve(self, prb: OXCSPProblem) -> OXSolutionStatus:
                # Execute solving algorithm
                # Populate self._solutions with results
                return OXSolutionStatus.OPTIMAL

Type System Architecture:
    The module employs a sophisticated type system for mathematical optimization:
    
    - **Generic Types**: Flexible type variables for different numeric representations
    - **Union Types**: Support for multiple constraint and variable formats
    - **Mapping Types**: Efficient dictionary-based data structures for solution storage
    - **Optional Types**: Graceful handling of missing or undefined solution components

Performance Considerations:
    - Solution data structures use efficient dictionary implementations for O(1) lookup
    - Type annotations enable static analysis and runtime optimization
    - Iterator protocols provide memory-efficient solution enumeration
    - Default factory patterns minimize object creation overhead

Module Dependencies:
    - constraints: OptiX constraint definitions and relational operators
    - problem: OptiX problem type definitions for CSP, LP, and GP
    - variables: OptiX decision variable and variable set implementations
    - base: Core OptiX object model and exception handling framework
"""

import enum
from collections import defaultdict
from dataclasses import dataclass, field
from typing import TypeVar, Union, Optional, List, Dict, Tuple, Any, Iterator
from uuid import UUID

from constraints.OXConstraint import OXConstraint, RelationalOperators
from constraints.OXSpecialConstraints import OXSpecialConstraint
from problem import OXGPProblem
from problem.OXProblem import OXCSPProblem, OXLPProblem
from variables.OXVariable import OXVariable
from variables.OXVariableSet import OXVariableSet

# TypeVar definitions
T = TypeVar('T')
NumericType = Union[float, int]
VariableType = Union[OXVariable, OXVariableSet]
SingleOrList = Union[T, List[T]]
ConstraintType = SingleOrList[OXConstraint]
SpecialConstraintType = SingleOrList[OXSpecialConstraint]
VariableValueMapping = Dict[UUID, NumericType]
ConstraintValueType = Tuple[NumericType, RelationalOperators, NumericType]
ConstraintValueMapping = Dict[UUID, ConstraintValueType]

SpecialContraintEqualityValue = Tuple[NumericType, NumericType]
ConditionalContraintValue = Tuple[ConstraintValueType, NumericType, ConstraintValueType, ConstraintValueType]
SpecialConstraintValueType = Union[SpecialContraintEqualityValue, ConditionalContraintValue]

SpecialContraintValueMapping = Dict[UUID, SpecialConstraintValueType]

LogType = Union[str, List[str]]
LogsType = List[LogType]

Parameters = Dict[str, Any]


class OXSolutionStatus(enum.Enum):
    """
    Enumeration defining standardized solution status codes for optimization problems.
    
    This enumeration provides a comprehensive set of status codes that represent the
    possible outcomes when solving optimization problems across different solver implementations.
    The status codes are designed to be solver-agnostic and provide consistent interpretation
    of solution quality and termination conditions.
    
    The status codes follow standard mathematical optimization terminology and are compatible
    with major optimization solver libraries including Gurobi, CPLEX, OR-Tools, and others.
    This ensures consistent behavior and easy integration when switching between solvers.
    
    Status Categories:
        - **Success States**: OPTIMAL, FEASIBLE - indicate successful problem solving
        - **Infeasibility States**: INFEASIBLE, UNBOUNDED - indicate problem formulation issues
        - **Termination States**: TIMEOUT - indicate early termination due to limits
        - **Error States**: ERROR, UNKNOWN - indicate solver or system issues
    
    Attributes:
        OPTIMAL (str): The solver successfully found a globally optimal solution to the
                      optimization problem. This indicates that no better solution exists
                      within the feasible region, and the solution satisfies all constraints
                      while optimizing the objective function to its theoretical best value.
                      
        INFEASIBLE (str): The optimization problem has no feasible solution. This occurs
                         when the constraints are contradictory or when the constraint set
                         defines an empty feasible region. No solution exists that can
                         satisfy all problem constraints simultaneously.
                         
        FEASIBLE (str): The solver found at least one feasible solution that satisfies
                       all constraints, but optimality cannot be guaranteed. This typically
                       occurs when the solver terminates early due to time limits or when
                       using heuristic algorithms that provide good but not proven optimal solutions.
                       
        UNBOUNDED (str): The optimization problem is unbounded, meaning the objective
                        function can be improved indefinitely without violating constraints.
                        This typically indicates an error in problem formulation where
                        necessary constraints are missing or incorrectly specified.
                        
        TIMEOUT (str): The solver reached the configured time limit before finding an
                      optimal solution or proving infeasibility. The solver may have found
                      feasible solutions during the search process, but was unable to
                      complete the optimization within the allocated time budget.
                      
        ERROR (str): An error occurred during the solving process, preventing successful
                    completion. This may be due to numerical issues, memory limitations,
                    invalid problem formulation, or solver-specific technical problems
                    that require investigation and resolution.
                    
        UNKNOWN (str): The solver status cannot be determined or classified into other
                      categories. This may occur with experimental solvers, custom algorithms,
                      or when interfacing with external optimization services where status
                      information is incomplete or unavailable.
    
    Usage:
        Status codes are returned by solver implementations and can be used for
        control flow and solution validation:
        
        .. code-block:: python
        
            status, solver = solve(problem, 'ORTools')
            
            if status == OXSolutionStatus.OPTIMAL:
                print("Found optimal solution")
                solution = solver[0]
                process_optimal_solution(solution)
                
            elif status == OXSolutionStatus.FEASIBLE:
                print("Found feasible solution, may not be optimal")
                solution = solver[0]
                process_feasible_solution(solution)
                
            elif status == OXSolutionStatus.INFEASIBLE:
                print("Problem has no feasible solution")
                analyze_constraint_conflicts(problem)
                
            elif status == OXSolutionStatus.TIMEOUT:
                print("Solver timed out, may have partial solutions")
                if len(solver) > 0:
                    process_partial_solutions(solver)
    
    Note:
        The string values of the enumeration members are designed to be human-readable
        and suitable for logging, debugging, and user interface display purposes.
        They follow lowercase naming conventions consistent with standard optimization
        terminology and solver documentation.
    """
    OPTIMAL = "optimal"
    INFEASIBLE = "infeasible"
    FEASIBLE = "feasible"
    UNBOUNDED = "unbounded"
    TIMEOUT = "timeout"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class OXSolverSolution:
    """
    Comprehensive data structure representing a complete optimization solution.
    
    This class provides a standardized representation of optimization solutions that
    encapsulates all relevant information about variable assignments, constraint
    satisfaction, objective function values, and solution metadata. It serves as
    the primary interface for accessing and analyzing optimization results across
    different solver implementations.
    
    The solution data structure is designed to support various optimization problem
    types including constraint satisfaction problems (CSP), linear programming (LP),
    and goal programming (GP) with comprehensive validation and analysis capabilities.
    
    Data Components:
        The solution captures multiple dimensions of optimization results:
        
        - **Variable Assignments**: Complete mapping of decision variable values
          with UUID-based identification for efficient lookup and cross-referencing
        - **Constraint Analysis**: Detailed evaluation of all constraints including
          left-hand side values, relational operators, and right-hand side bounds
        - **Objective Evaluation**: Optimization objective function value for
          linear and goal programming problems
        - **Special Constraints**: Advanced constraint types with specialized
          value representations for complex mathematical relationships
        - **Solution Status**: Quality and termination condition indicators
    
    Attributes:
        status (OXSolutionStatus): The termination status of the optimization process
                                  indicating solution quality (optimal, feasible, infeasible, etc.)
                                  and providing insight into solver performance and problem characteristics.
                                  Default: OXSolutionStatus.UNKNOWN
                                  
        decision_variable_values (VariableValueMapping): Complete mapping from variable
                                                        UUIDs to their assigned numerical values in the solution.
                                                        This provides the primary result of the optimization
                                                        process with efficient O(1) lookup capabilities.
                                                        Default: empty defaultdict
                                                        
        constraint_values (ConstraintValueMapping): Detailed constraint evaluation results
                                                   mapping constraint UUIDs to tuples containing
                                                   (left_hand_side_value, operator, right_hand_side_value).
                                                   This enables comprehensive constraint satisfaction
                                                   analysis and validation. Default: empty defaultdict
                                                   
        objective_function_value (NumericType): The evaluated objective function value
                                               for optimization problems. For minimization problems,
                                               lower values indicate better solutions. For maximization
                                               problems, higher values are preferred. Default: 0
                                               
        special_constraint_values (SpecialContraintValueMapping): Specialized constraint
                                                                 evaluation results for advanced
                                                                 constraint types including multiplicative,
                                                                 division, modulo, and conditional constraints.
                                                                 Default: empty defaultdict
    
    Solution Analysis Features:
        The class provides comprehensive methods for solution analysis and reporting:
        
        - **Formatted Output**: Human-readable solution reports with variable names
        - **Constraint Validation**: Detailed constraint satisfaction analysis
        - **Cross-References**: Mapping between UUIDs and problem entities
        - **Status Interpretation**: Solution quality assessment and recommendations
    
    Usage:
        Solutions are typically created by solver implementations and accessed
        through the solver interface:
        
        .. code-block:: python
        
            status, solver = solve(problem, 'ORTools')
            
            if len(solver) > 0:
                solution = solver[0]  # Get first solution
                
                # Access variable values
                for var_id, value in solution.decision_variable_values.items():
                    variable = problem.variables[var_id]
                    print(f"{variable.name} = {value}")
                
                # Check objective function
                print(f"Objective value: {solution.objective_function_value}")
                
                # Analyze constraint satisfaction
                for const_id, (lhs, op, rhs) in solution.constraint_values.items():
                    constraint = problem.constraints[const_id]
                    satisfied = evaluate_constraint(lhs, op, rhs)
                    print(f"{constraint.name}: {lhs} {op} {rhs} ({'✓' if satisfied else '✗'})")
    
    Performance Considerations:
        - Dictionary-based storage provides O(1) access to solution components
        - Default factory patterns minimize memory allocation overhead
        - Lazy evaluation of constraint satisfaction enables efficient analysis
        - UUID-based indexing ensures consistent cross-referencing across problem components
        
    Validation:
        The solution structure supports comprehensive validation including:
        
        - Variable bound checking against problem constraints
        - Constraint satisfaction verification using numerical tolerances
        - Objective function value validation for optimization problems
        - Special constraint evaluation for complex mathematical relationships
        
    Note:
        Solution objects are typically immutable after creation by solver implementations.
        Modifications should be performed through solver re-execution rather than
        direct manipulation of solution data structures.
    """
    # TODO Can add statistics?
    status: OXSolutionStatus = field(default=OXSolutionStatus.UNKNOWN)
    decision_variable_values: VariableValueMapping = field(default_factory=defaultdict)
    constraint_values: ConstraintValueMapping = field(default_factory=defaultdict)
    objective_function_value: NumericType = field(default=0)
    special_constraint_values: SpecialContraintValueMapping = field(default_factory=defaultdict)

    def print_solution_for(self, prb: OXCSPProblem):
        """Print a formatted solution with variable names and constraint names from the problem.
        
        This method prints a detailed solution report including the objective function value,
        decision variable values with their names, and constraint values with their names.
        
        Args:
            prb (OXCSPProblem): The problem instance containing variable and constraint definitions.
        """
        result = f"Solution Found {self.status}\n"
        result += f"\tObjective Function Value: {self.objective_function_value}\n"
        result += f"\tDecision Variable Values:\n"
        for var_id, var_value in self.decision_variable_values.items():
            result += f"\t\t{str(prb.variables[var_id])}: {var_value}\n"
        result += f"\tConstraints:\n"
        for constraint_id, (lhs, operator, rhs) in self.constraint_values.items():
            result += f"\t\t{prb.constraints[constraint_id].name
                             if constraint_id in prb.constraints else prb.goal_constraints[constraint_id].name}: {lhs} {operator} {rhs}\n"
        print(result)

    def __str__(self):
        """Return a string representation of the solution.
        
        Returns:
            str: A formatted string containing solution details.
        """
        result = f"Solution Found {self.status}\n"
        result += f"\tObjective Function Value: {self.objective_function_value}\n"
        result += f"\tDecision Variable Values:\n"
        for var_id, var_value in self.decision_variable_values.items():
            result += f"\t\t{var_id}: {var_value}\n"
        result += f"\tConstraints:\n"
        for constraint_id, (lhs, operator, rhs) in self.constraint_values.items():
            result += f"\t\t{constraint_id}: {lhs} {operator} {rhs}\n"
        return result


class OXSolverInterface:
    """
    Abstract base class defining the standard interface for all optimization solver implementations.
    
    This class establishes the fundamental contract that all concrete solver implementations
    must adhere to within the OptiX optimization framework. It provides a comprehensive
    template for integrating diverse optimization engines while maintaining consistent
    behavior, standardized method signatures, and uniform solution handling patterns.
    
    The interface design follows the Template Method pattern, defining the overall
    algorithm structure for solving optimization problems while allowing subclasses
    to implement solver-specific details. This ensures consistent problem setup,
    solving workflows, and solution extraction across different optimization engines.
    
    Core Responsibilities:
        - **Variable Management**: Standardized creation and mapping of decision variables
          from OptiX problem formulations to solver-specific representations
        - **Constraint Translation**: Systematic conversion of OptiX constraints to
          native solver constraint formats with proper operator and coefficient handling
        - **Objective Configuration**: Setup of optimization objectives for linear
          and goal programming problems with support for minimization and maximization
        - **Solution Extraction**: Comprehensive retrieval of optimization results
          including variable values, constraint evaluations, and solver statistics
        - **Parameter Management**: Flexible configuration of solver-specific parameters
          for performance tuning and algorithmic customization
    
    Interface Methods:
        The class defines both abstract methods (must be implemented by subclasses)
        and concrete methods (provide common functionality):
        
        **Abstract Methods** (require implementation):
        - `_create_single_variable()`: Variable creation in solver-specific format
        - `_create_single_constraint()`: Constraint creation with proper translation
        - `create_special_constraints()`: Advanced constraint type handling
        - `create_objective()`: Objective function setup for optimization problems
        - `solve()`: Core solving algorithm execution and solution extraction
        - `get_solver_logs()`: Diagnostic and debugging information retrieval
        
        **Concrete Methods** (provided by base class):
        - `create_variable()`: Orchestrates creation of all problem variables
        - `create_constraints()`: Manages setup of all standard constraints
        - Collection access methods for solution enumeration and analysis
    
    Attributes:
        _parameters (Parameters): Comprehensive dictionary storing solver-specific
                                 configuration parameters including algorithmic settings,
                                 performance tuning options, and behavioral controls.
                                 This enables flexible customization of solver behavior
                                 without modifying core implementation code.
                                 
        _solutions (List[OXSolverSolution]): Ordered collection of optimization solutions
                                           found during the solving process. Supports
                                           multiple solution enumeration for problems
                                           with multiple optimal or feasible solutions.
                                           Provides efficient access through indexing
                                           and iteration protocols.
    
    Solving Workflow:
        The standard solving process follows a well-defined sequence:
        
        1. **Problem Setup**: Variable and constraint creation from OptiX problem definition
        2. **Solver Configuration**: Parameter application and algorithmic customization
        3. **Objective Setup**: Optimization direction and objective function configuration
        4. **Solution Process**: Core solving algorithm execution with progress monitoring
        5. **Result Extraction**: Solution data retrieval and status determination
        6. **Validation**: Solution verification and constraint satisfaction checking
        
        .. code-block:: python
        
            # Standard workflow implementation
            solver = ConcretesolverInterface(**parameters)
            solver.create_variable(problem)
            solver.create_constraints(problem)
            solver.create_special_constraints(problem)
            
            if isinstance(problem, OXLPProblem):
                solver.create_objective(problem)
                
            status = solver.solve(problem)
            
            # Access results
            for solution in solver:
                analyze_solution(solution)
    
    Extensibility Design:
        The interface is designed to accommodate diverse optimization paradigms:
        
        - **Linear Programming**: Continuous optimization with linear constraints
        - **Integer Programming**: Discrete optimization with integer variables
        - **Constraint Programming**: Logical constraint satisfaction and enumeration
        - **Goal Programming**: Multi-objective optimization with priority levels
        - **Heuristic Algorithms**: Approximate optimization with custom algorithms
    
    Parameter Management:
        Solver parameters enable fine-grained control over optimization behavior:
        
        - **Algorithmic Parameters**: Solver-specific algorithm selection and tuning
        - **Performance Parameters**: Time limits, memory limits, and precision settings
        - **Output Parameters**: Logging levels, solution enumeration, and debugging options
        - **Problem-Specific Parameters**: Customization for particular problem characteristics
    
    Solution Management:
        The interface provides comprehensive solution handling capabilities:
        
        - **Multiple Solutions**: Support for enumeration of alternative optimal solutions
        - **Solution Quality**: Status tracking and optimality verification
        - **Incremental Results**: Progressive solution improvement tracking
        - **Solution Comparison**: Utilities for comparing and ranking multiple solutions
    
    Error Handling:
        The interface defines consistent error handling patterns:
        
        - **Implementation Errors**: NotImplementedError for missing abstract methods
        - **Parameter Validation**: Custom exceptions for invalid solver parameters
        - **Numerical Issues**: Graceful handling of solver-specific numerical problems
        - **Resource Limitations**: Proper handling of memory and time limit violations
    
    Performance Considerations:
        - Solution storage uses efficient data structures for large solution sets
        - Parameter dictionaries provide O(1) configuration access
        - Iterator protocols enable memory-efficient solution enumeration
        - Abstract method design minimizes overhead in concrete implementations
        
    Example Implementation:
        Basic structure for implementing a custom solver interface:
        
        .. code-block:: python
        
            class CustomSolverInterface(OXSolverInterface):
                def __init__(self, **kwargs):
                    super().__init__(**kwargs)
                    self._native_solver = initialize_custom_solver()
                    self._var_mapping = {}
                    
                def _create_single_variable(self, var: OXVariable):
                    native_var = self._native_solver.add_variable(
                        name=var.name,
                        lower_bound=var.lower_bound,
                        upper_bound=var.upper_bound
                    )
                    self._var_mapping[var.id] = native_var
                    
                def solve(self, prb: OXCSPProblem) -> OXSolutionStatus:
                    status = self._native_solver.solve()
                    if status == 'optimal':
                        solution = self._extract_solution()
                        self._solutions.append(solution)
                        return OXSolutionStatus.OPTIMAL
                    return OXSolutionStatus.UNKNOWN
    
    Note:
        Concrete implementations should carefully handle solver-specific exceptions
        and translate them to appropriate OXSolutionStatus values for consistent
        error reporting across the framework.
    """
    # TODO: Change Parameters to OXProblem.

    def __init__(self, **kwargs):
        """Initialize the solver interface with optional parameters.
        
        Args:
            **kwargs: Solver-specific parameters passed as keyword arguments.
        """
        self._parameters: Parameters = defaultdict(None, **kwargs)
        self._solutions: list[OXSolverSolution] = []

    def _create_single_variable(self, var: OXVariable):
        """Create a single variable in the solver.
        
        Args:
            var (OXVariable): The variable to create.
            
        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("This method should be implemented in the subclass.")

    def create_variable(self, prb: OXCSPProblem):
        """Create all variables from the problem in the solver.
        
        Args:
            prb (OXCSPProblem): The problem containing variables to create.
        """
        for var in prb.variables:
            self._create_single_variable(var)

    def _create_single_constraint(self, constraint: OXConstraint):
        """Create a single constraint in the solver.
        
        Args:
            constraint (OXConstraint): The constraint to create.
            
        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("This method should be implemented in the subclass.")

    def create_constraints(self, prb: OXCSPProblem):
        """Create all regular constraints from the problem in the solver.
        
        This method creates all constraints except those that are part of
        special constraints (which are handled separately).
        
        Args:
            prb (OXCSPProblem): The problem containing constraints to create.
        """
        for constraint in prb.constraints:
            if constraint.id in prb.constraints_in_special_constraints:
                continue
            self._create_single_constraint(constraint)
        if isinstance(prb, OXGPProblem):
            for constraint in prb.goal_constraints:
                self._create_single_constraint(constraint)

    def create_special_constraints(self, prb: OXCSPProblem):
        """Create all special constraints from the problem in the solver.
        
        Args:
            prb (OXCSPProblem): The problem containing special constraints to create.
            
        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError()

    def create_objective(self, prb: OXLPProblem):
        """Create the objective function in the solver.
        
        Args:
            prb (OXLPProblem): The linear programming problem containing the objective function.
            
        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError()

    def solve(self, prb: OXCSPProblem) -> OXSolutionStatus:
        """Solve the optimization problem.
        
        Args:
            prb (OXCSPProblem): The problem to solve.
            
        Returns:
            OXSolutionStatus: The status of the solution process.
            
        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError()

    def get_solver_logs(self) -> Optional[LogsType]:
        """Get solver-specific logs and debugging information.
        
        Returns:
            Optional[LogsType]: Solver logs if available, None otherwise.
            
        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError()

    def __getitem__(self, item) -> OXSolverSolution:
        """Get a solution by index.
        
        Args:
            item: The index of the solution to retrieve.
            
        Returns:
            OXSolverSolution: The solution at the specified index.
        """
        return self._solutions[item]

    def __len__(self) -> int:
        """Get the number of solutions found.
        
        Returns:
            int: The number of solutions in the solution list.
        """
        return len(self._solutions)

    def __iter__(self) -> Iterator[OXSolverSolution]:
        """Iterate over all solutions.
        
        Returns:
            Iterator[OXSolverSolution]: An iterator over the solutions.
        """
        return iter(self._solutions)

    @property
    def parameters(self) -> Parameters:
        """Get the solver parameters.
        
        Returns:
            Parameters: Dictionary of solver parameters.
            
        Warning:
            Users can modify these parameters, but validation mechanisms
            should be implemented to ensure parameters are valid for the specific solver.
        """
        # WARN Here we are expecting to user to modify the solver parameters, however we need to create a
        #      validation mechanism to ensure that the parameters are valid for the specific solver.
        return self._parameters
