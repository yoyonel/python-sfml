import numpy as np
import pytest
from sfml import sf

from softshadow_volume.compute_clip import (
    compute_clip_edge_with_influence_light_circle
)
from tests.conftest import half_sqrt_two


@pytest.mark.parametrize(
    'test_input,expected',
    [
        ({'pos_light': sf.Vector2(),
          'radius_light': 1.0,
          'edge_v0': sf.Vector2(), 'edge_v1': sf.Vector2()},
         []),
        ({'pos_light': sf.Vector2(),
          'radius_light': 1.0,
          'edge_v0': sf.Vector2(-1.5, 0.0), 'edge_v1': sf.Vector2(-0.5, 0.0)},
         [sf.Vector2(-1.0, 0.0), sf.Vector2(-0.5, 0.0)]),
        ({'pos_light': sf.Vector2(),
          'radius_light': 1.0,
          'edge_v0': sf.Vector2(0.0, 1.5), 'edge_v1': sf.Vector2(0.0, 0.5)},
         [sf.Vector2(0.0, 1.0), sf.Vector2(0.0, 0.5)]),
        ({'pos_light': sf.Vector2(),
          'radius_light': 1.0,
          'edge_v0': sf.Vector2(-0.5, 0.0), 'edge_v1': sf.Vector2(0.0, 0.5)},
         [sf.Vector2(-0.5, 0.0), sf.Vector2(0.0, 0.5)]),
        ({'pos_light': sf.Vector2(),
          'radius_light': 1.0,
          'edge_v0': sf.Vector2(0.0, 1.5), 'edge_v1': sf.Vector2(1.5, 1.0)},
         []),
        ({'pos_light': sf.Vector2(),
          'radius_light': 1.0,
          'edge_v0': sf.Vector2(-1.0, 1.0), 'edge_v1': sf.Vector2(1.0, -1.0)},
         [sf.Vector2(-half_sqrt_two, +half_sqrt_two),
          sf.Vector2(+half_sqrt_two, -half_sqrt_two)]),
    ]
)
def test_compute_clip_edge_with_influence_light_circle(test_input, expected):
    results = compute_clip_edge_with_influence_light_circle(**test_input)
    # TODO: do better comparison :p
    if not np.allclose([list(iter(v)) for v in results],
                       [list(iter(v)) for v in expected]):
        raise ValueError(
            f"results={results} not equal to expected={expected}")
