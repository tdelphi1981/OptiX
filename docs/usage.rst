.. _usage:

Usage
=====

Basic Usage
----------

Here's a simple example of how to use OptiX:

.. code-block:: python

    from optix.problem import OXProblem
    from optix.variables import OXVariable, OXVariableSet
    from optix.constraints import OXConstraint

    # Create a new optimization problem
    problem = OXProblem("My Optimization Problem")
    
    # Define variables
    x = OXVariable("x", lower_bound=0, upper_bound=10)
    y = OXVariable("y", lower_bound=0, upper_bound=10)
    
    # Add variables to the problem
    var_set = OXVariableSet("variables")
    var_set.add(x)
    var_set.add(y)
    problem.add_variable_set(var_set)
    
    # Define and add constraints
    # ...
    
    # Solve the problem
    # ...

Advanced Usage
-------------

For more advanced usage examples, please refer to the API documentation.