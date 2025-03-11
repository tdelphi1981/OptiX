from dataclasses import dataclass, field, fields
from typing import Any

from base import OXObject, OXception

NON_SCENARIO_FIELDS = ["active_scenario", "scenarios", "id", "class_name"]


@dataclass
class OXData(OXObject):
    active_scenario: str = "Default"
    scenarios: dict[str, dict[str, Any]] = field(default_factory=dict)

    def __getattribute__(self, item):
        if item in NON_SCENARIO_FIELDS:  # Prevent Infinite Loop!
            return super().__getattribute__(item)
        active_scenario_values = self.scenarios.get(self.active_scenario, {})
        if len(active_scenario_values) > 0:
            if item in active_scenario_values:
                return active_scenario_values[item]
        return super().__getattribute__(item)

    def create_scenario(self, scenario_name: str, **kwargs):
        if 'Default' not in self.scenarios:
            self.scenarios['Default'] = {}
            obj_fields = fields(self)
            for field in obj_fields:
                if field.name not in NON_SCENARIO_FIELDS:
                    self.scenarios['Default'][field.name] = getattr(self, field.name)
        self.scenarios[scenario_name] = {}
        for key, value in kwargs.items():
            if key not in NON_SCENARIO_FIELDS:
                if hasattr(self, key):
                    self.scenarios[scenario_name][key] = value
                else:
                    raise OXception(f"Object {self} has no attribute {key}")
