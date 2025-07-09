Examples
========

This section contains examples of how to use OptiX for various optimization problems.

Bus Assignment Problem
----------------------

Here's an example based on the bus assignment problem from the samples:

.. literalinclude:: ../samples/bus_assignment_problem/01_simple_bus_assignment_problem.py
   :language: python
   :linenos:

More Examples
-------------

Additional examples can be found in the ``samples/`` directory of the OptiX repository. These examples demonstrate:

* Linear programming problems
* Mixed-integer programming
* Constraint satisfaction problems
* Custom solver implementations

Running Examples
----------------

To run the examples:

.. code-block:: bash

   cd samples/bus_assignment_problem
   python 01_simple_bus_assignment_problem.py