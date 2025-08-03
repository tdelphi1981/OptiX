import math
import sys
from fractions import Fraction
from typing import Optional

from base import OXception
from constraints import OXConstraint, OXGoalConstraint, RelationalOperators
from problem import OXCSPProblem, OXLPProblem, OXGPProblem, ObjectiveType
from solvers.OXSolverInterface import OXSolverInterface, OXSolutionStatus
from solvers.OXSolverInterface import LogsType, OXSolverSolution
from variables import OXVariable

import gurobipy as gp
from gurobipy import GRB


class OXGurobiSolverInterface(OXSolverInterface):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self._model = gp.Model("OptiX Model")

        self._var_mapping = {}
        self._constraint_mapping = {}
        self._constraint_expr_mapping = {}

    def _create_single_variable(self, var: OXVariable):
        if var.lower_bound == 0 and var.upper_bound == 1:
            self._var_mapping[var.id] = self._model.addVar(vtype=GRB.BINARY, name=var.name)
        else:
            if self._parameters["use_continuous"]:
                self._var_mapping[var.id] = self._model.addVar(vtype=GRB.CONTINUOUS, lb=var.lower_bound,
                                                               ub=var.upper_bound, name=var.name)
            else:
                lbound = var.lower_bound
                ubound = var.upper_bound
                if math.isinf(ubound):
                    ubound = sys.maxsize
                if math.isinf(lbound):
                    lbound = -sys.maxsize
                if isinstance(lbound, float):
                    lbound = round(lbound)
                if isinstance(ubound, float):
                    ubound = round(ubound)
                self._var_mapping[var.id] = self._model.addVar(vtype=GRB.INTEGER, lb=lbound, ub=ubound, name=var.name)

    def _create_single_continuous_constraint(self, constraint: OXConstraint):
        weight = constraint.expression.weights
        rhs = constraint.rhs

        expr = sum(self._var_mapping[v] * w for v, w in zip(constraint.expression.variables, weight))
        if isinstance(constraint, OXGoalConstraint):
            expr = expr - self._var_mapping[constraint.positive_deviation_variable.id] + self._var_mapping[
                constraint.negative_deviation_variable.id]
            self._constraint_expr_mapping[constraint.id] = expr
            self._constraint_mapping[constraint.id] = self._model.addConstr(expr == rhs)
        else:
            if constraint.relational_operator == RelationalOperators.GREATER_THAN:
                self._constraint_mapping[constraint.id] = self._model.addConstr(expr > rhs)
            elif constraint.relational_operator == RelationalOperators.GREATER_THAN_EQUAL:
                self._constraint_mapping[constraint.id] = self._model.addConstr(expr >= rhs)
            elif constraint.relational_operator == RelationalOperators.EQUAL:
                self._constraint_mapping[constraint.id] = self._model.addConstr(expr == rhs)
            elif constraint.relational_operator == RelationalOperators.LESS_THAN_EQUAL:
                self._constraint_mapping[constraint.id] = self._model.addConstr(expr <= rhs)
            elif constraint.relational_operator == RelationalOperators.LESS_THAN:
                self._constraint_mapping[constraint.id] = self._model.addConstr(expr < rhs)
            else:
                raise OXception(f"Unsupported relational operator: {constraint.relational_operator}")
            self._constraint_expr_mapping[constraint.id] = expr

    def _create_single_integer_constraint(self, constraint: OXConstraint):
        weights = constraint.expression.weights
        rhs = constraint.rhs
        if any(isinstance(weight, float) for weight in weights) or isinstance(rhs, float) or any(
                isinstance(weight, Fraction) for weight in weights) or isinstance(rhs, Fraction):
            if "equalizeDenominators" in self._parameters and self._parameters["equalizeDenominators"]:
                weights = [round(constraint.rhs_denominator * weight) for weight in
                           constraint.expression.integer_weights]
                rhs = round(constraint.expression.integer_denominator * constraint.rhs_numerator)
            else:
                raise OXception(
                    "Current Gurobi settings does not support float weights in objective functions. Use integers instead or adjust parameters.")
        expr = sum(self._var_mapping[v] * w for v, w in zip(constraint.expression.variables, weights))
        if isinstance(constraint, OXGoalConstraint):
            expr = expr - self._var_mapping[constraint.positive_deviation_variable.id] + self._var_mapping[
                constraint.negative_deviation_variable.id]
            self._constraint_expr_mapping[constraint.id] = expr
            self._constraint_mapping[constraint.id] = self._model.addConstr(expr == rhs)
        else:
            self._constraint_expr_mapping[constraint.id] = expr
            if constraint.relational_operator == RelationalOperators.GREATER_THAN:
                self._constraint_mapping[constraint.id] = self._model.addConstr(expr > rhs)
            elif constraint.relational_operator == RelationalOperators.GREATER_THAN_EQUAL:
                self._constraint_mapping[constraint.id] = self._model.addConstr(expr >= rhs)
            elif constraint.relational_operator == RelationalOperators.EQUAL:
                self._constraint_mapping[constraint.id] = self._model.addConstr(expr == rhs)
            elif constraint.relational_operator == RelationalOperators.LESS_THAN_EQUAL:
                self._constraint_mapping[constraint.id] = self._model.addConstr(expr <= rhs)
            elif constraint.relational_operator == RelationalOperators.LESS_THAN:
                self._constraint_mapping[constraint.id] = self._model.addConstr(expr < rhs)
            else:
                raise OXception(f"Unsupported relational operator: {constraint.relational_operator}")

    def _create_single_constraint(self, constraint: OXConstraint):
        if self._parameters["use_continuous"]:
            self._create_single_continuous_constraint(constraint)
        else:
            self._create_single_integer_constraint(constraint)

    def create_special_constraints(self, prb: OXCSPProblem):
        pass

    def create_objective(self, prb: OXLPProblem):
        if prb is None or prb.objective_function is None:
            raise OXception(f"No objective function specified")
        if len(prb.objective_function.variables) == 0:
            if isinstance(prb, OXGPProblem):
                prb.create_objective_function()
            else:
                raise OXception(f"No objective function specified")

        weights = prb.objective_function.weights
        vars = [self._var_mapping[v] for v in prb.objective_function.variables]
        if "use_continuous" in self._parameters and self._parameters["use_continuous"]:
            pass
        else:
            if any(isinstance(weight, float) for weight in weights):
                if 'equalizeDenominators' in self._parameters and self._parameters["equalizeDenominators"]:
                    weights = [weight for weight in prb.objective_function.integer_weights]
                else:
                    raise OXception(
                        "Current Gurobi settings does not support float weights in objective functions. Use integers instead or adjust parameters.")
        expr = sum(var * weight for var, weight in zip(vars, weights))

        if prb.objective_type == ObjectiveType.MINIMIZE:
            self._model.setObjective(expr, GRB.MINIMIZE)
        else:
            self._model.setObjective(expr, GRB.MAXIMIZE)

    def solve(self, prb: OXCSPProblem) -> OXSolutionStatus:
        self._model.optimize()

        if self._model.Status == GRB.OPTIMAL:
            solution_object = OXSolverSolution()
            solution_object.status = OXSolutionStatus.OPTIMAL
            solution_object.decision_variable_values = {var_id: self._var_mapping[var_id].X for var_id in
                                                        self._var_mapping}
            solution_object.constraint_values = {
                constraint_id: (self._constraint_expr_mapping[constraint_id].getValue(),
                                prb.constraints[constraint_id].relational_operator,
                                prb.constraints[constraint_id].rhs)
                if constraint_id in prb.constraints
                else (self._constraint_expr_mapping[constraint_id].getValue(),
                      prb.goal_constraints[constraint_id].relational_operator,
                      prb.goal_constraints[constraint_id].rhs)
                for constraint_id in self._constraint_expr_mapping
            }

            if isinstance(prb, OXLPProblem):
                solution_object.objective_function_value = self._model.getObjective().getValue()
            self._solutions.append(solution_object)
            return OXSolutionStatus.OPTIMAL
        elif self._model.Status == GRB.INFEASIBLE:
            return OXSolutionStatus.INFEASIBLE
        elif self._model.Status == GRB.UNBOUNDED:
            return OXSolutionStatus.UNBOUNDED
        elif self._model.Status == GRB.INF_OR_UNBD:
            return OXSolutionStatus.ERROR
        else:
            return OXSolutionStatus.ERROR

    def get_solver_logs(self) -> Optional[LogsType]:
        pass
