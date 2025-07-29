from dataclasses import dataclass, field
from fractions import Fraction
from uuid import UUID

from constraints import RelationalOperators
from data import OXData
from problem import OXGPProblem, OXLPProblem, OXCSPProblem
from solvers import solve


@dataclass
class BusGroup(OXData):
    name: str = ""
    number_of_busses: int = 0
    seated_capacity: int = 0
    standing_capacity: int = 0

    @property
    def total_capacity(self):
        return self.seated_capacity + self.standing_capacity


@dataclass
class Line(OXData):
    name: str = ""
    passenger_demand: int = 0
    forward_duration: int = 0
    backward_duration: int = 0
    idle_duration: int = 0
    banned_groups: list[UUID] = field(default_factory=list)

    @property
    def total_duration(self):
        return self.forward_duration + self.backward_duration + self.idle_duration


@dataclass
class LineSegment(OXData):
    start_stop: str = ""
    end_stop: str = ""
    related_lines: list[UUID] = field(default_factory=list)
    passenger_demand: int = 0


@dataclass
class GeneralProblemParameters(OXData):
    time_period: int = 0


def prepare_database(prb: OXCSPProblem):
    busses = [
        BusGroup(name="A", number_of_busses=7, seated_capacity=26, standing_capacity=77),
        BusGroup(name="B", number_of_busses=5, seated_capacity=33, standing_capacity=77),
        BusGroup(name="C", number_of_busses=14, seated_capacity=34, standing_capacity=77),
        BusGroup(name="D", number_of_busses=2, seated_capacity=35, standing_capacity=77),
        BusGroup(name="E", number_of_busses=5, seated_capacity=48, standing_capacity=117),
    ]
    lines = [
        Line(name="114", forward_duration=40, idle_duration=5, backward_duration=40,
             banned_groups=[busses[-1].id], passenger_demand=390),
        Line(name="115", forward_duration=40, idle_duration=5, backward_duration=40,
             banned_groups=[busses[-1].id], passenger_demand=265),
        Line(name="120", forward_duration=35, idle_duration=5, backward_duration=35,
             banned_groups=[], passenger_demand=323),
        Line(name="121", forward_duration=55, idle_duration=5, backward_duration=55,
             banned_groups=[busses[-1].id], passenger_demand=476),
    ]
    segments = [
        LineSegment(start_stop="70", end_stop="71",
                    related_lines=[lines[0].id, lines[2].id], passenger_demand=145),
        LineSegment(start_stop="71", end_stop="29",
                    related_lines=[lines[0].id], passenger_demand=104),
        LineSegment(start_stop="28", end_stop="29",
                    related_lines=[lines[1].id, lines[3].id], passenger_demand=136),
        LineSegment(start_stop="192", end_stop="193",
                    related_lines=[lines[2].id], passenger_demand=155),
        LineSegment(start_stop="34", end_stop="35",
                    related_lines=[lines[0].id, lines[1].id, lines[3].id], passenger_demand=157),
        LineSegment(start_stop="36", end_stop="37",
                    related_lines=[lines[0].id, lines[1].id, lines[2].id, lines[3].id], passenger_demand=174),
        LineSegment(start_stop="43", end_stop="104",
                    related_lines=[lines[2].id, lines[3].id], passenger_demand=150),
        LineSegment(start_stop="43", end_stop="44",
                    related_lines=[lines[0].id, lines[1].id], passenger_demand=83),
        LineSegment(start_stop="107", end_stop="108",
                    related_lines=[lines[3].id], passenger_demand=146),
        LineSegment(start_stop="23", end_stop="24",
                    related_lines=[lines[1].id], passenger_demand=26),
        LineSegment(start_stop="50", end_stop="51",
                    related_lines=[lines[0].id, lines[2].id, lines[3].id], passenger_demand=41),
    ]

    for bus in busses:
        prb.db.add_object(bus)

    for line in lines:
        prb.db.add_object(line)

    for segment in segments:
        prb.db.add_object(segment)

    prb.db.add_object(GeneralProblemParameters(time_period=120))

    return busses, lines, segments


def main():
    bap = OXGPProblem()
    _, _, _ = prepare_database(bap)

    parameters = bap.db.search_by_function(lambda var: isinstance(var, GeneralProblemParameters))[0]

    bap.create_variables_from_db(
        BusGroup, Line,
        var_name_template="# of Trips of Bus Group {busgroup_name} on Line {line_name}",
        var_description_template="The total number of Trips should be performed by Bus Group {busgroup_name} on Line {line_name}",
        lower_bound=0,
        upper_bound=2000
    )

    # Ban bus groups on lines

    for line in bap.db.search_by_function(lambda var: isinstance(var, Line)):
        if len(line.banned_groups) > 0:
            bap.create_constraint(
                variable_search_function=lambda var: var.related_data["line"] == line.id and var.related_data[
                    "busgroup"] in line.banned_groups,
                weight_calculation_function=lambda var, prb: 1,
                operator=RelationalOperators.EQUAL,
                value=0,
                name=f"Bus groups {",".join(bap.db[var].name for var in line.banned_groups)} is banned on Line {line.name}"
            )

    # Each line has at least one trip

    for line in bap.db.search_by_function(lambda var: isinstance(var, Line)):
        bap.create_constraint(
            variable_search_function=lambda var: var.related_data["line"] == line.id,
            weight_calculation_function=lambda var, prb: 1,
            operator=RelationalOperators.GREATER_THAN_EQUAL,
            value=1,
            name=f"At least one trip should be performed on Line {line.name}"
        )

    # Group-based bus count contraint

    for bus in bap.db.search_by_function(lambda var: isinstance(var, BusGroup)):
        bap.create_goal_constraint(
            variable_search_function=lambda var: var.related_data["busgroup"] == bus.id,
            weight_calculation_function=lambda var, prb: Fraction(prb.db[prb.variables[var].related_data[
                "line"]].total_duration, parameters.time_period),
            operator=RelationalOperators.LESS_THAN_EQUAL,
            value=bus.number_of_busses,
            name=f"Bus {bus.name} should not use more than {bus.number_of_busses} busses"
        )

    # Satisfy Line passenger demand

    for line in bap.db.search_by_function(lambda var: isinstance(var, Line)):
        bap.create_constraint(
            variable_search_function=lambda var: var.related_data["line"] == line.id,
            weight_calculation_function=lambda var, prb: prb.db[
                prb.variables[var].related_data["busgroup"]].total_capacity,
            operator=RelationalOperators.GREATER_THAN_EQUAL,
            value=line.passenger_demand,
            name=f"Line {line.name} should handle at least {line.passenger_demand} passengers"
        )

    # Satisfy Line Segment passenger demand

    for segment in bap.db.search_by_function(lambda var: isinstance(var, LineSegment)):
        for line_id in segment.related_lines:
            bap.create_constraint(
                variable_search_function=lambda var: var.related_data["line"] == line_id,
                weight_calculation_function=lambda var, prb: prb.db[
                    prb.variables[var].related_data["busgroup"]].total_capacity,
                operator=RelationalOperators.GREATER_THAN_EQUAL,
                value=segment.passenger_demand,
                name=f"Line Segment {segment.start_stop}-{segment.end_stop} should handle at least {segment.passenger_demand}"
            )

    # Time Constraint

    # Objective function
    bap.create_objective_function()

    status, solver = solve(bap, 'Gurobi', use_continuous=False, equalizeDenominators=True)

    print(f"Status: {status}")

    for solution in solver:
        solution.print_solution_for(bap)


if __name__ == '__main__':
    main()
