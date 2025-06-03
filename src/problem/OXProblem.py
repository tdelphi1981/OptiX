import itertools
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Self
from uuid import UUID

from base import OXObject, OXception
from constraints.OXConstraint import OXConstraint, OXGoalConstraint, RelationalOperators
from constraints.OXpression import OXpression
from data.OXDatabase import OXDatabase
from variables.OXVariable import OXVariable
from variables.OXVariableSet import OXVariableSet


@dataclass
class OXCSPProblem(OXObject):
    db: OXDatabase = field(default_factory=OXDatabase)
    variables: OXVariableSet = field(default_factory=OXVariableSet)
    constraints: list[OXConstraint] = field(default_factory=list)

    def create_variables_from_db(self,
                                 var_name_template: str = "",
                                 var_description_template: str = "",
                                 upper_bound: float | int = float("inf"),
                                 lower_bound: float | int = 0,
                                 *args):
        available_object_type_set = set(self.db.get_object_types())
        argument_set = set(t.__name__.lower() for t in args)
        invalid_arguments = argument_set.difference(available_object_type_set)
        if len(invalid_arguments) > 0:
            raise OXception(f"Invalid db object type(s) detected : {invalid_arguments}")
        object_type_names = []
        object_instances = []
        for object_type in argument_set:
            object_type_names.append(object_type)
            object_instances.append(self.db.search_by_function(
                lambda x: x.class_name.lower().endswith(object_type.lower())))

        for instances_tuple in itertools.product(*object_instances):
            related_data = {}
            for i in range(len(object_type_names)):
                related_data[object_type_names[i]] = instances_tuple[i].id
            var_name = var_name_template.format(**related_data)
            var_description = var_description_template.format(**related_data)
            self.create_decision_variable(var_name=var_name, description=var_description,
                                          upper_bound=upper_bound, lower_bound=lower_bound,
                                          **related_data)

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
                          weight_calculation_function: Callable[[OXVariable, Self], float | int] = None,
                          variables: list[UUID] = None,
                          weights: list[float | int] = None,
                          operator: RelationalOperators = RelationalOperators.LESS_THAN_EQUAL,
                          value: float | int = None):
        # TODO value için fonksiyonel bir mekanizma koyulabilir mi? Ne için lazım acaba?
        self._check_parameters(variable_search_function, variables, weight_calculation_function, weights)

        if variable_search_function is not None:
            variables = self.variables.search_by_function(variable_search_function)
            weights = [weight_calculation_function(var, self) for var in variables]

        expr = OXpression(variables=variables, weights=weights)
        constraint = OXConstraint(expression=expr, relational_operator=operator, rhs=value)
        self.constraints.append(constraint)

    def _check_parameters(self, variable_search_function, variables, weight_calculation_function, weights):
        if variable_search_function is None and variables is None:
            raise OXception("Either variable_search_function or variables must be provided.")
        if variable_search_function is not None and variables is not None:
            raise OXception("Only one of variable_search_function or variables can be provided.")
        if weight_calculation_function is None and weights is None:
            raise OXception("Either weight_calculation_function or weights must be provided.")
        if weight_calculation_function is not None and weights is not None:
            raise OXception("Only one of weight_calculation_function or weights can be provided.")
        if variable_search_function is not None and weight_calculation_function is None:
            raise OXception("weight_calculation_function must be provided if variable_search_function is provided.")
        if variables is not None and weights is None:
            raise OXception("weights must be provided if variables is provided.")
        if variables is not None and len(variables) != len(weights):
            raise OXception("variables and weights must have the same length.")


class ObjectiveType(StrEnum):
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"


@dataclass
class OXLPProblem(OXCSPProblem):
    objective_function: OXpression = field(default_factory=OXpression)
    objective_type: ObjectiveType = ObjectiveType.MINIMIZE

    def create_objective_function(self,
                                  variable_search_function: Callable[[OXObject], bool] = None,
                                  weight_calculation_function: Callable[[OXVariable, Self], float | int] = None,
                                  variables: list[UUID] = None,
                                  weights: list[float | int] = None,
                                  objective_type: ObjectiveType = ObjectiveType.MINIMIZE):
        self._check_parameters(variable_search_function, variables, weight_calculation_function, weights)

        if variable_search_function is not None:
            variables = self.variables.search_by_function(variable_search_function)
            weights = [weight_calculation_function(var, self) for var in variables]

        self.objective_function = OXpression(variables=variables, weights=weights)
        self.objective_type = objective_type


@dataclass
class OXGPProblem(OXLPProblem):
    goal_constraints: list[OXGoalConstraint] = field(default_factory=list)

    def create_goal_constraint(self,
                               variable_search_function: Callable[[OXObject], bool] = None,
                               weight_calculation_function: Callable[[OXVariable, Self], float | int] = None,
                               variables: list[UUID] = None,
                               weights: list[float | int] = None,
                               operator: RelationalOperators = RelationalOperators.LESS_THAN_EQUAL,
                               value: float | int = None):
        self.create_constraint(variable_search_function, weight_calculation_function, variables, weights, operator,
                               value)

        last_constraint = self.constraints.pop()
        goal_constraint = last_constraint.to_goal()
        self.goal_constraints.append(goal_constraint)

    def create_objective_function(self,
                                  variable_search_function: Callable[[OXObject], bool] = None,
                                  weight_calculation_function: Callable[[OXVariable, Self], float | int] = None,
                                  variables: list[UUID] = None,
                                  weights: list[float | int] = None,
                                  objective_type: ObjectiveType = ObjectiveType.MINIMIZE):
        variables = []

        for constraint in self.goal_constraints:
            variables.extend(constraint.undesired_variables)

        weights = [1.0] * len(variables)

        self.objective_function = OXpression(variables=variables, weights=weights)
        self.objective_type = ObjectiveType.MINIMIZE

