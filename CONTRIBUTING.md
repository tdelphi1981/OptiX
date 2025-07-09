# Contributing to OptiX

Thank you for your interest in contributing to OptiX! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- [Poetry](https://python-poetry.org/) for dependency management

### Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/optix.git
   cd optix
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

## Development Workflow

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bugfix-name
   ```

2. Make your changes, following the coding standards outlined below.

3. Write tests for your changes.

4. Run the tests to ensure they pass:
   ```bash
   pytest
   ```

   For specific test files:
   ```bash
   pytest tests/test_OXVariable.py
   ```

5. Commit your changes with a descriptive commit message:
   ```bash
   git commit -m "Add feature: your feature description"
   ```

6. Push your branch to the repository:
   ```bash
   git push origin feature/your-feature-name
   ```

7. Create a pull request against the main branch.

## Pull Request Process

1. Ensure your code follows the project's coding standards.
2. Update the README.md if necessary with details of changes to the interface.
3. Update the CHANGELOG.md following the format described below.
4. The pull request will be reviewed by the maintainers, who may request changes or improvements.
5. Once approved, your pull request will be merged.

## Coding Standards

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide for Python code.
- Use meaningful variable and function names.
- Write comprehensive docstrings for all functions, classes, and methods.
- Keep functions and methods focused on a single responsibility.
- Use type hints extensively (see `OXSolverInterface.py` for examples).
- Organize imports alphabetically within their groups.
- Use dataclasses for data structures when appropriate.
- Follow the existing naming conventions (e.g., `OX` prefix for main classes).
- Implement proper error handling with custom exceptions.
- Use abstract base classes for defining interfaces.

## Testing Guidelines

- Write unit tests for all new functionality.
- Ensure all tests pass before submitting a pull request.
- Aim for high test coverage of your code.
- Place tests in the `tests/` directory, following the existing structure.
- Test files should be named `test_<component>.py` (e.g., `test_OXVariable.py`).
- Include integration tests for solver implementations.
- Test both positive and negative scenarios (error handling).

## Documentation Guidelines

- Update documentation for any changes to the public API.
- Include examples where appropriate.
- Keep the README.md up to date with any significant changes.

## Versioning and Changelog

This project follows [Semantic Versioning](https://semver.org/) and uses the [Keep a Changelog](https://keepachangelog.com/) format.

When contributing, please update the CHANGELOG.md file with your changes under the "Unreleased" section, categorizing them as:

- `Added` for new features.
- `Changed` for changes in existing functionality.
- `Deprecated` for soon-to-be removed features.
- `Removed` for now removed features.
- `Fixed` for any bug fixes.
- `Security` in case of vulnerabilities.

Example:
```markdown
## [Unreleased]

### Added
- New feature description

### Fixed
- Bug fix description
```

## Project Structure

The project is organized as follows:

- `src/`: Source code
  - `base/`: Base classes and exceptions (`OXObject`, `OXObjectPot`, `OXception`)
  - `constraints/`: Constraint-related classes (`OXConstraint`, `OXSpecialConstraints`, `OXpression`)
  - `data/`: Data management classes (`OXData`, `OXDatabase`)
  - `problem/`: Problem definition classes (`OXLPProblem`, `OXCSPProblem`, etc.)
  - `serialization/`: Serialization utilities for data persistence
  - `solvers/`: Solver interfaces and implementations
    - `OXSolverInterface`: Abstract base class for all solvers
    - `OXSolverFactory`: Factory for creating and managing solvers
    - `ortools/`: OR-Tools specific implementation
  - `utilities/`: Utility functions and classes (`class_loaders`, etc.)
  - `variables/`: Variable-related classes (`OXVariable`, `OXVariableSet`)
- `samples/`: Example problems and use cases
  - `bus_assignment_problem/`: Real-world optimization examples
- `tests/`: Comprehensive test suite covering all components

## Contact

If you have any questions or need help, please contact the project maintainers:
- Tolga BERBER (tolga.berber@fen.ktu.edu.tr)
- Beyzanur SİYAH (beyzanursiyah@ktu.edu.tr)

Thank you for contributing to OptiX!