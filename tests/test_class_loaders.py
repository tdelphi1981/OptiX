from src.utilities.class_loaders import load_class


def test_load_class_valid_class():
    # Test loading a valid class
    clazz = load_class("base.OXObject.OXObject")
    assert clazz.__name__ == "OXObject"
    assert clazz.__module__ == "base.OXObject"
    obj = clazz()
    assert obj.id is not None
    assert obj.class_name == "base.OXObject.OXObject"

    clazz2 = load_class("base.OXObjectPot.OXObjectPot")
    assert clazz2.__name__ == "OXObjectPot"
    assert clazz2.__module__ == "base.OXObjectPot"
    obj2 = clazz2()
    assert obj2.id is not None
    assert obj2.class_name == "base.OXObjectPot.OXObjectPot"

