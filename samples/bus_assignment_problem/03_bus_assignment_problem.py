from dataclasses import dataclass, field
from uuid import UUID

from constraints import RelationalOperators
from data import OXData
from problem import OXGPProblem


@dataclass
class BusGroup(OXData):
    name: str = ""
    number_of_busses: int = 0
    seated_capacity: int = 0
    standing_capacity: int = 0


@dataclass
class Line(OXData):
    name: str = ""
    passenger_demand: int = 0
    forward_duration: int = 0
    backward_duration: int = 0
    idle_duration: int = 0
    banned_groups: list[UUID] = field(default_factory=list)


@dataclass
class LineSegment(OXData):
    start_stop: str = ""
    end_stop: str = ""
    related_lines: list[UUID] = field(default_factory=list)
    passenger_demand: int = 0


def prepare_database(prb: OXGPProblem):
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

    return busses, lines, segments


def main():
    bap = OXGPProblem()
    busses, lines, segments = prepare_database(bap)

    bap.create_variables_from_db(
        BusGroup, Line,
        var_name_template="# of Trips of Bus Group {busgroup_name} on Line {line_name}",
        var_description_template="The total number of Trips should be performed by Bus Group {busgroup_name} on Line {line_name}",
        lower_bound=0,
        upper_bound=2000
    )

    bap.create_variables_from_db(
        Line,
        var_name_template="Duration between consecutive Trips of Line {line_name}",
        var_description_template="The duration between consecutive Trips of Line {line_name}",
        lower_bound=0,
        upper_bound=2000
    )

    # Ban bus groups on lines

    for line in lines:
        if len(line.banned_groups) > 0:
            bap.create_constraint(
                variable_search_function=lambda var: var.related_data["line"] == line.id and var.related_data["busgroup"] in line.banned_groups,
                weight_calculation_function=lambda var, prb: 1,
                operator=RelationalOperators.EQUAL,
                value=0,
                name=f"Bus groups {",".join(bap.variables[var].name for var in line.banned_groups)} is banned on Line {line.name}"
            )

    # Each line has at least one trip

    for line in lines:
        bap.create_constraint(
            variable_search_function=lambda var: var.related_data["line"] == line.id,
            weight_calculation_function=lambda var, prb: 1,
            operator=RelationalOperators.GREATER_THAN_EQUAL,
            value=1,
            name=f"At least one trip should be performed on Line {line.name}"
        )

    # Do not use more than owned busses

    # Group-based bus count contraint

    # Satisfy Line passenger demand

    # Satisfy Line Segment passenger demand

    # Time Constraint

    # Objective function


if __name__ == '__main__':
    main()
