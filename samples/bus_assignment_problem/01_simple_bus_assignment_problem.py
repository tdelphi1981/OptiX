"""
Simple Bus Assignment Problem Example
====================================

This example demonstrates key OptiX framework capabilities through a straightforward bus assignment
optimization problem. The implementation showcases how to model resource allocation problems using
OptiX's data-driven approach, automated variable generation, and constraint formulation features.

Problem Overview:
    A transit agency needs to assign different bus groups to various lines to meet passenger demand
    while minimizing the total number of trips. This is a classic assignment problem that demonstrates:
    
    - **Cross-product variable generation** between two data types (BusGroup × Line)
    - **Database-driven problem construction** using OptiX's OXData framework  
    - **Capacity constraint modeling** with automated weight calculation
    - **Random problem instance generation** for testing and demonstration

OptiX Features Demonstrated:
    - **Data Modeling**: Custom OXData classes with structured attributes
    - **Database Integration**: Automatic object management and relationship tracking
    - **Variable Generation**: `create_variables_from_db()` with cross-product relationships
    - **Constraint Creation**: `create_constraint()` with search functions and weight calculations
    - **Objective Functions**: `create_objective_function()` with uniform weighting
    - **Solver Integration**: Unified solving interface with Gurobi backend

Problem Structure:
    **Decision Variables**: Number of trips each bus group makes on each line
    **Constraints**: Each line must receive enough bus capacity to meet passenger demand  
    **Objective**: Minimize total weighted trips (weight = 1.5 per trip)
    
    Mathematical formulation:
    - Minimize: Σ(1.5 × trips[i,j]) for all bus groups i and lines j
    - Subject to: Σ(capacity[i] × trips[i,j]) ≥ demand[j] for each line j
    - Bounds: 0 ≤ trips[i,j] ≤ 20

Random Problem Generation:
    - **Bus Groups**: 3-8 groups with capacity 25-50 passengers, fleet size 5-10 buses
    - **Lines**: 5-10 lines with demand 200-500 passengers per day
    - **Problem Size**: 15-80 variables, 5-10 constraints typically

Usage:
    Run directly to see OptiX solve a randomly generated instance:
    
    ```bash
    python 01_simple_bus_assignment_problem.py
    ```
    
    Output includes optimization status, trip assignments, and solution validation.

Learning Objectives:
    - Understanding OptiX data modeling with OXData inheritance
    - Cross-product variable generation between multiple data types
    - Constraint formulation with search functions and weight calculations
    - Integration of random problem generation with OptiX workflow
    - Solver configuration and solution interpretation
"""

import random
from dataclasses import dataclass

from constraints.OXConstraint import RelationalOperators
from data.OXData import OXData
from problem.OXProblem import OXLPProblem, ObjectiveType
from solvers.OXSolverFactory import solve


@dataclass
class BusGroup(OXData):
    """Represents a group of buses with identical characteristics.
    
    This class demonstrates OptiX data modeling using OXData inheritance. Each BusGroup
    will participate in cross-product variable generation with Line objects to create
    assignment variables.
    
    Attributes:
        capacity (int): Passenger capacity per bus in this group. Used as weight 
                       coefficient in demand satisfaction constraints.
        number_of_busses (int): Number of buses available in this group. Currently
                               for reference only, not used in constraints.
    """
    capacity: int = 0
    number_of_busses: int = 0


@dataclass
class Line(OXData):
    """Represents a transit line with passenger demand.
    
    This class demonstrates OptiX constraint generation where each Line object
    creates a demand satisfaction constraint ensuring adequate bus capacity
    is assigned to meet passenger needs.
    
    Attributes:
        daily_passenger_demand (int): Number of passengers that must be transported
                                     on this line per day. Used as the right-hand side
                                     value in the capacity constraint.
    """
    daily_passenger_demand: int = 0


def main():
    """Demonstrates OptiX framework capabilities through a simple bus assignment problem.
    
    This function shows how to:
    1. Create random problem data (bus groups and lines)
    2. Use cross-product variable generation between two data types
    3. Formulate constraints with search functions and weight calculations
    4. Define an objective function and solve with Gurobi
    5. Display and validate the solution
    
    The problem assigns bus groups to lines to meet passenger demand while minimizing trips.
    Each bus group has a capacity, and each line has a daily passenger demand that must be satisfied.
    
    OptiX Features Showcased:
        - OXData inheritance for custom data classes
        - Database-driven variable creation with create_variables_from_db()
        - Constraint formulation with lambda functions for search and weight calculation
        - Automated problem validation with assertions
        - Unified solver interface with detailed solution output
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

    status, solver = solve(bap, 'Gurobi', use_continuous=False, equalizeDenominators=True)

    print(f"Status: {status}")

    for solution in solver:
        solution.print_solution_for(bap)


if __name__ == '__main__':
    main()
