Installation
============

This guide will help you install OptiX and its dependencies on your system.

.. raw:: html

   <div class="install-steps">

System Requirements
-------------------

.. raw:: html

   <div class="install-step">

**Python Requirements**

OptiX requires Python 3.12 or higher. Check your Python version:

.. code-block:: bash

   python --version

If you need to install or upgrade Python, visit the `official Python website <https://www.python.org/downloads/>`_.

.. raw:: html

   </div>

.. raw:: html

   <div class="install-step">

**Poetry Installation**

OptiX uses Poetry for dependency management. Install Poetry:

.. tabs::

   .. tab:: macOS/Linux

      .. code-block:: bash

         curl -sSL https://install.python-poetry.org | python3 -

   .. tab:: Windows (PowerShell)

      .. code-block:: powershell

         (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

   .. tab:: Alternative (pip)

      .. code-block:: bash

         pip install poetry

Verify Poetry installation:

.. code-block:: bash

   poetry --version

.. raw:: html

   </div>

.. raw:: html

   <div class="install-step">

**Hardware Recommendations**

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Component
     - Minimum
     - Recommended
   * - **CPU**
     - Dual-core processor
     - Quad-core or higher
   * - **RAM**
     - 4GB
     - 8GB or more
   * - **Storage**
     - 1GB free space
     - 5GB+ for development
   * - **Network**
     - Internet connection for installation
     - Stable connection for updates

.. raw:: html

   </div>

.. raw:: html

   </div>

Installing OptiX
-----------------

.. raw:: html

   <div class="install-steps">

.. raw:: html

   <div class="install-step">

**Clone the Repository**

.. code-block:: bash

   # Clone from GitHub
   git clone https://github.com/yourusername/optix.git
   cd OptiX

.. raw:: html

   </div>

.. raw:: html

   <div class="install-step">

**Install Dependencies**

.. code-block:: bash

   # Install all dependencies including development tools
   poetry install

   # Install only production dependencies
   poetry install --no-dev

.. raw:: html

   </div>

.. raw:: html

   <div class="install-step">

**Activate Virtual Environment**

.. code-block:: bash

   # Activate the Poetry virtual environment
   poetry shell

   # Or run commands with Poetry
   poetry run python your_script.py

.. raw:: html

   </div>

.. raw:: html

   </div>

Solver Installation
-------------------

OptiX supports multiple optimization solvers. Install the ones you need:

OR-Tools (Recommended)
~~~~~~~~~~~~~~~~~~~~~~

OR-Tools is automatically installed with OptiX dependencies.

.. code-block:: bash

   # Verify OR-Tools installation
   poetry run python -c "import ortools; print('OR-Tools version:', ortools.__version__)"

.. note::
   OR-Tools is free and open-source, making it the recommended solver for getting started.

Gurobi (Commercial)
~~~~~~~~~~~~~~~~~~~

.. raw:: html

   <div class="install-steps">

.. raw:: html

   <div class="install-step">

**Download and Install Gurobi**

1. Visit `Gurobi Downloads <https://www.gurobi.com/downloads/>`_
2. Create a free account
3. Download the appropriate version for your platform
4. Follow the installation instructions for your operating system

.. raw:: html

   </div>

.. raw:: html

   <div class="install-step">

**Get a License**

.. tabs::

   .. tab:: Academic License (Free)

      1. Visit `Gurobi Academic Licenses <https://www.gurobi.com/downloads/licenses/>`_
      2. Register with your academic email
      3. Download the license file
      4. Follow activation instructions

   .. tab:: Commercial License

      Contact Gurobi sales for commercial licensing options.

.. raw:: html

   </div>

.. raw:: html

   <div class="install-step">

**Set Environment Variables**

.. tabs::

   .. tab:: Linux/macOS

      Add to your ``.bashrc`` or ``.zshrc``:

      .. code-block:: bash

         export GUROBI_HOME="/opt/gurobi1000/linux64"
         export PATH="${PATH}:${GUROBI_HOME}/bin"
         export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"

   .. tab:: Windows

      Set environment variables in System Properties:

      .. code-block:: batch

         GUROBI_HOME=C:\gurobi1000\win64
         PATH=%PATH%;%GUROBI_HOME%\bin
         LD_LIBRARY_PATH=%LD_LIBRARY_PATH%;%GUROBI_HOME%\lib

.. raw:: html

   </div>

.. raw:: html

   <div class="install-step">

**Install Python Interface**

.. code-block:: bash

   # Install Gurobi Python package
   poetry run pip install gurobipy

   # Verify installation
   poetry run python -c "import gurobipy; print('Gurobi installed successfully')"

.. raw:: html

   </div>

.. raw:: html

   </div>

Alternative Installation Methods
--------------------------------

Using pip (Not Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you prefer pip over Poetry:

.. code-block:: bash

   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies (if requirements.txt exists)
   pip install -r requirements.txt

Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~

For contributing to OptiX development:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/yourusername/optix.git
   cd OptiX

   # Install with development dependencies
   poetry install --with dev,test,docs

   # Install pre-commit hooks
   poetry run pre-commit install

   # Run tests to verify installation
   poetry run pytest

Verification
------------

Test your installation with this simple script:

.. code-block:: python

   # test_installation.py
   from problem import OXLPProblem, ObjectiveType
   from constraints import RelationalOperators
   from solvers import solve, get_available_solvers

   def test_installation():
       print("=== OptiX Installation Test ===")
       
       # Check available solvers
       solvers = get_available_solvers()
       print(f"Available solvers: {solvers}")
       
       # Create a simple problem
       problem = OXLPProblem()
       problem.create_decision_variable("x", "Test variable", 0, 10)
       
       problem.create_constraint(
           variables=[problem.variables[0].id],
           weights=[1],
           operator=RelationalOperators.LESS_THAN_EQUAL,
           value=5
       )
       
       problem.create_objective_function(
           variables=[problem.variables[0].id],
           weights=[1],
           objective_type=ObjectiveType.MAXIMIZE
       )
       
       # Test solving
       for solver in solvers:
           try:
               status, solution = solve(problem, solver)
               print(f"✅ {solver}: {status}")
               if solution:
                   print(f"   Objective value: {solution[0].objective_value}")
           except Exception as e:
               print(f"❌ {solver}: {e}")
       
       print("\n✅ Installation test completed!")

   if __name__ == "__main__":
       test_installation()

Run the test:

.. code-block:: bash

   poetry run python test_installation.py

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Poetry not found**

.. code-block:: bash

   # Add Poetry to PATH (macOS/Linux)
   export PATH="$HOME/.local/bin:$PATH"
   
   # Restart your terminal and try again

**OR-Tools import error**

.. code-block:: bash

   # Reinstall OR-Tools
   poetry run pip uninstall ortools-python
   poetry install --force

**Gurobi license error**

.. code-block:: bash

   # Check license status
   grbgetkey your-license-key
   
   # Verify license file location
   echo $GRB_LICENSE_FILE

**Permission errors (Linux/macOS)**

.. code-block:: bash

   # Fix permissions for Poetry installation
   sudo chown -R $(whoami) ~/.local/share/pypoetry

Getting Help
~~~~~~~~~~~~

If you encounter issues:

1. Check the `GitHub Issues <https://github.com/yourusername/optix/issues>`_ page
2. Review the :doc:`../development/troubleshooting` section
3. Join our community discussions
4. Contact the development team

.. tip::
   **Quick Start**: Once installed, head to the :doc:`quickstart` guide to create your first optimization problem!

.. note::
   **Performance Note**: For large-scale problems, consider installing Gurobi for better performance, 
   especially for mixed-integer programming problems.