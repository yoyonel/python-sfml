"""
"""
from typing import Dict, List

from sfml import sf

from softshadow_volume.renderer.circle import build_circle_shape
from softshadow_volume.renderer.edge import build_edge_shape
from softshadow_volume.light_wall import LightWall


def build_shapes_for_light_wall(
        lw: LightWall,
        sv_alpha: float = 1.0
) -> Dict[str, List[sf.Drawable]]:
    vertex_params = dict(outline_thickness=2,
                         outline_color=sf.Color.GREEN,
                         fill_color=sf.Color.RED)

    bvs = lw.build_bounding_volumes_for_shadow_volumes(sf.Color.BLUE)

    shapes = {
        "vertex": [
            build_circle_shape(radius=2.5, position=v, **vertex_params)
            for v in (lw.v0, lw.v1)
        ],
        "edge": build_edge_shape(lw.v0, lw.v1, sf.Color.GREEN),
        'shadow_volumes': []
    }
    for bv in bvs['hard_shadow']:
        shape = bv.shape
        fill_color = shape.fill_color
        fill_color.a = int(sv_alpha*255)
        shape.fill_color = fill_color
    shapes['shadow_volumes'] += [
        bv.shape
        for bv in bvs['hard_shadow']
    ]

    hsv_points = [
        build_circle_shape(
            radius=1.5,
            position=shape.get_point(i) + shape.position,
            **vertex_params
        )
        for shape in shapes['shadow_volumes']
        for i in range(shape.point_count)
    ]
    shapes['shadow_volumes'] += hsv_points

    shapes['shadow_volumes'] += [
        build_circle_shape(
            radius=5,
            position=p,
            fill_color=sf.Color.BLUE
        )
        for p in lw.clip_wall_with_light()
    ]

    # penumbras
    shapes['penumbras'] = []
    cpl_points = [
        build_circle_shape(
            radius=2,
            position=proj_center_light + lw.light.pos,
            outline_color=sf.Color.RED,
            fill_color=sf.Color.RED
        )
        for bv in bvs['penumbras']
        for p_light in bv.p_light
        for proj_center_light in p_light
    ]
    shapes['penumbras'] += cpl_points

    #
    proj_edge_cpl_points = [
        build_circle_shape(
            radius=2,
            position=proj_vertex_with_projs_light + lw.light.pos,
            outline_color=sf.Color.RED,
            fill_color=sf.Color.RED
        )
        for bv in bvs['penumbras']
        for proj_edge_with_projs_light in bv.proj_edge_with_projs_light
        for proj_vertex_with_projs_light in proj_edge_with_projs_light
    ]
    shapes['penumbras'] += proj_edge_cpl_points

    #
    proj_edge_cpl_points = [
        build_circle_shape(
            radius=2,
            position=p_bv + lw.light.pos,
            outline_color=sf.Color(255, 64, 64, 255),
            fill_color=sf.Color.TRANSPARENT,
        )
        for bv in bvs['penumbras']
        for p_bv in bv.bv
    ]
    shapes['penumbras'] += proj_edge_cpl_points

    for bv in bvs['penumbras']:
        for shape_in_inner_penumbra in bv.shapes_inner_penumbras:
            fill_color = shape_in_inner_penumbra.fill_color
            fill_color.a = int(sv_alpha*255)
            shape_in_inner_penumbra.fill_color = fill_color
        for shape_in_outer_penumbra in bv.shapes_outer_penumbras:
            fill_color = shape_in_outer_penumbra.fill_color
            fill_color.a = int(sv_alpha*255)
            shape_in_outer_penumbra.fill_color = fill_color

    shapes['penumbras'] += [
        shape_in_inner_penumbra
        for bv in bvs['penumbras']
        for shape_in_inner_penumbra in bv.shapes_inner_penumbras
    ]
    shapes['penumbras'] += [
        shape_in_outer_penumbra
        for bv in bvs['penumbras']
        for shape_in_outer_penumbra in bv.shapes_outer_penumbras
    ]
    
    return shapes
