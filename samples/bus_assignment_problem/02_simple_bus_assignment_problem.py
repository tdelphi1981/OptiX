"""
Advanced Bus Assignment Problem Example
======================================

This example demonstrates enhanced OptiX framework capabilities through an improved version of the
basic bus assignment problem. Building on the foundation of 01_simple_bus_assignment_problem.py,
this implementation showcases advanced OptiX features for better problem modeling, constraint
management, and solution interpretation.

Improvements Over Basic Version:
    This advanced example extends the basic bus assignment problem with several key enhancements
    that demonstrate additional OptiX capabilities:
    
    - **Named Constraints**: All constraints include descriptive names for better solution analysis
    - **Dual Constraint Types**: Both demand satisfaction AND fleet capacity constraints
    - **Enhanced Data Modeling**: Added ordering fields for improved identification and naming
    - **Advanced Variable Naming**: Uses dataclass field values in variable name templates
    - **Fleet Capacity Modeling**: Realistic operational limits based on available buses
    - **Improved Solution Reporting**: More detailed constraint information in output

OptiX Features Demonstrated:
    - **Named Constraint Creation**: Using the `name` parameter in `create_constraint()`
    - **Multiple Constraint Types**: Different constraint formulations in the same problem
    - **Field-Based Variable Naming**: Template variables using dataclass field values
    - **Complex Weight Calculations**: Different weight functions for different constraint types
    - **Enhanced Data Relationships**: Order fields for better object identification

Problem Structure Comparison:
    **Basic Version (01)**:
    - Decision Variables: trips[bus_group][line]
    - Constraints: Demand satisfaction only (one per line)
    - Objective: Minimize weighted trips (weight = 1.5)
    - Variable naming: Uses object IDs
    
    **Advanced Version (02)**:
    - Decision Variables: trips[bus_group][line] (same structure)
    - Constraints: Demand satisfaction + Fleet capacity (lines + groups constraints)
    - Objective: Minimize total trips (weight = 1.0, no artificial weighting)
    - Variable naming: Uses order fields for human-readable names
    - Additional: All constraints have descriptive names

Key Enhancements Explained:
    1. **Order Fields**: Both BusGroup and Line classes include `order` fields for better identification
    2. **Named Constraints**: Each constraint includes a descriptive name explaining its purpose
    3. **Fleet Constraints**: New constraint type limiting trips per bus group to operational capacity
    4. **Enhanced Naming**: Variable names use order numbers instead of UUIDs for readability
    5. **Dual Validation**: Assertions check both demand and fleet constraint counts

Mathematical Formulation:
    - Minimize: Σ(trips[i,j]) for all bus groups i and lines j
    - Subject to: 
        * Demand: Σ(capacity[i] × trips[i,j]) ≥ demand[j] for each line j
        * Fleet: Σ(trips[i,j]) ≤ 2 × fleet_size[i] for each bus group i
    - Bounds: 0 ≤ trips[i,j] ≤ 20

Usage:
    Run directly to see advanced OptiX features in action:
    
    ```bash
    python 02_simple_bus_assignment_problem.py
    ```
    
    Output includes named constraints and enhanced solution reporting.

Learning Objectives:
    - Understanding named constraints for better solution interpretation
    - Multiple constraint types in the same optimization problem
    - Advanced variable naming with dataclass field values
    - Fleet capacity modeling in transportation problems
    - Enhanced problem validation with multiple constraint sets
"""
import pprint
import random
from dataclasses import dataclass

from constraints.OXConstraint import RelationalOperators
from data.OXData import OXData
from problem.OXProblem import OXLPProblem, ObjectiveType
from solvers.OXSolverFactory import solve, solve_all_scenarios


@dataclass
class BusGroup(OXData):
    """Enhanced bus group model with ordering for improved identification.
    
    This enhanced version of BusGroup adds ordering capability for better variable naming
    and constraint identification. The order field enables human-readable variable names
    and more descriptive constraint names in the optimization output.
    
    Improvements over basic version:
        - Added order field for sequential identification
        - Enables enhanced variable naming templates using {busgroup_order}
        - Used in fleet capacity constraints (new constraint type)
        - Supports more readable solution output
    
    Attributes:
        capacity (int): Passenger capacity per bus. Used as weight coefficient
                       in demand satisfaction constraints.
        number_of_busses (int): Fleet size available in this group. Used to
                               calculate fleet capacity constraint limits (number_of_busses × 2).
        order (int): Sequential ordering index for identification and naming.
                    Used in variable name templates and constraint descriptions.
    """
    capacity: int = 0
    number_of_busses: int = 0
    order: int = 0


@dataclass
class Line(OXData):
    """Enhanced transit line model with ordering for improved identification.
    
    This enhanced version of Line adds ordering capability for better variable naming
    and constraint identification. The order field enables human-readable variable names
    and more descriptive constraint names in the optimization output.
    
    Improvements over basic version:
        - Added order field for sequential identification  
        - Enables enhanced variable naming templates using {line_order}
        - Used in named demand satisfaction constraints
        - Supports more readable solution output
    
    Attributes:
        daily_passenger_demand (int): Number of passengers requiring transportation
                                     per day. Used as right-hand side value in
                                     demand satisfaction constraints.
        order (int): Sequential ordering index for identification and naming.
                    Used in variable name templates and constraint descriptions.
    """
    daily_passenger_demand: int = 0
    order: int = 0


def main():
    """Demonstrates advanced OptiX capabilities through enhanced bus assignment problem.
    
    This improved version showcases additional OptiX features compared to the basic example:
    
    Key Improvements Demonstrated:
        1. **Named Constraints**: All constraints include descriptive names using the `name` parameter
        2. **Dual Constraint Types**: Both demand satisfaction AND fleet capacity constraints
        3. **Enhanced Variable Naming**: Uses order fields in variable name templates
        4. **Fleet Capacity Modeling**: Realistic operational limits (2 trips per bus maximum)
        5. **Improved Data Organization**: Order fields for better identification
    
    Advanced OptiX Features Showcased:
        - Named constraint creation for better solution interpretation
        - Multiple constraint types with different weight calculation functions
        - Field-based variable naming using dataclass attributes in templates
        - Complex constraint formulations (fleet capacity based on available buses)
        - Enhanced problem validation with multiple constraint set assertions
    
    Problem Enhancements vs Basic Version:
        - **More Constraints**: Lines + Groups constraints instead of just Lines
        - **Better Naming**: Order-based variable names instead of UUID-based
        - **Fleet Realism**: Cannot exceed available bus capacity (2 trips per bus)
        - **Solution Clarity**: Named constraints improve output readability
        - **Weight Simplification**: Uses weight=1.0 instead of artificial 1.5 weighting
    
    Constraint Structure:
        1. **Demand Satisfaction** (one per line): 
           Σ(capacity[i] × trips[i,j]) ≥ demand[j] for line j
        2. **Fleet Capacity** (one per bus group):
           Σ(trips[i,j]) ≤ 2 × fleet_size[i] for bus group i
    """
    bap = OXLPProblem()

    number_of_groups = random.randint(3, 8)
    number_of_lines = random.randint(5, 10)

    for i in range(number_of_groups):
        group = BusGroup()
        group.capacity = random.randint(25, 50)
        group.number_of_busses = random.randint(5, 10)
        group.order = i
        group.create_scenario("epidemic", capacity=random.randint(12, 20))
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
    status, solver = solve(bap, 'ORTools', use_continuous=False, equalizeDenominators=True)

    print(f"Status: {status}")

    for solution in solver:
        solution.print_solution_for(bap)

    results = solve_all_scenarios(bap, 'ORTools', use_continuous=False, equalizeDenominators=True)

    for scenario in results:
        print(f"=== Scenario: {scenario} ===")
        print(f"=== Status: {results[scenario]['status']} ===")
        print(f"=== Solution: ===")
        if results[scenario]['solution']:
            results[scenario]['solution'].print_solution_for(bap)
        else:
            print("  No solution found.")


if __name__ == '__main__':
    main()
