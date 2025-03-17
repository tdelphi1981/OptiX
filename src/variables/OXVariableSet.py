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

    def query(self, **kwargs) -> list[OXObject]:

        def query_function(object: OXObject):
            if isinstance(object, OXVariable):
                number_of_keys_found = 0
                for key, value in kwargs.items():
                    if key in object.related_data:
                        number_of_keys_found += 1
                        if object.related_data[key] != value:
                            return False
                if number_of_keys_found == 0:
                    return False
                return True
            else:
                raise OXception("This should not happen.")

        return self.search_by_function(query_function)
