"""
TODO: pénombres
- travailler sur la nomenclature/naming => c'est la fête du slip :p
- continuer à écrire des tests portant sur des propriétés géométriques
"""
from typing import List
from sfml import sf

from softshadow_volume.bounding_volume import BoundingVolumePenumbra
from softshadow_volume.compute_intersection import (
    compute_intersection_solid_angle_2d,
    compute_intersection_of_tangents_lines_on_circle)
from softshadow_volume.light import Light
from softshadow_volume.vector2_tools import normalize, det
from softshadow_volume.vector3_tools import to_vec3, prod_vec3


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
    """
    # compute light solid angles for each edge's vertices
    p_light_for_edge = [
        [
            p * light.inner_radius
            for p in compute_intersection_solid_angle_2d(v_e)
        ]
        for v_e in clipped_edge_in_ls
    ]

    # project edge's vertice from points on light
    proj_p_light = [
        [
            normalize(p_e - pc) * light.influence_radius
            for pc in p_light
        ]
        for p_e, p_light in zip(clipped_edge_in_ls, p_light_for_edge)
    ]

    #
    bv = [
        compute_intersection_of_tangents_lines_on_circle(*proj_ss)
        for proj_ss in proj_p_light
    ]

    #
    # build shape shadow-volume
    # https://pysfml2-cython.readthedocs.io/en/latest/reference/graphics/drawing.html#sfml.ConvexShape
    shapes_inner_penumbras = []
    shapes_outer_penumbras = []

    def _set_position_color_to_shape(s, c=color):
        s.position = light.pos
        s.outline_color = c
        s.fill_color = c

    # vdir_edge = normalize(clipped_edge_in_ls[1] - clipped_edge_in_ls[0])
    vdir_edge = clipped_edge_in_ls[1] - clipped_edge_in_ls[0]

    for p_e, vdir_edge_orientation in zip(clipped_edge_in_ls, [+1, -1]):
        # vdir_p_e = normalize(p_e)
        vdir_p_e = p_e
        v3_z_for_e = prod_vec3(to_vec3(vdir_edge * vdir_edge_orientation),
                               to_vec3(vdir_p_e))
        edge_orientation = False if v3_z_for_e.z < 0 else True

        #  projective centers for edge's vertex
        proj_centers = [
            p * light.inner_radius
            for p in compute_intersection_solid_angle_2d(p_e)
        ]

        d_proj_p_e = {}
        for proj_center in proj_centers:
            # edge's vertex projection
            # with center projection on influence circle
            proj_p_e = normalize(p_e - proj_center) * light.influence_radius

            proj_center_orientation = det(proj_center, vdir_p_e) > 0
            if edge_orientation:
                if proj_center_orientation:
                    d_proj_p_e['outer'] = proj_p_e
                else:
                    d_proj_p_e['inner'] = proj_p_e
            else:
                if proj_center_orientation:
                    d_proj_p_e['inner'] = proj_p_e
                else:
                    d_proj_p_e['outer'] = proj_p_e

        # bounding volume
        # TODO: étudier le cas de non validité
        if len(d_proj_p_e.values()) == 2:
            p_bv = compute_intersection_of_tangents_lines_on_circle(
                *d_proj_p_e.values()
            )

            # shape generation
            shape = sf.ConvexShape(3)
            shape.set_point(0, p_e)
            shape.set_point(1, p_bv)
            shape.set_point(2, d_proj_p_e['inner'])

            _set_position_color_to_shape(shape)
            shapes_inner_penumbras.append(shape)

            # shape generation
            shape = sf.ConvexShape(3)
            shape.set_point(0, p_e)
            shape.set_point(1, d_proj_p_e['outer'])
            shape.set_point(2, p_bv)

            _set_position_color_to_shape(shape, c=sf.Color.GREEN)
            shapes_outer_penumbras.append(shape)

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
