# coding: utf-8
"""
"""
from dataclasses import dataclass, field
import numpy as np
from sfml import sf
import sys
from typing import List

EPSILON = sys.float_info.epsilon


@dataclass
class SolutionsForQuadraticEquation:
    has_real_solutions: bool = False
    roots: np.array = field(default_factory=np.array)

    def __eq__(self, other):
        return (self.has_real_solutions == other.has_real_solutions) and \
               np.allclose(self.roots, other.roots)


def min_vector2(v0: sf.Vector2, v1: sf.Vector2):
    return sf.Vector2(min(v0.x, v1.x), min(v0.y, v1.y))


def max_vector2(v0: sf.Vector2, v1: sf.Vector2):
    return sf.Vector2(max(v0.x, v1.x), max(v0.y, v1.y))


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


def DOT(p1: sf.Vector2, p2: sf.Vector2) -> float:
    return (p1.x * p2.x) + (p1.y * p2.y)


def NORM2(p: sf.Vector2) -> float:
    return DOT(p, p)


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
    constant = NORM2(p) - radius
    linear = 2 * DOT(p, dir)
    quadratic = NORM2(dir)
    return solve_quadratic_equation(constant, linear, quadratic)


def compute_clip_edge_with_influence_light_circle(
        pos_light: sf.Vector2,
        radius_light: float,
        edge_v0: sf.Vector2,
        edge_v1: sf.Vector2,
) -> List[sf.Vector2]:
    """
    bool Compute_Intersection_Segment_Circle(
         // IN
         const vec2& pos_light,
         const float r,
         const vec2 &E0,
         const vec2 &E1,
         // OUT
         vec2 intersections_segment_circle[2]
     )

    :param pos_light:
    :param radius_light:
    :param edge_v0:
    :param edge_v1:
    :return:
    """
    # results: intersections segment with circle
    results = []

    # to Light space
    l1 = edge_v0 - pos_light  # type: sf.Vector2
    l2 = edge_v1 - pos_light  # type: sf.Vector2

    # Intersection test between light circle's BBox and edge/wall
    if intersect_bounding_box(l1, l2, sf.Vector2(-radius_light, -radius_light),
                              sf.Vector2(+radius_light, +radius_light)):
        sqr_radius_light = radius_light * radius_light
        l1_to_l2 = l2 - l1  # type: sf.Vector2

        # (1-b) Using quadratic equation to find intersections of wall's
        # support line and influence light circle (at origin)
        solutions = compute_intersection_line_origin_circle(l1, l1_to_l2,
                                                            sqr_radius_light)

        # if real solutions => intersection between the support line and
        # the influence light circle
        if solutions.has_real_solutions:
            u1 = min(solutions.roots)
            u2 = max(solutions.roots)
            intersections_line_circle = (l1 + l1_to_l2 * u1, l1 + l1_to_l2 * u2)

            # O: center of the source light => O=(0, 0)
            # Compute the square root of
            # - segment [l1, l2]
            # - segment [O, l1]
            # - segment [O, l2]
            # - segment [l1, i1]
            # - segment [l1, i2]
            sqr_l1l2 = DOT(l1_to_l2, l1_to_l2)
            sqr_l1 = DOT(l1, l1)
            sqr_l2 = DOT(l2, l2)
            sqr_l1i1 = (u1 * u1) * sqr_l1l2
            sqr_l1i2 = (u2 * u2) * sqr_l1l2

            # 4 possibles intersections/inclusions between the edge and
            # the influence light circle.
            # ... first point of the edge in the circle ?
            test10 = (sqr_l1 <= sqr_radius_light)
            # ... second point of the edge in the circle ?
            test11 = (sqr_l2 <= sqr_radius_light)
            # ... le segment d'intersection intersecte le segment/wall ?
            test01 = not (
                    (u1 <= 0 and u2 <= 0) or
                    (sqr_l1i1 >= sqr_l1l2 and
                     sqr_l1i2 >= sqr_l1l2)
            )
            # ... edge's vertex are outside the circle ?
            test00 = not (test10 or test11)
            # ... the first edge's vertex is not in the circle ?
            test20 = not test10
            # ... the second edge's vertex is in the circle ?
            test21 = test11
            # ... le 1er point du segment/wall est dans le cercle ?
            test30 = test10
            # ... le 2nd point du segment/wall n'est pas dans le cercle ?
            test31 = not test11

            # cas 1: les vertex du segment/wall ne sont pas inclus dans
            # le cercle et il y a intersection
            if test00 and test01:
                results = intersections_line_circle
            # cas 2: les vertex du segment/wall sont inclus (tous les 2) dans
            # le cercle
            elif test10 and test11:
                results = [l1, l2]
            # cas 3: Un des deux sommets du segment/wall est inclu dans
            # le cercle (le 1er sommet dans ce cas)
            elif test20 and test21:
                results = [intersections_line_circle[0], l2]
            # cas 4: Un des deux sommets du segment/wall est inclu dans
            # le cercle (le 2nd sommet dans ce cas)
            elif test30 and test31:
                results = [l1, intersections_line_circle[1]]
            # sinon le segment/wall n'intersecte pas le cercle de lumiere
            # (donc ne projette pas d'ombre).
            # Ce cas correspond a la presence du segment dans un coin de la
            # boundingbox du cercle (mais non inclut dans le cercle)

    return results
