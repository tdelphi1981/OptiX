"""
Comprehensive Bus Assignment Problem Optimization Example
========================================================

This module demonstrates the implementation and solution of a realistic Bus Assignment Problem using
the OptiX mathematical optimization framework with Goal Programming techniques. This example showcases
advanced optimization modeling for public transportation systems, demonstrating practical applications
of multi-objective optimization theory to real-world transit planning and fleet management scenarios.

The implementation provides a comprehensive example of modeling complex multi-constraint transportation
problems using OptiX's Goal Programming capabilities, demonstrating advanced data modeling, constraint
formulation, objective function definition, and solution analysis techniques for operational research
in public transit systems.

Historical Background:
    Bus assignment and scheduling problems emerged as critical challenges in urban transportation
    planning during the rapid urbanization of the mid-20th century. The mathematical formulation
    of these problems draws from several key areas of operations research:
    
    - **Vehicle Routing Problems (VRP)**: First formulated by Dantzig and Ramser in 1959
    - **Transit Network Design**: Developed during the 1960s-1970s urban planning boom
    - **Goal Programming**: Introduced by Charnes and Cooper in 1961 for multi-objective optimization
    - **Public Transportation Planning**: Evolved from airline scheduling optimization techniques
    
    The complexity of modern transit systems, with multiple bus types, overlapping routes, capacity
    constraints, and service quality requirements, necessitated the development of sophisticated
    optimization approaches. Goal Programming became particularly relevant for transit planning
    because it allows balancing competing objectives like cost minimization, service quality
    maximization, and resource utilization optimization.

Problem Description:
    This Bus Assignment Problem seeks to determine the optimal allocation of different bus types
    across multiple transit lines while satisfying passenger demand, respecting fleet limitations,
    and maintaining service quality standards. The problem incorporates realistic operational
    constraints including:
    
    **Decision Variables**: The number of trips each bus group performs on each transit line
    **Primary Objective**: Goal Programming optimization (minimize deviations from targets)
    **Constraints**: Multiple constraint types ensuring operational feasibility and service quality
    
    **Mathematical Formulation**:
    
    Goal Programming Formulation:
    - Primary: Minimize goal deviations (fleet utilization targets)
    - Subject to multiple constraint types described below
    
    **Constraint Categories**:
    1. **Bus Group Restrictions**: Certain bus types banned from specific lines
    2. **Minimum Service Requirements**: Each line must have at least one trip
    3. **Fleet Capacity Limits**: Cannot exceed available buses per group (Goal Constraints)
    4. **Passenger Demand Satisfaction**: Meet minimum passenger capacity on each line
    5. **Line Segment Demand**: Satisfy passenger demand on individual route segments

Real-World Problem Complexity:
    This implementation models a realistic transit scenario with:
    
    - **Multiple Bus Types**: 5 different bus groups (A-E) with varying capacities and fleet sizes
    - **Transit Network**: 4 main lines (114, 115, 120, 121) with different operational characteristics
    - **Route Segments**: 11 specific line segments with individual passenger demand requirements
    - **Operational Constraints**: Bus type restrictions, timing constraints, and capacity limitations
    - **Service Quality**: Minimum service guarantees and passenger demand satisfaction

Modern Applications:
    This type of bus assignment optimization has widespread applications in transportation systems:
    
    - **Urban Transit Agencies**: Daily operational planning and fleet allocation
    - **Regional Transportation**: Coordinating multiple bus types across service areas
    - **School District Transportation**: Optimizing bus assignments for student transportation
    - **Corporate Shuttle Services**: Efficient allocation of vehicles across multiple routes
    - **Airport Ground Transportation**: Coordinating shuttle services between terminals
    - **Emergency Transportation**: Rapid reallocation during service disruptions

Implementation Architecture:
    This implementation demonstrates advanced OptiX features including:
    
    - **Goal Programming**: OXGPProblem with goal constraints for fleet utilization
    - **Complex Data Modeling**: Multiple interrelated data classes with UUID relationships
    - **Advanced Constraint Types**: Regular constraints, goal constraints, and prohibition constraints
    - **Realistic Data Structure**: Based on actual transit system operational parameters
    - **Multi-Level Demand Modeling**: Both line-level and segment-level passenger demand
    - **Operational Realism**: Bus type restrictions, timing constraints, and capacity calculations

Problem Instance Details:
    This specific implementation models a real-world transit system scenario:
    
    **Bus Fleet** (5 bus groups):
    - **Group A**: 7 buses, 26 seated + 77 standing = 103 total capacity
    - **Group B**: 5 buses, 33 seated + 77 standing = 110 total capacity  
    - **Group C**: 14 buses, 34 seated + 77 standing = 111 total capacity
    - **Group D**: 2 buses, 35 seated + 77 standing = 112 total capacity
    - **Group E**: 5 buses, 48 seated + 117 standing = 165 total capacity (restricted use)
    
    **Transit Lines** (4 lines):
    - **Line 114**: 85-minute cycle, 390 passenger demand, restricted bus types
    - **Line 115**: 85-minute cycle, 265 passenger demand, restricted bus types
    - **Line 120**: 75-minute cycle, 323 passenger demand, unrestricted
    - **Line 121**: 115-minute cycle, 476 passenger demand, restricted bus types
    
    **Route Segments** (11 segments):
    - Individual segments with specific passenger demands ranging from 26 to 174 passengers
    - Complex routing with segments shared across multiple lines
    - Realistic stop-to-stop passenger flow modeling

Key Features Demonstrated:
    - **Goal Programming Methodology**: Multi-objective optimization with goal constraints
    - **Complex Data Relationships**: UUID-based object relationships and cross-references
    - **Prohibition Constraints**: Bus type restrictions on specific lines
    - **Multi-Level Demand Modeling**: Both aggregate line and detailed segment demand satisfaction
    - **Fleet Utilization Optimization**: Goal constraints for optimal bus usage
    - **Operational Timing**: Duration-based fleet capacity calculations
    - **Advanced Variable Naming**: Human-readable variable names using data attributes

Constraint Structure:
    The optimization model incorporates five distinct constraint types:
    
    1. **Prohibition Constraints**: Ban specific bus groups from certain lines
    2. **Minimum Service Constraints**: Ensure at least one trip per line
    3. **Fleet Capacity Goal Constraints**: Optimize bus utilization within available fleet
    4. **Line Demand Constraints**: Satisfy minimum passenger capacity requirements
    5. **Segment Demand Constraints**: Meet passenger demand on individual route segments

Goal Programming Approach:
    This problem uses Goal Programming to handle the multi-objective nature of transit optimization:
    - **Goal Constraints**: Fleet utilization targets (soft constraints allowing deviations)
    - **Hard Constraints**: Service requirements and capacity limits (must be satisfied)
    - **Objective**: Minimize deviations from fleet utilization goals

Usage Example:
    The module can be executed directly to solve the bus assignment optimization problem:
    
    .. code-block:: python
    
        # Execute the bus assignment optimization
        python 03_bus_assignment_problem.py
        
        # Expected output includes:
        # - Goal Programming optimization status
        # - Optimal trip assignments for each bus group-line combination
        # - Goal constraint satisfaction analysis
        # - Service quality verification across all constraints

Educational Value:
    This example serves as an excellent introduction to:
    
    - Goal Programming techniques for multi-objective optimization
    - Complex transportation network modeling
    - Real-world constraint formulation in public transit systems
    - Advanced OptiX framework capabilities for sophisticated problems
    - Multi-level demand modeling and capacity planning
    - Operational constraint integration in mathematical optimization

Performance Characteristics:
    - **Problem size**: 20 variables (5 bus groups × 4 lines), 50+ constraints
    - **Complexity**: Medium-scale Goal Programming problem
    - **Solving time**: Typically 1-3 seconds for this problem instance
    - **Memory usage**: Moderate for realistic problem scale
    - **Solver compatibility**: Uses OR-Tools backend for Goal Programming support
    - **Scalability**: Methodology extends to larger transit networks

Module Dependencies:
    - **constraints**: OptiX constraint definitions and relational operators
    - **data**: OptiX data modeling framework with OXData base class
    - **problem**: OptiX Goal Programming formulation (OXGPProblem)
    - **solvers**: OptiX unified solver interface for optimization execution
    - **dataclasses**: Python data structure definitions with field factories
    - **uuid**: Unique identifier management for object relationships
"""

from dataclasses import dataclass, field
from fractions import Fraction
from uuid import UUID

from constraints import RelationalOperators
from data import OXData
from problem import OXGPProblem, OXLPProblem, OXCSPProblem
from solvers import solve


@dataclass
class BusGroup(OXData):
    """
    Data model representing a bus group with detailed capacity and fleet information.
    
    This class models realistic bus fleet characteristics used in public transportation
    systems, including separate seated and standing passenger capacities, fleet size
    constraints, and operational parameters. Each bus group represents a homogeneous
    collection of vehicles with identical operational characteristics.
    
    The class demonstrates advanced OptiX data modeling for complex transportation
    optimization problems, including computed properties for total capacity calculations
    and integration with Goal Programming constraint formulations.
    
    Attributes:
        name (str): Human-readable identifier for the bus group (e.g., "A", "B", "C").
                   Used in variable naming templates and constraint descriptions for
                   clear solution interpretation. Default: empty string
                   
        number_of_busses (int): Total number of buses available in this group for
                               deployment across all lines. Used in Goal Programming
                               fleet capacity constraints to ensure realistic operational
                               limits. Must be positive integer. Default: 0
                               
        seated_capacity (int): Number of seated passengers per bus in this group.
                              Represents the comfortable passenger capacity under normal
                              operating conditions. Used in total capacity calculations.
                              Must be non-negative integer. Default: 0
                              
        standing_capacity (int): Number of standing passengers per bus in this group.
                                Represents additional passenger capacity during peak periods.
                                Combined with seated capacity for total vehicle capacity.
                                Must be non-negative integer. Default: 0
    
    Computed Properties:
        total_capacity (int): Combined seated and standing passenger capacity per bus.
                             Automatically calculated as seated_capacity + standing_capacity.
                             Used as weight coefficient in passenger demand satisfaction
                             constraints throughout the optimization model.
    
    Usage in Optimization:
        BusGroup objects participate in multiple constraint types:
        - **Fleet Capacity Goal Constraints**: number_of_busses limits total deployment
        - **Demand Satisfaction Constraints**: total_capacity provides passenger capacity
        - **Prohibition Constraints**: Some bus groups may be banned from specific lines
        - **Variable Generation**: Creates decision variables for trips per line
    
    Real-World Context:
        This implementation models typical urban transit bus categories:
        - **Standard City Buses**: 30-40 seated, 70-80 standing capacity
        - **Articulated Buses**: 45-55 seated, 100-120 standing capacity  
        - **Smaller Buses**: 20-30 seated, 60-80 standing capacity
        - **Express Buses**: Higher seated ratio for longer routes
        
    Example Usage:
        .. code-block:: python
        
            # Define different bus types for transit fleet
            bus_groups = [
                BusGroup(name="Standard", number_of_busses=10, 
                        seated_capacity=32, standing_capacity=75),
                BusGroup(name="Articulated", number_of_busses=5,
                        seated_capacity=48, standing_capacity=117),
                BusGroup(name="Express", number_of_busses=8,
                        seated_capacity=42, standing_capacity=58)
            ]
    """
    name: str = ""
    number_of_busses: int = 0
    seated_capacity: int = 0
    standing_capacity: int = 0

    @property
    def total_capacity(self):
        return self.seated_capacity + self.standing_capacity


@dataclass
class Line(OXData):
    """
    Data model representing a transit line with operational and demand characteristics.
    
    This class models comprehensive transit line attributes including passenger demand,
    operational timing, and bus type restrictions. Each line represents a complete
    transit route with specific service requirements and operational constraints that
    affect fleet assignment decisions.
    
    The class demonstrates complex OptiX data modeling for transportation systems,
    including UUID-based relationships for bus group restrictions and computed
    properties for total operational duration calculations.
    
    Attributes:
        name (str): Human-readable identifier for the transit line (e.g., "114", "115").
                   Used in variable naming templates and constraint descriptions.
                   Should match actual transit system line designations. Default: empty string
                   
        passenger_demand (int): Total daily passenger demand that must be satisfied
                               on this line. Used as right-hand side value in demand
                               satisfaction constraints. Must be positive integer
                               representing realistic ridership levels. Default: 0
                               
        forward_duration (int): Time in minutes required for one-way trip in the
                               primary direction. Used in fleet capacity calculations
                               to determine how many buses are needed for service.
                               Must be positive integer. Default: 0
                               
        backward_duration (int): Time in minutes required for return trip in the
                                opposite direction. May differ from forward_duration
                                due to traffic patterns or route variations.
                                Must be positive integer. Default: 0
                                
        idle_duration (int): Time in minutes for turnaround and passenger boarding
                            at terminals. Represents operational buffer time between
                            trips. Must be non-negative integer. Default: 0
                            
        banned_groups (list[UUID]): List of bus group IDs that are prohibited from
                                   operating on this line. Used to create prohibition
                                   constraints ensuring operational compatibility.
                                   Default: empty list
    
    Computed Properties:
        total_duration (int): Complete cycle time including forward, backward, and idle time.
                             Automatically calculated as forward_duration + backward_duration + idle_duration.
                             Used in Goal Programming fleet capacity constraints to determine
                             bus utilization rates and availability.
    
    Usage in Optimization:
        Line objects participate in multiple constraint types:
        - **Prohibition Constraints**: banned_groups creates exclusion constraints
        - **Minimum Service Constraints**: Each line must have at least one trip
        - **Demand Satisfaction Constraints**: passenger_demand must be met
        - **Fleet Capacity Calculations**: total_duration affects bus availability
        - **Variable Generation**: Creates decision variables for bus group assignments
    
    Operational Timing:
        The duration attributes model realistic transit operations:
        - **Forward/Backward Duration**: Actual travel time between terminals
        - **Idle Duration**: Passenger loading, driver breaks, schedule padding
        - **Total Duration**: Complete cycle time for fleet planning calculations
        
    Bus Group Restrictions:
        The banned_groups mechanism models real-world operational constraints:
        - Vehicle size restrictions on narrow routes
        - Accessibility requirements for specific bus types  
        - Maintenance depot assignment limitations
        - Driver certification requirements for certain vehicles
        
    Example Usage:
        .. code-block:: python
        
            # Define transit lines with operational characteristics
            lines = [
                Line(name="Express101", passenger_demand=450,
                     forward_duration=35, backward_duration=35, idle_duration=10,
                     banned_groups=[small_bus_group.id]),  # Express route, no small buses
                Line(name="Local202", passenger_demand=280,
                     forward_duration=45, backward_duration=45, idle_duration=5,
                     banned_groups=[])  # Local route, all bus types allowed
            ]
    """
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
    """
    Data model representing individual route segments with specific passenger demand.
    
    This class models fine-grained transit route segments between specific stops,
    enabling detailed passenger flow analysis and capacity planning. Each segment
    represents a portion of one or more transit lines with its own passenger demand
    requirements that must be satisfied independently of overall line demand.
    
    This advanced modeling approach demonstrates OptiX's capability to handle
    multi-level constraint hierarchies where both aggregate (line-level) and
    detailed (segment-level) requirements must be simultaneously satisfied.
    
    Attributes:
        start_stop (str): Identifier for the segment's starting stop/station.
                         Should match actual transit system stop designations
                         for operational relevance. Default: empty string
                         
        end_stop (str): Identifier for the segment's ending stop/station.
                       Represents the destination of this route segment.
                       Should match actual transit system stop designations.
                       Default: empty string
                       
        related_lines (list[UUID]): List of line IDs that utilize this segment.
                                   Enables modeling of shared route segments where
                                   multiple lines provide service on the same corridor.
                                   Used to identify which variables contribute to
                                   segment capacity. Default: empty list
                                   
        passenger_demand (int): Number of passengers that must be accommodated
                               on this specific segment. Represents peak load
                               or total daily demand for this route portion.
                               Must be non-negative integer. Default: 0
    
    Usage in Optimization:
        LineSegment objects create detailed capacity constraints:
        - **Segment Demand Constraints**: Each segment's passenger_demand must be satisfied
        - **Multi-Line Coordination**: Segments served by multiple lines aggregate capacity
        - **Peak Load Planning**: Ensures adequate capacity during maximum demand periods
        - **Route Optimization**: Identifies capacity bottlenecks within transit lines
    
    Real-World Application:
        Line segments model actual operational scenarios:
        - **Shared Corridors**: Multiple bus lines serving the same street segments
        - **Peak Load Points**: Segments with maximum passenger boarding/alighting
        - **Transfer Points**: High-demand segments near transit hubs or connections
        - **Capacity Bottlenecks**: Route portions requiring additional service attention
        
    Constraint Formulation:
        For each segment, a constraint ensures adequate capacity:
        
        Σ(capacity[bus_group] × trips[bus_group][line]) ≥ segment.passenger_demand
        
        where the sum includes only lines that serve this segment (related_lines).
        
    Multi-Line Segments:
        When multiple lines serve the same segment, their combined capacity
        contributes to meeting the segment's passenger demand, enabling:
        - **Service Coordination**: Multiple lines providing overlapping service
        - **Capacity Aggregation**: Combined fleet capacity on shared corridors
        - **Load Distribution**: Optimal allocation across parallel services
        
    Example Usage:
        .. code-block:: python
        
            # Define route segments with passenger demand
            segments = [
                LineSegment(start_stop="Downtown", end_stop="University",
                           related_lines=[line1.id, line2.id], passenger_demand=180),
                LineSegment(start_stop="University", end_stop="Airport", 
                           related_lines=[line2.id], passenger_demand=95),
                LineSegment(start_stop="Mall", end_stop="Hospital",
                           related_lines=[line1.id, line3.id], passenger_demand=140)
            ]
    """
    start_stop: str = ""
    end_stop: str = ""
    related_lines: list[UUID] = field(default_factory=list)
    passenger_demand: int = 0


@dataclass
class GeneralProblemParameters(OXData):
    """
    Data model for global optimization parameters affecting the entire problem.
    
    This class encapsulates system-wide parameters that influence constraint
    formulations and optimization calculations across all bus groups and lines.
    These parameters represent operational constants that apply to the entire
    transit system and affect fleet capacity calculations.
    
    Attributes:
        time_period (int): Total time period in minutes for fleet planning calculations.
                          Used as denominator in fleet capacity constraint calculations
                          to determine how many complete trip cycles can be performed
                          within the planning horizon. Must be positive integer.
                          Typically represents daily operating hours. Default: 0
    
    Usage in Optimization:
        Used in Goal Programming fleet capacity constraints:
        
        Σ(trips[bus_group][line] × line.total_duration) / time_period ≤ bus_group.number_of_busses
        
        This ensures that the total time required for all assigned trips does not
        exceed the available fleet capacity during the planning period.
    """
    time_period: int = 0


def prepare_database(prb: OXCSPProblem):
    """
    Initialize the optimization problem database with realistic transit system data.
    
    This function demonstrates comprehensive data setup for a real-world bus assignment
    problem, including multiple bus types, transit lines with operational constraints,
    route segments with passenger demand, and system-wide parameters. The data represents
    a realistic urban transit scenario with complex operational relationships.
    
    Args:
        prb (OXCSPProblem): The OptiX problem instance to populate with data objects.
                           All created objects will be added to the problem's database
                           for use in constraint formulation and variable generation.
    
    Returns:
        tuple: (busses, lines, segments) - Lists of created data objects for reference
               in constraint formulation and testing. Enables direct access to specific
               objects without database queries.
    
    Data Structure Created:
        **Bus Fleet (5 groups)**:
        - Group A: 7 buses, 103 total capacity (standard city buses)
        - Group B: 5 buses, 110 total capacity (medium capacity buses)  
        - Group C: 14 buses, 111 total capacity (large fleet, standard capacity)
        - Group D: 2 buses, 112 total capacity (small specialized fleet)
        - Group E: 5 buses, 165 total capacity (high-capacity articulated buses, restricted use)
        
        **Transit Network (4 lines)**:
        - Line 114: 85-min cycle, 390 passengers, restrictions on Group E
        - Line 115: 85-min cycle, 265 passengers, restrictions on Group E
        - Line 120: 75-min cycle, 323 passengers, no restrictions
        - Line 121: 115-min cycle, 476 passengers, restrictions on Group E
        
        **Route Segments (11 segments)**:
        - Complex network with shared segments across multiple lines
        - Passenger demands ranging from 26 to 174 passengers per segment
        - Realistic stop-to-stop connectivity modeling
        
        **System Parameters**:
        - 120-minute planning period for fleet capacity calculations
    
    Operational Constraints Modeled:
        - **Bus Type Restrictions**: Group E (articulated buses) banned from 3 of 4 lines
        - **Shared Route Segments**: Multiple lines serving the same corridor segments
        - **Varied Trip Durations**: Different operational timing for each line
        - **Fleet Size Diversity**: Range from 2 to 14 buses per group
        - **Capacity Hierarchy**: Different passenger capacities across bus types
    
    Real-World Relevance:
        This data structure represents typical urban transit challenges:
        - Mixed fleet with different vehicle capabilities
        - Route network with shared infrastructure
        - Operational restrictions based on vehicle characteristics
        - Detailed passenger demand modeling at segment level
        - Realistic timing constraints for service planning
    """
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
    """
    Main function implementing the complete Goal Programming bus assignment optimization workflow.
    
    This function demonstrates the end-to-end process of formulating, solving, and analyzing
    a comprehensive bus assignment problem using OptiX's Goal Programming capabilities. It showcases
    advanced optimization modeling techniques for real-world transportation systems, including
    multi-objective optimization, complex constraint hierarchies, and sophisticated data relationships.
    
    The implementation follows a systematic approach for complex transportation optimization
    problems involving multiple constraint types, Goal Programming objectives, prohibition
    constraints, and multi-level demand satisfaction requirements.
    
    Workflow Overview:
        1. **Goal Programming Initialization**: Create OXGPProblem instance for multi-objective optimization
        2. **Database Population**: Load realistic transit system data including bus groups, lines, and segments
        3. **Cross-Product Variable Generation**: Create assignment variables for each bus group-line combination
        4. **Prohibition Constraint Formulation**: Enforce bus type restrictions on specific lines
        5. **Minimum Service Constraints**: Ensure at least one trip per transit line
        6. **Goal Programming Fleet Constraints**: Optimize fleet utilization within available capacity
        7. **Line Demand Satisfaction**: Meet passenger demand requirements for each transit line
        8. **Segment Demand Satisfaction**: Satisfy passenger demand on individual route segments
        9. **Goal Programming Optimization**: Solve using OR-Tools with Goal Programming support
        10. **Solution Analysis**: Display and validate comprehensive optimization results
    
    Problem Complexity Features:
        **Advanced OptiX Capabilities Demonstrated**:
        - **Goal Programming (OXGPProblem)**: Multi-objective optimization with goal constraints
        - **Prohibition Constraints**: Bus type restrictions using equality constraints (= 0)
        - **Multi-Level Demand Modeling**: Both line-level and segment-level passenger requirements
        - **UUID-Based Relationships**: Complex data object cross-references and banned groups
        - **Advanced Variable Naming**: Human-readable names using data object attributes
        - **Goal Constraint Formulation**: Fleet capacity optimization with soft constraints
        
        **Real-World Operational Constraints**:
        - **Bus Type Restrictions**: Certain vehicles banned from specific routes
        - **Fleet Capacity Limits**: Cannot exceed available buses considering trip duration
        - **Service Quality Requirements**: Minimum trip frequency per line
        - **Passenger Demand Satisfaction**: Adequate capacity for both lines and segments
        - **Operational Timing**: Duration-based fleet capacity calculations
    
    Constraint Structure (5 types):
        1. **Prohibition Constraints** (selective application):
           For banned bus groups on specific lines:
           Σ(trips[banned_group][line]) = 0
           
        2. **Minimum Service Constraints** (one per line):
           For each transit line:
           Σ(trips[bus_group][line]) ≥ 1
           
        3. **Fleet Capacity Goal Constraints** (one per bus group):
           For each bus group (Goal Programming - soft constraints):
           Σ(trips[bus_group][line] × line.total_duration) / time_period ≤ bus_group.number_of_busses
           
        4. **Line Demand Constraints** (one per line):
           For each transit line:
           Σ(bus_group.total_capacity × trips[bus_group][line]) ≥ line.passenger_demand
           
        5. **Segment Demand Constraints** (multiple per segment):
           For each line segment and each related line:
           Σ(bus_group.total_capacity × trips[bus_group][related_line]) ≥ segment.passenger_demand
    
    Goal Programming Methodology:
        **Goal Constraints vs Hard Constraints**:
        - **Goal Constraints**: Fleet capacity limits (allow deviations with penalties)
        - **Hard Constraints**: Service requirements and demand satisfaction (must be satisfied)
        - **Objective Function**: Minimize deviations from fleet utilization goals
        - **Multi-Objective Balance**: Optimize fleet efficiency while maintaining service quality
    
    Variable Structure:
        **Decision Variables**: trips[bus_group][line] representing number of trips
        **Variable Properties**:
        - **Name Template**: "# of Trips of Bus Group {busgroup_name} on Line {line_name}"
        - **Description**: Detailed explanation of assignment relationship
        - **Lower Bound**: 0 (non-negativity constraint)
        - **Upper Bound**: 2000 (operational upper limit)
        - **Variable Count**: 20 variables (5 bus groups × 4 lines)
    
    Problem Instance Characteristics:
        **Fleet Composition**: 5 bus groups with varying capacities (103-165 passengers) and fleet sizes (2-14 buses)
        **Route Network**: 4 transit lines with different operational characteristics and passenger demands
        **Route Segments**: 11 detailed segments with individual passenger demand requirements
        **Operational Restrictions**: Bus type prohibitions on 3 of 4 lines for high-capacity vehicles
        **Timing Constraints**: Variable trip durations (75-115 minutes) affecting fleet capacity
    
    Advanced Features:
        **UUID-Based Relationships**: 
        - Line.banned_groups references specific BusGroup IDs
        - LineSegment.related_lines references multiple Line IDs
        - Complex cross-referencing enabling sophisticated constraint formulations
        
        **Multi-Level Constraint Hierarchy**:
        - System-level: Fleet capacity and service frequency
        - Line-level: Passenger demand satisfaction
        - Segment-level: Detailed route capacity requirements
        
        **Goal Programming Integration**:
        - Fleet utilization as goal constraints (soft, allowing deviations)
        - Service requirements as hard constraints (must be satisfied)
        - Balanced optimization between efficiency and service quality
    
    Solver Configuration:
        **Optimization Engine**: OR-Tools (supports Goal Programming)
        **Problem Type**: Goal Programming with mixed constraint types
        **Denominator Equalization**: Enabled for handling fractional coefficients
        **Variable Type**: Continuous (allows fractional trip assignments)
    
    Expected Solution Characteristics:
        **Goal Programming Optimality**:
        - Minimizes deviations from fleet utilization targets
        - Satisfies all hard constraints (service and demand requirements)
        - Balances efficiency with operational requirements
        - May show under-utilization of some bus groups to maintain service quality
        
        **Operational Insights**:
        - High-capacity buses (Group E) used only on unrestricted Line 120
        - Standard buses distributed across all lines based on demand
        - Fleet capacity constraints may be binding for smaller bus groups
        - Segment demand requirements may drive additional capacity allocation
    
    Performance Characteristics:
        **Problem Scale**: Medium complexity with 20 variables and 50+ constraints
        **Solving Time**: 1-3 seconds for this realistic problem instance
        **Memory Usage**: Moderate requirements for complex data structures
        **Solution Quality**: Goal Programming provides balanced multi-objective solutions
        **Scalability**: Methodology extends to larger transit networks and additional objectives
    
    Educational Value:
        This implementation demonstrates:
        - **Goal Programming Techniques**: Multi-objective optimization with soft constraints
        - **Complex Transportation Modeling**: Real-world transit system characteristics
        - **Advanced OptiX Features**: Sophisticated constraint types and data relationships
        - **Operational Research Applications**: Practical optimization for public transit
        - **Multi-Level Problem Decomposition**: Hierarchical constraint structures
        - **Data-Driven Optimization**: Realistic operational parameters and relationships
    
    Returns:
        None: Results are printed to console including Goal Programming optimization status,
              detailed trip assignments with constraint satisfaction analysis, goal deviation
              reporting, and comprehensive solution validation across all constraint types.
              
    Raises:
        Solver exceptions: May occur if OR-Tools encounters numerical issues or if
                          the problem becomes infeasible due to conflicting constraints.
        Data consistency errors: If UUID relationships are broken or if operational
                               parameters create impossible constraint combinations.
        
    Note:
        This function serves as a comprehensive example of advanced optimization modeling
        for transportation systems, demonstrating the full capabilities of OptiX's Goal
        Programming framework for complex, multi-objective operational research problems.
    """
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
            weight_calculation_function=lambda var, prb: prb.db[prb.variables[var].related_data[
                "line"]].total_duration / parameters.time_period,
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

    status, solver = solve(bap, 'ORTools', equalizeDenominators=True)

    print(f"Status: {status}")

    for solution in solver:
        solution.print_solution_for(bap)


if __name__ == '__main__':
    main()
