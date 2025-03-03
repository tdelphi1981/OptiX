from dataclasses import dataclass, field
from uuid import UUID, uuid4

from utilities.class_loaders import get_fully_qualified_name


@dataclass
class OXObject:
    id: UUID = field(default_factory=uuid4)
    class_name: str = ""

    def __post_init__(self):
        self.class_name = get_fully_qualified_name(type(self))

    def __str__(self):
        return f"{self.class_name}({self.id})"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.id)


