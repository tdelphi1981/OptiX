"""Advanced Bus Assignment Problem Example.

This example demonstrates a more complex bus assignment optimization problem 
with enhanced naming and constraint management. It includes:
- Ordered bus groups and lines for better identification
- Named constraints for improved solution readability
- Capacity constraints for both demand satisfaction and fleet limitations
- Enhanced variable naming using dataclass field values

The problem involves:
- Bus groups with specific capacities, fleet sizes, and ordering
- Lines with daily passenger demands and ordering
- Demand satisfaction constraints (must meet passenger demand)
- Fleet capacity constraints (cannot exceed available buses)
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
    """Represents a group of buses with specific capacity, fleet size, and order.
    
    Attributes:
        capacity (int): The passenger capacity of each bus in this group.
        number_of_busses (int): The number of buses available in this group.
        order (int): The ordering index of this bus group for identification.
    """
    capacity: int = 0
    number_of_busses: int = 0
    order: int = 0


@dataclass
class Line(OXData):
    """Represents a transit line with passenger demand and ordering.
    
    Attributes:
        daily_passenger_demand (int): The number of passengers that need to be
            transported on this line per day.
        order (int): The ordering index of this line for identification.
    """
    daily_passenger_demand: int = 0
    order: int = 0


def main():
    """Solve an advanced bus assignment problem with named constraints.
    
    This function creates a linear programming problem to assign bus groups
    to lines optimally, with enhanced constraint naming and fleet capacity
    limitations.
    
    The problem formulation:
    - Decision variables: Number of trips for each bus group on each line
    - Demand constraints: Each line must have enough capacity to handle its demand
    - Fleet constraints: Each bus group cannot exceed its available capacity
    - Objective: Minimize total number of trips
    
    Features demonstrated:
    - Named constraints for better solution interpretation
    - Enhanced variable naming using dataclass field values
    - Dual constraint types (demand satisfaction and fleet capacity)
    - Improved solution reporting with constraint names
    """
    bap = OXLPProblem()

    number_of_groups = random.randint(3, 8)
    number_of_lines = random.randint(5, 10)

    for i in range(number_of_groups):
        group = BusGroup()
        group.capacity = random.randint(25, 50)
        group.number_of_busses = random.randint(5, 10)
        group.order = i
        bap.db.add_object(group)

    for i in range(number_of_lines):
        line = Line()
        line.daily_passenger_demand = random.randint(200, 500)
        line.order = i
        bap.db.add_object(line)

    bap.create_variables_from_db(
        BusGroup, Line,
        var_name_template="Number of Trips of Bus Group[{busgroup_order}] for Line[{line_order}]",
        var_description_template="Number of Trips of {line_order} of Bus Group {busgroup_order}",
        lower_bound=0,
        upper_bound=20
    )

    assert len(bap.variables) == number_of_groups * number_of_lines

    for line in bap.db.search_by_function(lambda var: isinstance(var, Line)):
        bap.create_constraint(
            variable_search_function=lambda var: var.related_data["line"] == line.id,
            weight_calculation_function=lambda var, prb: prb.db[prb.variables[var].related_data["busgroup"]].capacity,
            operator=RelationalOperators.GREATER_THAN_EQUAL,
            value=line.daily_passenger_demand,
            name=f"Perform number of trips that handles at least {line.daily_passenger_demand} passengers of Line {line.order}"
        )

    for busgroup in bap.db.search_by_function(lambda data: isinstance(data, BusGroup)):
        bap.create_constraint(
            variable_search_function=lambda var: var.related_data["busgroup"] == busgroup.id,
            weight_calculation_function=lambda var, prb: 1.0,
            operator=RelationalOperators.LESS_THAN_EQUAL,
            value=busgroup.number_of_busses * 2,
            name=f"Number of trips does not exceed 2 times per bus ({busgroup.number_of_busses}) of Bus Group {busgroup.order}"
        )

    assert len(bap.constraints) == (number_of_lines + number_of_groups)

    bap.create_objective_function(
        variable_search_function=lambda var: True,
        weight_calculation_function=lambda var, prb: 1.0,
    )

    status, solver = solve(bap, 'Gurobi', use_continuous=False, equalizeDenominators=True)

    print(f"Status: {status}")

    for solution in solver:
        solution.print_solution_for(bap)


if __name__ == '__main__':
    main()
