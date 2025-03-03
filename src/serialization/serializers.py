from dataclasses import asdict

from base import OXObject
from base import OXception
from utilities.class_loaders import load_class


def serialize_to_python_dict(obj: OXObject) -> dict:
    return asdict(obj)


def deserialize_from_python_dict(dct: dict) -> OXObject:
    if "class_name" not in dct:
        raise OXception("class_name not found in dictionary")
    if "id" not in dct:
        raise OXception("id not found in dictionary")
    class_name = dct["class_name"]
    clazz = load_class(class_name)
    retval = clazz()
    retval.id = dct["id"]
    for key, value in dct.items():
        if key != "class_name" and key != "id":
            if isinstance(value, dict):
                try:
                    value = deserialize_from_python_dict(value)
                except OXception:
                    pass
            if isinstance(value, list):
                for i in range(len(value)):
                    if isinstance(value[i], dict):
                        try:
                            value[i] = deserialize_from_python_dict(value[i])
                        except OXception:
                            pass
            setattr(retval, key, value)
    return retval
