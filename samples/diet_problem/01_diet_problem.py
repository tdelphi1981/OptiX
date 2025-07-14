import uuid
from dataclasses import dataclass, field
from uuid import UUID

from constraints import RelationalOperators
from data import OXData
from problem import OXLPProblem, ObjectiveType
from solvers import solve


@dataclass
class Food(OXData):
    name: str = ""
    c: float = 0.0
    v: float = 0.0


@dataclass
class Nutrient(OXData):
    name: str = ""
    n_min: float = 0.0
    n_max: float | None = None


def main():
    dp = OXLPProblem()

    foods = [Food(name="Cheeseburger", c=1.84, v=4.0),
             Food(name="Ham Sandwich", c=2.19, v=7.5),
             Food(name="Hamburger", c=1.84, v=3.5),
             Food(name="Fish Sandwich", c=1.44, v=5.0),
             Food(name="Chicken Sandwich", c=2.29, v=7.3),
             Food(name="Fries", c=.77, v=2.6),
             Food(name="Sausage Biscuit", c=1.29, v=4.1),
             Food(name="Lowfat Milk", c=.60, v=8.0),
             Food(name="Orange Juice", c=.72, v=12.0)]

    for food in foods:
        dp.db.add_object(food)

    nutrients = [Nutrient(name="Cal", n_min=2000),
                 Nutrient(name="Carbo", n_min=350, n_max=375),
                 Nutrient(name="Protein", n_min=55),
                 Nutrient(name="VitA", n_min=100),
                 Nutrient(name="VitC", n_min=100),
                 Nutrient(name="Calc", n_min=100),
                 Nutrient(name="Iron", n_min=100)]

    for nutrient in nutrients:
        dp.db.add_object(nutrient)

    a = [
        [510, 34, 28, 15, 6, 30, 20],
        [370, 35, 24, 15, 10, 20, 20],
        [500, 42, 25, 6, 2, 25, 20],
        [370, 38, 14, 2, 0, 15, 10],
        [400, 42, 31, 8, 15, 15, 8],
        [220, 26, 3, 0, 15, 0, 2],
        [345, 27, 15, 4, 0, 20, 15],
        [110, 12, 9, 10, 4, 30, 0],
        [80, 20, 1, 2, 120, 2, 2]
    ]

    Vmax = 75

    dp.create_variables_from_db(
        Food,
        var_name_template="{food_name} to consume",
        var_description_template="Number of servings of {food_name} to consume",
        lower_bound=0,
        upper_bound=2000
    )

    variable_ids = [v.id for v in dp.variables.objects]

    for j, nutrient in enumerate(nutrients):
        weights = [food_weight[j] for food_weight in a]

        dp.create_constraint(
            variables=variable_ids,
            weights=weights,
            operator=RelationalOperators.GREATER_THAN_EQUAL,
            value=nutrient.n_min,
        )

        if nutrient.n_max is not None:
            dp.create_constraint(
                variables=variable_ids,
                weights=weights,
                operator=RelationalOperators.LESS_THAN_EQUAL,
                value=nutrient.n_max,
            )

    dp.create_constraint(
        variables=variable_ids,
        weights=[f.v for f in foods],
        operator=RelationalOperators.LESS_THAN_EQUAL,
        value=Vmax,
    )

    dp.create_objective_function(
        variables=variable_ids,
        weights=[f.c for f in foods],
        objective_type=ObjectiveType.MINIMIZE
    )

    status, solver = solve(dp, 'ORTools', equalizeDenominators=True)

    print(f"Status: {status}")

    for solution in solver:
        solution.print_solution_for(dp)


if __name__ == '__main__':
    main()
