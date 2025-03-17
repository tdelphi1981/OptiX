from dataclasses import dataclass, field

from base import OXObject, OXception
from constraints.OXConstraint import OXConstraint, OXGoalConstraint
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


@dataclass
class OXLPProblem(OXProblem):
    objective_function: OXpression = field(default_factory=OXpression)


@dataclass
class OXGPProblem(OXLPProblem):
    goal_constraints: list[OXGoalConstraint] = field(default_factory=list)
