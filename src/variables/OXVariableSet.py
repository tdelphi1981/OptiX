from dataclasses import dataclass

from base import OXObjectPot, OXObject, OXception
from variables.OXVariable import OXVariable


@dataclass
class OXVariableSet(OXObjectPot):

    def add_object(self, obj: OXObject):
        if not isinstance(obj, OXVariable):
            raise OXception("Only OXVariable can be added to OXVariableSet")
        super().add_object(obj)

    def remove_object(self, obj: OXObject):
        if not isinstance(obj, OXVariable):
            raise OXception("Only OXVariable can be removed from OXVariableSet")
        super().remove_object(obj)
