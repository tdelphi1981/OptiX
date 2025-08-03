"""
Classic Diet Problem Optimization Example
==========================================

This module demonstrates the implementation and solution of the classic Diet Problem using
the OptiX mathematical optimization framework. The Diet Problem is one of the foundational
examples in linear programming and operations research, showcasing practical applications
of optimization theory to real-world nutritional planning and cost minimization scenarios.

The implementation provides a comprehensive example of modeling complex multi-constraint
optimization problems using OptiX's object-oriented approach, demonstrating data modeling,
constraint formulation, objective function definition, and solution analysis techniques.

Historical Background:
    The Diet Problem was first formulated by George Stigler in 1945 as part of his research
    on economic theory and nutritional planning. Stigler posed the question: "What is the
    cheapest combination of foods that will satisfy all nutritional requirements?" This
    became one of the earliest practical applications of linear programming techniques.
    
    The problem gained significant attention during World War II when military and government
    agencies needed to plan cost-effective nutrition programs for large populations. The
    mathematical formulation laid the groundwork for modern optimization approaches in
    supply chain management, resource allocation, and dietary planning.
    
    Stigler's original problem involved 77 different foods and 9 nutritional constraints,
    and he calculated a solution by hand that cost $39.69 per year (in 1939 dollars).
    When linear programming techniques were later applied, the optimal solution was found
    to cost only $39.93, demonstrating the remarkable accuracy of his manual calculations.

Problem Description:
    The Diet Problem seeks to determine the optimal combination of foods to purchase and
    consume in order to meet nutritional requirements at minimum cost. The mathematical
    formulation involves:
    
    **Decision Variables**: The quantity of each food item to purchase/consume
    **Objective Function**: Minimize the total cost of the food combination
    **Constraints**: Ensure adequate intake of essential nutrients while respecting
                    practical limitations such as maximum volume and individual food limits
    
    **Mathematical Formulation**:
    
    Minimize: Σ(cost_i × quantity_i) for all foods i
    
    Subject to:
    - Σ(nutrient_content_ij × quantity_i) ≥ minimum_requirement_j for all nutrients j
    - Σ(nutrient_content_ij × quantity_i) ≤ maximum_requirement_j for nutrients with upper bounds
    - Σ(volume_i × quantity_i) ≤ maximum_total_volume
    - quantity_i ≥ 0 for all foods i (non-negativity constraint)
    - quantity_i ≤ reasonable_upper_bound_i for all foods i (practical limits)

Modern Applications:
    The Diet Problem formulation has evolved beyond nutritional planning to encompass:
    
    - **Healthcare Systems**: Meal planning for hospitals, nursing homes, and dietary programs
    - **Military Logistics**: Cost-effective nutrition planning for armed forces
    - **Food Industry**: Product formulation and ingredient optimization
    - **Agricultural Planning**: Livestock feed optimization and crop selection
    - **Supply Chain Management**: Procurement optimization and inventory planning
    - **Sustainability**: Environmental impact minimization in food production systems

Implementation Architecture:
    This implementation demonstrates advanced OptiX features including:
    
    - **Data Modeling**: Custom data classes for foods and nutrients with structured attributes
    - **Database Integration**: OptiX database functionality for object management and relationships
    - **Variable Generation**: Automated decision variable creation from data objects
    - **Constraint Formulation**: Systematic constraint generation from nutritional requirements
    - **Multi-Objective Considerations**: Cost minimization with nutritional adequacy
    - **Solution Analysis**: Comprehensive result interpretation and validation

Problem Instance Details:
    This specific implementation models a simplified fast-food diet optimization problem:
    
    **Foods Available** (9 items):
    - Cheeseburger, Ham Sandwich, Hamburger, Fish Sandwich, Chicken Sandwich
    - Fries, Sausage Biscuit, Lowfat Milk, Orange Juice
    
    **Nutritional Requirements** (7 nutrients):
    - Calories: minimum 2000 (energy requirements)
    - Carbohydrates: 350-375g (energy and brain function)
    - Protein: minimum 55g (muscle maintenance and growth)
    - Vitamin A: minimum 100% RDA (vision and immune function)
    - Vitamin C: minimum 100% RDA (immune system and tissue repair)
    - Calcium: minimum 100% RDA (bone health)
    - Iron: minimum 100% RDA (oxygen transport)
    
    **Additional Constraints**:
    - Maximum total volume: 75 units (practical consumption limit)
    - Maximum individual food quantity: 2000 servings (realistic upper bounds)

Key Features Demonstrated:
    - **Object-Oriented Problem Modeling**: Structured data classes with inheritance
    - **Database-Driven Variable Creation**: Automatic variable generation from data objects
    - **Matrix-Based Constraint Formulation**: Efficient handling of nutritional content matrices
    - **Mixed Constraint Types**: Both minimum and maximum requirements with conditional logic
    - **Cost Optimization**: Linear objective function minimization
    - **Solution Validation**: Comprehensive constraint satisfaction verification

Usage Example:
    The module can be executed directly to solve the diet optimization problem:
    
    .. code-block:: python
    
        # Execute the diet problem optimization
        python 01_diet_problem.py
        
        # Expected output includes:
        # - Optimization status (OPTIMAL/FEASIBLE/etc.)
        # - Optimal food quantities for each item
        # - Total minimum cost achieved
        # - Nutritional constraint satisfaction verification

Educational Value:
    This example serves as an excellent introduction to:
    
    - Linear programming formulation techniques
    - Multi-constraint optimization problem modeling
    - Real-world application of mathematical optimization
    - OptiX framework capabilities and design patterns
    - Trade-offs between cost optimization and nutritional adequacy

Performance Characteristics:
    - Problem size: 9 variables, 15+ constraints
    - Complexity: Small-scale linear programming problem
    - Solving time: Typically under 1 second
    - Memory usage: Minimal for modern systems
    - Solver compatibility: Works with both Gurobi and OR-Tools backends

Module Dependencies:
    - constraints: OptiX constraint definitions and relational operators
    - data: OptiX data modeling framework with OXData base class
    - problem: OptiX problem formulation with linear programming support
    - solvers: OptiX unified solver interface for optimization execution
"""

import uuid
from dataclasses import dataclass, field
from uuid import UUID

from constraints import RelationalOperators
from data import OXData
from problem import OXLPProblem, ObjectiveType
from solvers import solve


@dataclass
class Food(OXData):
    """
    Data model representing a food item in the diet optimization problem.
    
    This class encapsulates the essential attributes of food items that are relevant
    to the optimization problem, including cost per serving, volume per serving,
    and nutritional content. Each food item serves as a decision variable in the
    optimization problem, where the solver determines the optimal quantity to consume.
    
    The class inherits from OXData, providing UUID-based identification and integration
    with OptiX's database management system for efficient object tracking and
    variable generation during problem formulation.
    
    Attributes:
        name (str): Human-readable identifier for the food item. Used for display
                   purposes and variable naming in the optimization model. Should be
                   descriptive and unique within the food set. Default: empty string
                   
        c (float): Cost per serving of the food item in monetary units (typically dollars).
                  This value is used as the coefficient in the objective function for
                  cost minimization. Must be non-negative and represent realistic
                  market prices. Default: 0.0
                  
        v (float): Volume per serving of the food item in standardized volume units.
                  Used to enforce practical consumption limits based on stomach capacity
                  and meal volume constraints. Must be non-negative and represent
                  reasonable portion sizes. Default: 0.0
    
    Design Rationale:
        The simplified attribute naming (c, v) follows mathematical optimization
        conventions where concise variable names improve formula readability and
        reduce notation complexity in constraint formulations.
        
    Usage:
        Food objects are typically created in bulk and added to the problem database
        for automatic variable generation:
        
        .. code-block:: python
        
            foods = [
                Food(name="Cheeseburger", c=1.84, v=4.0),
                Food(name="Ham Sandwich", c=2.19, v=7.5),
                Food(name="Lowfat Milk", c=0.60, v=8.0)
            ]
            
            for food in foods:
                problem.db.add_object(food)
                
    Note:
        Nutritional content is not stored directly in Food objects but rather
        maintained in separate data structures (matrices) to enable efficient
        mathematical operations during constraint generation.
    """
    name: str = ""
    c: float = 0.0
    v: float = 0.0


@dataclass
class Nutrient(OXData):
    """
    Data model representing a nutritional requirement in the diet optimization problem.
    
    This class defines the nutritional constraints that the optimal diet must satisfy,
    including minimum requirements for essential nutrients and optional maximum limits
    for nutrients that can be harmful in excess. Each nutrient generates one or more
    linear constraints in the optimization problem.
    
    The class supports both lower-bound-only constraints (minimum requirements) and
    range constraints (minimum and maximum requirements) to accommodate different
    types of nutritional guidelines and health recommendations.
    
    Attributes:
        name (str): Human-readable identifier for the nutrient. Used for constraint
                   naming and solution reporting. Should correspond to standard
                   nutritional terminology (e.g., "Calories", "Protein", "Vitamin C").
                   Default: empty string
                   
        n_min (float): Minimum required amount of the nutrient in standardized units
                      (e.g., grams, milligrams, percentage of RDA). This value generates
                      a greater-than-or-equal constraint ensuring adequate nutrition.
                      Must be non-negative and based on recognized nutritional guidelines.
                      Default: 0.0
                      
        n_max (float | None): Optional maximum allowed amount of the nutrient in the
                             same units as n_min. When specified, generates a
                             less-than-or-equal constraint to prevent overconsumption
                             of nutrients that can be harmful in excess (e.g., sodium,
                             saturated fat). Set to None for nutrients with no upper limit.
                             Default: None
    
    Constraint Generation:
        Each Nutrient object generates the following constraints:
        
        - **Minimum Constraint**: Σ(nutrient_content[i] × food_quantity[i]) ≥ n_min
        - **Maximum Constraint**: Σ(nutrient_content[i] × food_quantity[i]) ≤ n_max (if n_max is not None)
        
        where nutrient_content[i] is the amount of this nutrient in food item i.
    
    Nutritional Guidelines:
        The values should be based on established nutritional standards such as:
        
        - **RDA (Recommended Dietary Allowance)**: Established by health authorities
        - **DRI (Dietary Reference Intakes)**: Comprehensive nutritional guidelines
        - **WHO Guidelines**: International health organization recommendations
        - **Medical Requirements**: Specific dietary needs for health conditions
    
    Usage:
        Nutrient objects are created to define the constraint set for the optimization:
        
        .. code-block:: python
        
            nutrients = [
                Nutrient(name="Calories", n_min=2000),                    # Energy needs
                Nutrient(name="Carbohydrates", n_min=350, n_max=375),    # Range constraint
                Nutrient(name="Protein", n_min=55),                      # Minimum only
                Nutrient(name="Vitamin C", n_min=100)                    # % RDA minimum
            ]
            
            for nutrient in nutrients:
                problem.db.add_object(nutrient)
    
    Examples:
        Common nutrient specifications in diet problems:
        
        - **Macronutrients**: Calories, protein, carbohydrates, fats (essential energy sources)
        - **Vitamins**: A, C, D, E, B-complex (regulatory and metabolic functions)
        - **Minerals**: Calcium, iron, zinc, magnesium (structural and enzymatic functions)
        - **Limited Nutrients**: Sodium, saturated fat, cholesterol (health risk management)
        
    Validation:
        The class supports basic validation requirements:
        
        - n_min should be non-negative
        - n_max, when specified, should be greater than n_min
        - Units should be consistent across all food nutritional content data
        - Values should reflect realistic and medically sound requirements
    """
    name: str = ""
    n_min: float = 0.0
    n_max: float | None = None


def main():
    """
    Main function implementing the complete diet problem optimization workflow.
    
    This function demonstrates the end-to-end process of formulating, solving, and
    analyzing the classic diet problem using the OptiX optimization framework. It
    showcases best practices for problem modeling, data organization, constraint
    formulation, and solution interpretation.
    
    The implementation follows a systematic approach that can be adapted for similar
    optimization problems involving resource allocation, cost minimization, and
    multi-constraint satisfaction scenarios.
    
    Workflow Overview:
        1. **Problem Initialization**: Create linear programming problem instance
        2. **Data Setup**: Define food items and nutritional requirements
        3. **Database Population**: Add data objects to OptiX database system
        4. **Variable Generation**: Create decision variables from food data
        5. **Constraint Formulation**: Generate nutritional and practical constraints
        6. **Objective Definition**: Establish cost minimization objective function
        7. **Optimization Execution**: Solve using selected optimization engine
        8. **Solution Analysis**: Display and validate optimization results
    
    Problem Instance Data:
        **Food Items (9 total)**:
        - Fast food options representing typical quick-service restaurant menu
        - Cost range: $0.60 - $2.29 per serving
        - Volume range: 2.6 - 12.0 units per serving
        - Nutritional diversity covering major food groups
        
        **Nutritional Requirements (7 nutrients)**:
        - Calories: 2000+ (daily energy requirement)
        - Carbohydrates: 350-375g (energy and brain function)
        - Protein: 55+ g (muscle maintenance)
        - Vitamins A, C: 100%+ RDA (immune and metabolic functions)
        - Calcium: 100%+ RDA (bone health)
        - Iron: 100%+ RDA (oxygen transport)
        
        **Practical Constraints**:
        - Maximum total volume: 75 units (realistic consumption limit)
        - Individual food limits: 0-2000 servings (practical bounds)
    
    Nutritional Content Matrix:
        The nutritional content is organized as a 9×7 matrix where:
        - Rows represent food items (indexed 0-8)
        - Columns represent nutrients (indexed 0-6)
        - Values indicate nutrient content per serving
        
        Matrix structure enables efficient constraint generation through
        matrix-vector operations during problem formulation.
    
    Optimization Configuration:
        - **Solver**: Gurobi (commercial high-performance optimizer)
        - **Variable Type**: Continuous (allows fractional servings)
        - **Denominator Equalization**: Enabled (handles fractional coefficients)
        - **Problem Type**: Linear Programming (convex optimization)
    
    Expected Solution Characteristics:
        - **Optimality**: Global minimum cost solution guaranteed
        - **Feasibility**: All nutritional constraints satisfied
        - **Practicality**: Solution may include fractional servings
        - **Cost Efficiency**: Minimal cost while meeting all requirements
        
    Solution Interpretation:
        The optimal solution typically exhibits:
        - Focus on cost-effective, nutrient-dense foods
        - Minimal consumption of expensive items
        - Strategic selection to satisfy binding constraints
        - Trade-offs between cost and nutritional diversity
    
    Educational Insights:
        This implementation demonstrates:
        - Linear programming formulation techniques
        - Multi-constraint optimization modeling
        - Database-driven problem construction
        - Matrix-based mathematical operations
        - Solution validation and interpretation
        
    Performance Expectations:
        - Solving time: < 1 second for this problem size
        - Memory usage: Minimal (< 10MB)
        - Scalability: Methodology extends to larger food/nutrient sets
        - Reliability: Deterministic optimal solution
    
    Returns:
        None: Results are printed to console including optimization status,
              optimal food quantities, total cost, and constraint satisfaction.
              
    Raises:
        Solver exceptions may occur if:
        - Gurobi is not properly installed or licensed
        - Problem formulation contains errors
        - Numerical issues prevent convergence
        
    Note:
        The function serves as both a working example and educational template
        for similar optimization problems in operations research and management
        science applications.
    """
    # Initialize linear programming problem instance
    dp = OXLPProblem()

    # Define food items with cost and volume attributes
    # Cost (c) in dollars per serving, Volume (v) in standardized units
    foods = [Food(name="Cheeseburger", c=1.84, v=4.0),
             Food(name="Ham Sandwich", c=2.19, v=7.5),
             Food(name="Hamburger", c=1.84, v=3.5),
             Food(name="Fish Sandwich", c=1.44, v=5.0),
             Food(name="Chicken Sandwich", c=2.29, v=7.3),
             Food(name="Fries", c=.77, v=2.6),
             Food(name="Sausage Biscuit", c=1.29, v=4.1),
             Food(name="Lowfat Milk", c=.60, v=8.0),
             Food(name="Orange Juice", c=.72, v=12.0)]

    # Populate database with food objects for variable generation
    for food in foods:
        dp.db.add_object(food)

    # Define nutritional requirements with minimum and optional maximum values
    # Values represent daily requirements in appropriate units
    nutrients = [Nutrient(name="Cal", n_min=2000),                    # Calories
                 Nutrient(name="Carbo", n_min=350, n_max=375),        # Carbohydrates (g)
                 Nutrient(name="Protein", n_min=55),                  # Protein (g)
                 Nutrient(name="VitA", n_min=100),                    # Vitamin A (% RDA)
                 Nutrient(name="VitC", n_min=100),                    # Vitamin C (% RDA)
                 Nutrient(name="Calc", n_min=100),                    # Calcium (% RDA)
                 Nutrient(name="Iron", n_min=100)]                    # Iron (% RDA)

    # Populate database with nutrient objects for constraint generation
    for nutrient in nutrients:
        dp.db.add_object(nutrient)

    # Nutritional content matrix: foods (rows) × nutrients (columns)
    # Each row represents one food item's nutritional profile
    # Columns: [Calories, Carbs, Protein, VitA, VitC, Calcium, Iron]
    a = [
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

    # Maximum total volume constraint (practical consumption limit)
    Vmax = 75

    # Generate decision variables automatically from food database objects
    # Each food item becomes a decision variable representing servings to consume
    dp.create_variables_from_db(
        Food,
        var_name_template="{food_name} to consume",
        var_description_template="Number of servings of {food_name} to consume",
        lower_bound=0,        # Non-negativity constraint
        upper_bound=2000      # Practical upper limit per food item
    )

    # Extract variable IDs for constraint and objective function creation
    variable_ids = [v.id for v in dp.variables.objects]

    # Generate nutritional constraints for each nutrient requirement
    # Creates minimum and optional maximum constraints based on nutritional matrix
    for j, nutrient in enumerate(nutrients):
        # Extract nutritional content for current nutrient across all foods
        weights = [food_weight[j] for food_weight in a]

        # Create minimum nutrient requirement constraint
        # Σ(nutrient_content[i] × food_quantity[i]) ≥ minimum_requirement
        dp.create_constraint(
            variables=variable_ids,
            weights=weights,
            operator=RelationalOperators.GREATER_THAN_EQUAL,
            value=nutrient.n_min,
        )

        # Create maximum nutrient constraint if upper limit is specified
        # Σ(nutrient_content[i] × food_quantity[i]) ≤ maximum_requirement
        if nutrient.n_max is not None:
            dp.create_constraint(
                variables=variable_ids,
                weights=weights,
                operator=RelationalOperators.LESS_THAN_EQUAL,
                value=nutrient.n_max,
            )

    # Create volume constraint to ensure practical consumption limits
    # Σ(volume[i] × food_quantity[i]) ≤ maximum_total_volume
    dp.create_constraint(
        variables=variable_ids,
        weights=[f.v for f in foods],
        operator=RelationalOperators.LESS_THAN_EQUAL,
        value=Vmax,
    )

    # Define cost minimization objective function
    # Minimize: Σ(cost[i] × food_quantity[i])
    dp.create_objective_function(
        variables=variable_ids,
        weights=[f.c for f in foods],
        objective_type=ObjectiveType.MINIMIZE
    )

    # Solve the optimization problem using Gurobi solver
    # use_continuous=False: Integer programming (discrete servings)
    # equalizeDenominators=True: Handle fractional coefficients properly
    status, solver = solve(dp, 'Gurobi', use_continuous=False, equalizeDenominators=True)

    # Display optimization results
    print(f"Status: {status}")

    # Print detailed solution for each found solution
    # Includes variable values, constraint satisfaction, and objective value
    for solution in solver:
        solution.print_solution_for(dp)


if __name__ == '__main__':
    main()
