import sys
from dataclasses import dataclass, field
from uuid import UUID

from base import OXObject, OXception


@dataclass
class OXVariable(OXObject):
    """A decision variable in an optimization problem.

    This class represents a decision variable with bounds and a current value.
    Variables can be linked to other objects in the system through the related_data
    dictionary.

    Attributes:
        name (str): The name of the variable. If not provided, it will be
            automatically generated as "var_<id>".
        description (str): A description of the variable.
        value (float | int | bool): The current value of the variable.
        upper_bound (float | int): The upper bound for the variable.
            Defaults to infinity.
        lower_bound (float | int): The lower bound for the variable.
            Defaults to 0.
        related_data (dict[str, UUID]): A dictionary mapping object types to
            object IDs, linking this variable to other objects in the system.

    Examples:
        >>> var = OXVariable(name="x1", description="Variable 1", lower_bound=0, upper_bound=10)
        >>> print(var.name)
        x1
        >>> print(var.lower_bound)
        0
        >>> print(var.upper_bound)
        10

    See Also:
        :class:`variables.OXDeviationVar.OXDeviationVar`
        :class:`variables.OXVariableSet.OXVariableSet`
    """
    name: str = ""
    description: str = ""
    value: float | int | bool = None
    upper_bound: float | int = float("inf")
    lower_bound: float | int = 0
    related_data: dict[str, UUID] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize the object after it is created.

        This method is automatically called after the object is initialized.
        It calls the parent's __post_init__ method and then ensures that the
        variable has a name, generating one based on the UUID if necessary.
        """
        super().__post_init__()
        if self.lower_bound > self.upper_bound:
            raise OXception("Lower bound cannot be greater than upper bound.")
        if self.name.strip() == "":
            self.name = f"var_{self.id}"
