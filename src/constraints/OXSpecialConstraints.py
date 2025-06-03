from dataclasses import dataclass, field
from uuid import UUID

from base import OXObject


@dataclass
class OXSpecialConstraint(OXObject):
    pass


@dataclass
class OXNonLinearEqualityConstraint(OXSpecialConstraint):
    output_variable: UUID = field(default_factory=UUID)


@dataclass
class OXMultiplicativeEqualityConstraint(OXNonLinearEqualityConstraint):
    input_variables: list[UUID] = field(default_factory=list)


@dataclass
class OXDivisionEqualityConstraint(OXNonLinearEqualityConstraint):
    input_variable: UUID = field(default_factory=UUID)
    denominator: int = 1


@dataclass
class OXModuloEqualityConstraint(OXNonLinearEqualityConstraint):
    input_variable: UUID = field(default_factory=UUID)
    denominator: int = 1


@dataclass
class OXSummationEqualityConstraint(OXSpecialConstraint):
    input_variables: list[UUID] = field(default_factory=list)
    output_variable: UUID = field(default_factory=UUID)


@dataclass
class OXConditionalConstraint(OXSpecialConstraint):
    indicator_variable: UUID = field(default_factory=UUID)
    input_constraint: UUID = field(default_factory=UUID)
    constraint_if_true: UUID = field(default_factory=UUID)
    constraint_if_false: UUID = field(default_factory=UUID)
