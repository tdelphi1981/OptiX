import random

from constraints.OXConstraint import RelationalOperators
from data.OXData import OXData
from problem.OXProblem import OXLPProblem, ObjectiveType
from solvers.OXSolverFactory import solve


class BusGroup(OXData):
    capacity: int
    number_of_busses: int


class Line(OXData):
    daily_passenger_demand: int


def main():
    bap = OXLPProblem()

    number_of_groups = random.randint(3, 8)
    number_of_lines = random.randint(5, 10)

    for _ in range(number_of_groups):
        group = BusGroup()
        group.capacity = random.randint(25, 50)
        group.number_of_busses = random.randint(5, 10)
        bap.db.add_object(group)

    for _ in range(number_of_lines):
        line = Line()
        line.daily_passenger_demand = random.randint(200, 500)
        bap.db.add_object(line)

    bap.create_variables_from_db(
        BusGroup, Line,
        var_name_template="Bus Group[{busgroup}]-Line[{line}]",
        var_description_template="Number of Trips of {line} of Bus Group {busgroup}",
        lower_bound=0,
        upper_bound=20
    )

    assert len(bap.variables) == number_of_groups * number_of_lines

    for line in bap.db.search_by_function(lambda var: isinstance(var, Line)):
        bap.create_constraint(
            variable_search_function=lambda var: var.related_data["line"] == line.id,
            weight_calculation_function=lambda var, prb: prb.db[prb.variables[var].related_data["busgroup"]].capacity,
            operator=RelationalOperators.GREATER_THAN_EQUAL,
            value=line.daily_passenger_demand)

    assert len(bap.constraints) == number_of_lines

    bap.create_objective_function(
        variable_search_function=lambda var: True,
        weight_calculation_function=lambda var, prb: 1.5,
    )

    status, solver = solve(bap, 'ORTools', equalizeDenominators=True)

    print(f"Status: {status}")

    for solution in solver:
        print(solution)
        solution.print_solution_for(bap)


if __name__ == '__main__':
    main()
