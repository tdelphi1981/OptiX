# OptiX

OptiX is a comprehensive Python framework for mathematical optimization problems, supporting linear programming (LP), goal programming (GP), and constraint satisfaction problems (CSP).

## Description

OptiX provides a comprehensive framework for defining and solving optimization problems. It features:
- **Multi-solver support**: Currently supports OR-Tools with extensible solver interface
- **Flexible problem modeling**: Create decision variables, constraints, and objective functions
- **Advanced constraint types**: Support for regular constraints and special constraints
- **Database integration**: Built-in data management with OXData and OXDatabase
- **Solution management**: Comprehensive solution tracking and analysis
- **Example problems**: Includes real-world examples like bus assignment problems

## Installation

OptiX requires Python 3.12 or higher. You can install it using Poetry:

```bash
# Clone the repository
git clone https://github.com/yourusername/optix.git
cd optix

# Install dependencies using Poetry
poetry install
```

## Usage

### Basic Linear Programming Example

```python
from problem.OXProblem import OXLPProblem, ObjectiveType
from constraints.OXConstraint import RelationalOperators
from solvers.OXSolverFactory import solve

# Create a new LP problem
problem = OXLPProblem()

# Create decision variables
problem.create_decision_variable(var_name="x1", description="Variable 1", lower_bound=0, upper_bound=10)
problem.create_decision_variable(var_name="x2", description="Variable 2", lower_bound=0, upper_bound=15)

# Create constraints
# For example: 2x1 + 3x2 <= 20
problem.create_constraint(
    variables=[var.id for var in problem.variables.search_by_function(lambda x: x.name in ["x1", "x2"])],
    weights=[2, 3],
    operator=RelationalOperators.LESS_THAN_EQUAL,
    value=20
)

# Create objective function
# For example: maximize 5x1 + 4x2
problem.create_objective_function(
    variables=[var.id for var in problem.variables.search_by_function(lambda x: x.name in ["x1", "x2"])],
    weights=[5, 4],
    objective_type=ObjectiveType.MAXIMIZE
)

# Solve the problem
status, solver = solve(problem, 'ORTools')

# Access solutions
print(f"Status: {status}")
for solution in solver:
    print(solution)
    solution.print_solution_for(problem)
```

### Advanced Example with Database Integration

See `samples/bus_assignment_problem/01_simple_bus_assignment_problem.py` for a comprehensive example that demonstrates:
- Database integration with custom data classes
- Variable creation from database objects
- Dynamic constraint and objective function creation
- Solution analysis and reporting

## Supported Solvers

- **OR-Tools**: Google's optimization tools (primary solver)
- **Extensible Interface**: Easy to add new solvers through `OXSolverInterface`

## Project Structure

- `src/base/`: Core classes and exception handling
- `src/constraints/`: Constraint definitions and special constraints
- `src/data/`: Database and data management
- `src/problem/`: Problem definition classes (LP, GP, CSP)
- `src/solvers/`: Solver interfaces and implementations
- `src/variables/`: Variable definitions and management
- `src/utilities/`: Utility functions and serialization
- `samples/`: Example problems and use cases
- `tests/`: Comprehensive test suite

## License

This project is licensed under the Academic Free License ("AFL") v. 3.0 - see the [LICENSE](LICENSE) file for details.

## Authors

- Tolga BERBER (tolga.berber@fen.ktu.edu.tr)
- Beyzanur SİYAH (beyzanursiyah@ktu.edu.tr)