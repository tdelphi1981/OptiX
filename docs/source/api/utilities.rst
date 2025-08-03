Utilities Module
===============

The utilities module provides simple utility functions for dynamic class loading within the OptiX framework.
It contains basic functions that support object serialization and deserialization by enabling runtime class resolution.

.. currentmodule:: utilities

Module Functions
----------------

Class Loading Functions
~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: get_fully_qualified_name

.. autofunction:: load_class

Examples
--------

Basic Class Loading
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from utilities import get_fully_qualified_name, load_class
   from base.OXObject import OXObject

   # Generate module.ClassName string
   class_id = get_fully_qualified_name(OXObject)
   print(class_id)  # Output: 'base.OXObject.OXObject'

   # Dynamically load the class
   loaded_class = load_class(class_id)
   instance = loaded_class()

   # Verify roundtrip integrity
   assert loaded_class is OXObject

Integration with Serialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from utilities import get_fully_qualified_name, load_class
   from serialization import serialize_to_python_dict, deserialize_from_python_dict
   from problem.OXProblem import OXLPProblem

   # Create a problem
   problem = OXLPProblem(name="Test Problem")

   # Serialize to dictionary
   problem_dict = serialize_to_python_dict(problem)
   print(f"Class name in serialized data: {problem_dict['class_name']}")

   # Deserialize from dictionary
   restored_problem = deserialize_from_python_dict(problem_dict)
   assert restored_problem.name == "Test Problem"

Error Handling
~~~~~~~~~~~~~~

.. code-block:: python

   from utilities import load_class
   from base.OXception import OXception

   try:
       # Attempt to load a non-existent class
       bad_class = load_class("nonexistent.module.BadClass")
   except OXception as e:
       print(f"Failed to load class: {e}")

See Also
--------

* :doc:`base` - Base classes that use the utilities module
* :doc:`serialization` - Serialization system that relies on dynamic class loading
* :doc:`../development/architecture` - Framework architecture overview