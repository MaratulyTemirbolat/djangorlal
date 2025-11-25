from apps.auths.tools import Tool, Calculator
import pytest
from contextlib import nullcontext as does_not_raise
from typing import Any


def test_example():
    assert 1 == 1, "1 must be equal 1"


def test_tool():
    my_a: int = 5
    assert Tool.a == my_a, f"{Tool.a} must be equal {my_a}"


class TestCalculator:
    @pytest.mark.parametrize(
        argnames=["x", "y", "res", "expectation"],
        argvalues=[
            (1, 2, 3, does_not_raise()),
            (0, 0, 0, does_not_raise()),
            (-1, 1, 0, does_not_raise()),
            (2.5, 2.5, 5.0, does_not_raise()),
            ("10", 5, None, pytest.raises(TypeError)),  # This will fail since "10" is a string
        ]
    )
    def test_calculator_add(self, x: int | float, y: int | float, res: int | float, expectation: Any) -> None:
        with expectation:
            my_rest: float | int = Calculator.add(x, y)
            assert my_rest == res, f"{my_rest} must be equal {res}"

    @pytest.mark.parametrize(
        argnames=["x", "y", "res", "expectation"],
        argvalues=[
            (4, 2, 2.0, does_not_raise()),
            (5, 2, 2.5, does_not_raise()),
            (1, 0, None, pytest.raises(ZeroDivisionError)),
        ]
    )
    def test_calculator_divide(self, x: int | float, y: int | float, res: float, expectation: Any) -> None:
        with expectation:
            my_res: float = Calculator.divide(x, y)
            assert my_res == res, f"{my_res} must be equal {res}"
