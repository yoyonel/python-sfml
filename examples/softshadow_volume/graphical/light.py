"""
"""
from typing import Dict

from sfml import sf

from softshadow_volume.graphical.circle import build_circle_shape
from softshadow_volume.light import Light


def build_shapes_for_light(l: Light) -> Dict[str, sf.Shape]:
    """

    :param l:
    :return:
    """
    return {
        'inner': build_circle_shape(
            radius=l.inner_radius,
            position=l.pos,
            fill_color=l.color,
            outline_color=sf.Color.GREEN,
            outline_thickness=2
        ),
        'outer': build_circle_shape(
            radius=l.influence_radius,
            position=l.pos,
            fill_color=sf.Color.TRANSPARENT,
            outline_color=sf.Color.CYAN,
            outline_thickness=1
        )
    }
