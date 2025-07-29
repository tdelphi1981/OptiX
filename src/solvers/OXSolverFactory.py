"""Solver factory module for OptiX optimization framework.

This module provides a factory interface for creating and managing different solver instances.
It acts as a centralized registry for available solvers and provides a unified solve function.
"""

from base import OXception
from problem.OXProblem import OXCSPProblem, OXLPProblem
from solvers.gurobi.OXGurobiSolverInterface import OXGurobiSolverInterface
from solvers.ortools.OXORToolsSolverInterface import OXORToolsSolverInterface

_available_solvers = {
    'ORTools': OXORToolsSolverInterface,
    'Gurobi': OXGurobiSolverInterface
}


def solve(problem: OXCSPProblem, solver: str, **kwargs):
    """Solve an optimization problem using the specified solver.
    
    This function provides a unified interface for solving optimization problems
    across different solvers. It handles the complete solving workflow including
    variable creation, constraint setup, and objective function configuration.
    
    Args:
        problem (OXCSPProblem): The optimization problem to solve.
        solver (str): The name of the solver to use. Must be a key in _available_solvers.
        **kwargs: Additional keyword arguments passed to the solver constructor.
        
    Returns:
        tuple: A tuple containing:
            - status (OXSolutionStatus): The solution status returned by the solver.
            - solver_obj (OXSolverInterface): The solver instance used for solving.
            
    Raises:
        OXception: If the specified solver is not available.
        
    Example:
        >>> from problem.OXProblem import OXCSPProblem
        >>> problem = OXCSPProblem()
        >>> status, solver = solve(problem, 'ORTools')
    """
    if solver not in _available_solvers:
        raise OXception(f"Solver not available : {solver}")
    solver_obj = _available_solvers[solver](**kwargs)

    solver_obj.create_variable(problem)
    solver_obj.create_constraints(problem)
    solver_obj.create_special_constraints(problem)
    if isinstance(problem, OXLPProblem):
        solver_obj.create_objective(problem)

    status = solver_obj.solve(problem)

    return status, solver_obj
