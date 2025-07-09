Overview
========

OptiX is a Python optimization framework that provides a unified interface for various optimization solvers. It allows users to define optimization problems in a consistent way and solve them using different backends.

Key Features
------------

* **Unified Interface**: Work with different optimization solvers through a common API
* **Extensible Design**: Easy to add new solvers and constraint types
* **Object-Oriented**: Clean, modular design with inheritance hierarchies
* **Type Safety**: Built with Python type hints for better development experience

Architecture
------------

The OptiX framework is built around several core components:

- **Base Classes**: Foundation classes that provide common functionality
- **Variables**: Representation of optimization variables
- **Constraints**: Definition and management of optimization constraints
- **Problems**: High-level problem definition interface
- **Solvers**: Backend solver interfaces and implementations
- **Data Management**: Tools for handling optimization data

Supported Solvers
------------------

Currently, OptiX supports:

* **OR-Tools**: Google's optimization tools for linear and mixed-integer programming

Getting Started
---------------

To get started with OptiX, see the :doc:`quickstart` guide for installation instructions and basic usage examples.