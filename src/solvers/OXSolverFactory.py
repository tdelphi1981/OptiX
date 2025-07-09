from base import OXception
from problem.OXProblem import OXCSPProblem, OXLPProblem
from solvers.ortools.OXORToolsSolverInterface import OXORToolsSolverInterface

_available_solvers = {
    'ORTools': OXORToolsSolverInterface
}


def solve(problem: OXCSPProblem, solver: str, **kwargs):
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
