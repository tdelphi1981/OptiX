Variables Module
===============

The variables module provides comprehensive decision variable management for the OptiX optimization framework.
It implements a complete variable system supporting linear programming (LP), goal programming (GP), and 
constraint satisfaction problems (CSP) with advanced features for bounds management, relationship tracking, 
and specialized variable types.

.. currentmodule:: variables

Core Variable Classes
---------------------

Base Decision Variable
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: OXVariable
   :members:
   :undoc-members:
   :show-inheritance:

Goal Programming Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: OXDeviationVar
   :members:
   :undoc-members:
   :show-inheritance:

Goal Programming Examples
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from variables import OXDeviationVar, OXVariableSet

   # Create deviation variables for goal programming
   goal_vars = OXVariableSet()

   # Positive deviation (over-achievement) - undesirable
   budget_overrun = OXDeviationVar(
       name="budget_deviation_positive",
       description="Amount exceeding budget target",
       lower_bound=0,
       upper_bound=float('inf'),
       desired=False  # We want to minimize this
   )
   goal_vars.add_object(budget_overrun)

   # Negative deviation (under-achievement) - sometimes desirable
   cost_savings = OXDeviationVar(
       name="cost_deviation_negative",
       description="Amount below cost target",
       lower_bound=0,
       upper_bound=float('inf'),
       desired=True  # We want to maximize savings
   )
   goal_vars.add_object(cost_savings)

   # Quality deviation - minimize any deviation from target
   quality_deviation = OXDeviationVar(
       name="quality_deviation",
       description="Deviation from quality target",
       lower_bound=0,
       upper_bound=float('inf'),
       desired=False  # Any deviation is undesirable
   )
   goal_vars.add_object(quality_deviation)

   # Print deviation variable details
   for var in goal_vars:
       print(f"{var.name}: desired={var.desired}")
       print(f"  String representation: {str(var)}")

Variable Collections
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: OXVariableSet
   :members:
   :undoc-members:
   :show-inheritance:

Variable Architecture
---------------------

OptiX variables are designed for optimization problems with the following key features:

* **Bounds Management**: All variables support lower and upper bounds with automatic validation
* **Relationship Tracking**: UUID-based linking to business entities through related_data
* **Value Storage**: Optional value assignment for initial solutions or fixed variables  
* **Goal Programming**: Specialized deviation variables with desirability indicators

Examples
--------

Creating Variables
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from variables import OXVariable
   from uuid import uuid4

   # Create a basic decision variable
   production_rate = OXVariable(
       name="production_rate",
       description="Daily production rate (units/day)",
       lower_bound=0.0,
       upper_bound=1000.0,
       value=500.0  # Optional initial value
   )

   # Create a variable with entity relationships
   facility_id = uuid4()
   machine_hours = OXVariable(
       name="machine_hours",
       description="Machine operating hours per day",
       lower_bound=0,
       upper_bound=24,
       related_data={"facility": facility_id}
   )

   # Variables auto-generate names if not provided
   auto_var = OXVariable(
       description="Automatically named variable",
       lower_bound=0,
       upper_bound=100
   )
   print(f"Auto-generated name: {auto_var.name}")  # Will be "var_<uuid>"

   print(f"Production rate bounds: [{production_rate.lower_bound}, {production_rate.upper_bound}]")
   print(f"Machine hours facility: {machine_hours.related_data.get('facility')}")

Variable Sets and Collections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from variables import OXVariableSet, OXVariable

   # Create variable set
   variables = OXVariableSet()

   # Add variables for production planning
   products = ["A", "B", "C"]
   factories = ["Factory_1", "Factory_2"]

   for product in products:
       for factory in factories:
           var = OXVariable(
               name=f"production_{product}_{factory}",
               description=f"Production of {product} at {factory}",
               lower_bound=0,
               upper_bound=500,
               variable_type="continuous"
           )
           variables.add_variable(var)

   print(f"Total variables: {len(variables)}")

   # Search for specific variables
   product_a_vars = variables.search_by_function(
       lambda v: "product_A" in v.name
   )
   print(f"Product A variables: {len(product_a_vars)}")

   # Search by name pattern
   factory_1_vars = variables.search_by_name("Factory_1")
   print(f"Factory 1 variables: {len(factory_1_vars)}")

   # Search by type
   continuous_vars = variables.search_by_type("continuous")
   print(f"Continuous variables: {len(continuous_vars)}")

Advanced Variable Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def create_transportation_variables(origins, destinations, products):
       """Create variables for a transportation problem."""
       
       variables = OXVariableSet()
       
       for origin in origins:
           for destination in destinations:
               for product in products:
                   # Flow variable
                   flow_var = OXVariable(
                       name=f"flow_{origin.id}_{destination.id}_{product.id}",
                       description=f"Flow of {product.name} from {origin.name} to {destination.name}",
                       lower_bound=0,
                       upper_bound=min(origin.capacity, destination.demand[product.id]),
                       related_data={
                           "origin": origin.id,
                           "destination": destination.id,
                           "product": product.id
                       }
                   )
                   variables.add_object(flow_var)
                   
                   # Binary variable for route activation
                   route_var = OXVariable(
                       name=f"route_{origin.id}_{destination.id}_{product.id}",
                       description=f"Route activation for {product.name} from {origin.name} to {destination.name}",
                       lower_bound=0,
                       upper_bound=1,
                       related_data={
                           "origin": origin.id,
                           "destination": destination.id,
                           "product": product.id,
                           "is_binary": True
                       }
                   )
                   variables.add_object(route_var)
       
       return variables

   # Usage example
   # variables = create_transportation_variables(warehouses, customers, products)

Working with Variable Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from variables import OXVariable

   # Create variable with initial value
   machine_capacity = OXVariable(
       name="machine_capacity",
       description="Machine processing capacity",
       lower_bound=0,
       upper_bound=1000,
       value=500  # Initial value
   )

   # Update value
   machine_capacity.value = 800
   print(f"Current value: {machine_capacity.value}")

   # Update bounds directly
   machine_capacity.lower_bound = 100
   machine_capacity.upper_bound = 1200
   print(f"New bounds: [{machine_capacity.lower_bound}, {machine_capacity.upper_bound}]")

   # Manual validation of values
   test_values = [50, 150, 1100, 1300]
   for test_value in test_values:
       is_valid = machine_capacity.lower_bound <= test_value <= machine_capacity.upper_bound
       print(f"Value {test_value} is within bounds: {is_valid}")

Variable Search and Filtering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def demonstrate_variable_search(variable_set):
       """Demonstrate various variable search capabilities."""
       from uuid import uuid4
       
       print("Variable Search Examples")
       print("=" * 40)
       
       # Search by name pattern using list comprehension
       production_vars = [v for v in variable_set if "production" in v.name.lower()]
       print(f"Production variables: {len(production_vars)}")
       
       # Search by bounds
       bounded_vars = [v for v in variable_set if 0 <= v.lower_bound and v.upper_bound <= 100]
       print(f"Variables bounded between 0 and 100: {len(bounded_vars)}")
       
       # Search by description keywords
       cost_vars = [v for v in variable_set if "cost" in v.description.lower()]
       print(f"Cost-related variables: {len(cost_vars)}")
       
       # Query by relationships (if you've set up related_data)
       # Example: Find all variables related to a specific facility
       facility_id = uuid4()  # Example facility ID
       facility_vars = variable_set.query(facility=facility_id)
       print(f"Variables for facility {facility_id}: {len(facility_vars)}")
       
       # Find variables by checking related_data for binary indicators
       binary_vars = [v for v in variable_set if v.related_data.get("is_binary", False)]
       print(f"Binary variables: {len(binary_vars)}")
       
       # Get specific variables by name
       target_names = ["production_A_Factory_1", "production_B_Factory_1"]
       specific_vars = [v for v in variable_set if v.name in target_names]
       print(f"Specific named variables found: {len(specific_vars)}")

Dynamic Variable Creation
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def create_scheduling_variables(tasks, time_periods, resources):
       """Create variables for a scheduling problem with dynamic structure."""
       
       variables = OXVariableSet()
       
       # Task assignment variables (binary)
       for task in tasks:
           for period in time_periods:
               if task.can_start_in_period(period):
                   var = OXVariable(
                       name=f"start_{task.id}_period_{period}",
                       description=f"Task {task.name} starts in period {period}",
                       lower_bound=0,
                       upper_bound=1,
                       related_data={"task": task.id, "period": period, "is_binary": True}
                   )
                   variables.add_object(var)
       
       # Resource allocation variables (continuous)
       for task in tasks:
           for resource in resources:
               if task.can_use_resource(resource):
                   var = OXVariable(
                       name=f"allocation_{task.id}_{resource.id}",
                       description=f"Allocation of {resource.name} to {task.name}",
                       lower_bound=0,
                       upper_bound=resource.capacity,
                       related_data={"task": task.id, "resource": resource.id}
                   )
                   variables.add_object(var)
       
       # Completion time variables (continuous)
       for task in tasks:
           var = OXVariable(
               name=f"completion_{task.id}",
               description=f"Completion time of {task.name}",
               lower_bound=task.earliest_start,
               upper_bound=task.latest_finish,
               related_data={"task": task.id}
           )
           variables.add_object(var)
       
       return variables

Variable Validation and Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def validate_variable_set(variable_set):
       """Validate a variable set for common issues."""
       
       issues = []
       
       # Check for duplicate names
       names = [var.name for var in variable_set]
       duplicate_names = set([name for name in names if names.count(name) > 1])
       
       if duplicate_names:
           issues.append(f"Duplicate variable names: {duplicate_names}")
       
       # Check for invalid bounds
       invalid_bounds_vars = []
       for var in variable_set:
           if var.lower_bound > var.upper_bound:
               invalid_bounds_vars.append(var.name)
       
       if invalid_bounds_vars:
           issues.append(f"Variables with invalid bounds: {invalid_bounds_vars}")
       
       # Check for extremely large bounds (potential numerical issues)
       large_bound_vars = []
       for var in variable_set:
           if abs(var.lower_bound) > 1e6 or abs(var.upper_bound) > 1e6:
               large_bound_vars.append(var.name)
       
       if large_bound_vars:
           issues.append(f"Variables with very large bounds: {large_bound_vars}")
       
       # Check for missing descriptions
       no_description_vars = [var.name for var in variable_set if not var.description]
       
       if no_description_vars:
           issues.append(f"Variables without descriptions: {no_description_vars}")
       
       return issues

   def analyze_variable_structure(variable_set):
       """Analyze the structure and properties of a variable set."""
       
       analysis = {
           'total_variables': len(variable_set),
           'variable_types': {},
           'bound_statistics': {
               'min_lower_bound': float('inf'),
               'max_lower_bound': float('-inf'),
               'min_upper_bound': float('inf'),
               'max_upper_bound': float('-inf'),
               'unbounded_variables': 0
           },
           'fixed_variables': 0,
           'name_patterns': {}
       }
       
       # Since OXVariable doesn't have variable_type attribute, we can infer from bounds
       for var in variable_set:
           # Infer type based on bounds and related_data
           if var.related_data.get("is_binary", False) or (var.lower_bound == 0 and var.upper_bound == 1):
               var_type = "binary"
           elif var.lower_bound == int(var.lower_bound) and var.upper_bound == int(var.upper_bound):
               var_type = "integer"
           else:
               var_type = "continuous"
           analysis['variable_types'][var_type] = analysis['variable_types'].get(var_type, 0) + 1
           
           # Bound statistics
           if var.lower_bound != float('-inf'):
               analysis['bound_statistics']['min_lower_bound'] = min(
                   analysis['bound_statistics']['min_lower_bound'], var.lower_bound
               )
               analysis['bound_statistics']['max_lower_bound'] = max(
                   analysis['bound_statistics']['max_lower_bound'], var.lower_bound
               )
           
           if var.upper_bound != float('inf'):
               analysis['bound_statistics']['min_upper_bound'] = min(
                   analysis['bound_statistics']['min_upper_bound'], var.upper_bound
               )
               analysis['bound_statistics']['max_upper_bound'] = max(
                   analysis['bound_statistics']['max_upper_bound'], var.upper_bound
               )
           
           if (var.lower_bound == float('-inf') or var.upper_bound == float('inf')):
               analysis['bound_statistics']['unbounded_variables'] += 1
           
           # Check if variable has a fixed value
           if var.value is not None:
               analysis['fixed_variables'] += 1
           
           # Name patterns
           name_parts = var.name.split('_')
           if len(name_parts) > 1:
               pattern = name_parts[0]
               analysis['name_patterns'][pattern] = analysis['name_patterns'].get(pattern, 0) + 1
       
       return analysis

   def print_variable_analysis(analysis):
       """Print formatted variable analysis."""
       
       print("Variable Set Analysis")
       print("=" * 50)
       print(f"Total Variables: {analysis['total_variables']}")
       print(f"Fixed Variables: {analysis['fixed_variables']}")
       
       print("\nVariable Types:")
       for var_type, count in analysis['variable_types'].items():
           percentage = (count / analysis['total_variables']) * 100
           print(f"  {var_type}: {count} ({percentage:.1f}%)")
       
       print("\nBound Statistics:")
       bounds = analysis['bound_statistics']
       if bounds['min_lower_bound'] != float('inf'):
           print(f"  Lower bounds range: [{bounds['min_lower_bound']}, {bounds['max_lower_bound']}]")
       if bounds['min_upper_bound'] != float('inf'):
           print(f"  Upper bounds range: [{bounds['min_upper_bound']}, {bounds['max_upper_bound']}]")
       print(f"  Unbounded variables: {bounds['unbounded_variables']}")
       
       print("\nName Patterns:")
       sorted_patterns = sorted(analysis['name_patterns'].items(), key=lambda x: x[1], reverse=True)
       for pattern, count in sorted_patterns[:10]:  # Top 10 patterns
           print(f"  {pattern}_*: {count} variables")

   # Usage examples
   issues = validate_variable_set(variable_set)
   if issues:
       print("Variable Set Issues:")
       for issue in issues:
           print(f"  - {issue}")
   else:
       print("Variable set validation passed!")

   analysis = analyze_variable_structure(variable_set)
   print_variable_analysis(analysis)

Variable Transformation and Scaling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def scale_variables(variable_set, scaling_factor=1.0):
       """Scale variable bounds by a given factor."""
       
       scaled_variables = OXVariableSet()
       
       for var in variable_set:
           scaled_var = OXVariable(
               name=var.name,
               description=var.description,
               lower_bound=var.lower_bound * scaling_factor,
               upper_bound=var.upper_bound * scaling_factor,
               value=var.value * scaling_factor if var.value is not None else None,
               related_data=var.related_data.copy()
           )
           scaled_variables.add_object(scaled_var)
       
       return scaled_variables

   def normalize_variables(variable_set):
       """Normalize variables to [0, 1] range."""
       
       normalized_variables = OXVariableSet()
       
       for var in variable_set:
           # Check if variable appears to be binary
           is_binary = var.related_data.get("is_binary", False) or (var.lower_bound == 0 and var.upper_bound == 1)
           
           if not is_binary:
               # Normalize to [0, 1] range
               normalized_var = OXVariable(
                   name=f"norm_{var.name}",
                   description=f"Normalized {var.description}",
                   lower_bound=0.0,
                   upper_bound=1.0
               )
               normalized_variables.add_object(normalized_var)
           else:
               # Keep binary variables as is
               normalized_variables.add_object(var)
       
       return normalized_variables

   def create_auxiliary_variables(base_variables, auxiliary_type="slack"):
       """Create auxiliary variables (slack, surplus, artificial) for constraints."""
       
       auxiliary_variables = OXVariableSet()
       
       for i, base_var in enumerate(base_variables):
           if auxiliary_type == "slack":
               aux_var = OXVariable(
                   name=f"slack_{i}",
                   description=f"Slack variable for constraint {i}",
                   lower_bound=0,
                   upper_bound=float('inf')
               )
           elif auxiliary_type == "surplus":
               aux_var = OXVariable(
                   name=f"surplus_{i}",
                   description=f"Surplus variable for constraint {i}",
                   lower_bound=0,
                   upper_bound=float('inf')
               )
           elif auxiliary_type == "artificial":
               aux_var = OXVariable(
                   name=f"artificial_{i}",
                   description=f"Artificial variable for constraint {i}",
                   lower_bound=0,
                   upper_bound=float('inf')
               )
           
           auxiliary_variables.add_object(aux_var)
       
       return auxiliary_variables

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def optimize_variable_access(variable_set):
       """Optimize variable set for faster access patterns."""
       
       # Create lookup dictionaries for O(1) access
       name_lookup = {var.name: var for var in variable_set}
       id_lookup = {var.id: var for var in variable_set}
       type_lookup = {}
       
       # Group variables by inferred type
       for var in variable_set:
           # Infer type from bounds and related_data
           if var.related_data.get("is_binary", False) or (var.lower_bound == 0 and var.upper_bound == 1):
               var_type = "binary"
           elif var.lower_bound == int(var.lower_bound) and var.upper_bound == int(var.upper_bound):
               var_type = "integer"
           else:
               var_type = "continuous"
           
           if var_type not in type_lookup:
               type_lookup[var_type] = []
           type_lookup[var_type].append(var)
       
       # Create optimized variable set with fast lookups
       class OptimizedVariableSet(OXVariableSet):
           def __init__(self, variables):
               super().__init__()
               self.data = list(variables)
               self._name_lookup = name_lookup
               self._id_lookup = id_lookup
               self._type_lookup = type_lookup
           
           def get_variable_by_name_fast(self, name):
               return self._name_lookup.get(name)
           
           def get_variable_by_id_fast(self, var_id):
               return self._id_lookup.get(var_id)
           
           def get_variables_by_type_fast(self, var_type):
               return self._type_lookup.get(var_type, [])
       
       return OptimizedVariableSet(variable_set)

   # Usage
   optimized_vars = optimize_variable_access(variable_set)
   var = optimized_vars.get_variable_by_name_fast("production_A_Factory_1")

Variable Export and Import
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import json
   from datetime import datetime

   def export_variables_to_json(variable_set, filename=None):
       """Export variable set to JSON format."""
       
       if filename is None:
           filename = f"variables_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
       
       export_data = {
           'metadata': {
               'export_date': datetime.now().isoformat(),
               'total_variables': len(variable_set),
               'optix_version': '1.0.0'
           },
           'variables': []
       }
       
       for var in variable_set:
           var_data = {
               'id': str(var.id),
               'name': var.name,
               'description': var.description,
               'lower_bound': var.lower_bound if var.lower_bound != float('-inf') else None,
               'upper_bound': var.upper_bound if var.upper_bound != float('inf') else None,
               'value': var.value,
               'related_data': {k: str(v) for k, v in var.related_data.items()}
           }
           export_data['variables'].append(var_data)
       
       with open(filename, 'w') as f:
           json.dump(export_data, f, indent=2)
       
       return filename

   def import_variables_from_json(filename):
       """Import variable set from JSON format."""
       
       with open(filename, 'r') as f:
           import_data = json.load(f)
       
       variable_set = OXVariableSet()
       
       for var_data in import_data['variables']:
           # Reconstruct related_data with UUIDs
           from uuid import UUID
           related_data = {}
           for k, v in var_data.get('related_data', {}).items():
               try:
                   related_data[k] = UUID(v)
               except:
                   related_data[k] = v
           
           var = OXVariable(
               name=var_data['name'],
               description=var_data['description'],
               lower_bound=var_data.get('lower_bound', 0),
               upper_bound=var_data.get('upper_bound', float('inf')),
               value=var_data.get('value'),
               related_data=related_data
           )
           
           variable_set.add_object(var)
       
       return variable_set

   # Usage
   filename = export_variables_to_json(variable_set)
   print(f"Variables exported to {filename}")
   
   imported_variables = import_variables_from_json(filename)
   print(f"Imported {len(imported_variables)} variables")

See Also
--------

* :doc:`problem` - Problem classes that use variables
* :doc:`constraints` - Constraint definitions that reference variables
* :doc:`data` - Database integration for variable creation
* :doc:`../user_guide/variables` - Advanced variable management guide