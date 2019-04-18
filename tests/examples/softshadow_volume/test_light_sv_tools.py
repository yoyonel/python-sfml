import pytest

from softshadow_volume.light_sv_tools import solve_quadratic_equation


def test_light_sv_tools():
    solutions = solve_quadratic_equation(1, 1, 1)
    assert solutions.has_real_solutions is False

    solutions = solve_quadratic_equation(1, 2, 1)
    assert solutions.has_real_solutions is True
    assert len(solutions.roots) == 2
    assert min(solutions.roots) == pytest.approx(-1.00)
    assert max(solutions.roots) == pytest.approx(-1.00)

    solutions = solve_quadratic_equation(-4, 0, 1)
    assert solutions.has_real_solutions is True
    assert len(solutions.roots) == 2
    assert min(solutions.roots) == pytest.approx(-2.00)
    assert max(solutions.roots) == pytest.approx(+2.00)
