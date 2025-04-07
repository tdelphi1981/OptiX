# OptiX

OptiX is a Python library for mathematical optimization problems, particularly focused on linear programming (LP) and goal programming (GP).

## Description

OptiX provides a framework for defining and solving optimization problems. It allows users to:
- Create decision variables with bounds
- Define constraints with relational operators
- Create objective functions to minimize or maximize
- Work with goal constraints for goal programming

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

Here's a simple example of how to use OptiX to create and define a linear programming problem:

```python
from problem.OXProblem import OXLPProblem, ObjectiveType
from variables.OXVariable import OXVariable
from constraints.OXConstraint import RelationalOperators

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

# Now the problem is ready to be solved with your preferred solver
```

## License

This project is licensed under the Academic Free License ("AFL") v. 3.0 - see the [LICENSE](LICENSE) file for details.

## Authors

- Tolga BERBER (tolga.berber@fen.ktu.edu.tr)
- Beyzanur SİYAH (beyzanursiyah@ktu.edu.tr)