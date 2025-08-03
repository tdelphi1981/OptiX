# OptiX - Mathematical Optimization Framework

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/Poetry-1.4+-green.svg)](https://python-poetry.org/)
[![OR-Tools](https://img.shields.io/badge/OR--Tools-9.0+-orange.svg)](https://developers.google.com/optimization)
[![Gurobi](https://img.shields.io/badge/Gurobi-10.0+-red.svg)](https://www.gurobi.com/)
[![License](https://img.shields.io/badge/License-AFL--3.0-yellow.svg)](LICENSE)

OptiX is a comprehensive Python framework for mathematical optimization problems, supporting linear programming (LP), goal programming (GP), and constraint satisfaction problems (CSP). Built with multi-solver architecture and advanced constraint modeling capabilities.

## 🎯 System Overview

### Core Architecture

OptiX provides a hierarchical problem-solving framework with increasing complexity:

- **🔧 Multi-Solver Support**: OR-Tools and Gurobi integration with extensible solver interface
- **📊 Problem Types**: Progressive complexity from CSP → LP → GP
- **⚡ Advanced Constraints**: Support for special constraints (multiplication, division, modulo, conditional)
- **🗄️ Database Integration**: Built-in data management with OXData and OXDatabase
- **📈 Solution Management**: Comprehensive solution tracking and analysis
- **🔍 Variable Management**: Flexible variable creation from database objects using Cartesian products
- **📋 Goal Programming**: Multi-objective optimization with goal constraints and deviation variables

### Key Features

- **🚀 Hierarchical Problem Types**: CSP, LP, and GP with progressive complexity
- **🎛️ Flexible Modeling**: Create decision variables, constraints, and objective functions
- **🌐 Multi-Solver Architecture**: OR-Tools and Gurobi with unified interface
- **📱 Special Constraints**: Non-linear operations (×, ÷, mod, if-then)
- **🔄 Database Integration**: Object-relational mapping for complex data structures
- **📋 Comprehensive Examples**: Real-world problems including bus assignment and diet optimization
- **🧪 Full Test Coverage**: Comprehensive test suite for all major components

## 🛠️ Prerequisites

### System Requirements

- **Python**: 3.12 or higher
- **Poetry**: 1.4 or higher (for dependency management)
- **OR-Tools**: 9.0 or higher (Google's optimization library)
- **Gurobi**: 10.0 or higher (optional, commercial solver)

### Hardware Requirements

- **CPU**: Multi-core processor (recommended for complex optimization problems)
- **RAM**: Minimum 4GB (8GB recommended for large-scale problems)
- **Storage**: 1GB for framework and examples

## 📦 Installation

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/optix.git
cd OptiX

# Install dependencies using Poetry
poetry install

# Activate virtual environment
poetry shell
```

### Alternative: Using pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt  # If available
```

### Solver Installation

#### OR-Tools Setup (Free)

```bash
# OR-Tools is automatically installed with the framework
# Verify installation
poetry run python -c "import ortools; print('OR-Tools installed successfully')"
```

#### Gurobi Setup (Commercial)

```bash
# Download and install Gurobi from: https://www.gurobi.com/downloads/
# Get license from: https://www.gurobi.com/downloads/licenses/

# Set environment variables
export GUROBI_HOME="/opt/gurobi1000/linux64"
export PATH="${PATH}:${GUROBI_HOME}/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"

# Install Gurobi Python interface
poetry run pip install gurobipy

# Verify installation
poetry run python -c "import gurobipy; print('Gurobi installed successfully')"
```

## 🚀 Usage

### Basic Linear Programming Example

```python
from problem import OXLPProblem, ObjectiveType
from constraints import RelationalOperators
from solvers import solve

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

# Solve the problem with your preferred solver
status, solver = solve(problem, 'ORTools')  # or 'Gurobi'

# Access solutions
print(f"Status: {status}")
for solution in solver:
    print(solution)
    solution.print_solution_for(problem)
```

### Goal Programming Example

```python
from problem import OXGPProblem, ObjectiveType
from constraints import RelationalOperators
from solvers import solve

# Create a Goal Programming problem
gp_problem = OXGPProblem()

# Create decision variables
gp_problem.create_decision_variable("buses_line1", "Buses on Line 1", 0, 20)
gp_problem.create_decision_variable("buses_line2", "Buses on Line 2", 0, 15)

# Create goal constraints (with deviation variables)
gp_problem.create_goal_constraint(
    variables=["buses_line1", "buses_line2"],
    weights=[1, 1],
    target_value=25,
    description="Total fleet utilization target"
)

# Solve with goal programming approach
status, solution = solve(gp_problem, 'ORTools')
```

### Special Constraints Example

```python
from problem import OXLPProblem, SpecialConstraintType

problem = OXLPProblem()

# Create variables
problem.create_decision_variable("x", "Variable X", 0, 100)
problem.create_decision_variable("y", "Variable Y", 0, 100)
problem.create_decision_variable("result", "Result Variable", 0, 10000)

# Create special constraint: x * y = result
problem.create_special_constraint(
    constraint_type=SpecialConstraintType.MULTIPLICATION,
    left_variable_id=problem.variables.search_by_name("x")[0].id,
    right_variable_id=problem.variables.search_by_name("y")[0].id,
    result_variable_id=problem.variables.search_by_name("result")[0].id
)
```

## 📚 Example Problems

### 🚌 Bus Assignment Problem (Goal Programming)

Located in `samples/bus_assignment_problem/`, this comprehensive example demonstrates:

- **Goal Programming Implementation**: Multi-objective optimization with conflicting goals
- **Database Integration**: Custom data classes for buses, routes, and schedules
- **Variable Creation**: Dynamic variable generation from database objects using Cartesian products
- **Complex Constraints**: Fleet limitations, service requirements, and operational restrictions
- **Solution Analysis**: Detailed reporting and goal deviation analysis

```bash
# Run the basic bus assignment problem
poetry run python samples/bus_assignment_problem/01_simple_bus_assignment_problem.py

# Run the advanced version with comprehensive features
poetry run python samples/bus_assignment_problem/03_bus_assignment_problem.py
```

**Key Features Demonstrated:**
- Multi-objective optimization balancing cost, service quality, and resource utilization
- Real-world constraint modeling (bus restrictions, minimum service levels)
- Advanced solution analysis with goal deviation reporting
- Database-driven variable and constraint generation

### 🍎 Diet Problem (Classic Linear Programming)

Located in `samples/diet_problem/01_diet_problem.py`, this classic optimization example showcases:

- **Historical Context**: Implementation of Stigler's 1945 diet optimization problem
- **Cost Minimization**: Finding the cheapest combination of foods meeting nutritional requirements
- **Nutritional Constraints**: Minimum and maximum nutrient requirements
- **Practical Limitations**: Volume constraints and reasonable food quantity bounds
- **Mathematical Formulation**: Clear demonstration of LP problem structure

```bash
# Run the diet problem example
poetry run python samples/diet_problem/01_diet_problem.py
```

**Mathematical Formulation:**
```
Minimize: Σ(cost_i × quantity_i) for all foods i

Subject to:
- Σ(nutrient_content_ij × quantity_i) ≥ minimum_requirement_j for all nutrients j
- Σ(nutrient_content_ij × quantity_i) ≤ maximum_requirement_j for nutrients with upper bounds  
- Σ(volume_i × quantity_i) ≤ maximum_total_volume
- quantity_i ≥ 0 for all foods i
- quantity_i ≤ reasonable_upper_bound_i for all foods i
```

## 🔧 Problem Types

OptiX supports three main problem types with increasing complexity:

### 🎯 CSP (Constraint Satisfaction Problems)
```python
from problem import OXCSPProblem

csp = OXCSPProblem()
# Variables and constraints only
# Focus on finding feasible solutions
```

### 📈 LP (Linear Programming)
```python
from problem import OXLPProblem, ObjectiveType

lp = OXLPProblem()
# CSP + objective function optimization
# Single objective optimization (minimize/maximize)
```

### 🎛️ GP (Goal Programming)  
```python
from problem import OXGPProblem

gp = OXGPProblem()
# LP + multi-objective goal constraints with deviation variables
# Handle conflicting objectives with priority levels
```

## ⚡ Special Constraints

Advanced constraint types for non-linear operations:

| Constraint Type | Mathematical Form | Use Case |
|----------------|------------------|----------|
| **Multiplication** | `x₁ × x₂ = result` | Production capacity calculations |
| **Division** | `x₁ ÷ x₂ = result` | Rate and ratio computations |
| **Modulo** | `x₁ mod x₂ = result` | Scheduling and cyclic constraints |
| **Conditional** | `if condition then x₁ else x₂` | Decision-dependent constraints |

## 🚀 Supported Solvers

### OR-Tools (Google)
- **Type**: Open-source optimization suite
- **Strengths**: Fast, reliable, comprehensive algorithm support
- **Installation**: Automatic with OptiX
- **License**: Apache 2.0

### Gurobi (Commercial)
- **Type**: Commercial optimization solver  
- **Strengths**: High performance, advanced features, excellent support
- **Installation**: Requires separate license and installation
- **License**: Commercial (free academic licenses available)

### Extensible Architecture
- **Custom Solvers**: Easy to add new solvers through `OXSolverInterface`
- **Unified API**: Same code works with different solvers
- **Solver Factory**: Automatic solver selection and configuration

## 🧪 Testing

### Running Tests

```bash
# Run all tests
poetry run python -m pytest

# Run specific test file  
poetry run python -m pytest tests/test_OXProblem.py

# Run tests with specific pattern
poetry run python -m pytest -k "test_name_pattern"

# Run with verbose output
poetry run python -m pytest -v

# Run with coverage report
poetry run python -m pytest --cov=src --cov-report=html
```

### Test Structure

```
tests/
├── test_base/              # Base class tests
├── test_constraints/       # Constraint system tests  
├── test_data/             # Database and data tests
├── test_problem/          # Problem type tests
├── test_solvers/          # Solver interface tests
├── test_variables/        # Variable management tests
└── test_utilities/        # Utility function tests
```

## 📁 Project Structure

```
OptiX/
├── src/                           # Core framework source code
│   ├── base/                      # Core classes and exception handling
│   │   ├── OXObject.py           # Base class with UUID-based identity
│   │   └── OXception.py          # Custom exception handling
│   ├── constraints/               # Constraint definitions and special constraints
│   │   ├── OXConstraint.py       # Regular linear constraints
│   │   ├── OXConstraintSet.py    # Constraint collections
│   │   ├── OXSpecialConstraint.py # Non-linear constraints
│   │   └── OXpression.py         # Mathematical expressions
│   ├── data/                      # Database and data management
│   │   ├── OXData.py             # Individual data objects
│   │   └── OXDatabase.py         # Data collections and filtering
│   ├── problem/                   # Problem definition classes
│   │   └── OXProblem.py          # CSP, LP, and GP problem types
│   ├── solvers/                   # Solver interfaces and implementations
│   │   ├── OXSolverInterface.py  # Base solver interface
│   │   ├── OXSolverFactory.py    # Solver factory and unified solving
│   │   ├── ortools/              # OR-Tools solver integration
│   │   │   └── OXORToolsSolverInterface.py
│   │   └── gurobi/               # Gurobi solver integration
│   │       └── OXGurobiSolverInterface.py
│   ├── variables/                 # Variable definitions and management
│   │   ├── OXVariable.py         # Decision variables with bounds
│   │   └── OXVariableSet.py      # Variable collections with search
│   └── utilities/                 # Utility functions and serialization
│       ├── OXClassLoader.py      # Dynamic class loading
│       └── OXSerialization.py    # Object serialization utilities
├── samples/                       # Example problems and use cases
│   ├── bus_assignment_problem/    # Goal Programming examples
│   │   ├── 01_simple_bus_assignment_problem.py
│   │   ├── 02_simple_bus_assignment_problem.py
│   │   └── 03_bus_assignment_problem.py
│   └── diet_problem/              # Classic Linear Programming example
│       └── 01_diet_problem.py
├── tests/                         # Comprehensive test suite
│   ├── test_base/                # Base class tests
│   ├── test_constraints/         # Constraint system tests
│   ├── test_data/               # Database integration tests
│   ├── test_problem/            # Problem type tests
│   ├── test_solvers/            # Solver interface tests
│   ├── test_variables/          # Variable management tests
│   └── test_utilities/          # Utility function tests
├── pyproject.toml               # Poetry configuration and dependencies
├── CLAUDE.md                    # Development and AI assistant guidance
├── CHANGELOG.md                 # Version history and changes
└── README.md                    # This documentation file
```

## 🔧 Development Commands

### Installation and Environment

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Update dependencies
poetry update
```

### Testing Commands

```bash
# Run all tests
poetry run python -m pytest

# Run specific test file
poetry run python -m pytest tests/test_OXProblem.py

# Run tests with specific pattern
poetry run python -m pytest -k "test_name_pattern"

# Run with verbose output
poetry run python -m pytest -v

# Generate coverage report
poetry run python -m pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code with black
poetry run black src/ tests/ samples/

# Sort imports with isort  
poetry run isort src/ tests/ samples/

# Type checking with mypy
poetry run mypy src/

# Linting with flake8
poetry run flake8 src/ tests/ samples/
```

## 🔧 Configuration

### Solver Configuration

OptiX automatically detects available solvers and provides unified access:

```python
from solvers import solve, get_available_solvers

# Check available solvers
available = get_available_solvers()
print(f"Available solvers: {available}")

# Solve with specific solver
status, solution = solve(problem, 'ORTools')
status, solution = solve(problem, 'Gurobi')

# Automatic solver selection
status, solution = solve(problem)  # Uses best available solver
```

### Environment Variables

```bash
# Gurobi Configuration (if installed)
export GUROBI_HOME="/opt/gurobi1000/linux64"
export PATH="${PATH}:${GUROBI_HOME}/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"

# Logging Configuration
export LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
export LOG_FILE="optix.log"

# Performance Settings
export OPTIX_SOLVER_TIMEOUT="3600"  # Solver timeout in seconds
export OPTIX_THREAD_LIMIT="4"       # Maximum threads for parallel solving
```

## 📖 API Documentation

### Problem Creation Workflow

```python
# 1. Create problem instance
from problem import OXLPProblem, ObjectiveType

problem = OXLPProblem()

# 2. Create decision variables
var1 = problem.create_decision_variable(
    var_name="production_rate",
    description="Daily production rate",
    lower_bound=0,
    upper_bound=1000
)

# 3. Add constraints
from constraints import RelationalOperators

problem.create_constraint(
    variables=[var1.id],
    weights=[1],
    operator=RelationalOperators.LESS_THAN_EQUAL,
    value=500,
    description="Maximum production capacity"
)

# 4. Define objective function
problem.create_objective_function(
    variables=[var1.id],
    weights=[10],  # Profit per unit
    objective_type=ObjectiveType.MAXIMIZE
)

# 5. Solve the problem
from solvers import solve

status, solution = solve(problem, 'ORTools')
```

### Variable Management

```python
from variables import OXVariable, OXVariableSet

# Create individual variables
var = OXVariable(
    name="inventory_level",
    description="Current inventory level",
    lower_bound=0,
    upper_bound=10000,
    variable_type="continuous"
)

# Search variables by criteria
matching_vars = problem.variables.search_by_function(
    lambda v: "production" in v.name
)

# Filter variables by type
continuous_vars = problem.variables.search_by_function(
    lambda v: v.variable_type == "continuous"
)
```

### Database Integration

```python
from data import OXData, OXDatabase

# Create data objects
product = OXData(name="Product A", cost=10.5, demand=100)
factory = OXData(name="Factory 1", capacity=500, location="City A")

# Create database collections
products_db = OXDatabase([product])
factories_db = OXDatabase([factory])

# Create variables from database objects (Cartesian product)
problem.create_variables_from_database_objects(
    database_objects=[products_db, factories_db],
    variable_name_template="production_{0}_{1}",
    variable_description_template="Production of {0} at {1}",
    lower_bound=0,
    upper_bound=1000
)
```

## 🚀 Advanced Features

### Custom Solver Integration

```python
from solvers import OXSolverInterface, OXSolverSolution

class CustomSolverInterface(OXSolverInterface):
    """Custom solver implementation"""
    
    def solve(self, problem):
        # Implement solver-specific logic
        pass
    
    def get_solution(self):
        # Return solution in standard format
        return OXSolverSolution(...)

# Register custom solver
from solvers import register_solver
register_solver("CustomSolver", CustomSolverInterface)
```

### Performance Optimization

```python
# Parallel solving with multiple solvers
from solvers import solve_parallel

results = solve_parallel(
    problem, 
    solvers=['ORTools', 'Gurobi'],
    timeout=300  # 5 minutes
)

# Best solution selection
best_solution = min(results, key=lambda x: x.objective_value)
```

## 🔒 Security Considerations

### Input Validation

- All user inputs are validated for type safety and bounds checking
- SQL injection protection through parameterized queries (if database extensions used)
- Memory usage monitoring for large-scale problems

### Best Practices

1. **Validate Problem Formulation**: Always check constraint feasibility before solving
2. **Resource Limits**: Set appropriate solver timeouts and memory limits
3. **Data Sanitization**: Validate all numerical inputs and constraints
4. **Error Handling**: Implement proper exception handling for solver failures

## 📊 Performance Guidelines

### Problem Size Recommendations

| Problem Type | Variables | Constraints | Expected Solve Time |
|-------------|-----------|-------------|-------------------|
| **Small** | < 1,000 | < 1,000 | < 1 second |
| **Medium** | 1,000 - 10,000 | 1,000 - 10,000 | 1 - 60 seconds |
| **Large** | 10,000 - 100,000 | 10,000 - 100,000 | 1 - 30 minutes |
| **Very Large** | > 100,000 | > 100,000 | > 30 minutes |

### Optimization Tips

```python
# 1. Use appropriate variable bounds to reduce search space
problem.create_decision_variable("x", bounds=(0, 100))  # Better than unbounded

# 2. Simplify constraints when possible
# Instead of: x + y + z <= 10 AND x + y + z >= 10
# Use: x + y + z == 10

# 3. Choose the right solver for your problem type
# OR-Tools: Better for routing and scheduling problems
# Gurobi: Better for large-scale linear and quadratic problems

# 4. Use special constraints judiciously
# They can significantly increase solve time
```

## 🔧 Troubleshooting

### Common Issues

#### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'ortools'`

**Solution**:
```bash
# Reinstall dependencies
poetry install

# Verify OR-Tools installation
poetry run python -c "import ortools; print('OR-Tools version:', ortools.__version__)"

# If using conda, install OR-Tools separately
conda install -c conda-forge ortools-python
```

#### Solver Failures

**Problem**: `OXception: Solver failed to find solution`

**Solution**:
```python
# Check problem feasibility
from solvers import check_feasibility

is_feasible = check_feasibility(problem)
if not is_feasible:
    print("Problem is infeasible - check constraints")

# Increase solver timeout
status, solution = solve(problem, solver='ORTools', timeout=3600)

# Try different solver
status, solution = solve(problem, solver='Gurobi')
```

#### Performance Issues

**Problem**: Slow solving times for large problems

**Solution**:
```bash
# Enable parallel solving
export OPTIX_THREAD_LIMIT="8"

# Use Gurobi for better performance on large problems
poetry run python your_script.py --solver=Gurobi

# Profile your code to identify bottlenecks
poetry run python -m cProfile -o profile.stats your_script.py
```

#### Memory Issues

**Problem**: `MemoryError` for large-scale problems

**Solution**:
```python
# Reduce problem size by aggregating variables
# Use sparse constraint representation
# Implement incremental solving for very large problems

# Monitor memory usage
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

## 📖 Additional Resources

### Documentation

- **API Reference**: Comprehensive docstrings in all modules
- **Examples**: Real-world problems in `samples/` directory
- **Test Cases**: Extensive test coverage demonstrating usage patterns
- **Development Guide**: See `CLAUDE.md` for development guidelines

### External Resources

- [OR-Tools Documentation](https://developers.google.com/optimization)
- [Gurobi Documentation](https://www.gurobi.com/documentation/)
- [Linear Programming Theory](https://en.wikipedia.org/wiki/Linear_programming)
- [Goal Programming Overview](https://en.wikipedia.org/wiki/Goal_programming)

### Academic References

1. Stigler, G. J. (1945). "The Cost of Subsistence". Journal of Farm Economics
2. Charnes, A., & Cooper, W. W. (1961). "Management Models and Industrial Applications of Linear Programming"
3. Dantzig, G. B. (1963). "Linear Programming and Extensions"

## 👥 Contributing

### Development Guidelines

1. **Code Style**: Follow PEP 8 and use provided formatters
2. **Testing**: Add comprehensive tests for new functionality  
3. **Documentation**: Update docstrings and examples
4. **Git Workflow**: Use feature branches and meaningful commit messages
5. **Performance**: Consider algorithmic complexity for large-scale problems

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with appropriate tests
4. Run the test suite (`poetry run pytest`)
5. Update documentation as needed
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the Academic Free License ("AFL") v. 3.0 - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

**Tolga BERBER**
- **Email**: tolga.berber@fen.ktu.edu.tr
- **Institution**: Karadeniz Technical University
- **Department**: Computer Science
- **Role**: Lead Developer & Project Architect

**Beyzanur SİYAH**
- **Email**: beyzanursiyah@ktu.edu.tr  
- **Institution**: Karadeniz Technical University
- **Role**: Core Developer & Research Assistant

---

### 🚀 Ready to optimize? Start with our [examples](samples/) or dive into the [API documentation](#-api-documentation)!