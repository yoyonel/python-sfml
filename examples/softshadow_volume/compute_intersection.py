from dataclasses import dataclass, field

import numpy as np
from sfml import sf

from softshadow_volume.vector2_tools import min_vector2, max_vector2, norm2, \
    dot, normal, det


@dataclass
class SolutionsForQuadraticEquation:
    has_real_solutions: bool = False
    roots: np.array = field(default_factory=np.array)

    def __eq__(self, other):
        return (self.has_real_solutions == other.has_real_solutions) and \
               np.allclose(self.roots, other.roots)


def intersect_bounding_box(_v00: sf.Vector2, _v01: sf.Vector2,
                           _v10: sf.Vector2, _v11: sf.Vector2) -> bool:
    """
    bool Intersect_BoundingBox( const vec2& _v00, const vec2& _v01,
                                const vec2& _v10, const vec2& _v11)

    :param _v00:
    :param _v01:
    :param _v10:
    :param _v11:
    :return:
    """
    min_0 = min_vector2(_v00, _v01)
    max_0 = max_vector2(_v00, _v01)
    min_1 = min_vector2(_v10, _v11)
    max_1 = max_vector2(_v10, _v11)

    return not ((min_0.x > max_1.x) or
                (min_1.x > max_0.x) or
                (min_0.y > max_1.y) or
                (min_1.y > max_0.y))


def solve_quadratic_equation(
        constant: float,
        linear: float,
        quadratic: float
) -> SolutionsForQuadraticEquation:
    """
    Typ_Solutions_Quadratic_Equation Solve_Quadratic_Equation(
        float A, float B, float C
    )

    :param constant:
    :param linear:
    :param quadratic:
    :return:
    """
    roots = np.roots([quadratic, linear, constant])
    return SolutionsForQuadraticEquation(
        has_real_solutions=(len(roots) > 0) and all(np.isreal(roots)),
        roots=roots
    )


def compute_intersection_line_origin_circle(
        p: sf.Vector2,
        dir: sf.Vector2,
        radius: float
) -> SolutionsForQuadraticEquation:
    """
    Typ_Solutions_Quadratic_Equation Solve_Quadratic_Equation(
        vec2 _A,
        vec2 _AB,
        float _radius
    )

    :param p:
    :param dir:
    :param radius:
    :return:
    """
    # (1-b)  systeme quadratique pour trouver les intersections
    # de la droite support du mur et le cercle a  l'origine
    constant = norm2(p) - radius*radius
    linear = 2 * dot(p, dir)
    quadratic = norm2(dir)
    return solve_quadratic_equation(constant, linear, quadratic)


def compute_intersection_of_tangents_lines_on_circle(
        P1: sf.Vector2,
        P3: sf.Vector2
) -> sf.Vector2:
    """
    vec2 Compute_Intersection_Lines( const vec2& P1, const vec2& P3)

    P1, P2 points on the same circle.
    note: don't test if lines are colinear

    :param P1:
    :param P2:
    :return:
    """
    P2 = P1 + normal(P1)
    P4 = P3 + normal(P3)

    P3P1 = P1 - P4
    P1P2 = P2 - P1
    P3P4 = P4 - P3

    denum = 1 / det(P1P2, P3P4)
    ua = det(P3P4, P3P1) * denum

    return P1 + P1P2 * ua