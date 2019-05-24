"""
TODO: pénombres
- travailler sur la nomenclature/naming => c'est la fête du slip :p
- continuer à écrire des tests portant sur des propriétés géométriques
"""
import logging
from typing import List, Container

import numpy as np

from sfml import sf
from softshadow_volume.bounding_volume import BoundingVolumePenumbra
from softshadow_volume.compute_intersection import (
    compute_intersection_of_tangents_lines_on_circle,
    compute_intersection_line_origin_circle,
    compute_projectives_centers, SolutionsForQuadraticEquation)
from softshadow_volume.light import Light
from softshadow_volume.vector2_tools import det, norm2
from softshadow_volume.vector3_tools import to_vec3, prod_vec3

logger = logging.getLogger(__name__)


def construct_bounding_volumes_for_penumbras_volumes(
        clipped_edge_in_ls: List[sf.Vector2],
        light: Light,
        color: sf.Color
) -> List[BoundingVolumePenumbra]:
    """
    All process in Light Space (light circle at origin unit scale)

    std::vector<Bounding_Volume> Light_Wall::Construct_Penumbras_Bounding_Volumes(
        const vec2 intersections_segment_circle[2],
        const vec2 proj_intersections[2],
        const vec2 &E0_LS_to_E1_LS
    )

    https://pysfml2-cython.readthedocs.io/en/latest/reference/graphics/drawing.html#sfml.ConvexShape
    """

    def _build_convex_shape(
            vertices: Container[sf.Vector2],
            c: sf.Color = color,
    ) -> sf.Shape:
        shape = sf.ConvexShape(len(vertices))
        for i, vertex in enumerate(vertices):
            shape.set_point(i, vertex)
        #
        shape.position = light.pos
        shape.outline_color = c
        shape.fill_color = c
        #
        return shape

    def _compute_orientation_edge_light(
            oriented_edge: sf.Vector2,
            edge_vertex_in_ls: sf.Vector2
    ) -> bool:
        v3_z_from_edge_light = prod_vec3(to_vec3(oriented_edge),
                                         to_vec3(edge_vertex_in_ls))
        return v3_z_from_edge_light.z >= 0

    def find_penumbra_type_name(ori_el: bool, ori_pc: bool) -> str:
        return 'outer' if (ori_el and ori_pc) or not (
                ori_el or ori_pc) else 'inner'

    p_light_for_edge = []
    proj_p_light = []
    bv = []
    shapes_inner_penumbras = []
    shapes_outer_penumbras = []

    vdir_edge = clipped_edge_in_ls[1] - clipped_edge_in_ls[0]

    for p_e, vdir_edge_orientation in zip(clipped_edge_in_ls, [+1, -1]):
        orientation_edge_light = _compute_orientation_edge_light(
            vdir_edge * vdir_edge_orientation,
            p_e
        )

        # projective centers for edge's vertex
        proj_centers = compute_projectives_centers(p_e, light.inner_radius)

        # compute light solid angles for each edge's vertices
        p_light_for_edge.append(proj_centers)

        map_proj_p_e = {}
        for proj_center in proj_centers:
            # edge's vertex projection
            # with center projection on influence circle
            proj_center_to_p_e = p_e - proj_center
            
            # FIXME: need to improve stability !
            if np.isclose(norm2(proj_center_to_p_e), 0.):
                solutions = SolutionsForQuadraticEquation(True, [0.])
            else:
                solutions = compute_intersection_line_origin_circle(
                    p_e,
                    proj_center_to_p_e,
                    light.influence_radius
                )
                # TODO: reinforce the stability
                if not solutions.has_real_solutions:
                    # RuntimeError:
                    # compute_intersection_line_origin_circle(
                    #     p_e=(-12.0, -16.0),
                    #     proj_center_to_p_e=(0.0, 0.0),
                    #     light.influence_radius = 350
                    # )
                    # has
                    # 0(real)
                    # solutions( = SolutionsForQuadraticEquation(
                    #     has_real_solutions=False, roots=array([], dtype=float64)))
                    msg_err = f"""
                    compute_intersection_line_origin_circle(
                        p_e={p_e},
                        proj_center_to_p_e={proj_center_to_p_e},
                        light.influence_radius={light.influence_radius}
                    )
                    has 0 (real) solutions(={solutions})
                    """
                    logger.error(msg_err)
                    raise RuntimeError(msg_err)

            proj_p_e = p_e + proj_center_to_p_e * max(solutions.roots)
            # project edge's vertex from points on light
            proj_p_light += ((proj_p_e,),)

            orientation_proj_center = det(proj_center, p_e) > 0
            penumbra_type_name = find_penumbra_type_name(
                orientation_edge_light, orientation_proj_center)
            map_proj_p_e[penumbra_type_name] = proj_p_e

        # bounding volume
        assert len(map_proj_p_e.values()) == 2

        p_bv = compute_intersection_of_tangents_lines_on_circle(
            *map_proj_p_e.values()
        )
        bv += (p_bv,)

        # build shapes penumbras volumes
        # inner penumbra
        shapes_inner_penumbras += (_build_convex_shape(
            (p_e, p_bv, map_proj_p_e['inner'])),)
        # outer penumbra
        shapes_outer_penumbras += (
            _build_convex_shape((p_e, map_proj_p_e['outer'], p_bv),
                                sf.Color.GREEN),
        )

    return [
        BoundingVolumePenumbra(
            p_light=p_light_for_edge,
            clipped_edge_in_ls=clipped_edge_in_ls,
            proj_edge_with_projs_light=proj_p_light,
            bv=bv,
            shapes_inner_penumbras=shapes_inner_penumbras,
            shapes_outer_penumbras=shapes_outer_penumbras,
        )
    ]
