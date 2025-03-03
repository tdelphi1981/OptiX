import sys
from dataclasses import dataclass, field
from uuid import UUID

from base import OXObject


@dataclass
class OXVariable(OXObject):
    name: str = ""
    description: str = ""
    value: float | int | bool = None
    upper_bound: float | int = float("inf")
    lower_bound: float | int = 0
    related_data: dict[str, UUID] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        if self.name.strip() == "":
            self.name = f"var_{self.id}"
