from collections.abc import Callable
from dataclasses import dataclass, field

from base import OXObject
from base.OXObject import OXObject



@dataclass
class OXObjectPot(OXObject):
    objects: list[OXObject] = field(default_factory=list)

    def search(self, **kwargs) -> list[OXObject]:
        result = []
        for object in self.objects:
            should_include = True
            for key, value in kwargs.items():
                if not hasattr(object, key) and getattr(object, key) != value:
                    should_include = False
                    break
            if should_include:
                result.append(object)
        return result

    def search_by_function(self, function: Callable[[OXObject], bool]) -> list[OXObject]:
        result = []
        for object in self.objects:
            if function(object):
                result.append(object)
        return result

    def add_object(self, obj: OXObject):
        self.objects.append(obj)

    def remove_object(self, obj: OXObject):
        self.objects.remove(obj)

    def __iter__(self):
        return iter(self.objects)

    def __len__(self):
        return len(self.objects)

    def query(self, **kwargs) -> list[OXObject]:

        def query_function(object: OXObject):
            if isinstance(object, OXObject):
                number_of_keys_found = 0
                for key, value in kwargs.items():
                    if key in object.related_data:
                        number_of_keys_found += 1
                        if object.related_data[key] != value:
                            return False
                if number_of_keys_found == 0:
                    return False
            return True

        return self.search_by_function(query_function)
