"""
"""
from typing import Dict

from sfml import sf

from softshadow_volume.renderer.circle import build_shape_for_circle
from softshadow_volume.light import Light


def build_shapes_for_light(l: Light) -> Dict[str, sf.Shape]:
    """

    :param l:
    :return:
    """
    return {
        'inner': build_shape_for_circle(
            radius=l.inner_radius,
            position=l.pos,
            fill_color=l.color,
            outline_color=sf.Color.GREEN,
            outline_thickness=2
        ),
        'outer': build_shape_for_circle(
            radius=l.influence_radius,
            position=l.pos,
            fill_color=sf.Color.TRANSPARENT,
            outline_color=sf.Color.CYAN,
            outline_thickness=1
        )
    }
