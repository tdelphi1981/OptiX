from dataclasses import dataclass

from serialization.serializers import serialize_to_python_dict, deserialize_from_python_dict
from src.data.OXData import OXData


def test_OXData_initial_state():
    # Test initial state of OXData
    data = OXData()
    assert data.active_scenario == "Default"
    assert isinstance(data.scenarios, dict)
    assert len(data.scenarios) == 0


@dataclass
class TestOtobusSinifi(OXData):
    ayakta: int = 10
    oturan: int = 10


def test_OXData_add_scenario():
    obj = TestOtobusSinifi()
    assert obj.active_scenario == "Default"
    assert obj.ayakta == 10
    assert obj.oturan == 10
    obj.create_scenario("TestScenario", ayakta=20, oturan=20)
    obj.active_scenario = "TestScenario"
    assert obj.ayakta == 20
    assert obj.oturan == 20
    obj.create_scenario("TestScenario2", ayakta=30, oturan=30)
    obj.active_scenario = "TestScenario2"
    assert obj.ayakta == 30
    assert obj.oturan == 30


def test_OXData_serialize():
    obj = TestOtobusSinifi()
    obj.create_scenario("TestScenario", ayakta=20, oturan=20)
    obj.active_scenario = "TestScenario"
    obj.create_scenario("TestScenario2", ayakta=30, oturan=30)
    obj.active_scenario = "TestScenario2"

    result = serialize_to_python_dict(obj)

    obj1 = deserialize_from_python_dict(result)
    obj1.active_scenario = "Default"
    assert obj1.ayakta == 10
    assert obj1.oturan == 10
    obj1.active_scenario = "TestScenario"
    assert obj1.ayakta == 20
    assert obj1.oturan == 20
    obj1.active_scenario = "TestScenario2"
    assert obj1.ayakta == 30
    assert obj1.oturan == 30
