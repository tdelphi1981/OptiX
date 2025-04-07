from dataclasses import dataclass, field, fields
from typing import Any

from base import OXObject, OXception

#: List of field names that are not part of scenarios
NON_SCENARIO_FIELDS = ["active_scenario", "scenarios", "id", "class_name"]


@dataclass
class OXData(OXObject):
    """A base class for data objects with scenario support.

    This class provides a mechanism for storing different attribute values
    for different scenarios. When an attribute is accessed, the system first
    checks if it exists in the active scenario, and if not, falls back to
    the object's own attribute.

    Attributes:
        active_scenario (str): The name of the currently active scenario.
            Defaults to "Default".
        scenarios (dict[str, dict[str, Any]]): A dictionary mapping scenario names
            to dictionaries of attribute values.

    Examples:
        >>> data = OXData()
        >>> data.value = 10
        >>> data.create_scenario("Optimistic", value=20)
        >>> data.create_scenario("Pessimistic", value=5)
        >>> print(data.value)  # Default scenario
        10
        >>> data.active_scenario = "Optimistic"
        >>> print(data.value)  # Optimistic scenario
        20
        >>> data.active_scenario = "Pessimistic"
        >>> print(data.value)  # Pessimistic scenario
        5
    """
    active_scenario: str = "Default"
    scenarios: dict[str, dict[str, Any]] = field(default_factory=dict)

    def __getattribute__(self, item):
        """Custom attribute access that checks the active scenario first.

        When an attribute is accessed, this method first checks if it exists
        in the active scenario, and if not, falls back to the object's own attribute.

        Args:
            item (str): The name of the attribute to access.

        Returns:
            Any: The value of the attribute in the active scenario, or the
                object's own attribute if not found in the active scenario.
        """
        if item in NON_SCENARIO_FIELDS:  # Prevent Infinite Loop!
            return super().__getattribute__(item)
        active_scenario_values = self.scenarios.get(self.active_scenario, {})
        if len(active_scenario_values) > 0:
            if item in active_scenario_values:
                return active_scenario_values[item]
        return super().__getattribute__(item)

    def create_scenario(self, scenario_name: str, **kwargs):
        """Create a new scenario with the specified attribute values.

        If the "Default" scenario doesn't exist yet, it is created first,
        capturing the object's current attribute values.

        Args:
            scenario_name (str): The name of the new scenario.
            **kwargs: Attribute-value pairs for the new scenario.

        Raises:
            OXception: If an attribute in kwargs doesn't exist in the object.

        Examples:
            >>> data = OXData()
            >>> data.value = 10
            >>> data.create_scenario("Optimistic", value=20)
            >>> data.active_scenario = "Optimistic"
            >>> print(data.value)
            20
        """
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
