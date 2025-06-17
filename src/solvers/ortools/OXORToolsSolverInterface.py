from typing import Optional

from ortools.sat.python.cp_model import CpModel

from base import OXception
from constraints.OXConstraint import OXConstraint, OXGoalConstraint, RelationalOperators
from constraints.OXpression import OXpression
from problem.OXProblem import ObjectiveType

from solvers.OXSolverInterface import OXSolverInterface, LogsType, SpecialContraintValueMapping, ConstraintValueMapping, \
    VariableValueMapping, NumericType, OXSolutionStatus, SpecialConstraintType, ConstraintType, VariableType
from variables.OXVariable import OXVariable


class OXORToolsSolverInterface(OXSolverInterface):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Supported Parameters:
        # - equalizeDenominators: Use denominator equalization (bool)
        self._model = CpModel()

        self._var_mapping = {}
        self._constraint_mapping = {}

    def _create_single_variable(self, var: OXVariable):
        if var.lower_bound == 0 and var.upper_bound == 1:
            self._var_mapping[var.id] = self._model.new_bool_var(var.name)
        else:
            self._var_mapping[var.id] = self._model.new_int_var(round(var.lower_bound), round(var.upper_bound),
                                                                var.name)

    def _create_single_constraint(self, constraint: OXConstraint):
        if isinstance(constraint, OXGoalConstraint):
            self._create_single_variable(constraint.negative_deviation_variable)
            self._create_single_variable(constraint.positive_deviation_variable)
        weights = constraint.expression.weights
        rhs = constraint.rhs
        if any(isinstance(weight, float) for weight in weights) or isinstance(rhs, float):
            if self._parameters["equalizeDenominators"]:
                weights = [round(constraint.rhs_denominator * weight) for weight in
                           constraint.expression.integer_weights]
                rhs = round(constraint.expression.integer_denominator * constraint.rhs_numerator)
            else:
                raise OXception("OR-Tools does not support float weights in constraints. Use integers instead.")
        if isinstance(constraint, OXGoalConstraint):
            expr = sum(self._var_mapping[v] * w for v, w in zip(constraint.expression.variables, weights))
            expr = expr - self._var_mapping[constraint.positive_deviation_variable.id] + self._var_mapping[constraint.negative_deviation_variable.id]
            self._constraint_mapping[constraint.id] = self._model.add(expr == rhs)
        else:
            if constraint.relational_operator == RelationalOperators.GREATER_THAN:
                self._constraint_mapping[constraint.id] = self._model.add(
                    sum(self._var_mapping[v] * w for v, w in zip(constraint.expression.variables, weights)) > rhs)
            elif constraint.relational_operator == RelationalOperators.GREATER_THAN_EQUAL:
                self._constraint_mapping[constraint.id] = self._model.add(
                    sum(self._var_mapping[v] * w for v, w in zip(constraint.expression.variables, weights)) >= rhs)
            elif constraint.relational_operator == RelationalOperators.EQUAL:
                self._constraint_mapping[constraint.id] = self._model.add(
                    sum(self._var_mapping[v] * w for v, w in zip(constraint.expression.variables, weights)) == rhs)
            elif constraint.relational_operator == RelationalOperators.LESS_THAN_EQUAL:
                self._constraint_mapping[constraint.id] = self._model.add(
                    sum(self._var_mapping[v] * w for v, w in zip(constraint.expression.variables, weights)) <= rhs)
            elif constraint.relational_operator == RelationalOperators.LESS_THAN:
                self._constraint_mapping[constraint.id] = self._model.add(
                    sum(self._var_mapping[v] * w for v, w in zip(constraint.expression.variables, weights)) < rhs)
            else:
                raise OXception(f"Unsupported relational operator: {constraint.relational_operator}")

    def create_special_constraints(self, constraint: SpecialConstraintType):
        pass

    def create_objective(self, expression: OXpression, objective_type: ObjectiveType):
        pass

    def solve(self) -> OXSolutionStatus:
        pass

    def get_solution(self) -> VariableValueMapping:
        pass

    def get_status(self) -> OXSolutionStatus:
        pass

    def get_objective_value(self) -> Optional[NumericType]:
        pass

    def get_variable_values(self) -> Optional[VariableValueMapping]:
        pass

    def get_constraint_values(self) -> Optional[ConstraintValueMapping]:
        pass

    def get_special_constraint_values(self) -> Optional[SpecialContraintValueMapping]:
        pass

    def get_solver_logs(self) -> Optional[LogsType]:
        pass
