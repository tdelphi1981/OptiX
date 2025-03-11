from dataclasses import dataclass, field
from enum import StrEnum
from fractions import Fraction

from base import OXObject
from constraints.OXpression import OXpression
from variables.OXDeviationVar import OXDeviationVar


class RelationalOperators(StrEnum):
    GREATER_THAN = ">"
    GREATER_THAN_EQUAL = ">="
    EQUAL = "="
    LESS_THAN = "<"
    LESS_THAN_EQUAL = "<="


@dataclass
class OXConstraint(OXObject):
    expression: OXpression = field(default_factory=OXpression)
    relational_operator: RelationalOperators = RelationalOperators.EQUAL
    rhs: float | int = 0

    @property
    def rhs_numerator(self):
        return Fraction(self.rhs).numerator

    @property
    def rhs_denominator(self):
        return Fraction(self.rhs).denominator

    def to_goal(self) -> "OXGoalConstraint":
        result = OXGoalConstraint()
        result.expression = self.expression
        result.relational_operator = RelationalOperators.EQUAL
        result.rhs = self.rhs
        if self.relational_operator in [RelationalOperators.LESS_THAN, RelationalOperators.LESS_THAN_EQUAL]:
            result.negative_deviation_variable.desired = True
        elif self.relational_operator in [RelationalOperators.GREATER_THAN, RelationalOperators.GREATER_THAN_EQUAL]:
            result.positive_deviation_variable.desired = True
        return result


@dataclass
class OXGoalConstraint(OXConstraint):
    positive_deviation_variable: OXDeviationVar = field(default_factory=OXDeviationVar)
    negative_deviation_variable: OXDeviationVar = field(default_factory=OXDeviationVar)

    @property
    def desired_variables(self) -> list[OXDeviationVar]:
        result = []
        if self.positive_deviation_variable.desired:
            result.append(self.positive_deviation_variable)
        if self.negative_deviation_variable.desired:
            result.append(self.negative_deviation_variable)
        return result

    @property
    def undesired_variables(self) -> list[OXDeviationVar]:
        result = []
        if not self.positive_deviation_variable.desired:
            result.append(self.positive_deviation_variable)
        if not self.negative_deviation_variable.desired:
            result.append(self.negative_deviation_variable)
        return result
