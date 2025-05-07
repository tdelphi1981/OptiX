from dataclasses import dataclass

import pytest

from base import OXception
from data.OXData import OXData
from problem.OXProblem import OXProblem


@dataclass
class Otobus(OXData):
    ayakta: int = 10
    oturan: int = 10
    adi: str = "A"


@dataclass
class Hat(OXData):
    kodu: str = "A"


@dataclass
class Beyza(OXData):
    adi: str = "Beyza"


def init_problem():
    problem = OXProblem()
    problem.db.add_object(Otobus(adi="A"))
    problem.db.add_object(Otobus(adi="B"))
    problem.db.add_object(Otobus(adi="C"))

    problem.db.add_object(Hat(kodu="A"))
    problem.db.add_object(Hat(kodu="B"))
    problem.db.add_object(Hat(kodu="C"))

    return problem


def test_create_variables_from_db():
    problem = init_problem()

    problem.create_variables_from_db("X_{otobus}_{hat}",
                                     "Otobus Grubu {otobus} için Hat {hat} taki sefer sayısı",
                                     100,
                                     0,
                                     Otobus, Hat)

    assert len(problem.variables) == 9


def test_create_variables_from_db_with_invalid_arguments():
    problem = init_problem()

    with pytest.raises(OXception):
        problem.create_variables_from_db("X_{otobus}_{hat}",
                                         "Otobus Grubu {otobus} için Hat {hat} taki sefer sayısı",
                                         100,
                                         0,
                                         Otobus, Beyza)
