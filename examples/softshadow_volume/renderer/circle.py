"""
"""
from sfml import sf


def build_shape_for_circle(
        radius: float,
        position: sf.Vector2,
        outline_thickness=2,
        outline_color=sf.Color.GREEN,
        fill_color=sf.Color.WHITE
) -> sf.Shape:
    shape = sf.CircleShape(radius=radius)
    #
    shape.outline_thickness = outline_thickness
    shape.outline_color = outline_color
    shape.fill_color = fill_color
    #
    origin = sf.Vector2(radius, radius) * 0.5
    shape.origin = origin
    shape.position = position - origin

    return shape
