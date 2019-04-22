from math import pi, cos, sin

import numpy as np
import pytest
from sfml import sf

from softshadow_volume.compute_intersection import (
    SolutionsForQuadraticEquation,
    compute_intersection_line_origin_circle,
    compute_intersection_circle_circle, compute_intersection_solid_angle_1d,
    compute_intersection_solid_angle_2d)
from softshadow_volume.vector2_tools import normalize, norm
from tests.conftest import half_sqrt_two


@pytest.mark.parametrize(
    'test_input,expected',
    [
        ((sf.Vector2(), sf.Vector2(), 1.0),
         SolutionsForQuadraticEquation(False, np.array([]))),
        # axis x, y from origin
        ((sf.Vector2(), sf.Vector2(1, 0), 1.0),
         SolutionsForQuadraticEquation(True, np.array([-1, +1]))),
        ((sf.Vector2(), sf.Vector2(0, 1), 1.0),
         SolutionsForQuadraticEquation(True, np.array([-1, +1]))),
        # diagonal from origin
        ((sf.Vector2(), sf.Vector2(1, 1), 1.0),
         SolutionsForQuadraticEquation(True,
                                       np.array([-1.0, +1.0]) * half_sqrt_two)),
        ((sf.Vector2(), normalize(sf.Vector2(1, 1)), 1.0),
         SolutionsForQuadraticEquation(True, np.array([-1.0, +1.0]))),
        ((sf.Vector2(), normalize(sf.Vector2(10, 10)), 1.0),
         SolutionsForQuadraticEquation(True, np.array([-1.0, +1.0]))),
        # tangent to the circle
        ((sf.Vector2(1, 0), sf.Vector2(0, 1), 1.0),
         SolutionsForQuadraticEquation(True, np.array([0, 0]))),
    ]
)
def test_compute_intersection_line_origin_circle(test_input, expected):
    solutions = compute_intersection_line_origin_circle(*test_input)
    assert solutions == expected


@pytest.mark.parametrize(
    'test_input,expected',
    [
        ((sf.Vector2(), 1.0, sf.Vector2(), 10.0),
         None),
        ((sf.Vector2(5.0), 1.0, sf.Vector2(), 10.0),
         None),
        ((sf.Vector2(0.0), 1.0, sf.Vector2(2.0), 1.0),
         (sf.Vector2(1.0, 0.0),) * 2),
    ]
)
def test_compute_intersection_circle_circle(test_input, expected):
    results = compute_intersection_circle_circle(*test_input)
    assert results == expected


@pytest.mark.parametrize(
    'test_input',
    [
        0.0,
        1.0,
        2.0,
        3.0,
        # ...
    ]
)
def test_compute_intersection_solid_angle(test_input):
    exsec = test_input
    results = compute_intersection_solid_angle_1d(exsec)
    nb_results = len(results)
    if nb_results == 1:
        assert results == [sf.Vector2(1, 0)]
    elif nb_results == 2:
        # 1D Problem (along x-axis)
        p = sf.Vector2(exsec + 1.0, 0.0)
        for vert_sa in results:
            p_sa0 = vert_sa - p
            # compute intersections
            sol = compute_intersection_line_origin_circle(p, p_sa0, 1.0)
            # test geometrical properties:
            # - have valid intersection(s)
            # - all solutions are the same => 1 solution
            # - intersection and vertex from solid angle are the same
            # => on circle and tangent
            assert sol.has_real_solutions
            assert np.allclose(*sol.roots)
            assert sol.roots[0] == 1.0
    else:
        raise ValueError


@pytest.mark.parametrize(
    'test_input',
    [
        sf.Vector2(1.0, 0.0),
        sf.Vector2(0.0, 1.0),
        sf.Vector2(cos(pi/4.0), sin(pi/4.0)),
        #
        sf.Vector2(1.0, 0.0) * 2,
        sf.Vector2(0.0, 1.0) * 3,
        #
        sf.Vector2(cos(+pi/4.0), sin(+pi/4.0)) * 4,
        sf.Vector2(cos(+pi/4.0*3), sin(-pi/4.0*3)) * 3,
    ]
)
def test_compute_intersection_solid_angle_2d(test_input):
    p = test_input
    results = compute_intersection_solid_angle_2d(p)
    nb_results = len(results)
    if nb_results == 1:
        assert results[0] == p
    elif nb_results == 2:
        for vert_sa in results:
            # vertex on unit origin circle
            assert np.isclose(norm(vert_sa), 1.0)

            p_sa0 = vert_sa - p
            # compute intersections
            sol = compute_intersection_line_origin_circle(p, p_sa0, 1.0)
            # test geometrical properties:
            # - have valid intersection(s)
            # - all solutions are the same => 1 solution
            # - intersection and vertex from solid angle are the same
            # => on circle and tangent
            assert sol.has_real_solutions
            assert np.allclose(*sol.roots)
            assert sol.roots[0] == 1.0
    else:
        raise ValueError
