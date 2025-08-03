OptiX - Mathematical Optimization Framework
==========================================

.. image:: ../_static/optix_logo.svg
   :alt: OptiX Logo
   :align: center
   :class: optix-logo

|

Welcome to **OptiX**, a comprehensive Python framework for mathematical optimization problems, supporting 
Constraint Satisfaction Problems (CSP), Linear Programming (LP), and Goal Programming (GP) with multi-solver architecture.

.. raw:: html

   <div class="feature-grid">
     <div class="feature-card">
       <h3>🎯 Multi-Problem Types</h3>
       <p>Support for CSP, LP, and GP with progressive complexity and hierarchical problem modeling.</p>
     </div>
     <div class="feature-card">
       <h3>🔧 Multi-Solver Support</h3>
       <p>Integrated OR-Tools and Gurobi solvers with extensible architecture for custom solvers.</p>
     </div>
     <div class="feature-card">
       <h3>⚡ Advanced Constraints</h3>
       <p>Special constraints for non-linear operations: multiplication, division, modulo, and conditional logic.</p>
     </div>
     <div class="feature-card">
       <h3>🗄️ Database Integration</h3>
       <p>Built-in data management with OXData and OXDatabase for complex optimization scenarios.</p>
     </div>
     <div class="feature-card">
       <h3>📈 Goal Programming</h3>
       <p>Multi-objective optimization with goal constraints and deviation variables for conflicting objectives.</p>
     </div>
     <div class="feature-card">
       <h3>🧪 Comprehensive Testing</h3>
       <p>Full test coverage with real-world examples including bus assignment and diet optimization problems.</p>
     </div>
   </div>

Quick Start
-----------

Install OptiX using Poetry:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/yourusername/optix.git
   cd OptiX

   # Install dependencies
   poetry install

   # Activate virtual environment
   poetry shell

Create your first optimization problem:

.. code-block:: python

   from problem import OXLPProblem, ObjectiveType
   from constraints import RelationalOperators
   from solvers import solve

   # Create a Linear Programming problem
   problem = OXLPProblem()

   # Add decision variables
   problem.create_decision_variable("x1", "Variable 1", 0, 10)
   problem.create_decision_variable("x2", "Variable 2", 0, 15)

   # Add constraints: 2x1 + 3x2 <= 20
   problem.create_constraint(
       variables=[var.id for var in problem.variables.search_by_function(lambda x: x.name in ["x1", "x2"])],
       weights=[2, 3],
       operator=RelationalOperators.LESS_THAN_EQUAL,
       value=20
   )

   # Set objective: maximize 5x1 + 4x2
   problem.create_objective_function(
       variables=[var.id for var in problem.variables.search_by_function(lambda x: x.name in ["x1", "x2"])],
       weights=[5, 4],
       objective_type=ObjectiveType.MAXIMIZE
   )

   # Solve the problem
   status, solution = solve(problem, 'ORTools')

Problem Types
-------------

OptiX supports three main problem types with increasing complexity:

.. raw:: html

   <div class="problem-type-section csp">

**Constraint Satisfaction Problems (CSP)**

Focus on finding feasible solutions that satisfy all constraints without optimization.

.. code-block:: python

   from problem import OXCSPProblem
   
   csp = OXCSPProblem()
   # Variables and constraints only
   # Focus on finding feasible solutions

.. raw:: html

   </div>

.. raw:: html

   <div class="problem-type-section lp">

**Linear Programming (LP)**

Extends CSP with objective function optimization for single-objective problems.

.. code-block:: python

   from problem import OXLPProblem, ObjectiveType
   
   lp = OXLPProblem()
   # CSP + objective function optimization
   # Single objective optimization (minimize/maximize)

.. raw:: html

   </div>

.. raw:: html

   <div class="problem-type-section gp">

**Goal Programming (GP)**

Extends LP with multi-objective goal constraints and deviation variables.

.. code-block:: python

   from problem import OXGPProblem
   
   gp = OXGPProblem()
   # LP + multi-objective goal constraints with deviation variables
   # Handle conflicting objectives with priority levels

.. raw:: html

   </div>

Supported Solvers
-----------------

.. raw:: html

   <div style="margin: 2rem 0;">
     <span class="solver-badge ortools">OR-Tools</span>
     <span class="solver-badge gurobi">Gurobi</span>
     <span class="solver-badge extensible">Extensible</span>
   </div>

* **OR-Tools**: Google's open-source optimization suite with comprehensive algorithm support
* **Gurobi**: Commercial optimization solver with high performance and advanced features
* **Extensible Architecture**: Easy integration of custom solvers through unified interface

Performance Guidelines
----------------------

.. raw:: html

   <table class="performance-table">
     <thead>
       <tr>
         <th>Problem Size</th>
         <th>Variables</th>
         <th>Constraints</th>
         <th>Expected Solve Time</th>
       </tr>
     </thead>
     <tbody>
       <tr>
         <td><strong>Small</strong></td>
         <td>&lt; 1,000</td>
         <td>&lt; 1,000</td>
         <td>&lt; 1 second</td>
       </tr>
       <tr>
         <td><strong>Medium</strong></td>
         <td>1,000 - 10,000</td>
         <td>1,000 - 10,000</td>
         <td>1 - 60 seconds</td>
       </tr>
       <tr>
         <td><strong>Large</strong></td>
         <td>10,000 - 100,000</td>
         <td>10,000 - 100,000</td>
         <td>1 - 30 minutes</td>
       </tr>
       <tr>
         <td><strong>Very Large</strong></td>
         <td>&gt; 100,000</td>
         <td>&gt; 100,000</td>
         <td>&gt; 30 minutes</td>
       </tr>
     </tbody>
   </table>

Documentation Structure
-----------------------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart
   examples/index

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user_guide/problem_types
   user_guide/solvers
   user_guide/constraints
   user_guide/variables
   user_guide/database_integration

.. toctree::
   :maxdepth: 2
   :caption: Tutorials

   tutorials/linear_programming
   tutorials/goal_programming
   tutorials/special_constraints
   tutorials/custom_solvers

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/diet_problem
   examples/bus_assignment
   examples/production_planning
   examples/portfolio_optimization

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/problem
   api/constraints
   api/variables
   api/solvers
   api/data
   api/utilities

.. toctree::
   :maxdepth: 2
   :caption: Development

   development/contributing
   development/testing
   development/architecture
   development/extending

.. toctree::
   :maxdepth: 1
   :caption: About

   changelog
   license
   authors

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. note::
   OptiX is under active development. For the latest updates and releases, 
   visit our `GitHub repository <https://github.com/yourusername/optix>`_.

.. tip::
   **New to optimization?** Start with our :doc:`quickstart` guide and explore 
   the :doc:`examples/diet_problem` for a practical introduction to linear programming.