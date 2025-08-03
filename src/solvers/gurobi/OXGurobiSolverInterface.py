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
from constraints import OXConstraint, OXGoalConstraint, RelationalOperators
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
        pass

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
