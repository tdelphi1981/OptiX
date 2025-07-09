import enum
from collections import defaultdict
from dataclasses import dataclass, field
from typing import TypeVar, Union, Optional, List, Dict, Tuple, Any, Generator, Iterator
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
    OPTIMAL = "optimal"
    INFEASIBLE = "infeasible"
    FEASIBLE = "feasible"
    UNBOUNDED = "unbounded"
    TIMEOUT = "timeout"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class OXSolverSolution:
    # TODO Can add statistics?
    status: OXSolutionStatus = field(default=OXSolutionStatus.UNKNOWN)
    decision_variable_values: VariableValueMapping = field(default_factory=defaultdict)
    constraint_values: ConstraintValueMapping = field(default_factory=defaultdict)
    objective_function_value: NumericType = field(default=0)
    special_constraint_values: SpecialContraintValueMapping = field(default_factory=defaultdict)

    def print_solution_for(self, prb:OXCSPProblem):
        result = f"Solution Found {self.status}\n"
        result += f"\tObjective Function Value: {self.objective_function_value}\n"
        result += f"\tDecision Variable Values:\n"
        for var_id, var_value in self.decision_variable_values.items():
            result += f"\t\t{prb.variables[var_id].name}: {var_value}\n"
        result += f"\tConstraints:\n"
        for constraint_id, (lhs, operator, rhs) in self.constraint_values.items():
            result += f"\t\t{constraint_id}: {lhs} {operator} {rhs}\n"
        print(result)

    def __str__(self):
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
    # TODO: Change Parameters to OXProblem.

    def __init__(self, **kwargs):
        self._parameters: Parameters = defaultdict(None, **kwargs)
        self._solutions: list[OXSolverSolution] = []

    def _create_single_variable(self, var: OXVariable):
        raise NotImplementedError("This method should be implemented in the subclass.")

    def create_variable(self, prb: OXCSPProblem):
        for var in prb.variables:
            self._create_single_variable(var)

    def _create_single_constraint(self, constraint: OXConstraint):
        raise NotImplementedError("This method should be implemented in the subclass.")

    def create_constraints(self, prb: OXCSPProblem):
        for constraint in prb.constraints:
            if constraint.id in prb.constraints_in_special_constraints:
                continue
            self._create_single_constraint(constraint)

    def create_special_constraints(self, prb: OXCSPProblem):
        raise NotImplementedError()

    def create_objective(self, prb: OXLPProblem):
        raise NotImplementedError()

    def solve(self, prb: OXCSPProblem) -> OXSolutionStatus:
        raise NotImplementedError()

    def get_solver_logs(self) -> Optional[LogsType]:
        raise NotImplementedError()

    def __getitem__(self, item) -> OXSolverSolution:
        return self._solutions[item]

    def __len__(self) -> int:
        return len(self._solutions)

    def __iter__(self) -> Iterator[OXSolverSolution]:
        return iter(self._solutions)

    @property
    def parameters(self) -> Parameters:
        # WARN Here we are expecting to user to modify the solver parameters, however we need to create a
        #      validation mechanism to ensure that the parameters are valid for the specific solver.
        return self._parameters
