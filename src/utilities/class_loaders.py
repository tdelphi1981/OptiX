from base.OXception import OXception


def get_fully_qualified_name(cls: type):
    return cls.__module__ + "." + cls.__name__

def load_class(fully_qualified_name: str):
    try:
        module_name, class_name = fully_qualified_name.rsplit(".", 1)
        module = __import__(module_name, fromlist=[class_name])
        retval = getattr(module, class_name)
        if retval is None:
            raise OXception(f"Class {fully_qualified_name} not found")
        return retval
    except Exception as e:
        if isinstance(e, OXception):
            raise e
        raise OXception(f"Error loading class {fully_qualified_name}: {e}")

