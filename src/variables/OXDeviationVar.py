from dataclasses import dataclass

from variables.OXVariable import OXVariable


@dataclass
class OXDeviationVar(OXVariable):
    """A deviation variable for goal programming.

    This class extends OXVariable to represent a deviation variable, which
    measures how much a goal constraint is violated. In goal programming,
    the objective is typically to minimize undesired deviations.

    Attributes:
        desired (bool): A flag indicating whether the deviation is desired.
            Defaults to False.

    Examples:
        >>> pos_dev = OXDeviationVar(name="d+", desired=False)
        >>> neg_dev = OXDeviationVar(name="d-", desired=True)
        >>> print(pos_dev.desired)
        False
        >>> print(neg_dev.desired)
        True

    See Also:
        :class:`variables.OXVariable.OXVariable`
        :class:`constraints.OXConstraint.OXGoalConstraint`
    """
    desired: bool = False
