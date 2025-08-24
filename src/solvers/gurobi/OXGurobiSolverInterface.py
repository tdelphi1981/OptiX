"""
Gurobi Solver Interface Module
==============================

This module provides the Gurobi solver interface implementation for the OptiX mathematical
optimization framework. It integrates Gurobi's commercial optimization solver with OptiX's
unified solver interface, enabling high-performance optimization for linear programming (LP),
goal programming (GP), and constraint satisfaction problems (CSP).

The module implements Gurobi-specific solver operations including variable creation,
constraint handling, objective function setup, and solution extraction. It supports both
continuous and integer optimization modes with comprehensive parameter configuration.

Key Features:
    - **Gurobi Integration**: Direct interface to Gurobi's optimization engine
    - **Variable Type Support**: Binary, continuous, and integer variables with bounds
    - **Constraint Translation**: Automatic conversion of OptiX constraints to Gurobi format
    - **Goal Programming**: Support for deviation variables and goal constraints
    - **Flexible Parameters**: Configurable optimization parameters and settings
    - **Solution Extraction**: Comprehensive solution status and value retrieval

Supported Problem Types:
    - **Linear Programming (LP)**: Standard optimization with linear constraints
    - **Goal Programming (GP)**: Multi-objective optimization with priority levels
    - **Constraint Satisfaction (CSP)**: Feasibility problems without optimization

Usage:
    The solver interface is typically used through the OptiX solver factory:

    .. code-block:: python

        from solvers.OXSolverFactory import solve
        from problem import OXLPProblem
        
        # Create and configure your problem
        problem = OXLPProblem()
        # ... add variables, constraints, objective ...
        
        # Solve using Gurobi
        status = solve(problem, 'Gurobi')

Module Dependencies:
    - gurobipy: Gurobi Python API for optimization operations
    - base: OptiX base classes and exception handling
    - constraints: OptiX constraint definitions and operators
    - problem: OptiX problem type definitions
    - solvers.OXSolverInterface: Base solver interface
    - variables: OptiX variable definitions
"""

import math
import sys
from fractions import Fraction
from typing import Optional

from base import OXception
from constraints import OXConstraint, OXGoalConstraint, RelationalOperators, OXMultiplicativeEqualityConstraint, \
    OXDivisionEqualityConstraint, OXModuloEqualityConstraint, OXConditionalConstraint, OXSummationEqualityConstraint
from problem import OXCSPProblem, OXLPProblem, OXGPProblem, ObjectiveType
from solvers.OXSolverInterface import OXSolverInterface, OXSolutionStatus
from solvers.OXSolverInterface import LogsType, OXSolverSolution
from variables import OXVariable

import gurobipy as gp
from gurobipy import GRB


class OXGurobiSolverInterface(OXSolverInterface):
    """
    Gurobi-specific implementation of the OptiX solver interface.
    
    This class provides a concrete implementation of the OXSolverInterface for the Gurobi
    optimization solver. It handles the translation between OptiX's abstract problem
    representation and Gurobi's specific API calls, variable types, and constraint formats.
    
    The interface supports both continuous and integer optimization modes, with automatic
    handling of variable bounds, constraint operators, and objective function setup.
    Special support is provided for goal programming with positive and negative deviation
    variables.
    
    Attributes:
        _model (gp.Model): The underlying Gurobi model instance
        _var_mapping (dict): Maps OptiX variable IDs to Gurobi variable objects
        _constraint_mapping (dict): Maps OptiX constraint IDs to Gurobi constraint objects
        _constraint_expr_mapping (dict): Maps constraint IDs to their Gurobi expressions
        
    Parameters:
        use_continuous (bool): Whether to use continuous variables instead of integers
        equalizeDenominators (bool): Whether to normalize fractional coefficients
        
    Example:
        Direct usage of the Gurobi interface:
        
        .. code-block:: python
        
            solver = OXGurobiSolverInterface(use_continuous=True)
            
            # The solver is typically used through the factory pattern
            # but can be used directly for advanced Gurobi-specific features
            
            solver.create_variables(problem.variables)
            solver.create_constraints(problem.constraints)
            solver.create_objective(problem)
            
            status = solver.solve(problem)
            if status == OXSolutionStatus.OPTIMAL:
                solution = solver.get_solutions()[0]
    """

    def __init__(self, **kwargs):
        """
        Initialize the Gurobi solver interface with configuration parameters.
        
        Creates a new Gurobi model instance and initializes internal mappings for
        variables, constraints, and constraint expressions. Configuration parameters
        are passed to the parent OXSolverInterface class.
        
        Args:
            **kwargs: Configuration parameters including:
                use_continuous (bool): Use continuous variables instead of integers
                equalizeDenominators (bool): Normalize fractional coefficients
                
        Note:
            The Gurobi model is created with the name "OptiX Model" and uses
            default Gurobi settings unless modified through solver parameters.
        """
        super().__init__(**kwargs)

        self._model = gp.Model("OptiX Model")

        self._var_mapping = {}
        self._constraint_mapping = {}
        self._constraint_expr_mapping = {}
        self._helper_variables = []

    def _create_helper_variable(self, name: str = "", lb: float | int = 0, ub: float | int = 1,
                                continuous: bool = False, integer: bool = False, binary: bool = False):
        """
        Create a single Gurobi variable from scratch to help with special constraints.

        Creates a new helper variable with the specified bounds and variable types. This
        function aims to simplify the creation of helper variables for special constraint
        creation. It also stores the variable in _helper_variables array for later use.
        It is not intended for use in general optimization problems.

        Args:
            name (str): Variable name (internal use only) (default: "")
            lb (float | int): Lower bound for the variable (default: 0)
            ub (float | int): Upper bound for the variable (default: 1)
            continuous (bool): Whether to create a continuous variable (default: False)
            integer (bool): Whether to create an integer variable (default: False)
            binary (bool): Whether to create a binary variable (default: False)

        Raises:
            OXception: If more than one variable type is specified

        Returns:
            The created Gurobi variable object

        Note:
            - Binary variables: Created when binary parameter is True
            - Continuous variables: Created when continuous parameter is True
            - Integer variables: Created when integer parameter is True
            - Only creation of one type of variable is supported at a time
            - Infinite bounds are converted to system maximum values
        """
        requested_types = [binary, continuous, integer]
        if sum(requested_types) > 1:
            raise OXception("Only one variable type can be specified at a time.")
        if math.isinf(ub):
            ub = sys.maxsize
        if math.isinf(lb):
            lb = -sys.maxsize
        if any(requested_types):
            var = None
            if continuous:
                var = self._model.addVar(vtype=GRB.CONTINUOUS, lb=lb, ub=ub, name=name)
            elif integer:
                var = self._model.addVar(vtype=GRB.INTEGER, lb=lb, ub=ub, name=name)
            elif binary:
                var = self._model.addVar(vtype=GRB.BINARY, name=name)
            self._helper_variables.append(var)
            return var
        raise OXception("No Variable type specified.")

    def _create_single_variable(self, var: OXVariable):
        """
        Create a single Gurobi variable from an OptiX variable definition.
        
        Translates an OptiX variable to the appropriate Gurobi variable type based on
        bounds and solver configuration. Handles binary, continuous, and integer
        variable types with proper bound conversion.
        
        Args:
            var (OXVariable): OptiX variable to convert to Gurobi format
            
        Note:
            - Binary variables: Created when bounds are [0,1]
            - Continuous variables: Created when use_continuous parameter is True
            - Integer variables: Default for bounded variables in integer mode
            - Infinite bounds are converted to system maximum values
        """
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
        """
        Create a Gurobi constraint for continuous optimization mode.
        
        Converts an OptiX constraint to Gurobi format using continuous variables
        and expressions. Handles all relational operators and special goal
        constraint processing with deviation variables.
        
        Args:
            constraint (OXConstraint): OptiX constraint to convert
            
        Raises:
            OXception: If the relational operator is not supported
            
        Note:
            Goal constraints include positive and negative deviation variables
            that are automatically handled during constraint creation.
        """
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
        """
        Create a Gurobi constraint for integer optimization mode.
        
        Converts an OptiX constraint to Gurobi format using integer variables.
        Handles fractional coefficients through denominator equalization if
        configured, otherwise raises an error for unsupported float weights.
        
        Args:
            constraint (OXConstraint): OptiX constraint to convert
            
        Raises:
            OXception: If float weights are used without proper configuration
            OXception: If the relational operator is not supported
            
        Note:
            When equalizeDenominators is enabled, fractional coefficients are
            converted to integers by multiplying by appropriate denominators.
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
        """
        Create a single Gurobi constraint using the appropriate method.
        
        Delegates constraint creation to either continuous or integer constraint
        creation based on the solver's use_continuous parameter setting.
        
        Args:
            constraint (OXConstraint): OptiX constraint to convert to Gurobi format
        """
        if self._parameters["use_continuous"]:
            self._create_single_continuous_constraint(constraint)
        else:
            self._create_single_integer_constraint(constraint)

    def create_special_constraints(self, prb: OXCSPProblem):
        """
        Create special non-linear constraints for constraint satisfaction problems.
        
        This method is intended for handling special constraints that cannot be
        expressed as standard linear constraints (e.g., multiplication, division,
        modulo, conditional constraints). Currently not implemented for Gurobi.
        
        Args:
            prb (OXCSPProblem): Constraint satisfaction problem with special constraints
            
        Note:
            Implementation is pending for advanced constraint types that require
            special handling in the Gurobi solver.
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
        """
        Create and configure the objective function in the Gurobi model.
        
        Translates the OptiX objective function to Gurobi format, handling both
        minimization and maximization objectives. Supports continuous and integer
        coefficient modes with automatic goal programming objective creation.
        
        Args:
            prb (OXLPProblem): Problem instance with objective function definition
            
        Raises:
            OXception: If no objective function is specified
            OXException: If float weights are used in integer mode without proper configuration
            
        Note:
            - For goal programming problems, the objective is automatically created
            - Fractional coefficients require equalizeDenominators parameter in integer mode
            - Objective type (minimize/maximize) is preserved from the problem definition
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
        """
        Solve the optimization problem using Gurobi solver.
        
        Executes the Gurobi optimization process and extracts solution information
        including variable values, constraint evaluations, and objective function value.
        Creates a comprehensive solution object for optimal solutions.
        
        Args:
            prb (OXCSPProblem): Problem instance to solve
            
        Returns:
            OXSolutionStatus: Status of the optimization process:
                - OPTIMAL: Solution found successfully
                - INFEASIBLE: No feasible solution exists
                - UNBOUNDED: Problem is unbounded
                - ERROR: Solver encountered an error or indeterminate status
                
        Note:
            - Solution details are stored in the _solutions list for optimal solutions
            - Constraint values include left-hand side, operator, and right-hand side
            - Objective function value is included for linear programming problems
        """
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
        """
        Retrieve solver execution logs and diagnostic information.
        
        Returns detailed logs from the Gurobi solver execution including
        performance metrics, iteration details, and diagnostic messages.
        Currently not implemented.
        
        Returns:
            Optional[LogsType]: Solver logs if available, None otherwise
            
        Note:
            Implementation is pending for comprehensive log extraction
            from the Gurobi solver instance.
        """
        pass

    def __create_multiplicative_equality_constraint(self, constraint: OXMultiplicativeEqualityConstraint):
        """Create a multiplicative equality constraint.

        Args:
            constraint (OXMultiplicativeEqualityConstraint): The constraint to create.
        """
        out_var = self._var_mapping[constraint.output_variable]

        input_vars = [self._var_mapping[v] for v in constraint.input_variables]

        gurobi_version = gp.gurobi().version()

        if isinstance(gurobi_version, tuple) and gurobi_version[0] >= 12:
            expr = input_vars[0]
            for var in input_vars[1:]:
                expr = expr * var
            self._model.addGenConstrNL(out_var, expr)
        else:
            if len(input_vars) == 2:
                self._model.addGenConstrNL(out_var, input_vars[0] * input_vars[1])
            else:
                iterator = iter(input_vars)
                a = next(iterator)
                for b in iterator:
                    helper_var = self._create_helper_variable(lb=0, ub=math.inf, continuous=True)
                    self._model.addGenConstrNL(helper_var, a * b)
                    a = helper_var
                self._model.addGenConstrNL(out_var, a)

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
            self._model.addConstr(in_var == out_var * denominator)
        elif isinstance(constraint, OXModuloEqualityConstraint):
            helper_var = self._create_helper_variable(lb=0, ub=math.inf, integer=True)
            self._model.addConstr(in_var == helper_var * denominator + out_var)
            self._model.addConstr(out_var < denominator)
            self._model.addConstr(out_var >= 0)
        else:
            raise OXception(f"Unsupported special constraint type: {type(constraint)}")

    def __create_summation_equality_constraint(self, constraint: OXSummationEqualityConstraint):
        """Create a summation equality constraint.

        Args:
            constraint (OXSummationEqualityConstraint): The constraint to create.
        """
        out_var = self._var_mapping[constraint.output_variable]
        input_vars = [self._var_mapping[v] for v in constraint.input_variables]

        self._model.addConstr(out_var == sum(input_vars))

    def __create_constraint_expression(self, constraint: OXConstraint, M: float = 0.0, eps: float = 0.0,
                                       indicator_var=None, reverse_indicator_var=False):
        """Create a constraint expression for Gurobi.

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
        if any(isinstance(weight, float) or isinstance(weight, Fraction) for weight in weights) or isinstance(
                rhs, float) or isinstance(rhs, Fraction):
            if "equalizeDenominators" in self._parameters and self._parameters["equalizeDenominators"]:
                weights = [round(constraint.rhs_denominator * weight) for weight in
                           constraint.expression.integer_weights]
                rhs = round(constraint.expression.integer_denominator * constraint.rhs_numerator)
            else:
                weights = constraint.expression.weights
                rhs = constraint.rhs
        if indicator_var is not None:
            ind_expr = eps
            if reverse_indicator_var:
                ind_expr += M * (1 - indicator_var)
            else:
                ind_expr += M * indicator_var
            if constraint.relational_operator == RelationalOperators.GREATER_THAN:
                return sum(
                    self._var_mapping[v] * w for v, w in zip(constraint.expression.variables, weights)) + ind_expr > rhs
            elif constraint.relational_operator == RelationalOperators.GREATER_THAN_EQUAL:
                return sum(self._var_mapping[v] * w for v, w in
                           zip(constraint.expression.variables, weights)) + ind_expr >= rhs
            elif constraint.relational_operator == RelationalOperators.EQUAL:
                return sum(self._var_mapping[v] * w for v, w in
                           zip(constraint.expression.variables, weights)) + ind_expr == rhs
            elif constraint.relational_operator == RelationalOperators.LESS_THAN_EQUAL:
                return sum(self._var_mapping[v] * w for v, w in
                           zip(constraint.expression.variables, weights)) + ind_expr <= rhs
            elif constraint.relational_operator == RelationalOperators.LESS_THAN:
                return sum(
                    self._var_mapping[v] * w for v, w in zip(constraint.expression.variables, weights)) + ind_expr < rhs
            else:
                raise OXception(f"Unsupported relational operator: {constraint.relational_operator}")
        else:
            if constraint.relational_operator == RelationalOperators.GREATER_THAN:
                return sum(self._var_mapping[v] * w for v, w in
                           zip(constraint.expression.variables, weights)) > rhs
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

        M = sum(prb.variables[var_id].upper_bound for var_id in input_constraint.expression.variables) + 1
        eps = 1e-4

        input_expression = self.__create_constraint_expression(input_constraint, -M, eps, indicator_variable, True)
        input_reversed_expression = self.__create_constraint_expression(input_reversed, M, 0, indicator_variable)
        true_expression = self.__create_constraint_expression(true_constraint)
        false_expression = self.__create_constraint_expression(false_constraint)

        self._model.add(input_expression)
        self._model.add(input_reversed_expression)
        self._model.add((indicator_variable == 1) >> true_expression)
        self._model.add((indicator_variable == 0) >> false_expression)
