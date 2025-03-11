from dataclasses import dataclass

from variables.OXVariable import OXVariable


@dataclass
class OXDeviationVar(OXVariable):
    desired: bool = False
