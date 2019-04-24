from typing import List

from sfml import sf

from softshadow_volume.bounding_volume import BoundingVolume
from softshadow_volume.compute_intersection import (
    compute_intersection_of_tangents_lines_on_circle
)
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
