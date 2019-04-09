from examples.outrun.engine.project_point import ProjectedPoint
from sfml import sf


shape = sf.ConvexShape(4)


def draw_quad(
        w: sf.RenderWindow,
        c: sf.Color,
        p1: ProjectedPoint,
        p2: ProjectedPoint
) -> None:
    """

    :param w:
    :param c:
    :param p1:
    :param p2:
    """
    shape.fill_color = c
    shape.set_point(0, sf.Vector2(p1.x - p1.w, p1.y))
    shape.set_point(1, sf.Vector2(p2.x - p2.w, p2.y))
    shape.set_point(2, sf.Vector2(p2.x + p2.w, p2.y))
    shape.set_point(3, sf.Vector2(p1.x + p1.w, p1.y))
    w.draw(shape)
