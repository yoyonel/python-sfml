from math import sqrt

import numpy as np
import pytest
from sfml import sf

from softshadow_volume.light_sv_tools import (
    compute_intersection_line_origin_circle,
    SolutionsForQuadraticEquation,
    compute_clip_edge_with_influence_light_circle)


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
         SolutionsForQuadraticEquation(
             True, np.array([-sqrt(2.0) / 2.0, +sqrt(2.0) / 2.0]))),
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
        ({'pos_light': sf.Vector2(),
          'radius_light': 1.0,
          'edge_v0': sf.Vector2(),
          'edge_v1': sf.Vector2()},
         []),
        ({'pos_light': sf.Vector2(),
          'radius_light': 1.0,
          'edge_v0': sf.Vector2(-1.5, 0.0),
          'edge_v1': sf.Vector2(-0.5, 0.0)},
         [sf.Vector2(-1.0, 0.0), sf.Vector2(-0.5, 0.0)])
        # TODO: add more tests
    ]
)
def test_compute_clip_edge_with_influence_light_circle(test_input, expected):
    results = compute_clip_edge_with_influence_light_circle(**test_input)
    assert results == expected
