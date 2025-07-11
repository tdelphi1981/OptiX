"""Simple Bus Assignment Problem Example.

This example demonstrates a basic bus assignment optimization problem where
different bus groups with varying capacities are assigned to different lines
to meet passenger demands while minimizing the total number of trips.

The problem involves:
- Bus groups with specific capacities and fleet sizes
- Lines with daily passenger demands
- Constraints to ensure passenger demands are met
- Objective to minimize the total number of trips
"""

import random
from dataclasses import dataclass

from constraints.OXConstraint import RelationalOperators
from data.OXData import OXData
from problem.OXProblem import OXLPProblem, ObjectiveType
from solvers.OXSolverFactory import solve


@dataclass
class BusGroup(OXData):
    """Represents a group of buses with specific capacity and fleet size.
    
    Attributes:
        capacity (int): The passenger capacity of each bus in this group.
        number_of_busses (int): The number of buses available in this group.
    """
    capacity: int = 0
    number_of_busses: int = 0


@dataclass
class Line(OXData):
    """Represents a transit line with passenger demand.
    
    Attributes:
        daily_passenger_demand (int): The number of passengers that need to be
            transported on this line per day.
    """
    daily_passenger_demand: int = 0


def main():
    """Solve a simple bus assignment problem.
    
    This function creates a linear programming problem to assign bus groups
    to lines optimally, ensuring all passenger demands are met while
    minimizing the total number of trips.
    
    The problem formulation:
    - Decision variables: Number of trips for each bus group on each line
    - Constraints: Each line must have enough capacity to handle its demand
    - Objective: Minimize total weighted trips (weight = 1.5 per trip)
    """
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
        var_name_template="Bus Group[{busgroup_id}]-Line[{line_id}]",
        var_description_template="Number of Trips of {line_id} of Bus Group {busgroup_id}",
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
        solution.print_solution_for(bap)


if __name__ == '__main__':
    main()
