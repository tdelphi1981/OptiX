from typing import Optional

from ortools.sat.python.cp_model import CpModel

from base import OXception
from constraints.OXConstraint import OXConstraint, OXGoalConstraint, RelationalOperators
from constraints.OXSpecialConstraints import OXMultiplicativeEqualityConstraint, \
    OXDivisionEqualityConstraint, OXModuloEqualityConstraint, OXSummationEqualityConstraint, OXConditionalConstraint
from problem.OXProblem import OXCSPProblem, OXLPProblem, OXGPProblem, ObjectiveType
from solvers.OXSolverInterface import OXSolverInterface, LogsType, SpecialContraintValueMapping, ConstraintValueMapping, \
    VariableValueMapping, NumericType, OXSolutionStatus
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
            expr = expr - self._var_mapping[constraint.positive_deviation_variable.id] + self._var_mapping[
                constraint.negative_deviation_variable.id]
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

    def create_special_constraints(self, prb: OXCSPProblem):
        for constraint in prb.specials:
            if isinstance(constraint, OXMultiplicativeEqualityConstraint):
                self.__create_multiplicative_equality_constraint(constraint)
            elif isinstance(constraint, OXDivisionEqualityConstraint) or isinstance(constraint,
                                                                                    OXModuloEqualityConstraint):
                self.__create_division_modulo_equality_constraint(constraint)
            elif isinstance(constraint, OXSummationEqualityConstraint):
                self.__create_summation_equality_constraint(constraint)
            elif isinstance(constraint, OXConditionalConstraint):
                self.__create_conditional_constraint(constraint, prb)
            else:
                raise OXception(f"Unsupported special constraint type: {type(constraint)}")

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
        if any(isinstance(weight, float) for weight in weights):
            if self._parameters["equalizeDenominators"]:
                weights = [weight for weight in prb.objective_function.integer_weights]
            else:
                raise OXception("OR-Tools does not support float weights in objective functions. Use integers instead.")
        expr = sum(var * weight for var, weight in zip(vars, weights))

        if prb.objective_type == ObjectiveType.MINIMIZE:
            self._model.minimize(expr)
        else:
            self._model.maximize(expr)


    def solve(self, prb: OXCSPProblem) -> OXSolutionStatus:
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

    def __create_multiplicative_equality_constraint(self, constraint: OXMultiplicativeEqualityConstraint):
        out_var = self._var_mapping[constraint.output_variable]

        input_vars = [self._var_mapping[v] for v in constraint.input_variables]

        self._model.add_multiplication_equality(out_var, input_vars)

    def __create_division_modulo_equality_constraint(self,
                                                     constraint: OXDivisionEqualityConstraint | OXModuloEqualityConstraint):
        out_var = self._var_mapping[constraint.output_variable]
        in_var = self._var_mapping[constraint.input_variable]
        denominator = constraint.denominator

        if isinstance(constraint, OXDivisionEqualityConstraint):
            self._model.add_division_equality(out_var, in_var, denominator)
        elif isinstance(constraint, OXModuloEqualityConstraint):
            self._model.add_modulo_equality(out_var, in_var, denominator)
        else:
            raise OXception(f"Unsupported special constraint type: {type(constraint)}")

    def __create_summation_equality_constraint(self, constraint: OXSummationEqualityConstraint):
        out_var = self._var_mapping[constraint.output_variable]
        input_vars = [self._var_mapping[v] for v in constraint.input_variables]

        self._model.add(out_var == sum(input_vars))

    def __create_constraint_expression(self, constraint: OXConstraint):
        weights = constraint.expression.weights
        rhs = constraint.rhs
        if any(isinstance(weight, float) for weight in weights) or isinstance(rhs, float):
            if self._parameters["equalizeDenominators"]:
                weights = [round(constraint.rhs_denominator * weight) for weight in
                           constraint.expression.integer_weights]
                rhs = round(constraint.expression.integer_denominator * constraint.rhs_numerator)
            else:
                raise OXception("OR-Tools does not support float weights in constraints. Use integers instead.")

        if constraint.relational_operator == RelationalOperators.GREATER_THAN:
            return sum(self._var_mapping[v] * w for v, w in zip(constraint.expression.variables, weights)) > rhs
        elif constraint.relational_operator == RelationalOperators.GREATER_THAN_EQUAL:
            return sum(self._var_mapping[v] * w for v, w in zip(constraint.expression.variables, weights)) >= rhs
        elif constraint.relational_operator == RelationalOperators.EQUAL:
            return sum(self._var_mapping[v] * w for v, w in zip(constraint.expression.variables, weights)) == rhs
        elif constraint.relational_operator == RelationalOperators.LESS_THAN_EQUAL:
            return sum(self._var_mapping[v] * w for v, w in zip(constraint.expression.variables, weights)) <= rhs
        elif constraint.relational_operator == RelationalOperators.LESS_THAN:
            return sum(self._var_mapping[v] * w for v, w in zip(constraint.expression.variables, weights)) < rhs
        else:
            raise OXception(f"Unsupported relational operator: {constraint.relational_operator}")

    def __create_conditional_constraint(self, constraint: OXConditionalConstraint, prb: OXCSPProblem):
        indicator_variable = self._var_mapping[constraint.indicator_variable]

        input_constraint_id = constraint.input_constraint
        true_constraint_id = constraint.constraint_if_true
        false_constraint_id = constraint.constraint_if_false

        input_constraint = prb.find_constraint_by_id(input_constraint_id)
        true_constraint = prb.find_constraint_by_id(true_constraint_id)
        false_constraint = prb.find_constraint_by_id(false_constraint_id)
        input_reversed = input_constraint.reverse()

        input_expression = self.__create_constraint_expression(input_constraint)
        input_reversed_expression = self.__create_constraint_expression(input_reversed)
        true_expression = self.__create_constraint_expression(true_constraint)
        false_expression = self.__create_constraint_expression(false_constraint)

        self._model.add(input_expression).only_enforce_if(indicator_variable)
        self._model.add(input_reversed_expression).only_enforce_if(indicator_variable.Not())
        self._model.add(true_expression).only_enforce_if(indicator_variable)
        self._model.add(false_expression).only_enforce_if(indicator_variable.Not())
