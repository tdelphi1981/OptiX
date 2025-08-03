Classic Diet Problem
===================

The Diet Problem is one of the foundational examples in linear programming and operations research. 
This tutorial demonstrates how to implement and solve Stigler's 1945 diet optimization problem using OptiX.

.. note::
   This example is based on the complete implementation in ``samples/diet_problem/01_diet_problem.py``.

Problem Background
------------------

The Diet Problem was first formulated by George Stigler in 1945 as part of his research on economic theory 
and nutritional planning. The question posed was: **"What is the cheapest combination of foods that will 
satisfy all nutritional requirements?"**

Historical Context
~~~~~~~~~~~~~~~~~~

* **World War II Era**: Military and government agencies needed cost-effective nutrition programs
* **Stigler's Manual Solution**: Calculated by hand, cost $39.69 per year (1939 dollars)
* **Linear Programming Solution**: Later found optimal cost of $39.93, validating manual calculations
* **Modern Applications**: Supply chain management, resource allocation, dietary planning

Mathematical Formulation
~~~~~~~~~~~~~~~~~~~~~~~~

**Objective**: Minimize total food cost

.. math::

   \text{Minimize: } \sum_{i} \text{cost}_i \times \text{quantity}_i

**Subject to**:

.. math::

   \begin{align}
   \sum_{i} \text{nutrient}_{ij} \times \text{quantity}_i &\geq \text{min\_requirement}_j \quad \forall j \\
   \sum_{i} \text{nutrient}_{ij} \times \text{quantity}_i &\leq \text{max\_requirement}_j \quad \forall j \\
   \sum_{i} \text{volume}_i \times \text{quantity}_i &\leq \text{max\_volume} \\
   \text{quantity}_i &\geq 0 \quad \forall i \\
   \text{quantity}_i &\leq \text{reasonable\_limit}_i \quad \forall i
   \end{align}

Implementation
--------------

Data Structures
~~~~~~~~~~~~~~~

First, let's define the data structures for foods and nutrients:

.. code-block:: python

   from data import OXData, OXDatabase

   # Define food items with nutritional content
   foods_data = [
       OXData(
           name="Whole_Wheat_Bread",
           cost_per_unit=0.05,  # $ per slice
           volume_per_unit=25,  # ml per slice
           calories_per_unit=69,
           protein_per_unit=2.4,
           calcium_per_unit=23,
           iron_per_unit=0.7,
           vitamin_a_per_unit=0,
           thiamine_per_unit=0.09,
           riboflavin_per_unit=0.04,
           niacin_per_unit=1.1,
           ascorbic_acid_per_unit=0
       ),
       OXData(
           name="Enriched_White_Bread",
           cost_per_unit=0.04,
           volume_per_unit=25,
           calories_per_unit=65,
           protein_per_unit=2.0,
           calcium_per_unit=18,
           iron_per_unit=0.6,
           vitamin_a_per_unit=0,
           thiamine_per_unit=0.08,
           riboflavin_per_unit=0.03,
           niacin_per_unit=0.9,
           ascorbic_acid_per_unit=0
       ),
       # ... more foods
   ]

   # Create food database
   foods_database = OXDatabase(foods_data)

   # Define nutritional requirements
   nutritional_requirements = {
       'calories': {'min': 2000, 'max': 3000},
       'protein': {'min': 50, 'max': 200},
       'calcium': {'min': 800, 'max': 1600},
       'iron': {'min': 12, 'max': 50},
       'vitamin_a': {'min': 5000, 'max': 50000},
       'thiamine': {'min': 1.0, 'max': 10.0},
       'riboflavin': {'min': 1.2, 'max': 10.0},
       'niacin': {'min': 12, 'max': 100},
       'ascorbic_acid': {'min': 75, 'max': 1000}
   }

Problem Setup
~~~~~~~~~~~~~

.. code-block:: python

   from problem import OXLPProblem, ObjectiveType
   from constraints import RelationalOperators

   def create_diet_problem():
       """Create and configure the diet optimization problem."""
       
       # Create Linear Programming problem
       problem = OXLPProblem()
       
       # Create decision variables for food quantities
       food_variables = []
       for food in foods_database.data:
           var = problem.create_decision_variable(
               var_name=f"quantity_{food.name}",
               description=f"Quantity of {food.name.replace('_', ' ')} to consume",
               lower_bound=0.0,  # Cannot consume negative amounts
               upper_bound=50.0  # Reasonable upper limit
           )
           food_variables.append(var)
       
       return problem, food_variables

Adding Constraints
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def add_nutritional_constraints(problem, food_variables):
       """Add nutritional requirement constraints."""
       
       # Minimum nutritional requirements
       for nutrient, requirements in nutritional_requirements.items():
           # Get nutrient content per unit for each food
           nutrient_content = []
           for food in foods_database.data:
               content = getattr(food, f"{nutrient}_per_unit", 0)
               nutrient_content.append(content)
           
           # Minimum requirement constraint
           problem.create_constraint(
               variables=[var.id for var in food_variables],
               weights=nutrient_content,
               operator=RelationalOperators.GREATER_THAN_EQUAL,
               value=requirements['min'],
               description=f"Minimum {nutrient} requirement"
           )
           
           # Maximum requirement constraint (if applicable)
           if requirements['max'] < float('inf'):
               problem.create_constraint(
                   variables=[var.id for var in food_variables],
                   weights=nutrient_content,
                   operator=RelationalOperators.LESS_THAN_EQUAL,
                   value=requirements['max'],
                   description=f"Maximum {nutrient} limit"
               )

   def add_volume_constraint(problem, food_variables):
       """Add total volume constraint."""
       
       # Maximum daily food volume (2000 ml)
       volume_weights = [food.volume_per_unit for food in foods_database.data]
       
       problem.create_constraint(
           variables=[var.id for var in food_variables],
           weights=volume_weights,
           operator=RelationalOperators.LESS_THAN_EQUAL,
           value=2000.0,
           description="Maximum daily food volume"
       )

Setting Objective Function
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def set_cost_objective(problem, food_variables):
       """Set the cost minimization objective."""
       
       # Cost per unit for each food
       cost_weights = [food.cost_per_unit for food in foods_database.data]
       
       problem.create_objective_function(
           variables=[var.id for var in food_variables],
           weights=cost_weights,
           objective_type=ObjectiveType.MINIMIZE,
           description="Minimize total daily food cost"
       )

Complete Solution
~~~~~~~~~~~~~~~~~

.. code-block:: python

   def solve_diet_problem():
       """Solve the complete diet optimization problem."""
       
       # Create problem and variables
       problem, food_variables = create_diet_problem()
       
       # Add all constraints
       add_nutritional_constraints(problem, food_variables)
       add_volume_constraint(problem, food_variables)
       
       # Set objective function
       set_cost_objective(problem, food_variables)
       
       # Solve the problem
       from solvers import solve
       
       print("Solving Diet Optimization Problem...")
       print("=" * 50)
       
       # Try multiple solvers
       solvers_to_try = ['ORTools', 'Gurobi']
       
       for solver_name in solvers_to_try:
           try:
               print(f"\nSolving with {solver_name}...")
               status, solution = solve(problem, solver_name)
               
               if solution and solution[0].objective_value is not None:
                   print(f"✅ {solver_name} Status: {status}")
                   analyze_diet_solution(solution[0], food_variables)
                   return solution[0]
               else:
                   print(f"❌ {solver_name} failed to find solution")
                   
           except Exception as e:
               print(f"❌ {solver_name} error: {e}")
       
       print("❌ No solver could find a solution")
       return None

Solution Analysis
~~~~~~~~~~~~~~~~~

.. code-block:: python

   def analyze_diet_solution(solution, food_variables):
       """Analyze and display the optimal diet solution."""
       
       print(f"\n🎯 Optimal Daily Food Cost: ${solution.objective_value:.2f}")
       print("\n📊 Optimal Food Quantities:")
       print("-" * 60)
       
       total_cost = 0
       total_volume = 0
       nutritional_totals = {nutrient: 0 for nutrient in nutritional_requirements.keys()}
       
       # Display food quantities
       for i, var in enumerate(food_variables):
           quantity = solution.variable_values.get(var.id, 0)
           
           if quantity > 0.01:  # Only show significant quantities
               food = foods_database.data[i]
               cost = quantity * food.cost_per_unit
               volume = quantity * food.volume_per_unit
               
               total_cost += cost
               total_volume += volume
               
               # Calculate nutritional contribution
               for nutrient in nutritional_requirements.keys():
                   content = getattr(food, f"{nutrient}_per_unit", 0)
                   nutritional_totals[nutrient] += quantity * content
               
               print(f"{food.name.replace('_', ' '):<25}: {quantity:>8.2f} units "
                     f"(${cost:>6.2f}, {volume:>6.1f}ml)")
       
       print("-" * 60)
       print(f"{'Total':<25}: ${total_cost:>14.2f}, {total_volume:>6.1f}ml")
       
       # Display nutritional analysis
       print(f"\n🥗 Nutritional Analysis:")
       print("-" * 70)
       print(f"{'Nutrient':<15} {'Achieved':<12} {'Required':<15} {'Status':<10}")
       print("-" * 70)
       
       for nutrient, requirements in nutritional_requirements.items():
           achieved = nutritional_totals[nutrient]
           min_req = requirements['min']
           max_req = requirements.get('max', float('inf'))
           
           # Determine status
           if achieved < min_req:
               status = "❌ Low"
           elif achieved > max_req:
               status = "⚠️ High"
           else:
               status = "✅ OK"
           
           req_range = f"{min_req}-{max_req}" if max_req != float('inf') else f"{min_req}+"
           
           print(f"{nutrient:<15} {achieved:<12.2f} {req_range:<15} {status:<10}")

Advanced Features
-----------------

Sensitivity Analysis
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def perform_sensitivity_analysis(base_problem, food_variables):
       """Perform sensitivity analysis on food prices."""
       
       print("\n📈 Price Sensitivity Analysis")
       print("=" * 50)
       
       base_solution = solve_diet_problem()
       base_cost = base_solution.objective_value if base_solution else 0
       
       # Test price changes for each food
       for i, food in enumerate(foods_database.data):
           print(f"\nAnalyzing {food.name.replace('_', ' ')}:")
           
           # Test 10% price increase
           original_cost = food.cost_per_unit
           food.cost_per_unit *= 1.1  # 10% increase
           
           try:
               problem, vars = create_diet_problem()
               add_nutritional_constraints(problem, vars)
               add_volume_constraint(problem, vars)
               set_cost_objective(problem, vars)
               
               status, solution = solve(problem, 'ORTools')
               
               if solution:
                   new_cost = solution[0].objective_value
                   change = ((new_cost - base_cost) / base_cost) * 100
                   print(f"  10% price increase → {change:+.2f}% total cost change")
               
           except Exception as e:
               print(f"  Error: {e}")
           
           finally:
               food.cost_per_unit = original_cost  # Restore original price

Alternative Diet Plans
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def generate_alternative_diets():
       """Generate alternative diet plans with different constraints."""
       
       scenarios = [
           {
               'name': 'Vegetarian Diet',
               'excluded_foods': ['Beef', 'Pork', 'Chicken'],
               'description': 'Excluding meat products'
           },
           {
               'name': 'Low Sodium Diet',
               'max_sodium': 1500,  # mg
               'description': 'Limited sodium intake'
           },
           {
               'name': 'High Protein Diet',
               'min_protein_multiplier': 2.0,
               'description': 'Double protein requirements'
           }
       ]
       
       print("\n🍽️ Alternative Diet Scenarios")
       print("=" * 50)
       
       for scenario in scenarios:
           print(f"\n{scenario['name']} - {scenario['description']}:")
           
           # Modify problem based on scenario
           problem, food_variables = create_diet_problem()
           
           # Apply scenario-specific modifications
           if 'excluded_foods' in scenario:
               # Set upper bounds to 0 for excluded foods
               for var in food_variables:
                   food_name = var.name.replace('quantity_', '')
                   if any(excluded in food_name for excluded in scenario['excluded_foods']):
                       var.upper_bound = 0
           
           if 'min_protein_multiplier' in scenario:
               # Modify protein requirement
               modified_requirements = nutritional_requirements.copy()
               modified_requirements['protein']['min'] *= scenario['min_protein_multiplier']
           
           # Add constraints and solve
           add_nutritional_constraints(problem, food_variables)
           add_volume_constraint(problem, food_variables)
           set_cost_objective(problem, food_variables)
           
           try:
               status, solution = solve(problem, 'ORTools')
               if solution:
                   cost = solution[0].objective_value
                   print(f"  Optimal cost: ${cost:.2f}")
               else:
                   print(f"  No feasible solution found")
           except Exception as e:
               print(f"  Error: {e}")

Running the Complete Example
----------------------------

.. code-block:: python

   def main():
       """Run the complete diet problem example."""
       
       print("🍎 OptiX Diet Problem Optimization")
       print("=" * 50)
       print("Based on Stigler's 1945 nutritional optimization research")
       print("Demonstrates cost minimization with nutritional constraints")
       print()
       
       # Solve the main problem
       solution = solve_diet_problem()
       
       if solution:
           # Perform additional analyses
           perform_sensitivity_analysis(None, None)
           generate_alternative_diets()
           
           print("\n✅ Diet optimization completed successfully!")
           print("\n📚 Key Insights:")
           print("• Optimal diet focuses on cost-effective nutrient sources")
           print("• Nutritional constraints significantly impact food selection")
           print("• Price sensitivity varies greatly among different foods")
           print("• Alternative scenarios show trade-offs between cost and preferences")
       
       else:
           print("❌ Failed to find optimal diet solution")

   if __name__ == "__main__":
       main()

Expected Results
----------------

The optimization typically finds solutions with:

* **Daily Cost**: $1.50 - $3.00 (varies with food prices)
* **Primary Foods**: Bread, milk, eggs, and inexpensive vegetables
* **Nutritional Balance**: All requirements met at minimum cost
* **Volume**: Within reasonable daily consumption limits

Key Learning Points
-------------------

1. **Linear Programming**: Classic example of LP optimization
2. **Multi-constraint Problems**: Balancing multiple nutritional requirements
3. **Cost Optimization**: Real-world economic decision making
4. **Feasibility**: Understanding when problems have no solution
5. **Sensitivity Analysis**: How parameter changes affect optimal solutions

Extensions
----------

Try these modifications to explore further:

* Add food preference constraints
* Include seasonal price variations
* Consider meal planning (breakfast, lunch, dinner)
* Add food group diversity requirements
* Implement stochastic optimization for uncertain prices

.. tip::
   **Next Steps**: After mastering the diet problem, try the :doc:`bus_assignment` 
   example to learn Goal Programming techniques.

.. seealso::
   * :doc:`../tutorials/linear_programming` - LP theory and techniques
   * :doc:`../api/problem` - Problem class documentation
   * :doc:`../user_guide/constraints` - Advanced constraint modeling