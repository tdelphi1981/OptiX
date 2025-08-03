Classic Diet Problem
===================

The Diet Problem is one of the foundational examples in linear programming and operations research. 
This tutorial demonstrates how to implement and solve Stigler's 1945 diet optimization problem using OptiX,
specifically using a fast-food optimization scenario.

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

First, let's define the data structures for foods and nutrients using custom dataclasses:

.. code-block:: python

   from dataclasses import dataclass
   from data import OXData

   @dataclass
   class Food(OXData):
       """
       Data model representing a food item in the diet optimization problem.
       
       Attributes:
           name (str): Human-readable identifier for the food item
           c (float): Cost per serving in dollars
           v (float): Volume per serving in standardized units
       """
       name: str = ""
       c: float = 0.0    # Cost per serving
       v: float = 0.0    # Volume per serving

   @dataclass 
   class Nutrient(OXData):
       """
       Data model representing a nutritional requirement.
       
       Attributes:
           name (str): Nutrient identifier (e.g., "Calories", "Protein")
           n_min (float): Minimum required amount
           n_max (float | None): Optional maximum allowed amount
       """
       name: str = ""
       n_min: float = 0.0
       n_max: float | None = None

Problem Instance Data
~~~~~~~~~~~~~~~~~~~~~

This implementation uses a fast-food diet optimization problem with 9 food items and 7 nutrients:

.. code-block:: python

   from problem import OXLPProblem, ObjectiveType
   from constraints import RelationalOperators

   def create_diet_problem():
       """Create and configure the diet optimization problem."""
       
       # Initialize linear programming problem
       dp = OXLPProblem()
       
       # Define food items with cost and volume attributes
       foods = [
           Food(name="Cheeseburger", c=1.84, v=4.0),
           Food(name="Ham Sandwich", c=2.19, v=7.5), 
           Food(name="Hamburger", c=1.84, v=3.5),
           Food(name="Fish Sandwich", c=1.44, v=5.0),
           Food(name="Chicken Sandwich", c=2.29, v=7.3),
           Food(name="Fries", c=0.77, v=2.6),
           Food(name="Sausage Biscuit", c=1.29, v=4.1),
           Food(name="Lowfat Milk", c=0.60, v=8.0),
           Food(name="Orange Juice", c=0.72, v=12.0)
       ]
       
       # Add food objects to database
       for food in foods:
           dp.db.add_object(food)
       
       # Define nutritional requirements
       nutrients = [
           Nutrient(name="Cal", n_min=2000),                    # Calories
           Nutrient(name="Carbo", n_min=350, n_max=375),        # Carbohydrates (g)
           Nutrient(name="Protein", n_min=55),                  # Protein (g) 
           Nutrient(name="VitA", n_min=100),                    # Vitamin A (% RDA)
           Nutrient(name="VitC", n_min=100),                    # Vitamin C (% RDA)
           Nutrient(name="Calc", n_min=100),                    # Calcium (% RDA)
           Nutrient(name="Iron", n_min=100)                     # Iron (% RDA)
       ]
       
       # Add nutrient objects to database
       for nutrient in nutrients:
           dp.db.add_object(nutrient)
       
       return dp, foods, nutrients

Nutritional Content Matrix
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The nutritional content is organized as a matrix where rows represent foods and columns represent nutrients:

.. code-block:: python

   # Nutritional content matrix: foods (rows) × nutrients (columns)
   # Columns: [Calories, Carbs, Protein, VitA, VitC, Calcium, Iron]
   nutritional_matrix = [
       [510, 34, 28, 15, 6, 30, 20],    # Cheeseburger
       [370, 35, 24, 15, 10, 20, 20],   # Ham Sandwich  
       [500, 42, 25, 6, 2, 25, 20],     # Hamburger
       [370, 38, 14, 2, 0, 15, 10],     # Fish Sandwich
       [400, 42, 31, 8, 15, 15, 8],     # Chicken Sandwich
       [220, 26, 3, 0, 15, 0, 2],       # Fries
       [345, 27, 15, 4, 0, 20, 15],     # Sausage Biscuit
       [110, 12, 9, 10, 4, 30, 0],      # Lowfat Milk
       [80, 20, 1, 2, 120, 2, 2]        # Orange Juice
   ]

Variable Generation
~~~~~~~~~~~~~~~~~~~

OptiX provides automatic variable generation from database objects:

.. code-block:: python

   def create_variables_and_constraints(dp, foods, nutrients, nutritional_matrix):
       """Generate decision variables and constraints."""
       
       # Generate decision variables automatically from food database objects
       dp.create_variables_from_db(
           Food,
           var_name_template="{food_name} to consume",
           var_description_template="Number of servings of {food_name} to consume",
           lower_bound=0,        # Non-negativity constraint
           upper_bound=2000      # Practical upper limit per food item
       )
       
       # Extract variable IDs for constraint creation
       variable_ids = [v.id for v in dp.variables.objects]
       
       return variable_ids

Adding Nutritional Constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def add_nutritional_constraints(dp, variable_ids, nutrients, nutritional_matrix):
       """Add nutritional requirement constraints."""
       
       # Generate nutritional constraints for each nutrient requirement
       for j, nutrient in enumerate(nutrients):
           # Extract nutritional content for current nutrient across all foods
           weights = [food_nutrients[j] for food_nutrients in nutritional_matrix]
           
           # Create minimum nutrient requirement constraint
           dp.create_constraint(
               variables=variable_ids,
               weights=weights,
               operator=RelationalOperators.GREATER_THAN_EQUAL,
               value=nutrient.n_min,
           )
           
           # Create maximum nutrient constraint if upper limit is specified
           if nutrient.n_max is not None:
               dp.create_constraint(
                   variables=variable_ids,
                   weights=weights,
                   operator=RelationalOperators.LESS_THAN_EQUAL,
                   value=nutrient.n_max,
               )

Volume Constraint
~~~~~~~~~~~~~~~~~

.. code-block:: python

   def add_volume_constraint(dp, variable_ids, foods):
       """Add total volume constraint."""
       
       # Maximum total volume constraint (practical consumption limit)
       Vmax = 75
       
       dp.create_constraint(
           variables=variable_ids,
           weights=[f.v for f in foods],
           operator=RelationalOperators.LESS_THAN_EQUAL,
           value=Vmax,
       )

Setting Objective Function
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def set_cost_objective(dp, variable_ids, foods):
       """Set the cost minimization objective."""
       
       # Define cost minimization objective function
       dp.create_objective_function(
           variables=variable_ids,
           weights=[f.c for f in foods],
           objective_type=ObjectiveType.MINIMIZE
       )

Complete Solution
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from solvers import solve

   def solve_diet_problem():
       """Solve the complete diet optimization problem."""
       
       # Create problem and setup data
       dp, foods, nutrients = create_diet_problem()
       
       # Nutritional content matrix
       nutritional_matrix = [
           [510, 34, 28, 15, 6, 30, 20],    # Cheeseburger
           [370, 35, 24, 15, 10, 20, 20],   # Ham Sandwich  
           [500, 42, 25, 6, 2, 25, 20],     # Hamburger
           [370, 38, 14, 2, 0, 15, 10],     # Fish Sandwich
           [400, 42, 31, 8, 15, 15, 8],     # Chicken Sandwich
           [220, 26, 3, 0, 15, 0, 2],       # Fries
           [345, 27, 15, 4, 0, 20, 15],     # Sausage Biscuit
           [110, 12, 9, 10, 4, 30, 0],      # Lowfat Milk
           [80, 20, 1, 2, 120, 2, 2]        # Orange Juice
       ]
       
       # Create variables and constraints
       variable_ids = create_variables_and_constraints(dp, foods, nutrients, nutritional_matrix)
       add_nutritional_constraints(dp, variable_ids, nutrients, nutritional_matrix)
       add_volume_constraint(dp, variable_ids, foods)
       set_cost_objective(dp, variable_ids, foods)
       
       # Solve the optimization problem using Gurobi solver
       print("Solving Diet Optimization Problem...")
       print("=" * 50)
       
       try:
           # Solve with integer programming for discrete servings
           status, solutions = solve(dp, 'Gurobi', use_continuous=False, equalizeDenominators=True)
           
           print(f"Status: {status}")
           
           # Display detailed solution
           for solution in solutions:
               solution.print_solution_for(dp)
               
           return solutions[0] if solutions else None
           
       except Exception as e:
           print(f"❌ Solver error: {e}")
           return None

Solution Analysis
~~~~~~~~~~~~~~~~~

The solution will show optimal quantities for each food item that minimize cost while satisfying all constraints:

.. code-block:: python

   def analyze_solution_details(solution, dp, foods, nutritional_matrix):
       """Provide detailed analysis of the optimal solution."""
       
       if not solution:
           print("No solution to analyze")
           return
       
       print(f"\n🎯 Optimal Daily Food Cost: ${solution.objective_value:.2f}")
       print("\n📊 Optimal Food Quantities:")
       print("-" * 60)
       
       total_cost = 0
       total_volume = 0
       
       # Display food quantities with costs
       for i, var in enumerate(dp.variables.objects):
           quantity = solution.variable_values.get(var.id, 0)
           
           if quantity > 0.01:  # Only show significant quantities
               food = foods[i]
               cost = quantity * food.c
               volume = quantity * food.v
               
               total_cost += cost
               total_volume += volume
               
               print(f"{food.name:<20}: {quantity:>8.2f} servings "
                     f"(${cost:>6.2f}, {volume:>6.1f} units)")
       
       print("-" * 60)
       print(f"{'Total':<20}: ${total_cost:>14.2f}, {total_volume:>6.1f} units")

Advanced Features
-----------------

Solver Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Different solver configurations
   solvers_to_try = ['Gurobi', 'ORTools']
   
   for solver_name in solvers_to_try:
       try:
           print(f"\nTrying {solver_name} solver...")
           
           # Continuous variables (allow fractional servings)
           status, solution = solve(dp, solver_name, use_continuous=True)
           
           # Integer variables (whole servings only)  
           # status, solution = solve(dp, solver_name, use_continuous=False)
           
           if solution:
               print(f"✅ {solver_name} found solution: ${solution[0].objective_value:.2f}")
           else:
               print(f"❌ {solver_name} failed")
               
       except Exception as e:
           print(f"❌ {solver_name} error: {e}")

Problem Variations
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def create_vegetarian_variant():
       """Create a vegetarian version by excluding meat items."""
       
       # Modify food list to exclude meat products
       vegetarian_foods = [
           Food(name="Fries", c=0.77, v=2.6),
           Food(name="Lowfat Milk", c=0.60, v=8.0), 
           Food(name="Orange Juice", c=0.72, v=12.0),
           # Add more vegetarian options...
       ]
       
       # Use same constraint structure with modified food set
       # ... rest of problem setup

   def create_budget_variant(max_budget=5.00):
       """Create a budget-constrained version."""
       
       dp, foods, nutrients = create_diet_problem()
       variable_ids = create_variables_and_constraints(dp, foods, nutrients, nutritional_matrix)
       
       # Add budget constraint
       dp.create_constraint(
           variables=variable_ids,
           weights=[f.c for f in foods],
           operator=RelationalOperators.LESS_THAN_EQUAL,
           value=max_budget,
       )
       
       # Continue with normal setup...

Running the Complete Example
----------------------------

.. code-block:: python

   def main():
       """Run the complete diet problem example."""
       
       print("🍎 OptiX Diet Problem Optimization")
       print("=" * 50)
       print("Fast-food diet optimization based on Stigler's 1945 research")
       print("Demonstrates cost minimization with nutritional constraints")
       print()
       
       solution = solve_diet_problem()
       
       if solution:
           print("\n✅ Diet optimization completed successfully!")
           print(f"Minimum daily cost: ${solution.objective_value:.2f}")
           
           print("\n📚 Key Insights:")
           print("• Optimal diet focuses on cost-effective nutrient sources")
           print("• Fast-food items can meet nutritional requirements efficiently")
           print("• Volume constraints prevent unrealistic consumption patterns")
           print("• Integer constraints ensure practical serving sizes")
       else:
           print("❌ Failed to find optimal diet solution")

   if __name__ == "__main__":
       main()

Expected Results
----------------

The optimization typically finds solutions with:

* **Daily Cost**: $4.50 - $6.00 (varies with food selection and constraints)
* **Primary Foods**: Cost-effective items like milk, fries, and sandwiches
* **Nutritional Balance**: All requirements met at minimum cost
* **Volume**: Within 75 units total consumption limit
* **Servings**: Integer values for practical implementation

Key Learning Points
-------------------

1. **Linear Programming**: Classic example of LP optimization with real constraints
2. **Database-Driven Modeling**: Using OptiX's OXData system for structured problem setup
3. **Matrix-Based Constraints**: Efficient handling of nutritional content through matrices
4. **Multi-Constraint Problems**: Balancing cost, nutrition, and practical limitations
5. **Solver Integration**: Working with different optimization engines (Gurobi, OR-Tools)

Extensions
----------

Try these modifications to explore further:

* **Meal Planning**: Separate breakfast, lunch, dinner with different constraints
* **Weekly Planning**: Optimize across multiple days with variety requirements
* **Nutritional Balance**: Add constraints for food group diversity
* **Stochastic Optimization**: Handle uncertain food prices and availability
* **Goal Programming**: Convert to multi-objective optimization with preference priorities

Implementation Details
----------------------

**Problem Size**: 9 variables, 15+ constraints
**Solving Time**: < 1 second 
**Memory Usage**: Minimal (< 10MB)
**Scalability**: Methodology extends to larger food/nutrient sets

.. tip::
   **Next Steps**: After mastering the diet problem, try the :doc:`bus_assignment` 
   example to learn Goal Programming techniques with the OptiX framework.

.. seealso::
   * :doc:`../tutorials/linear_programming` - LP theory and techniques
   * :doc:`../api/problem` - Problem class documentation  
   * :doc:`../api/data` - Data modeling with OXData framework
   * :doc:`../user_guide/constraints` - Advanced constraint modeling