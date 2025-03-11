from dataclasses import dataclass

from base import OXObjectPot, OXObject, OXception
from data.OXData import OXData


@dataclass
class OXDatabase(OXObjectPot):

    def add_object(self, obj: OXObject):
        if not isinstance(obj, OXData):
            raise OXception("Only OXData can be added to OXDatabase")
        super().add_object(obj)

    def remove_object(self, obj: OXObject):
        if not isinstance(obj, OXData):
            raise OXception("Only OXData can be removed from OXDatabase")
        super().remove_object(obj)