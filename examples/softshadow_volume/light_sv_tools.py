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
{
    bool result = false;

    vec2 l1 = E0 - pos_light;
    vec2 l2 = E1 - pos_light;
    vec2 l1_to_l2 = l2 - l1;

    // Test d'intersection entres les BBox du cercle et du segment/wall
    if (Intersect_BoundingBox(l1, l2, sf::Vector2f(-r,-r), sf::Vector2f(+r,+r)))
    {
        float f_square_radius_light = r*r;

        // (1-b)  systeme quadratique pour trouver les intersections de la droite support du mur et le cercle d'influence a  l'origine
        Typ_Solutions_Quadratic_Equation solutions = Solve_Quadratic_Equation(l1, l1_to_l2, f_square_radius_light);

        //
        bool b_wall_intersect_circle = true;

        // - si intersection (la ligne support avec le cercle de lumiere)
        if (solutions.b_has_solutions)
        {
            const float &f_u1 = solutions.f_u0;
            const float &f_u2 = solutions.f_u1;
            // On reconstruit les intersections
            sf::Vector2f intersections_line_circle[2] = {
                sf::Vector2f(l1 + l1_to_l2*f_u1),
                sf::Vector2f(l1 + l1_to_l2*f_u2)
            };
            // On calcul les distances au carre
            //  du segment [l1, l2]
            //  du segment [O, l1] (O: centre de la source de lumiere => O=(0, 0))
            //  du segment [O, l2] (O: centre de la source de lumiere => O=(0, 0))
            //  du segment [l1, i1]
            //  du segment [l1, i2]
            float f_square_l1l2 = DOT(l1_to_l2, l1_to_l2);
            float f_square_l1   = DOT(l1, l1);
            float f_square_l2   = DOT(l2, l2);
            float f_square_l1i1 = (f_u1*f_u1)*f_square_l1l2;
            float f_square_l1i2 = (f_u2*f_u2)*f_square_l1l2;

            // 4 cas d'intersections/inclusion possibles pour le segment et le cercle
            // Est ce que ...
            bool test10 = (f_square_l1<=f_square_radius_light);                                                         // ... le 1er point du segment/wall est dans le cercle ?
            bool test11 = (f_square_l2<=f_square_radius_light);                                                         // ... le 2nd point du segment/wall est dans le cercle ?
            bool test01 = !((f_u1<=0 && f_u2<=0) || (f_square_l1i1>=f_square_l1l2 && f_square_l1i2>=f_square_l1l2));    // ... le segment d'intersection intersecte le segment/wall ?
            bool test00 = !(test10 || test11);                                                                          // ... les deux points du segment sont en dehors du cercle ?
            bool test20 = !test10;                                                                                      // ... le 1er point du segment/wall n'est pas dans le cercle ?
            bool &test21 = test11;                                                                                      // ... le 2nd point du segment/wall est dans le cercle ?
            bool &test30 = test10;                                                                                      // ... le 1er point du segment/wall est dans le cercle ?
            bool test31 = !test11;                                                                                      // ... le 2nd point du segment/wall n'est pas dans le cercle ?
            //
            if (test00&&test01) // cas 1: les vertex du segment/wall ne sont pas inclus dans le cercle et il y a intersection
            {
                intersections_segment_circle[0] = intersections_line_circle[0];
                intersections_segment_circle[1] = intersections_line_circle[1];
            }
            else if (test10&&test11) // cas 2: les vertex du segment/wall sont inclus (tous les 2) dans le cercle
            {
                intersections_segment_circle[0] = l1;
                intersections_segment_circle[1] = l2;
            }
            else if (test20&&test21) // cas 3: Un des deux sommets du segment/wall est inclu dans le cercle (le 1er sommet dans ce cas)
            {
                intersections_segment_circle[0] = intersections_line_circle[0];
                intersections_segment_circle[1] = l2;
            }
            else if (test30&&test31) // cas 4: Un des deux sommets du segment/wall est inclu dans le cercle (le 2nd sommet dans ce cas)
            {
                intersections_segment_circle[0] = l1;
                intersections_segment_circle[1] = intersections_line_circle[1];

            }
            else
            {
                // sinon le segment/wall n'intersecte pas le cercle de lumiere (donc ne projette pas d'ombre)
                // Ce cas correspond a  la presence du segment dans un coin de la boundingbox du cercle (mais non inclut dans le cercle)
                b_wall_intersect_circle = false;
            }
        }
        result = b_wall_intersect_circle && solutions.b_has_solutions;
    }

    return result;
}
"""
from dataclasses import dataclass, field

import numpy as np
from sfml import sf
import sys

EPSILON = sys.float_info.epsilon


@dataclass
class SolutionsForQuadraticEquation:
    has_real_solutions: bool = False
    roots: np.array = field(default_factory=np.array)


def min_vector2(v0: sf.Vector2, v1: sf.Vector2):
    return sf.Vector2(min(v0.x, v1.x), min(v0.y, v1.y))


def max_vector2(v0: sf.Vector2, v1: sf.Vector2):
    return sf.Vector2(max(v0.x, v1.x), max(v0.y, v1.y))


def intersect_bounding_box(_v00: sf.Vector2, _v01: sf.Vector2,
                           _v10: sf.Vector2, _v11: sf.Vector2) -> bool:
    """

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
        coef_constant: float,
        coef_linear: float,
        coef_quadratic: float
) -> SolutionsForQuadraticEquation:
    """

    :param coef_constant:
    :param coef_linear:
    :param coef_quadratic:
    :return:
    """
    roots = np.roots([coef_quadratic, coef_linear, coef_constant])
    return SolutionsForQuadraticEquation(
        has_real_solutions=all(np.isreal(roots)),
        roots=roots
    )
