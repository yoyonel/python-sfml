"""
"""
import numpy as np
import pytest
from sfml import sf

from softshadow_volume import EPSILON
from softshadow_volume.compute_clip import (
    compute_clip_edge_with_circle
)
from softshadow_volume.compute_intersection import (
    compute_intersection_line_origin_circle
)
from softshadow_volume.bv_shadow_volume import construct_bounding_volume_for_shadow
from softshadow_volume.vector2_tools import norm2, dot, normalize


def test_construct_shape_shadow_volume_raise_exception():
    pos_light = sf.Vector2()
    radius_influence_circle = 10.0
    vertex_walls = (sf.Vector2(),) * 2
    with pytest.raises(ValueError):
        construct_bounding_volume_for_shadow(
            pos_light,
            radius_influence_circle,
            compute_clip_edge_with_circle(
                pos_light, radius_influence_circle, *vertex_walls),
            color=sf.Color.WHITE
        )


# TODO: generate random edges (inside, intersect the influence light circle)
@pytest.mark.parametrize(
    'test_input',
    [
        ({'pos_light': sf.Vector2(),
          'radius_influence_circle': 1.0,
          'vertex_walls': (
          sf.Vector2(-1.0 / 3.0, 0.5), sf.Vector2(+1.0 / 3.0, 0.5))
          }),
        ({'pos_light': sf.Vector2(),
          'radius_influence_circle': 1.0,
          'vertex_walls': (sf.Vector2(+1.0 / 3.0, -0.5),
                           sf.Vector2(+1.0 / 3.0, 0.5))
          }),
    ]
)
def test_construct_shape_shadow_volume(test_input):
    pos_light = test_input['pos_light']
    radius_influence_circle = test_input['radius_influence_circle']
    vertex_walls = test_input['vertex_walls']

    result = construct_bounding_volume_for_shadow(
        pos_light,
        radius_influence_circle,
        compute_clip_edge_with_circle(
            pos_light, radius_influence_circle, *vertex_walls),
        color=sf.Color.WHITE
    )

    ############################################################################
    # Assert/tests geometrical properties
    ############################################################################
    # TODO: need schemas/ascii arts
    # projection clipped vertex on the influence light circle
    assert norm2(result.proj_clipped_vertex_0) == radius_influence_circle
    assert norm2(result.proj_clipped_vertex_1) == radius_influence_circle
    # bounding volume shadow volume vertex outside the influence light circle
    assert norm2(result.bv_sv_vertex_0) > radius_influence_circle
    assert norm2(result.bv_sv_vertex_1) > radius_influence_circle
    # projection clipped edge parallel to
    # bounding volume shadow volume edge
    assert dot(
        normalize(result.proj_clipped_vertex_1 - result.proj_clipped_vertex_0),
        normalize(result.bv_sv_vertex_1 - result.bv_sv_vertex_0)
    ) == 1.0
    # wall's edge parallel to bounding volume shadow volume edge
    assert dot(
        normalize(vertex_walls[1] - vertex_walls[0]),
        normalize(result.bv_sv_vertex_1 - result.bv_sv_vertex_0)
    ) == 1.0
    # bounding volume shadow volume edge tangent to influence light circle
    solutions = compute_intersection_line_origin_circle(
        result.bv_sv_vertex_0,
        normalize(result.bv_sv_vertex_1 - result.bv_sv_vertex_0),
        radius_influence_circle + EPSILON
    )
    # real solutions
    assert solutions.has_real_solutions
    # 2 solutions but very close ~=> 1 tangent solution
    # TODO: find a way to have an unique real tangent solution/intersection
    assert np.isclose(np.diff(solutions.roots), 0.0, atol=1e-7)
    ############################################################################
