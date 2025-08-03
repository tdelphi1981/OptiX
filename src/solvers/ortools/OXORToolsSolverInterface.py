"""
OR-Tools Solver Interface Module
=================================

This module provides a comprehensive implementation of the OXSolverInterface using Google's
OR-Tools CP-SAT solver for the OptiX optimization framework. It enables solving constraint
satisfaction problems (CSP), linear programming (LP), and goal programming (GP) problems
with advanced constraint types and optimization capabilities.

The module serves as a bridge between OptiX's high-level problem modeling interface and
OR-Tools' powerful constraint programming solver, providing seamless integration with
the framework's unified solving architecture.

Key Features:
    - **Constraint Programming**: Full CP-SAT solver integration for discrete optimization
    - **Variable Types**: Support for boolean, integer, and bounded decision variables  
    - **Linear Constraints**: Complete relational operator support (=, <=, >=, <, >)
    - **Special Constraints**: Advanced non-linear constraints including multiplication,
      division, modulo, summation, and conditional (if-then-else) logic
    - **Multi-Solution Support**: Configurable solution enumeration with callback mechanisms
    - **Float Handling**: Automatic denominator equalization for fractional coefficients
    - **Time Management**: Configurable solving time limits and early termination
    - **Solution Analysis**: Comprehensive solution data extraction and validation

Supported Problem Types:
    - **OXCSPProblem**: Constraint satisfaction problems with feasibility focus
    - **OXLPProblem**: Linear programming problems with optimization objectives
    - **OXGPProblem**: Goal programming problems with multi-objective optimization

Architecture:
    - **Variable Mapping**: Efficient UUID-based mapping between OptiX and OR-Tools variables
    - **Constraint Translation**: Automatic conversion of OptiX constraints to CP-SAT format
    - **Solution Callbacks**: Extensible callback system for multi-solution collection
    - **Parameter Management**: Flexible solver parameter configuration system

Example:
    Basic usage for solving a constraint satisfaction problem:

    .. code-block:: python

        from problem.OXProblem import OXCSPProblem
        from solvers.ortools import OXORToolsSolverInterface
        
        # Create and configure problem
        problem = OXCSPProblem()
        x = problem.create_decision_variable("x", 0, 10)
        y = problem.create_decision_variable("y", 0, 10)
        problem.create_constraint([x, y], [1, 1], "<=", 15)
        
        # Create solver with custom parameters
        solver = OXORToolsSolverInterface(
            equalizeDenominators=True,
            solutionCount=5,
            maxTime=300
        )
        
        # Solve and access results
        solver.create_variables(problem)
        solver.create_constraints(problem)
        status = solver.solve(problem)
        
        for solution in solver:
            print(f"Variables: {solution.decision_variable_values}")

Advanced Features:
    The solver supports sophisticated constraint types through special constraint handling:
    
    - **Multiplicative Constraints**: Product relationships between variables
    - **Division/Modulo Constraints**: Integer division and remainder operations  
    - **Conditional Constraints**: If-then-else logic with indicator variables
    - **Summation Constraints**: Explicit sum relationships for complex expressions

Performance Considerations:
    - OR-Tools CP-SAT is optimized for discrete optimization problems
    - Float coefficients are automatically converted to integers when possible
    - Solution enumeration uses efficient callback mechanisms to minimize memory usage
    - Time limits prevent infinite solving on difficult problem instances

Module Dependencies:
    - ortools.sat.python.cp_model: Core OR-Tools CP-SAT solver functionality
    - base: OptiX exception handling framework
    - constraints: OptiX constraint and expression definitions
    - problem: OptiX problem type definitions and interfaces
    - solvers: OptiX solver interface base classes and solution structures
    - variables: OptiX decision variable definitions and management
"""
import math
import sys
from fractions import Fraction
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
    """
    Concrete implementation of OptiX solver interface using Google OR-Tools CP-SAT solver.
    
    This class provides a comprehensive bridge between OptiX's problem modeling framework
    and Google's OR-Tools Constraint Programming solver. It handles the complete lifecycle
    of problem solving from variable and constraint creation through solution extraction
    and analysis.
    
    The implementation leverages OR-Tools' CP-SAT solver, which excels at discrete optimization
    problems including constraint satisfaction, integer programming, and mixed-integer 
    programming. The class automatically handles type conversions, constraint translations,
    and solution callbacks to provide seamless integration with OptiX workflows.
    
    Key Capabilities:
        - **Variable Management**: Automatic creation and mapping of boolean and integer variables
        - **Constraint Translation**: Comprehensive support for linear and special constraint types
        - **Multi-Solution Handling**: Configurable solution enumeration with callback system
        - **Parameter Configuration**: Flexible solver parameter management for performance tuning
        - **Solution Analysis**: Complete solution data extraction including constraint violations
        
    Solver Parameters:
        The class accepts various initialization parameters to customize solver behavior:
        
        - **equalizeDenominators** (bool): When True, enables automatic conversion of float
          coefficients to integers using common denominator calculation. This allows OR-Tools
          to handle fractional weights that would otherwise be rejected. Default: False
          
        - **solutionCount** (int): Maximum number of solutions to collect during enumeration.
          Higher values enable finding multiple feasible solutions but increase solving time.
          Default: 1
          
        - **maxTime** (int): Maximum solving time in seconds before termination. Prevents
          infinite solving on difficult instances. Default: 600 seconds (10 minutes)
    
    Attributes:
        _model (CpModel): The underlying OR-Tools CP-SAT model instance that stores all
                         variables, constraints, and objectives for the optimization problem.
        _var_mapping (Dict[str, IntVar|BoolVar]): Bidirectional mapping from OptiX variable
                                                 UUIDs to their corresponding OR-Tools variable
                                                 objects for efficient lookup during solving.
        _constraint_mapping (Dict[str, Constraint]): Mapping from OptiX constraint UUIDs to
                                                     OR-Tools constraint objects for tracking
                                                     and solution analysis purposes.
        _constraint_expr_mapping (Dict[str, LinearExpr]): Mapping from constraint UUIDs to
                                                          their mathematical expressions for
                                                          solution value calculation.
                                                          
    Type Support:
        - **Boolean Variables**: Automatically detected from 0-1 bounds, mapped to BoolVar
        - **Integer Variables**: Bounded integer variables with custom ranges, mapped to IntVar
        - **Linear Expressions**: Sum of variables with integer or float coefficients
        - **Special Constraints**: Non-linear relationships handled through CP-SAT primitives
        
    Example:
        Comprehensive solver setup and configuration:
        
        .. code-block:: python
        
            # Create solver with advanced configuration
            solver = OXORToolsSolverInterface(
                equalizeDenominators=True,  # Handle fractional coefficients
                solutionCount=10,           # Find up to 10 solutions
                maxTime=1800               # 30-minute time limit
            )
            
            # Setup problem
            solver.create_variables(problem)
            solver.create_constraints(problem)
            solver.create_special_constraints(problem)
            
            if isinstance(problem, OXLPProblem):
                solver.create_objective(problem)
            
            # Solve and analyze
            status = solver.solve(problem)
            
            if status == OXSolutionStatus.OPTIMAL:
                for i, solution in enumerate(solver):
                    print(f"Solution {i+1}: {solution.decision_variable_values}")
                    print(f"Objective: {solution.objective_function_value}")
                    
            # Access solver statistics
            logs = solver.get_solver_logs()
            
    Warning:
        OR-Tools CP-SAT requires integer coefficients for all constraints and objectives.
        When using float coefficients, the equalizeDenominators parameter must be enabled
        to perform automatic conversion, or an OXception will be raised during constraint
        creation.
        
    Note:
        This implementation is optimized for discrete optimization problems. For continuous
        optimization or large-scale linear programming, consider using the Gurobi solver
        interface which may provide better performance for those problem types.
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
            self._var_mapping[var.id] = self._model.new_int_var(lbound, ubound, var.name)

    def _create_single_constraint(self, constraint: OXConstraint):
        """Create a single constraint in the OR-Tools model.
        
        Args:
            constraint (OXConstraint): The constraint to create.
            
        Raises:
            OXception: If the constraint contains unsupported elements or float weights
                      without denominator equalization enabled.
        """
        weights = constraint.expression.weights
        rhs = constraint.rhs
        if any(isinstance(weight, float) for weight in weights) or isinstance(rhs, float) or any(
                isinstance(weight, Fraction) for weight in weights) or isinstance(rhs, Fraction):
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
                                self._problem.constraints[constraint_id].relational_operator,
                                self._problem.constraints[constraint_id].rhs)
                if constraint_id in self._problem.constraints else (
                    self.value(self._solver._constraint_expr_mapping[constraint_id]),
                    self._problem.goal_constraints[constraint_id].relational_operator,
                    self._problem.goal_constraints[constraint_id].rhs
                )
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

        input_constraint = prb.constraints[input_constraint_id]
        true_constraint = prb.constraints[true_constraint_id]
        false_constraint = prb.constraints[false_constraint_id]
        input_reversed = input_constraint.reverse()

        input_expression = self.__create_constraint_expression(input_constraint)
        input_reversed_expression = self.__create_constraint_expression(input_reversed)
        true_expression = self.__create_constraint_expression(true_constraint)
        false_expression = self.__create_constraint_expression(false_constraint)

        self._model.add(input_expression).only_enforce_if(indicator_variable)
        self._model.add(input_reversed_expression).only_enforce_if(indicator_variable.Not())
        self._model.add(true_expression).only_enforce_if(indicator_variable)
        self._model.add(false_expression).only_enforce_if(indicator_variable.Not())
