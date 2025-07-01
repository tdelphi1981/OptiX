from typing import TypeVar, Union, Optional, List, Dict, Tuple, Any
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


class OXSolutionStatus:
    OPTIMAL = "optimal"
    INFEASIBLE = "infeasible"
    FEASIBLE = "feasible"
    UNBOUNDED = "unbounded"
    TIMEOUT = "timeout"
    ERROR = "error"
    UNKNOWN = "unknown"


class OXSolverInterface:
    # TODO: Change Parameters to OXProblem.

    def __init__(self, **kwargs):
        self._parameters: Parameters = kwargs

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

    def get_solution(self) -> VariableValueMapping:
        raise NotImplementedError()

    def get_status(self) -> OXSolutionStatus:
        raise NotImplementedError()

    def get_objective_value(self) -> Optional[NumericType]:
        raise NotImplementedError()

    def get_variable_values(self) -> Optional[VariableValueMapping]:
        raise NotImplementedError()

    def get_constraint_values(self) -> Optional[ConstraintValueMapping]:
        raise NotImplementedError()

    def get_special_constraint_values(self) -> Optional[SpecialContraintValueMapping]:
        raise NotImplementedError()

    def get_solver_logs(self) -> Optional[LogsType]:
        raise NotImplementedError()

    @property
    def parameters(self) -> Parameters:
        # WARN Here we are expecting to user to modify the solver parameters, however we need to create a
        #      validation mechanism to ensure that the parameters are valid for the specific solver.
        return self._parameters
