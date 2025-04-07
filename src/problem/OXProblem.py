import itertools
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID

from base import OXObject, OXception
from constraints.OXConstraint import OXConstraint, OXGoalConstraint, RelationalOperators
from constraints.OXpression import OXpression
from data.OXDatabase import OXDatabase
from variables.OXVariable import OXVariable
from variables.OXVariableSet import OXVariableSet


@dataclass
class OXProblem(OXObject):
    """Base class for optimization problems.

    This class provides the foundation for defining optimization problems,
    including variables, constraints, and a database of related data.

    Attributes:
        db (OXDatabase): A database of related data objects.
        variables (OXVariableSet): A set of decision variables.
        constraints (list[OXConstraint]): A list of constraints.

    Examples:
        >>> problem = OXProblem()
        >>> problem.create_decision_variable("x1", "Variable 1", 10, 0)
        >>> problem.create_decision_variable("x2", "Variable 2", 15, 0)
        >>> problem.create_constraint(
        ...     variables=[var.id for var in problem.variables],
        ...     weights=[2, 3],
        ...     operator=RelationalOperators.LESS_THAN_EQUAL,
        ...     value=20
        ... )
    """
    db: OXDatabase = field(default_factory=OXDatabase)
    variables: OXVariableSet = field(default_factory=OXVariableSet)
    constraints: list[OXConstraint] = field(default_factory=list)

    def create_variables_from_db(self,
                                 var_name_template: str = "",
                                 var_description_template: str = "",
                                 upper_bound: float | int = float("inf"),
                                 lower_bound: float | int = 0,
                                 *args):
        """Create variables based on objects in the database.

        Note:
            This method appears to be incomplete in the current implementation.

        Args:
            var_name_template (str): A template for variable names.
            var_description_template (str): A template for variable descriptions.
            upper_bound (float | int): The upper bound for the variables.
            lower_bound (float | int): The lower bound for the variables.
            *args: Object types to include in the variable creation.

        Raises:
            OXception: If an invalid object type is specified.
        """
        available_object_type_set = set(self.db.get_object_types())
        argument_set = set(args)
        invalid_arguments = argument_set.difference(available_object_type_set)
        if len(invalid_arguments) > 0:
            raise OXception(f"Invalid db object type(s) detected : {invalid_arguments}")
        object_type_names = []
        object_instances = []
        for object_type in argument_set:
            object_type_names.append(object_type)
            object_instances.append(self.db.search_by_function(
                lambda x: x.class_name.lower().endswith(object_type.lower())))

        for instances_tuple in itertools.product(object_instances):
            related_data = {}
            for i in range(len(object_type_names)):
                related_data[object_type_names[i]] = instances_tuple[i].id
            var_name = var_name_template.format(**related_data)
            var_description = var_description_template.format(**related_data)

    def create_decision_variable(self, var_name: str = "", description: str = "",
                                 upper_bound: float | int = float("inf"),
                                 lower_bound: float | int = 0,
                                 **kwargs):
        """Create a decision variable and add it to the problem.

        Args:
            var_name (str): The name of the variable.
            description (str): A description of the variable.
            upper_bound (float | int): The upper bound for the variable.
            lower_bound (float | int): The lower bound for the variable.
            **kwargs: Related data for the variable, where keys are object types
                and values are object IDs.

        Raises:
            OXception: If an invalid key is specified in kwargs.

        Examples:
            >>> problem.create_decision_variable(
            ...     var_name="x1",
            ...     description="Variable 1",
            ...     upper_bound=10,
            ...     lower_bound=0
            ... )
        """
        d_var = OXVariable(name=var_name, description=description, upper_bound=upper_bound, lower_bound=lower_bound)
        db_types = self.db.get_object_types()
        for key, value in kwargs.items():
            if key not in db_types:
                raise OXception(f"Invalid key {key} for decision variable.")
            d_var.related_data[key] = value
        self.variables.add_object(d_var)

    def create_constraint(self,
                          variable_search_function: Callable[[OXObject], bool] = None,
                          variables: list[UUID] = None,
                          weights: list[float | int] = None,
                          operator: RelationalOperators = RelationalOperators.LESS_THAN_EQUAL,
                          value: float | int = None):
        """Create a constraint and add it to the problem.

        Args:
            variable_search_function (Callable[[OXObject], bool], optional): A function
                to search for variables to include in the constraint.
            variables (list[UUID], optional): A list of variable IDs to include
                in the constraint.
            weights (list[float | int], optional): A list of weights for the variables.
                If not provided, all weights are set to 1.
            operator (RelationalOperators): The relational operator for the constraint.
                Defaults to LESS_THAN_EQUAL.
            value (float | int): The right-hand side value for the constraint.

        Raises:
            OXception: If neither variable_search_function nor variables is provided,
                if both are provided, if no variables are found, if the number of
                weights doesn't match the number of variables, or if value is None.

        Examples:
            >>> problem.create_constraint(
            ...     variables=[var1.id, var2.id],
            ...     weights=[2, 3],
            ...     operator=RelationalOperators.LESS_THAN_EQUAL,
            ...     value=20
            ... )
        """
