from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID

from base import OXObject, OXception
from constraints.OXConstraint import OXConstraint, OXGoalConstraint, RelationalOperators
from constraints.OXpression import OXpression
from data.OXDatabase import OXDatabase
from variables.OXVariable import OXVariable
from variables.OXVariableSet import OXVariableSet


@dataclass
class OXProblem(OXObject):
    db: OXDatabase = field(default_factory=OXDatabase)
    variables: OXVariableSet = field(default_factory=OXVariableSet)
    constraints: list[OXConstraint] = field(default_factory=list)

    def create_decision_variable(self, var_name: str = "", description: str = "",
                                 upper_bound: float | int = float("inf"),
                                 lower_bound: float | int = 0,
                                 **kwargs):
        d_var = OXVariable(name=var_name, description=description, upper_bound=upper_bound, lower_bound=lower_bound)
        db_types = self.db.get_object_types()
        for key, value in kwargs.items():
            if key not in db_types:
                raise OXception(f"Invalid key {key} for decision variable.")
            d_var.related_data[key] = value
        self.variables.add_object(d_var)

    def create_constraint(self,
                          variable_search_function: Callable[[OXObject], bool] = None,
                          variables: list[UUID] = None,
                          weights: list[float | int] = None,
                          operator: RelationalOperators = RelationalOperators.LESS_THAN_EQUAL,
                          value: float | int = None):
        if variable_search_function is None and variables is None:
            raise OXception("Either variable_search_function or variables must be provided.")
        if variable_search_function is not None and variables is not None:
            raise OXception("Only one of variable_search_function or variables must be provided.")
        if variables is None:
            variables = self.variables.search_by_function(variable_search_function)
        if len(variables) == 0:
            raise OXception("Number of variables must be greater than 0.")
        if weights is None:
            weights = [1] * len(variables)
        if len(variables) != len(weights):
            raise OXception("Number of weights must be equal to number of variables.")
        if value is None:
            raise OXception("Value must be provided.")
        constraint = OXConstraint(expression=OXpression(variables=variables, weights=weights),
                                  relational_operator=operator,
                                  rhs=value)
        self.constraints.append(constraint)

    def __getitem__(self, item: UUID) -> OXConstraint | None:
        if not isinstance(item, UUID):
            raise OXception("Item must be UUID.")
        for constraint in self.constraints:
            if constraint.id == item:
                return constraint
        return None


class ObjectiveType(StrEnum):
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"


@dataclass
class OXLPProblem(OXProblem):
    objective_function: OXpression = field(default_factory=OXpression)
    objective_type: ObjectiveType = ObjectiveType.MINIMIZE


@dataclass
class OXGPProblem(OXLPProblem):
    goal_constraints: list[OXGoalConstraint] = field(default_factory=list)
