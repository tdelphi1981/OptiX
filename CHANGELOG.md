# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- OR-Tools solver integration with `OXORToolsSolverInterface`
- Comprehensive solver interface framework (`OXSolverInterface`)
- Solution management system with `OXSolverSolution` and `OXSolutionStatus`
- Special constraints support (`OXSpecialConstraints`)
- Solver factory pattern for easy solver selection
- Bus assignment problem example demonstrating real-world usage
- Diet problem optimization example showcasing classic linear programming
- Enhanced constraint value tracking and evaluation
- Comprehensive package structure with proper `__init__.py` files
- Extended test coverage for all major components
- Comprehensive API documentation across all modules

### Enhanced
- Problem classes now support constraint satisfaction problems (CSP)
- Improved variable creation from database objects
- Enhanced expression handling in `OXpression`
- Better serialization support for complex data structures
- Extended utility functions for class loading and management
- Documentation coverage for base, data, constraints, OXpression, serialization, utilities, variables, solvers, and test modules
- Sample problem documentation with detailed API references

### Fixed
- Core framework bugs and improved test functionality
- Variable and constraint management in solver interfaces
- Solution retrieval and value tracking
- Database integration and object relationships
- Fraction calculation and import paths in constraints module

## [0.1.0] - 2024-06-01

### Added
- Initial release of OptiX
- Framework for defining and solving optimization problems
- Support for linear programming (LP) and goal programming (GP)
- Decision variables with bounds
- Constraint definition with relational operators
- Objective function creation (minimize/maximize)
- Custom exception handling with OXception
- Data management with OXData and OXDatabase
- Variable management with OXVariable and OXVariableSet
- Serialization utilities
- Class loading utilities

### Requirements
- Python 3.12 or higher
- Poetry for dependency management