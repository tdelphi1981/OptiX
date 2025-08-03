Data Module
===========

The data module provides scenario-based data management capabilities for optimization problems.
It includes data objects with multi-scenario support and type-safe database collections for organizing data.

.. currentmodule:: data

Data Classes
------------

Data Objects
~~~~~~~~~~~~

.. autoclass:: OXData
   :members:
   :undoc-members:
   :show-inheritance:

Database Collections
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: OXDatabase
   :members:
   :undoc-members:
   :show-inheritance:

Constants
---------

.. autodata:: NON_SCENARIO_FIELDS

   List of field names that are excluded from scenario management to prevent infinite loops
   and maintain object integrity. These fields are always accessed from the base object.

Examples
--------

Basic Data Objects with Scenarios
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from data import OXData

   # Create a data object with base values
   demand_data = OXData()
   demand_data.quantity = 100
   demand_data.cost = 50.0

   # Create scenarios for sensitivity analysis
   demand_data.create_scenario("High_Demand", quantity=150, cost=55.0)
   demand_data.create_scenario("Low_Demand", quantity=75, cost=45.0)

   # Access values in different scenarios
   print(demand_data.quantity)  # 100 (Default scenario)

   demand_data.active_scenario = "High_Demand"
   print(demand_data.quantity)  # 150

   demand_data.active_scenario = "Low_Demand"  
   print(demand_data.quantity)  # 75

Database Collections
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from data import OXDatabase, OXData

   # Create a database for organizing data objects
   db = OXDatabase()

   # Create multiple data objects
   factory_a = OXData()
   factory_a.location = "Factory_A"
   factory_a.capacity = 500
   factory_a.create_scenario("Expansion", capacity=750)

   factory_b = OXData()
   factory_b.location = "Factory_B"
   factory_b.capacity = 300
   factory_b.create_scenario("Expansion", capacity=450)

   # Add objects to database
   db.add_object(factory_a)
   db.add_object(factory_b)

   print(f"Total factories: {len(db)}")

   # Iterate through all objects
   for factory in db:
       print(f"Factory at {factory.location}: capacity {factory.capacity}")

   # Switch to expansion scenario
   factory_a.active_scenario = "Expansion"
   factory_b.active_scenario = "Expansion"

   # Check expanded capacities
   for factory in db:
       print(f"Expanded {factory.location}: capacity {factory.capacity}")

Scenario Management for Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from data import OXData

   # Create demand data with multiple scenarios
   demand = OXData()
   demand.product = "Widget_A"
   demand.base_demand = 1000
   demand.seasonal_factor = 1.0

   # Create scenarios for different market conditions
   demand.create_scenario(
       "Optimistic", 
       base_demand=1200, 
       seasonal_factor=1.2
   )

   demand.create_scenario(
       "Pessimistic",
       base_demand=800,
       seasonal_factor=0.8
   )

   demand.create_scenario(
       "Realistic",
       base_demand=1000,
       seasonal_factor=1.0
   )

   # Function to calculate total demand
   def calculate_total_demand(data, season_multiplier=1.0):
       return data.base_demand * data.seasonal_factor * season_multiplier

   # Compare scenarios
   scenarios = ["Default", "Optimistic", "Pessimistic", "Realistic"]
   
   for scenario in scenarios:
       demand.active_scenario = scenario
       total = calculate_total_demand(demand)
       print(f"{scenario} scenario: {total} units")

Scenario-Based Sensitivity Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def run_sensitivity_analysis(data_objects, scenarios, optimization_function):
       """Run optimization across multiple scenarios."""
       
       results = {}
       
       for scenario_name in scenarios:
           print(f"Running scenario: {scenario_name}")
           
           # Switch all data objects to the same scenario
           for data_obj in data_objects:
               if scenario_name in data_obj.scenarios:
                   data_obj.active_scenario = scenario_name
               else:
                   data_obj.active_scenario = "Default"
           
           # Run optimization with current scenario data
           result = optimization_function(data_objects)
           results[scenario_name] = result
       
       return results

   # Usage example
   def simple_profit_calculation(data_objects):
       total_profit = 0
       for obj in data_objects:
           if hasattr(obj, 'revenue') and hasattr(obj, 'cost'):
               total_profit += obj.revenue - obj.cost
       return total_profit

   # Create test data
   product1 = OXData()
   product1.revenue = 100
   product1.cost = 60
   product1.create_scenario("HighPrice", revenue=120, cost=60)
   product1.create_scenario("LowCost", revenue=100, cost=45)

   product2 = OXData()
   product2.revenue = 80
   product2.cost = 50
   product2.create_scenario("HighPrice", revenue=95, cost=50)
   product2.create_scenario("LowCost", revenue=80, cost=40)

   products = [product1, product2]
   scenarios = ["Default", "HighPrice", "LowCost"]

   results = run_sensitivity_analysis(products, scenarios, simple_profit_calculation)
   
   for scenario, profit in results.items():
       print(f"{scenario}: ${profit} profit")

Working with Multiple Data Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from data import OXData, OXDatabase

   def create_supply_chain_data():
       """Create a multi-type supply chain dataset."""
       
       # Create suppliers with different scenarios
       supplier_db = OXDatabase()
       
       supplier_a = OXData()
       supplier_a.name = "Supplier_A"
       supplier_a.lead_time = 14
       supplier_a.reliability = 0.95
       supplier_a.cost_factor = 1.0
       supplier_a.create_scenario("Crisis", lead_time=21, reliability=0.85, cost_factor=1.3)
       
       supplier_b = OXData()
       supplier_b.name = "Supplier_B"
       supplier_b.lead_time = 7
       supplier_b.reliability = 0.98
       supplier_b.cost_factor = 1.1
       supplier_b.create_scenario("Crisis", lead_time=10, reliability=0.90, cost_factor=1.4)
       
       supplier_db.add_object(supplier_a)
       supplier_db.add_object(supplier_b)
       
       # Create demand points with scenarios
       demand_db = OXDatabase()
       
       region_1 = OXData()
       region_1.name = "Region_1"
       region_1.demand = 1000
       region_1.max_price = 50
       region_1.create_scenario("Growth", demand=1300, max_price=55)
       region_1.create_scenario("Recession", demand=700, max_price=45)
       
       region_2 = OXData()
       region_2.name = "Region_2"
       region_2.demand = 800
       region_2.max_price = 48
       region_2.create_scenario("Growth", demand=1100, max_price=52)
       region_2.create_scenario("Recession", demand=600, max_price=42)
       
       demand_db.add_object(region_1)
       demand_db.add_object(region_2)
       
       return supplier_db, demand_db

   # Create the data
   suppliers, demand_points = create_supply_chain_data()
   
   # Analyze different scenarios
   scenarios = ["Default", "Growth", "Crisis", "Recession"]
   
   for scenario in scenarios:
       print(f"\n=== {scenario} Scenario ===")
       
       # Switch all objects to the scenario
       for supplier in suppliers:
           if scenario in supplier.scenarios:
               supplier.active_scenario = scenario
           else:
               supplier.active_scenario = "Default"
       
       for demand in demand_points:
           if scenario in demand.scenarios:
               demand.active_scenario = scenario
           else:
               demand.active_scenario = "Default"
       
       # Calculate scenario metrics
       total_demand = sum(d.demand for d in demand_points)
       avg_lead_time = sum(s.lead_time for s in suppliers) / len(suppliers)
       avg_reliability = sum(s.reliability for s in suppliers) / len(suppliers)
       
       print(f"Total demand: {total_demand}")
       print(f"Avg lead time: {avg_lead_time:.1f} days")
       print(f"Avg reliability: {avg_reliability:.2%}")

UUID-Based Object Access
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from data import OXDatabase, OXData

   # Create database with data objects
   db = OXDatabase()

   # Add several objects
   for i in range(5):
       obj = OXData()
       obj.value = i * 10
       obj.category = f"Type_{i % 3}"
       db.add_object(obj)

   print(f"Database contains {len(db)} objects")

   # Access objects by UUID (inherited from OXObjectPot)
   first_obj = list(db)[0]
   found_obj = db.get_object_by_id(first_obj.id)
   print(f"Found object with value: {found_obj.value}")

   # Manual filtering using iteration
   type_0_objects = [obj for obj in db if obj.category == "Type_0"]
   print(f"Found {len(type_0_objects)} objects of Type_0")

   # Remove objects
   db.remove_object(first_obj)
   print(f"After removal: {len(db)} objects")

Advanced Scenario Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def create_monte_carlo_scenarios(base_data, num_scenarios=100):
       """Create multiple scenarios for Monte Carlo analysis."""
       import random
       
       for i in range(num_scenarios):
           # Create variations around base values
           demand_variation = random.uniform(0.8, 1.2)
           cost_variation = random.uniform(0.9, 1.1)
           
           scenario_name = f"MonteCarlo_{i+1:03d}"
           base_data.create_scenario(
               scenario_name,
               demand=int(base_data.demand * demand_variation),
               cost=base_data.cost * cost_variation
           )

   # Create base data
   product = OXData()
   product.demand = 1000
   product.cost = 50.0
   product.revenue = 75.0

   # Generate Monte Carlo scenarios
   create_monte_carlo_scenarios(product, 10)  # Create 10 scenarios

   # Run analysis across all scenarios
   profits = []
   for scenario_name in product.scenarios:
       product.active_scenario = scenario_name
       profit = product.revenue - product.cost
       profits.append((scenario_name, profit))

   # Show results
   for scenario, profit in sorted(profits, key=lambda x: x[1], reverse=True)[:5]:
       print(f"{scenario}: ${profit:.2f} profit")

Type Safety and Error Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from data import OXDatabase, OXData
   from base import OXObject, OXception

   # Demonstrate type safety
   db = OXDatabase()
   data_obj = OXData()
   
   # This works - OXData is allowed
   db.add_object(data_obj)
   print("OXData object added successfully")

   # This will fail - only OXData objects allowed
   try:
       non_data_obj = OXObject()  # Base object, not OXData
       db.add_object(non_data_obj)
   except OXception as e:
       print(f"Type safety error: {e}")

   # Scenario error handling
   try:
       data_obj.create_scenario("TestScenario", nonexistent_attr="value")
   except OXception as e:
       print(f"Scenario creation error: {e}")

See Also
--------

* :doc:`base` - Base classes that data objects inherit from
* :doc:`problem` - Problem classes that use data objects
* :doc:`variables` - Variable creation that can be linked to data objects
* :doc:`../user_guide/scenarios` - Advanced scenario modeling guide