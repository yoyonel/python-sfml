"""
TODO: pénombres
- décomposer les volumes de pénombres/ombres
- commencer à dessiner pour debugger et voir ce que ça donne
- continuer à écrire des tests portant sur des propriétés géométriques
"""
from typing import List

from sfml import sf

from softshadow_volume.bounding_volume import BoundingVolumePenumbra
from softshadow_volume.compute_intersection import (
    compute_intersection_solid_angle_2d
)
from softshadow_volume.vector2_tools import normalize


def construct_shape_penumbras_volumes(
        clipped_edge_with_influence_circle: List[sf.Vector2],
        vdir_edge: sf.Vector2,
        influence_radius: float,
        color: sf.Color
) -> List[BoundingVolumePenumbra]:
    """
    All process in Light Space (light circle at origin unit scale)

    std::vector<Bounding_Volume> Light_Wall::Construct_Penumbras_Bounding_Volumes(
        const vec2 intersections_segment_circle[2],
        const vec2 proj_intersections[2],
        const vec2 &E0_LS_to_E1_LS
    )

    """
    # clipped edge
    edge = clipped_edge_with_influence_circle

    # projective clipped edge
    proj_edge = [
        normalize(v_e) * influence_radius
        for v_e in edge
    ]

    # compute light solid angles for each edge's vertices
    p_light_for_edge = [
        compute_intersection_solid_angle_2d(v_e)
        for v_e in edge
    ]

    # project edge's vertice from points on light
    proj_p_light = [
        [
            normalize(e - p) * influence_radius
            for p in p_light
        ]
        for v_e in edge
        for e, p_light in zip(v_e, p_light_for_edge)
    ]

    # bv_for_e0 = [
    #     compute_intersection_of_tangents_lines_on_circle(p_proj, )
    #     for p_proj in proj_p_light_for_e0
    # ]
    # bv_p0_e0 = compute_intersection_of_tangents_lines_on_circle(proj_e0,
    #                                                             proj_p0_e0)
    # bv_p1_e0 = compute_intersection_of_tangents_lines_on_circle(proj_e0,
    #                                                             proj_p1_e0)
