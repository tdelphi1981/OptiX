Examples
========

This section provides comprehensive, real-world examples demonstrating OptiX's capabilities
across different optimization problem types and application domains.

.. raw:: html

   <div class="feature-grid">
     <div class="feature-card">
       <h3>🍎 Diet Problem</h3>
       <p>Classic Linear Programming example showcasing cost minimization with nutritional constraints. 
       Perfect introduction to LP concepts with historical context.</p>
       <a href="diet_problem.html">View Example →</a>
     </div>
     <div class="feature-card">
       <h3>🚌 Bus Assignment</h3>
       <p>Advanced Goal Programming example for public transportation systems. 
       Demonstrates multi-objective optimization with real-world complexity.</p>
       <a href="bus_assignment.html">View Example →</a>
     </div>
     <div class="feature-card">
       <h3>🏭 Production Planning</h3>
       <p>Manufacturing optimization with resource constraints, inventory management, 
       and multi-period planning scenarios.</p>
       <a href="production_planning.html">View Example →</a>
     </div>
     <div class="feature-card">
       <h3>📈 Portfolio Optimization</h3>
       <p>Financial portfolio optimization with risk constraints, diversification requirements, 
       and return maximization objectives.</p>
       <a href="portfolio_optimization.html">View Example →</a>
     </div>
   </div>

Example Categories
------------------

By Problem Type
~~~~~~~~~~~~~~~

**Linear Programming (LP)**
  * :doc:`diet_problem` - Cost minimization with constraints
  * :doc:`production_planning` - Resource allocation and planning
  * Transportation and logistics examples

**Goal Programming (GP)**
  * :doc:`bus_assignment` - Multi-objective transportation planning
  * Workforce planning with multiple criteria
  * Project selection with competing goals

**Constraint Satisfaction (CSP)**
  * Scheduling and timetabling problems
  * Configuration and assignment problems
  * Feasibility checking examples

By Application Domain
~~~~~~~~~~~~~~~~~~~~

**Transportation & Logistics**
  * :doc:`bus_assignment` - Public transit optimization
  * Vehicle routing and scheduling
  * Supply chain optimization

**Manufacturing & Production**
  * :doc:`production_planning` - Manufacturing optimization
  * Inventory management
  * Capacity planning

**Finance & Investment**
  * :doc:`portfolio_optimization` - Investment allocation
  * Risk management
  * Capital budgeting

**Healthcare & Resources**
  * :doc:`diet_problem` - Nutritional planning
  * Hospital resource allocation
  * Treatment scheduling

By Complexity Level
~~~~~~~~~~~~~~~~~~

**Beginner** 📚
  * :doc:`diet_problem` - Simple LP formulation
  * Basic production planning
  * Single-objective problems

**Intermediate** 🎯
  * :doc:`bus_assignment` - Goal programming introduction
  * Multi-constraint problems
  * Database integration

**Advanced** 🚀
  * :doc:`portfolio_optimization` - Complex financial modeling
  * Multi-period optimization
  * Stochastic programming

Complete Example List
--------------------

.. toctree::
   :maxdepth: 2

   diet_problem
   bus_assignment
   production_planning
   portfolio_optimization

Quick Example Browser
--------------------

.. tabs::

   .. tab:: Linear Programming

      **Diet Problem** - Cost minimization
        Classic optimization problem minimizing food costs while meeting nutritional requirements.
        
        * **Complexity**: Beginner
        * **Concepts**: Linear constraints, objective optimization
        * **Domain**: Nutrition and health

      **Production Planning** - Resource allocation
        Manufacturing optimization balancing production costs, inventory, and demand.
        
        * **Complexity**: Intermediate  
        * **Concepts**: Multi-period planning, capacity constraints
        * **Domain**: Manufacturing

   .. tab:: Goal Programming

      **Bus Assignment** - Multi-objective transportation
        Public transit optimization balancing cost, service quality, and resource utilization.
        
        * **Complexity**: Intermediate
        * **Concepts**: Goal constraints, deviation variables
        * **Domain**: Transportation

   .. tab:: Advanced Applications

      **Portfolio Optimization** - Financial planning
        Investment allocation with risk management and diversification requirements.
        
        * **Complexity**: Advanced
        * **Concepts**: Risk modeling, correlation constraints
        * **Domain**: Finance

Example Features
----------------

Each example includes:

✅ **Complete Source Code** - Fully functional implementations
✅ **Mathematical Formulation** - Clear problem definition
✅ **Step-by-Step Explanation** - Detailed implementation guide  
✅ **Real-World Data** - Practical datasets and scenarios
✅ **Solution Analysis** - Results interpretation and insights
✅ **Extensions** - Ideas for further development
✅ **Performance Tips** - Optimization best practices

Getting Started
---------------

1. **Choose by Interest**: Select examples matching your domain
2. **Start Simple**: Begin with Diet Problem for LP basics
3. **Progress Gradually**: Move to Bus Assignment for GP concepts
4. **Customize**: Adapt examples to your specific needs
5. **Experiment**: Try the suggested extensions and variations

Running Examples
---------------

All examples are located in the ``samples/`` directory:

.. code-block:: bash

   # Navigate to examples
   cd samples/

   # Run diet problem
   poetry run python diet_problem/01_diet_problem.py

   # Run bus assignment  
   poetry run python bus_assignment_problem/03_bus_assignment_problem.py

Common Patterns
--------------

Variable Creation
~~~~~~~~~~~~~~~~

.. code-block:: python

   # From data objects
   for product in products_db:
       problem.create_decision_variable(
           var_name=f"production_{product.name}",
           description=f"Production level for {product.name}",
           lower_bound=0,
           upper_bound=product.max_capacity
       )

Constraint Patterns
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Resource constraints
   problem.create_constraint(
       variables=production_vars,
       weights=resource_consumption,
       operator=RelationalOperators.LESS_THAN_EQUAL,
       value=available_resources
   )

   # Demand constraints  
   problem.create_constraint(
       variables=[product_var],
       weights=[1],
       operator=RelationalOperators.GREATER_THAN_EQUAL,
       value=minimum_demand
   )

Solution Analysis
~~~~~~~~~~~~~~~~

.. code-block:: python

   def analyze_solution(solution, problem):
       print(f"Objective Value: {solution.objective_value}")
       
       for variable in problem.variables:
           value = solution.variable_values.get(variable.id, 0)
           if abs(value) > 1e-6:
               print(f"{variable.name}: {value:.2f}")

Best Practices
--------------

**Problem Modeling**
  * Start with simple formulations
  * Validate constraints early
  * Use meaningful variable names
  * Add comprehensive descriptions

**Performance**
  * Monitor problem size (variables/constraints)
  * Use appropriate variable bounds
  * Choose optimal solver for problem type
  * Profile large-scale problems

**Development**
  * Implement validation functions
  * Create visualization of results
  * Add sensitivity analysis
  * Document assumptions and limitations

Contributing Examples
--------------------

We welcome contributions of new examples! Please ensure:

* **Complete Implementation**: Working code with all dependencies
* **Clear Documentation**: Problem description and solution approach
* **Real-World Relevance**: Practical application scenarios
* **Educational Value**: Clear learning objectives
* **Code Quality**: Following project conventions

Submit examples via GitHub pull requests with:

1. Source code in ``samples/`` directory
2. Documentation in ``docs/source/examples/``
3. Test cases and validation
4. README with usage instructions

.. tip::
   **Learning Path**: Start with Diet Problem → Bus Assignment → Production Planning → Portfolio Optimization
   for a comprehensive understanding of OptiX capabilities.

.. note::
   All examples include comprehensive error handling, input validation, and detailed output analysis
   to demonstrate production-ready optimization applications.

See Also
--------

* :doc:`../quickstart` - Get started with basic concepts
* :doc:`../user_guide/index` - Understanding problem types and features
* :doc:`../tutorials/index` - Step-by-step learning modules
* :doc:`../api/index` - Complete API reference