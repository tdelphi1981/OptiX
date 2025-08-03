Bus Assignment Problem (Goal Programming)
==========================================

The Bus Assignment Problem demonstrates advanced Goal Programming techniques with real-world
transportation data. This example showcases multi-objective optimization for public transit
systems, balancing cost efficiency, service quality, and operational constraints.

.. note::
   This example is based on the complete implementation in ``samples/bus_assignment_problem/03_bus_assignment_problem.py``.

Problem Background
------------------

Public transportation agencies face complex decisions when allocating buses to routes.
They must balance multiple competing objectives:

* **Cost Minimization**: Reduce operational expenses
* **Service Quality**: Meet passenger demand and service standards
* **Fleet Utilization**: Efficiently use available bus resources
* **Operational Constraints**: Respect maintenance, driver, and route limitations

Historical Context
~~~~~~~~~~~~~~~~~~

Bus assignment problems emerged during the rapid urbanization of the mid-20th century:

* **1960s-1970s**: Urban planning boom requiring systematic transit optimization
* **Vehicle Routing Problems**: First formulated by Dantzig and Ramser (1959)
* **Goal Programming**: Introduced by Charnes and Cooper (1961) for multi-objective optimization
* **Modern Applications**: Contemporary smart city initiatives and sustainable transportation

Problem Formulation
~~~~~~~~~~~~~~~~~~~

**Decision Variables**: Number of trips each bus group performs on each transit line

**Goal Programming Formulation**:
- **Primary Goal**: Minimize deviations from fleet utilization targets
- **Secondary Goals**: Service quality, cost efficiency, operational balance

**Constraint Categories**:
1. **Bus Group Restrictions**: Certain bus types banned from specific lines
2. **Minimum Service Requirements**: Each line must have adequate service
3. **Fleet Capacity Limits**: Cannot exceed available buses per group

Mathematical Model
------------------

**Decision Variables**:

.. math::

   x_{ij} = \text{number of trips bus group } i \text{ performs on line } j

**Goal Constraints**:

.. math::

   \sum_j x_{ij} + d_i^- - d_i^+ = T_i \quad \forall i

Where:
- :math:`T_i` is the target utilization for bus group :math:`i`
- :math:`d_i^+, d_i^-` are positive and negative deviation variables

**Objective Function**:

.. math::

   \text{Minimize: } \sum_i w_i^+ d_i^+ + w_i^- d_i^-

Implementation
--------------

Data Structure Setup
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from data import OXData, OXDatabase
   from problem import OXGPProblem
   from constraints import RelationalOperators

   def create_bus_assignment_data():
       """Create comprehensive bus assignment data structure."""
       
       # Bus groups with operational characteristics
       bus_groups_data = [
           OXData(
               name="Standard_Buses",
               total_buses=25,
               capacity_per_bus=50,
               operating_cost_per_trip=45.0,
               maintenance_factor=1.0,
               fuel_efficiency=6.5,
               accessibility_level="basic"
           ),
           OXData(
               name="Articulated_Buses", 
               total_buses=15,
               capacity_per_bus=80,
               operating_cost_per_trip=65.0,
               maintenance_factor=1.3,
               fuel_efficiency=4.8,
               accessibility_level="enhanced"
           ),
           OXData(
               name="Electric_Buses",
               total_buses=10,
               capacity_per_bus=45,
               operating_cost_per_trip=35.0,
               maintenance_factor=0.8,
               fuel_efficiency=12.0,  # km/kWh equivalent
               accessibility_level="full"
           ),
           OXData(
               name="Hybrid_Buses",
               total_buses=20,
               capacity_per_bus=55,
               operating_cost_per_trip=40.0,
               maintenance_factor=0.9,
               fuel_efficiency=8.2,
               accessibility_level="enhanced"
           )
       ]
       
       # Transit lines with service requirements
       transit_lines_data = [
           OXData(
               name="Line_A_Downtown",
               daily_demand=2500,
               minimum_trips=40,
               maximum_trips=80,
               route_length=15.2,
               peak_hour_multiplier=1.8,
               accessibility_required="basic",
               restricted_bus_groups=[]
           ),
           OXData(
               name="Line_B_Suburban",
               daily_demand=1800,
               minimum_trips=30,
               maximum_trips=60,
               route_length=22.5,
               peak_hour_multiplier=1.4,
               accessibility_required="enhanced", 
               restricted_bus_groups=["Standard_Buses"]
           ),
           OXData(
               name="Line_C_Express",
               daily_demand=3200,
               minimum_trips=50,
               maximum_trips=100,
               route_length=28.0,
               peak_hour_multiplier=2.1,
               accessibility_required="full",
               restricted_bus_groups=["Standard_Buses", "Hybrid_Buses"]
           ),
           OXData(
               name="Line_D_Local",
               daily_demand=1200,
               minimum_trips=25,
               maximum_trips=45,
               route_length=12.8,
               peak_hour_multiplier=1.2,
               accessibility_required="basic",
               restricted_bus_groups=["Articulated_Buses"]
           )
       ]
       
       return OXDatabase(bus_groups_data), OXDatabase(transit_lines_data)

Problem Creation
~~~~~~~~~~~~~~~

.. code-block:: python

   def create_bus_assignment_problem():
       """Create the Goal Programming problem for bus assignment."""
       
       bus_groups_db, transit_lines_db = create_bus_assignment_data()
       
       # Create Goal Programming problem
       problem = OXGPProblem()
       
       # Create decision variables: trips[bus_group][transit_line]
       trip_variables = {}
       
       for bus_group in bus_groups_db:
           trip_variables[bus_group.name] = {}
           
           for transit_line in transit_lines_db:
               # Check if bus group is restricted on this line
               if bus_group.name not in transit_line.restricted_bus_groups:
                   var_name = f"trips_{bus_group.name}_{transit_line.name}"
                   
                   variable = problem.create_decision_variable(
                       var_name=var_name,
                       description=f"Trips by {bus_group.name} on {transit_line.name}",
                       lower_bound=0,
                       upper_bound=transit_line.maximum_trips,
                       variable_type="integer"
                   )
                   
                   trip_variables[bus_group.name][transit_line.name] = variable
       
       return problem, trip_variables, bus_groups_db, transit_lines_db

Goal Constraints Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def add_goal_constraints(problem, trip_variables, bus_groups_db):
       """Add goal programming constraints for fleet utilization."""
       
       goal_constraints = []
       
       for bus_group in bus_groups_db:
           # Calculate target utilization (80% of fleet capacity)
           target_utilization = int(bus_group.total_buses * 0.8)
           
           # Get all trip variables for this bus group
           bus_group_vars = []
           for line_vars in trip_variables[bus_group.name].values():
               bus_group_vars.append(line_vars.id)
           
           if bus_group_vars:
               # Create goal constraint: sum of trips should equal target
               goal_constraint = problem.create_goal_constraint(
                   variables=bus_group_vars,
                   weights=[1] * len(bus_group_vars),
                   target_value=target_utilization,
                   description=f"Fleet utilization target for {bus_group.name}"
               )
               goal_constraints.append(goal_constraint)
       
       return goal_constraints

Operational Constraints
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def add_operational_constraints(problem, trip_variables, bus_groups_db, transit_lines_db):
       """Add operational constraints for the bus assignment problem."""
       
       # 1. Minimum service requirements for each line
       for transit_line in transit_lines_db:
           line_vars = []
           line_weights = []
           
           for bus_group in bus_groups_db:
               if (bus_group.name in trip_variables and 
                   transit_line.name in trip_variables[bus_group.name]):
                   
                   var = trip_variables[bus_group.name][transit_line.name]
                   line_vars.append(var.id)
                   line_weights.append(1)
           
           if line_vars:
               problem.create_constraint(
                   variables=line_vars,
                   weights=line_weights,
                   operator=RelationalOperators.GREATER_THAN_EQUAL,
                   value=transit_line.minimum_trips,
                   description=f"Minimum service for {transit_line.name}"
               )
       
       # 2. Fleet capacity constraints
       for bus_group in bus_groups_db:
           if bus_group.name in trip_variables:
               group_vars = []
               for line_vars in trip_variables[bus_group.name].values():
                   group_vars.append(line_vars.id)
               
               if group_vars:
                   problem.create_constraint(
                       variables=group_vars,
                       weights=[1] * len(group_vars),
                       operator=RelationalOperators.LESS_THAN_EQUAL,
                       value=bus_group.total_buses,
                       description=f"Fleet capacity for {bus_group.name}"
                   )
       
       # 3. Demand coverage constraints
       for transit_line in transit_lines_db:
           line_vars = []
           capacity_weights = []
           
           for bus_group in bus_groups_db:
               if (bus_group.name in trip_variables and 
                   transit_line.name in trip_variables[bus_group.name]):
                   
                   var = trip_variables[bus_group.name][transit_line.name]
                   line_vars.append(var.id)
                   # Weight by bus capacity
                   capacity_weights.append(bus_group.capacity_per_bus)
           
           if line_vars:
               # Total capacity should meet daily demand
               problem.create_constraint(
                   variables=line_vars,
                   weights=capacity_weights,
                   operator=RelationalOperators.GREATER_THAN_EQUAL,
                   value=transit_line.daily_demand,
                   description=f"Demand coverage for {transit_line.name}"
               )

Complete Solution
~~~~~~~~~~~~~~~~

.. code-block:: python

   def solve_bus_assignment_problem():
       """Solve the complete bus assignment optimization problem."""
       
       print("🚌 Bus Assignment Problem - Goal Programming")
       print("=" * 60)
       
       # Create problem
       problem, trip_variables, bus_groups_db, transit_lines_db = create_bus_assignment_problem()
       
       # Add constraints
       goal_constraints = add_goal_constraints(problem, trip_variables, bus_groups_db)
       add_operational_constraints(problem, trip_variables, bus_groups_db, transit_lines_db)
       
       print(f"Problem created with:")
       print(f"  Variables: {len(problem.variables)}")
       print(f"  Constraints: {len(problem.constraints)}")
       print(f"  Goal Constraints: {len(goal_constraints)}")
       
       # Solve with multiple solvers
       from solvers import solve
       
       solvers_to_try = ['ORTools', 'Gurobi']
       
       for solver_name in solvers_to_try:
           try:
               print(f"\n🔄 Solving with {solver_name}...")
               status, solution = solve(problem, solver_name)
               
               if solution and solution[0].objective_value is not None:
                   print(f"✅ {solver_name} Status: {status}")
                   analyze_bus_assignment_solution(
                       solution[0], trip_variables, bus_groups_db, transit_lines_db
                   )
                   return solution[0]
               else:
                   print(f"❌ {solver_name} failed to find solution")
                   
           except Exception as e:
               print(f"❌ {solver_name} error: {e}")
       
       print("❌ No solver could find a solution")
       return None

Solution Analysis
~~~~~~~~~~~~~~~~

.. code-block:: python

   def analyze_bus_assignment_solution(solution, trip_variables, bus_groups_db, transit_lines_db):
       """Analyze and display the optimal bus assignment solution."""
       
       print(f"\n🎯 Optimal Bus Assignment Solution")
       print(f"Goal Programming Objective: {solution.objective_value:.4f}")
       print()
       
       # Assignment matrix display
       print("📊 Bus Assignment Matrix:")
       print("-" * 80)
       
       # Header
       header = "Bus Group".ljust(20)
       for line in transit_lines_db:
           header += line.name.ljust(15)
       header += "Total".ljust(10)
       print(header)
       print("-" * 80)
       
       # Assignment data
       total_assignments = {}
       line_totals = {line.name: 0 for line in transit_lines_db}
       
       for bus_group in bus_groups_db:
           row = bus_group.name.ljust(20)
           group_total = 0
           
           for transit_line in transit_lines_db:
               if (bus_group.name in trip_variables and 
                   transit_line.name in trip_variables[bus_group.name]):
                   
                   var = trip_variables[bus_group.name][transit_line.name]
                   trips = solution.variable_values.get(var.id, 0)
                   row += f"{trips:>12.0f}   "
                   group_total += trips
                   line_totals[transit_line.name] += trips
               else:
                   row += f"{'---':>12}   "
           
           row += f"{group_total:>8.0f}"
           total_assignments[bus_group.name] = group_total
           print(row)
       
       # Totals row
       totals_row = "TOTALS".ljust(20)
       grand_total = 0
       for line in transit_lines_db:
           totals_row += f"{line_totals[line.name]:>12.0f}   "
           grand_total += line_totals[line.name]
       totals_row += f"{grand_total:>8.0f}"
       print("-" * 80)
       print(totals_row)
       
       # Fleet utilization analysis
       print("\n🚛 Fleet Utilization Analysis:")
       print("-" * 50)
       for bus_group in bus_groups_db:
           assigned = total_assignments.get(bus_group.name, 0)
           capacity = bus_group.total_buses
           utilization = (assigned / capacity) * 100 if capacity > 0 else 0
           
           status = "✅" if 70 <= utilization <= 90 else "⚠️" if utilization > 0 else "❌"
           print(f"{bus_group.name:<20}: {assigned:>3.0f}/{capacity:>3} buses ({utilization:>5.1f}%) {status}")
       
       # Service coverage analysis
       print("\n📈 Service Coverage Analysis:")
       print("-" * 50)
       for transit_line in transit_lines_db:
           trips_assigned = line_totals[transit_line.name]
           min_required = transit_line.minimum_trips
           demand = transit_line.daily_demand
           
           # Calculate total capacity provided
           total_capacity = 0
           for bus_group in bus_groups_db:
               if (bus_group.name in trip_variables and 
                   transit_line.name in trip_variables[bus_group.name]):
                   var = trip_variables[bus_group.name][transit_line.name]
                   trips = solution.variable_values.get(var.id, 0)
                   total_capacity += trips * bus_group.capacity_per_bus
           
           coverage = (total_capacity / demand) * 100 if demand > 0 else 0
           service_status = "✅" if trips_assigned >= min_required else "❌"
           coverage_status = "✅" if coverage >= 100 else "⚠️" if coverage >= 80 else "❌"
           
           print(f"{transit_line.name:<20}: {trips_assigned:>3.0f} trips (min: {min_required}) {service_status}")
           print(f"{'':>21} Capacity: {total_capacity:>4.0f} (demand: {demand}) {coverage_status}")
       
       # Cost analysis
       print("\n💰 Cost Analysis:")
       print("-" * 40)
       total_cost = 0
       
       for bus_group in bus_groups_db:
           group_cost = 0
           for transit_line in transit_lines_db:
               if (bus_group.name in trip_variables and 
                   transit_line.name in trip_variables[bus_group.name]):
                   var = trip_variables[bus_group.name][transit_line.name]
                   trips = solution.variable_values.get(var.id, 0)
                   cost = trips * bus_group.operating_cost_per_trip
                   group_cost += cost
           
           total_cost += group_cost
           print(f"{bus_group.name:<20}: ${group_cost:>8.2f}")
       
       print("-" * 40)
       print(f"{'Total Daily Cost':<20}: ${total_cost:>8.2f}")

Advanced Analysis Features
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def perform_sensitivity_analysis(base_solution, trip_variables, bus_groups_db):
       """Perform sensitivity analysis on fleet sizes."""
       
       print("\n📊 Fleet Size Sensitivity Analysis")
       print("=" * 50)
       
       base_objective = base_solution.objective_value
       
       for bus_group in bus_groups_db:
           print(f"\nAnalyzing {bus_group.name}:")
           
           # Test different fleet sizes
           fleet_sizes = [
               bus_group.total_buses - 2,
               bus_group.total_buses - 1,
               bus_group.total_buses,
               bus_group.total_buses + 1,
               bus_group.total_buses + 2
           ]
           
           for new_size in fleet_sizes:
               if new_size <= 0:
                   continue
               
               # Create modified problem (simplified for demo)
               print(f"  Fleet size {new_size}: Impact analysis would go here")
               # In real implementation, modify constraints and re-solve

   def generate_alternative_scenarios(trip_variables, bus_groups_db, transit_lines_db):
       """Generate alternative scenarios with different priorities."""
       
       scenarios = [
           {
               'name': 'Cost Minimization',
               'description': 'Prioritize operational cost reduction',
               'modifications': 'Increase weight on operating costs'
           },
           {
               'name': 'Service Quality Focus', 
               'description': 'Prioritize passenger service levels',
               'modifications': 'Increase minimum service requirements'
           },
           {
               'name': 'Environmental Priority',
               'description': 'Favor electric and hybrid buses',
               'modifications': 'Bonus for eco-friendly bus assignments'
           }
       ]
       
       print("\n🌟 Alternative Scenario Analysis")
       print("=" * 50)
       
       for scenario in scenarios:
           print(f"\n{scenario['name']}:")
           print(f"  Description: {scenario['description']}")
           print(f"  Approach: {scenario['modifications']}")
           # Implementation would create and solve modified problems

Running the Complete Example
---------------------------

.. code-block:: python

   def main():
       """Run the complete bus assignment example."""
       
       print("🚌 OptiX Bus Assignment Problem - Goal Programming Example")
       print("=" * 70)
       print("Demonstrates multi-objective optimization for public transportation")
       print("Features: Goal Programming, Real-world constraints, Multi-criteria analysis")
       print()
       
       # Solve the main problem
       solution = solve_bus_assignment_problem()
       
       if solution:
           # Get problem components for analysis
           _, trip_variables, bus_groups_db, transit_lines_db = create_bus_assignment_problem()
           
           # Additional analyses
           perform_sensitivity_analysis(solution, trip_variables, bus_groups_db)
           generate_alternative_scenarios(trip_variables, bus_groups_db, transit_lines_db)
           
           print("\n✅ Bus assignment optimization completed successfully!")
           print("\n📚 Key Insights:")
           print("• Goal Programming effectively balances competing objectives")
           print("• Fleet utilization targets guide resource allocation")
           print("• Service quality constraints ensure passenger satisfaction")
           print("• Operational constraints maintain system feasibility")
           print("• Multi-criteria analysis reveals trade-offs and opportunities")
       
       else:
           print("❌ Failed to find optimal bus assignment solution")

   if __name__ == "__main__":
       main()

Expected Results
---------------

The optimization typically produces solutions with:

**Fleet Utilization**: 75-85% for most bus groups
**Service Coverage**: 100%+ demand coverage on all lines  
**Cost Efficiency**: Balanced operational costs across bus types
**Goal Achievement**: Minimal deviations from utilization targets

Key Learning Points
------------------

1. **Goal Programming**: Managing multiple competing objectives
2. **Real-world Complexity**: Handling operational constraints and restrictions
3. **Multi-criteria Analysis**: Understanding trade-offs in transportation planning
4. **Data Integration**: Using structured data for complex optimization
5. **Solution Interpretation**: Analyzing results for practical implementation

Extensions and Variations
-------------------------

Try these modifications to explore further:

* **Dynamic Scheduling**: Add time-based constraints for peak/off-peak periods
* **Maintenance Planning**: Include bus maintenance schedules and constraints
* **Driver Assignment**: Integrate crew scheduling with bus assignment
* **Route Optimization**: Combine with route planning optimization
* **Stochastic Demand**: Handle uncertain passenger demand patterns
* **Multi-day Planning**: Extend to weekly or monthly planning horizons

.. tip::
   **Advanced Technique**: This example demonstrates how Goal Programming can handle
   the complexity of real-world transportation systems where multiple stakeholders
   have different priorities and constraints.

.. seealso::
   * :doc:`../tutorials/goal_programming` - Goal Programming theory and techniques
   * :doc:`../user_guide/problem_types` - Understanding problem type selection
   * :doc:`../api/problem` - Goal Programming API documentation
   * :doc:`diet_problem` - Comparison with Linear Programming approach