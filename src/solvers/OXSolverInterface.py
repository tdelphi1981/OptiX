"""Core solver interface and data structures for the OptiX optimization framework.

This module defines the abstract base class for all solvers and provides
common data structures for representing solutions, solution status, and
parameters. It serves as the foundation for all solver implementations.
"""

import enum
from collections import defaultdict
from dataclasses import dataclass, field
from typing import TypeVar, Union, Optional, List, Dict, Tuple, Any, Iterator
from uuid import UUID

from constraints.OXConstraint import OXConstraint, RelationalOperators
from constraints.OXSpecialConstraints import OXSpecialConstraint
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
    """Enumeration of possible solution statuses.
    
    This enum defines the possible states a solver can return after
    attempting to solve an optimization problem.
    
    Attributes:
        OPTIMAL (str): The solver found an optimal solution.
        INFEASIBLE (str): The problem has no feasible solution.
        FEASIBLE (str): The solver found a feasible solution but not necessarily optimal.
        UNBOUNDED (str): The problem is unbounded (objective can be improved indefinitely).
        TIMEOUT (str): The solver reached the time limit before finding a solution.
        ERROR (str): An error occurred during solving.
        UNKNOWN (str): The solver status is unknown or undefined.
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
    """Data class representing a solution to an optimization problem.
    
    This class encapsulates all information about a solution found by a solver,
    including variable values, constraint evaluations, and objective function value.
    
    Attributes:
        status (OXSolutionStatus): The status of the solution.
        decision_variable_values (VariableValueMapping): Mapping from variable IDs to their values.
        constraint_values (ConstraintValueMapping): Mapping from constraint IDs to their evaluated values.
        objective_function_value (NumericType): The value of the objective function.
        special_constraint_values (SpecialContraintValueMapping): Mapping from special constraint IDs to their values.
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
            result += f"\t\t{prb.variables[var_id].name}: {var_value}\n"
        result += f"\tConstraints:\n"
        for constraint_id, (lhs, operator, rhs) in self.constraint_values.items():
            result += f"\t\t{prb.find_constraint_by_id(constraint_id).name}: {lhs} {operator} {rhs}\n"
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
    """Abstract base class for all solver implementations.
    
    This class defines the interface that all solvers must implement.
    It provides a common structure for variable creation, constraint handling,
    and solution management.
    
    Attributes:
        _parameters (Parameters): Dictionary of solver-specific parameters.
        _solutions (list[OXSolverSolution]): List of solutions found by the solver.
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
