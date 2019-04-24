"""
"""
from sfml import sf


def build_edge_shape(v0: sf.Vector2, v1: sf.Vector2,
                     color: sf.Color) -> sf.Drawable:
    """

    :param v0:
    :param v1:
    :return:
    """
    points = sf.VertexArray()
    points.append(sf.Vertex(v0, color))
    points.append(sf.Vertex(v1, color))
    points.primitive_type = sf.PrimitiveType.LINES
    return points
