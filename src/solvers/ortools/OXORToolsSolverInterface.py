"""OR-Tools solver interface for the OptiX optimization framework.

This module provides a concrete implementation of the OXSolverInterface
using Google's OR-Tools CP-SAT solver. It supports constraint satisfaction
problems (CSP) and linear programming (LP) problems with various constraint types.
"""

from math import prod
from typing import Optional

from ortools.sat.python.cp_model import CpModel, CpSolver, CpSolverSolutionCallback, OPTIMAL, FEASIBLE, INFEASIBLE, \
    UNKNOWN, MODEL_INVALID

from base import OXception
from constraints.OXConstraint import OXConstraint, OXGoalConstraint, RelationalOperators
from constraints.OXSpecialConstraints import OXMultiplicativeEqualityConstraint, \
    OXDivisionEqualityConstraint, OXModuloEqualityConstraint, OXSummationEqualityConstraint, OXConditionalConstraint
from problem.OXProblem import OXCSPProblem, OXLPProblem, OXGPProblem, ObjectiveType
from solvers.OXSolverInterface import OXSolverInterface, LogsType, OXSolutionStatus, OXSolverSolution
from variables.OXVariable import OXVariable


class OXORToolsSolverInterface(OXSolverInterface):
    """OR-Tools CP-SAT solver interface implementation.
    
    This class provides a concrete implementation of the OXSolverInterface
    using Google's OR-Tools CP-SAT solver. It supports various constraint types
    and optimization problems.
    
    Attributes:
        _model (CpModel): The OR-Tools CP-SAT model.
        _var_mapping (dict): Mapping from OX variable IDs to OR-Tools variables.
        _constraint_mapping (dict): Mapping from constraint IDs to OR-Tools constraints.
        _constraint_expr_mapping (dict): Mapping from constraint IDs to their expressions.
    """

    def __init__(self, **kwargs):
        """Initialize the OR-Tools solver interface.
        
        Args:
            **kwargs: Solver parameters. Supported parameters:
                - equalizeDenominators (bool): Use denominator equalization for float handling.
                - solutionCount (int): Maximum number of solutions to find.
                - maxTime (int): Maximum solving time in seconds.
        """
        super().__init__(**kwargs)
        # Supported Parameters:
        # - equalizeDenominators: Use denominator equalization (bool)
        self._model = CpModel()

        self._var_mapping = {}
        self._constraint_mapping = {}
        self._constraint_expr_mapping = {}

    def _create_single_variable(self, var: OXVariable):
        """Create a single variable in the OR-Tools model.
        
        Args:
            var (OXVariable): The variable to create.
        """
        if var.lower_bound == 0 and var.upper_bound == 1:
            self._var_mapping[var.id] = self._model.new_bool_var(var.name)
        else:
            self._var_mapping[var.id] = self._model.new_int_var(round(var.lower_bound), round(var.upper_bound),
                                                                var.name)

    def _create_single_constraint(self, constraint: OXConstraint):
        """Create a single constraint in the OR-Tools model.
        
        Args:
            constraint (OXConstraint): The constraint to create.
            
        Raises:
            OXception: If the constraint contains unsupported elements or float weights
                      without denominator equalization enabled.
        """
        if isinstance(constraint, OXGoalConstraint):
            self._create_single_variable(constraint.negative_deviation_variable)
            self._create_single_variable(constraint.positive_deviation_variable)
        weights = constraint.expression.weights
        rhs = constraint.rhs
        if any(isinstance(weight, float) for weight in weights) or isinstance(rhs, float):
            if "equalizeDenominators" in self._parameters and self._parameters["equalizeDenominators"]:
                weights = [round(constraint.rhs_denominator * weight) for weight in
                           constraint.expression.integer_weights]
                rhs = round(constraint.expression.integer_denominator * constraint.rhs_numerator)
            else:
                raise OXception("OR-Tools does not support float weights in constraints. Use integers instead.")
        if isinstance(constraint, OXGoalConstraint):
            expr = sum(self._var_mapping[v] * w for v, w in zip(constraint.expression.variables, weights))
            expr = expr - self._var_mapping[constraint.positive_deviation_variable.id] + self._var_mapping[
                constraint.negative_deviation_variable.id]
            self._constraint_expr_mapping[constraint.id] = expr
            self._constraint_mapping[constraint.id] = self._model.add(expr == rhs)
        else:
            self._constraint_expr_mapping[constraint.id] = sum(
                self._var_mapping[v] * w for v, w in zip(constraint.expression.variables, weights))
            if constraint.relational_operator == RelationalOperators.GREATER_THAN:
                self._constraint_mapping[constraint.id] = self._model.add(
                    self._constraint_expr_mapping[constraint.id] > rhs)
            elif constraint.relational_operator == RelationalOperators.GREATER_THAN_EQUAL:
                self._constraint_mapping[constraint.id] = self._model.add(
                    self._constraint_expr_mapping[constraint.id] >= rhs)
            elif constraint.relational_operator == RelationalOperators.EQUAL:
                self._constraint_mapping[constraint.id] = self._model.add(
                    self._constraint_expr_mapping[constraint.id] == rhs)
            elif constraint.relational_operator == RelationalOperators.LESS_THAN_EQUAL:
                self._constraint_mapping[constraint.id] = self._model.add(
                    self._constraint_expr_mapping[constraint.id] <= rhs)
            elif constraint.relational_operator == RelationalOperators.LESS_THAN:
                self._constraint_mapping[constraint.id] = self._model.add(
                    self._constraint_expr_mapping[constraint.id] < rhs)
            else:
                raise OXception(f"Unsupported relational operator: {constraint.relational_operator}")

    def create_special_constraints(self, prb: OXCSPProblem):
        """Create all special constraints from the problem.
        
        Args:
            prb (OXCSPProblem): The problem containing special constraints.
            
        Raises:
            OXception: If an unsupported special constraint type is encountered.
        """
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
        """Create the objective function in the OR-Tools model.
        
        Args:
            prb (OXLPProblem): The linear programming problem containing the objective function.
            
        Raises:
            OXception: If no objective function is specified or if float weights are used
                      without denominator equalization enabled.
        """
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
            if 'equalizeDenominators' in self._parameters and self._parameters["equalizeDenominators"]:
                weights = [weight for weight in prb.objective_function.integer_weights]
            else:
                raise OXception("OR-Tools does not support float weights in objective functions. Use integers instead.")
        expr = sum(var * weight for var, weight in zip(vars, weights))

        if prb.objective_type == ObjectiveType.MINIMIZE:
            self._model.minimize(expr)
        else:
            self._model.maximize(expr)

    class SolutionLimiter(CpSolverSolutionCallback):
        """Callback class to limit the number of solutions found.
        
        This class extends CpSolverSolutionCallback to control the number of
        solutions collected during the solving process.
        
        Attributes:
            _solution_count (int): Current number of solutions found.
            _max_solution_count (int): Maximum number of solutions to collect.
            _solver (OXORToolsSolverInterface): Reference to the solver interface.
            _problem (OXCSPProblem): The problem being solved.
        """

        def __init__(self, max_solution_count: int,
                     solver: 'OXORToolsSolverInterface',
                     prb: OXCSPProblem):
            """Initialize the solution limiter callback.
            
            Args:
                max_solution_count (int): Maximum number of solutions to collect.
                solver (OXORToolsSolverInterface): Reference to the solver interface.
                prb (OXCSPProblem): The problem being solved.
            """
            super().__init__()
            self._solution_count = 0
            self._max_solution_count = max_solution_count
            self._solver = solver
            self._problem = prb

        def on_solution_callback(self):
            """Callback method called when a solution is found.
            
            This method creates an OXSolverSolution object with the current solution
            values and adds it to the solver's solution list.
            
            Raises:
                OXception: If an unsupported special constraint type is encountered.
            """
            self._solution_count += 1
            # TODO Read solution values from solver, prepare solution object and add to solver interface
            solution_object = OXSolverSolution()
            solution_object.status = OXSolutionStatus.OPTIMAL
            solution_object.decision_variable_values = {
                var_id: self.value(self._solver._var_mapping[var_id]) for var_id in self._solver._var_mapping
            }
            solution_object.constraint_values = {
                constraint_id: (self.value(self._solver._constraint_expr_mapping[constraint_id]),
                                self._problem.find_constraint_by_id(constraint_id).relational_operator,
                                self._problem.find_constraint_by_id(constraint_id).rhs)
                for constraint_id in self._solver._constraint_mapping
            }
            if isinstance(self._problem, OXLPProblem):
                solution_object.objective_function_value = self.ObjectiveValue()
            if len(self._problem.specials) > 0:
                for s_constraint in self._problem.specials:
                    if not isinstance(s_constraint, OXConditionalConstraint):
                        input_value = 0
                        output_value = 0
                        if isinstance(s_constraint, OXMultiplicativeEqualityConstraint):
                            input_value = prod(
                                self.value(self._solver._var_mapping[var]) for var in s_constraint.input_variables)
                            output_value = self.value(self._solver._var_mapping[s_constraint.output_variable])
                        elif isinstance(s_constraint, OXDivisionEqualityConstraint):
                            input_value = self.value(
                                self._solver._var_mapping[s_constraint.input_variable]) // s_constraint.denominator
                            output_value = self.value(self._solver._var_mapping[s_constraint.output_variable])
                        elif isinstance(s_constraint, OXModuloEqualityConstraint):
                            input_value = self.value(
                                self._solver._var_mapping[s_constraint.input_variable]) % s_constraint.denominator
                            output_value = self.value(self._solver._var_mapping[s_constraint.output_variable])
                        elif isinstance(s_constraint, OXSummationEqualityConstraint):
                            input_value = sum(
                                self.value(self._solver._var_mapping[var]) for var in s_constraint.input_variables)
                            output_value = self.value(self._solver._var_mapping[s_constraint.output_variable])
                        else:
                            raise OXception(f"Unsupported special constraint type: {type(s_constraint)}")
                        solution_object.special_constraint_values[s_constraint.id] = (input_value, output_value)
                    else:
                        input_constraint_value = solution_object.constraint_values[s_constraint.input_constraint]
                        indicator_value = self.value(self._solver._var_mapping[s_constraint.indicator_variable])
                        true_value = solution_object.constraint_values[s_constraint.constraint_if_true]
                        false_value = solution_object.constraint_values[s_constraint.constraint_if_false]
                        solution_object.special_constraint_values[s_constraint.id] = (input_constraint_value,
                                                                                      indicator_value, true_value,
                                                                                      false_value)
            self._solver._solutions.append(solution_object)
            if self._solution_count >= self._max_solution_count:
                self.StopSearch()

    def solve(self, prb: OXCSPProblem) -> OXSolutionStatus:
        """Solve the optimization problem using OR-Tools CP-SAT solver.
        
        Args:
            prb (OXCSPProblem): The problem to solve.
            
        Returns:
            OXSolutionStatus: The status of the solution process.
            
        Raises:
            OXception: If the solver returns an unexpected status.
        """
        solution_count = 1
        max_time = 10 * 60
        if "solutionCount" in self._parameters:
            solution_count = self._parameters["solutionCount"]
        if "maxTime" in self._parameters:
            max_time = self._parameters["maxTime"]

        solver = CpSolver()

        if max_time is not None:
            solver.parameters.max_time_in_seconds = max_time

        limiter = OXORToolsSolverInterface.SolutionLimiter(solution_count,
                                                           self,
                                                           prb)

        status = solver.solve(self._model, solution_callback=limiter)

        if status == OPTIMAL:
            return OXSolutionStatus.OPTIMAL
        elif status == FEASIBLE:
            return OXSolutionStatus.FEASIBLE
        elif status == INFEASIBLE:
            return OXSolutionStatus.INFEASIBLE
        elif status == UNKNOWN:
            return OXSolutionStatus.UNKNOWN
        elif status == MODEL_INVALID:
            return OXSolutionStatus.ERROR

        raise OXception(f"Solver returned status: {status}")

    def get_solver_logs(self) -> Optional[LogsType]:
        """Get solver logs and debugging information.
        
        Returns:
            Optional[LogsType]: Currently not implemented, returns None.
        """
        pass

    def __create_multiplicative_equality_constraint(self, constraint: OXMultiplicativeEqualityConstraint):
        """Create a multiplicative equality constraint.
        
        Args:
            constraint (OXMultiplicativeEqualityConstraint): The constraint to create.
        """
        out_var = self._var_mapping[constraint.output_variable]

        input_vars = [self._var_mapping[v] for v in constraint.input_variables]

        self._model.add_multiplication_equality(out_var, input_vars)

    def __create_division_modulo_equality_constraint(self,
                                                     constraint: OXDivisionEqualityConstraint | OXModuloEqualityConstraint):
        """Create a division or modulo equality constraint.
        
        Args:
            constraint (OXDivisionEqualityConstraint | OXModuloEqualityConstraint): The constraint to create.
            
        Raises:
            OXception: If the constraint type is not supported.
        """
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
        """Create a summation equality constraint.
        
        Args:
            constraint (OXSummationEqualityConstraint): The constraint to create.
        """
        out_var = self._var_mapping[constraint.output_variable]
        input_vars = [self._var_mapping[v] for v in constraint.input_variables]

        self._model.add(out_var == sum(input_vars))

    def __create_constraint_expression(self, constraint: OXConstraint):
        """Create a constraint expression for OR-Tools.
        
        Args:
            constraint (OXConstraint): The constraint to convert to an expression.
            
        Returns:
            The OR-Tools constraint expression.
            
        Raises:
            OXception: If the constraint contains unsupported elements or float weights
                      without denominator equalization enabled.
        """
        weights = constraint.expression.weights
        rhs = constraint.rhs
        if any(isinstance(weight, float) for weight in weights) or isinstance(rhs, float):
            if "equalizeDenominators" in self._parameters and self._parameters["equalizeDenominators"]:
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
        """Create a conditional constraint (if-then-else logic).
        
        Args:
            constraint (OXConditionalConstraint): The conditional constraint to create.
            prb (OXCSPProblem): The problem containing the referenced constraints.
        """
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
