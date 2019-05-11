from typing import List

from sfml import sf
from softshadow_volume.bounding_volume import BoundingVolume
from softshadow_volume.compute_intersection import (
    compute_intersection_of_tangents_lines_on_circle
)
from softshadow_volume.light import Light
from softshadow_volume.vector2_tools import normalize, compute_middle


def construct_bounding_volume_for_shadow(
        pos_light: sf.Vector2,
        radius_influence_circle: float,
        clipped_edge_with_influence_circle: List[sf.Vector2],
        color: sf.Color
) -> BoundingVolume:
    # Tuple[List[sf.Vector2], List[sf.Vector2], sf.ConvexShape]
    """
    sf::Shape construct_shadow_volume_shape(
        const vec2 &pos_light,
        const float r,
        const vec2 intersections_segment_circle[2],
        const sf::Color &color,
        sf::Vector2f proj_intersections[2],
        sf::Vector2f bounding_vertex_sv[2]
    )

    :return:
    """
    if not clipped_edge_with_influence_circle:
        raise ValueError(
            "No vertex after clipping with influence circle "
            "=> clipped_edge_with_influence_circle == []"
        )

    # projection des sommets clippes sur le cercle d'influence de la lumiere
    # i0, i1
    proj_clipped_edge = [
        normalize(clipped_vertex_edge) * radius_influence_circle
        for clipped_vertex_edge in clipped_edge_with_influence_circle
    ]
    # Milieu du segment clippe
    mid_i0_i1 = compute_middle(*proj_clipped_edge)
    # FIXME: assert len(mid_01_01) ~= 0.0 => can't normalize a null vector !
    # Projection du milieu (a) sur le cercle
    proj_mid_i0_i1 = normalize(mid_i0_i1) * radius_influence_circle

    # Calcul des vertex englobant
    # Ils correspondent aux intersections des lignes formees par:
    # les sommets de projection des intersections et
    # leurs normales associees, tangentes au cercle.
    bounding_vertex_sv = [
        compute_intersection_of_tangents_lines_on_circle(proj_clipped_vertex,
                                                         proj_mid_i0_i1)
        for proj_clipped_vertex in proj_clipped_edge
    ]

    # build shape shadow-volume
    # https://pysfml2-cython.readthedocs.io/en/latest/reference/graphics/drawing.html#sfml.ConvexShape
    shape = sf.ConvexShape(6)
    for i, v in enumerate(
            [
                clipped_edge_with_influence_circle[0],
                proj_clipped_edge[0],
                bounding_vertex_sv[0],
                bounding_vertex_sv[1],
                proj_clipped_edge[1],
                clipped_edge_with_influence_circle[1],
            ]
    ):
        shape.set_point(i, v)
    shape.position = pos_light
    shape.outline_color = color
    shape.fill_color = color

    return BoundingVolume(shape, *proj_clipped_edge, *bounding_vertex_sv)


def construct_bounding_volume_for_full_influence_light(
        light: Light,
        v0: sf.Vector2,
        v1: sf.Vector2,
        intersections_with_inner_circle: List[sf.Vector2],
        color: sf.Color = sf.Color.WHITE,
) -> BoundingVolume:
    """
    On construit la shape englobante pour l'influence de ce
    segment par rapport a  la lumiere en l'occurence si la segment
    est a  l'interieur de la lumiere,
    il influence toute la projection de la lumiere

    :param light:
    :param v0:
    :param v1:
    :param intersections_with_inner_circle:
    :param color:
    :return:
    """
    shape_bb_light = sf.ConvexShape(4)
    ir = light.influence_radius
    shape_bb_light.set_point(0, sf.Vector2(-ir, -ir))
    shape_bb_light.set_point(1, sf.Vector2(+ir, -ir))
    shape_bb_light.set_point(2, sf.Vector2(+ir, +ir))
    shape_bb_light.set_point(3, sf.Vector2(-ir, +ir))
    shape_bb_light.position = light.pos
    shape_bb_light.outline_color = color
    shape_bb_light.fill_color = color

    return BoundingVolume(shape_bb_light, v0 - light.pos, v1 - light.pos,
                          *intersections_with_inner_circle)
