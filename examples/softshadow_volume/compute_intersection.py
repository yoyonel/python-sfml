from dataclasses import dataclass, field
from math import sqrt
from typing import Tuple, Optional, List

import numpy as np
from sfml import sf

from softshadow_volume import EPSILON
from softshadow_volume.vector2_tools import min_vector2, max_vector2, norm2, \
    dot, normal, det, norm, normalize


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
        p_on_line: sf.Vector2,
        vdir_line: sf.Vector2,
        radius: float
) -> SolutionsForQuadraticEquation:
    """
    Typ_Solutions_Quadratic_Equation Solve_Quadratic_Equation(
        vec2 _A,
        vec2 _AB,
        float _radius
    )

    :param p_on_line:
    :param vdir_line:
    :param radius:
    :return:
    """
    # (1-b)  systeme quadratique pour trouver les intersections
    # de la droite support du mur et le cercle a  l'origine
    constant = norm2(p_on_line) - radius ** 2
    linear = 2 * dot(p_on_line, vdir_line)
    quadratic = norm2(vdir_line)
    return solve_quadratic_equation(constant, linear, quadratic)


def compute_intersection_of_tangents_lines_on_circle(
        p1: sf.Vector2,
        p3: sf.Vector2
) -> sf.Vector2:
    """
    vec2 Compute_Intersection_Lines( const vec2& P1, const vec2& P3)

    P1, P2 points on the same circle.
    note: don't test if lines are colinear

    :param p1:
    :param p3:
    :return:
    """
    p2 = p1 + normal(p1)
    p4 = p3 + normal(p3)

    p3_p1 = p1 - p4
    p1_p2 = p2 - p1
    p3_p4 = p4 - p3

    d = det(p1_p2, p3_p4)
    if np.isclose(d, 0.0):
        return p1

    denum = 1 / d
    ua = det(p3_p4, p3_p1) * denum

    return p1 + p1_p2 * ua


def compute_intersection_circle_circle(
        o0: sf.Vector2,
        r0: float,
        o1: sf.Vector2,
        r1: float
) -> Optional[List[sf.Vector2]]:
    """
    // url: http://mathworld.wolfram.com/Circle-CircleIntersection.html
    // Methode utilisant un changement de repere (2D)
    bool Compute_Intersection_Circles_1(
        const vec2& O0,
        const float R0,
        const vec2& O1,
        const float R1,
        vec2 P[2]
    )

    :param o0:
    :param r0:
    :param o1:
    :param r1:
    :return:
    """
    results = None

    o0_to_01 = o1 - o0
    normal_o0_to_01 = normal(o0_to_01)

    d = norm(o0_to_01)
    if np.isclose(d, 0.0):
        return None

    r = r1
    R = r0

    d2 = d * d
    r2 = r * r
    R2 = R * R

    # Calcul de la coordonnee x commune aux 2 intersections
    denum = 1 / (2 * d)
    denum2 = denum * denum
    x = (d2 - r2 + R2) * denum
    # Calcul des y des intersections
    square_y = (4 * d2 * R2 - (d2 - r2 + R2) * (d2 - r2 + R2)) * denum2
    # TODO: deal with square_y close to 0 => 1 solution
    if square_y >= -EPSILON:
        y01 = sqrt(square_y)
        y0 = +y01
        y1 = -y01
        # Normalisation des vecteurs caracterisant les axes
        # du repere de calcul d'intersections
        o0_to_01 = o0_to_01 / d
        normal_o0_to_01 = normalize(normal_o0_to_01)

        results = (
            o0_to_01 * x + normal_o0_to_01 * y0,
            o0_to_01 * x + normal_o0_to_01 * y1
        )

    return results


def compute_intersection_solid_angle_1d(
        exsec: float
) -> List[sf.Vector2]:
    """

    https://fr.wikipedia.org/wiki/Fonction_trigonom%C3%A9trique
    https://en.wikipedia.org/wiki/Exsecant
    https://www.dcode.fr/simplification-mathematique
    https://en.wikipedia.org/wiki/Solid_angle

    :param exsec:
    :return:
    """
    assert exsec >= 0.0

    if np.isclose(exsec, 0.0):
        return [sf.Vector2(1, 0)]

    # https://www.google.com/search?ei=RbO8XJvvIsuJlwSbrqmgCA&q=1%2F%28x%2B1%29&oq=1%2F%28x%2B1%29&gs_l=psy-ab.3..35i39j0j0i203l8.11913.41442..92049...4.0..1.113.632.1j5......0....1..gws-wiz.......0i71j0i7i30j0i30.iNZtWRk-E4Y
    x = 1 / (exsec + 1)
    # https://www.google.fr/search?ei=obK8XLatH9DeasautdgN&q=sqrt%28%28x*%28x%2B2%29%29%29%2F%28x%2B1%29&oq=sqrt%28%28x*%28x%2B2%29%29%29%2F%28x%2B1%29&gs_l=psy-ab.3..0i8i10i30j0i8i30j0i8i10i30l2j0i8i30l6.1163329.1164961..1165528...0.0..0.73.261.4......0....1..gws-wiz.......0i71.iYkBYeR_A0E
    y = sqrt(exsec * (exsec + 2)) * x

    # solutions
    return [sf.Vector2(x, -y), sf.Vector2(x, +y)]


def compute_intersection_solid_angle_2d(
        v: sf.Vector2
) -> List[sf.Vector2]:
    """

    https://stackoverflow.com/questions/4780119/2d-euclidean-vector-rotations

    :param v:
    :return:
    """
    # convert in 1d problem
    norm_v = norm(v)
    cos_theta, sin_theta = v / norm_v
    solid_angle_vectors = compute_intersection_solid_angle_1d(norm_v - 1.0)

    # return back to 2d problem with 2d rotation
    return [
        sf.Vector2(
            solid_angle_vector.x * cos_theta - solid_angle_vector.y * sin_theta,
            solid_angle_vector.x * sin_theta + solid_angle_vector.y * cos_theta,
        )
        for solid_angle_vector in solid_angle_vectors
    ]


def compute_projectives_centers(
        p_ls: sf.Vector2,
        inner_radius: float,
) -> List[sf.Vector2]:
    """

    Using Pythagore to resolve the problem.

    :param p_ls:
    :param inner_radius:
    :return:
    """
    # convert into 1D problem
    norm_p = norm(p_ls)
    # Pythagore => cosinus -> sinus
    cos_theta_cp = inner_radius / norm_p
    sin_theta_cp = sqrt(1 - cos_theta_cp ** 2)
    proj_centers_ls = (
        sf.Vector2(cos_theta_cp, sign_factor*sin_theta_cp) * inner_radius
        for sign_factor in (+1, -1)
    )

    # return back to 2d problem with 2d rotation
    # 2D orientation
    cos_theta_p, sin_theta_p = p_ls / norm_p
    return [
        sf.Vector2(
            proj_center_ls.x * cos_theta_p - proj_center_ls.y * sin_theta_p,
            proj_center_ls.x * sin_theta_p + proj_center_ls.y * cos_theta_p,
        )
        for proj_center_ls in proj_centers_ls
    ]
