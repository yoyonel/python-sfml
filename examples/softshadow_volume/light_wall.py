"""
"""
from collections import defaultdict
from dataclasses import dataclass, field
import numpy as np
from typing import List, Tuple, Dict

from sfml import sf

from softshadow_volume import EPSILON
from softshadow_volume.bounding_volume import BoundingVolume
from softshadow_volume.compute_intersection import \
    compute_intersection_line_origin_circle
from softshadow_volume.light import Light
from softshadow_volume.shape_penumbra_volume import \
    construct_shape_penumbras_volumes
from softshadow_volume.shape_shadow_volume import construct_shape_shadow_volume
from softshadow_volume.compute_clip import (
    compute_clip_edge_with_circle
)
from softshadow_volume.vector2_tools import norm2


@dataclass
class LightWall:
    # light_pos: sf.Vector2 = field(default_factory=sf.Vector2)
    # light_inner_radius: float = 0.0
    # light_influence_radius: float = 1.0
    light: Light

    v0: sf.Vector2 = field(default_factory=sf.Vector2)
    v1: sf.Vector2 = field(default_factory=sf.Vector2)

    # inside_influence_circle: bool = False

    # clipped_edge_in_light_space: List[sf.Vector2] = field(
    #     init=False)
    # E0_LS: sf.Vector2 = field(init=False)
    # E1_LS: sf.Vector2 = field(init=False)

    # def update(self):
    #     light_pos = self.light.pos
    #
    #     # E0_LS et E1_LS sont les positions des deux extremites du mur,
    #     # relatives au centre de la lumiere
    #     self.E0_LS = self.v0 - light_pos
    #     self.E1_LS = self.v1 - light_pos
    #
    #     # Calcul du clip du segment representant le mur avec le circle
    #     # d'influence de la lumière.
    #     clipped_results = compute_clip_edge_with_circle(
    #         light_pos, self.light.influence_radius, self.v0, self.v1)
    #     if len(clipped_results) == 0:
    #         self.inside_influence_circle = False
    #     else:
    #         self.inside_influence_circle = True
    #         self.clipped_edge_in_light_space = clipped_results

    def clip_wall_with_light_influence(self) -> List[sf.Vector2]:
        E0_LS = self.v0 - self.light.pos
        E1_LS = self.v1 - self.light.pos
        E0_E1_LS = E1_LS - E0_LS
        solutions = compute_intersection_line_origin_circle(
            E0_LS,
            E0_E1_LS,
            self.light.influence_radius
        )
        results = [
            (E0_LS + E0_E1_LS * root) + self.light.pos
            for root in filter(
                lambda root: (0.0 <= root <= 1.0) and
                             norm2(
                                 E0_LS + E0_E1_LS * root) <= self.light.influence_radius ** 2 + 10e-11,
                list(solutions.roots) + [0.0,
                                         1.0] if solutions.has_real_solutions else []
            )
        ]
        return results

    def build_bounding_volumes_for_shadow_volumes(
            self,
            bv_hs_color: sf.Color = sf.Color.BLUE
    ) -> Dict[str, List[BoundingVolume]]:
        bvs = defaultdict(list)

        light_pos = self.light.pos

        # Est ce que le segment est à l'interieur du cercle de lumière ?
        intersections_segment_inner_circle = compute_clip_edge_with_circle(
            light_pos, self.light.inner_radius, self.v0, self.v1)
        if len(intersections_segment_inner_circle) == 2:
            # On construit la shape englobante pour l'influence de ce
            # segment par rapport a  la lumiere en l'occurence si la segment
            # est a  l'interieur de la lumiere,
            # il influence toute la projection de la lumiere
            shape_bb_light = sf.ConvexShape(4)
            shape_bb_light.set_point(0, sf.Vector2(
                -self.light.influence_radius,
                -self.light.influence_radius))
            shape_bb_light.set_point(1, sf.Vector2(
                +self.light.influence_radius,
                -self.light.influence_radius))
            shape_bb_light.set_point(2, sf.Vector2(
                +self.light.influence_radius,
                +self.light.influence_radius))
            shape_bb_light.set_point(3, sf.Vector2(
                -self.light.influence_radius,
                +self.light.influence_radius))
            shape_bb_light.position = self.light.pos
            shape_bb_light.outline_color = sf.Color.WHITE
            shape_bb_light.fill_color = sf.Color.WHITE

            bvs += [
                BoundingVolume(shape_bb_light,
                               self.v0 - self.light.pos,
                               self.v1 - self.light.pos,
                               *intersections_segment_inner_circle)
            ]
        # sinon le segment est en dehors du disque de lumiere
        else:
            clipped_edge = self.clip_wall_with_light_influence()

            if len(clipped_edge) == 2:
                bvs['penumbras'] = []

                clipped_edge_in_ls = [
                    v - self.light.pos
                    for v in clipped_edge
                ]
                # Add Bounding Volume for Hard Shadow
                # => Hard Shadow and Inner Penumbra
                # Construct_Shadow_Volume_Bounding_Volume(...)
                # clipped_edge_in_light_space = compute_clip_edge_with_circle(
                #      light_pos, self.light.influence_radius, self.v0, self.v1
                # )
                bv_hard_shadow = construct_shape_shadow_volume(
                    self.light.pos,
                    self.light.influence_radius,
                    clipped_edge_in_ls,
                    bv_hs_color
                )
                bvs['hard_shadow'] = [bv_hard_shadow]

                # Add Bounding Volumes for Penumbra (Inner Outer)
                # Construct_Penumbras_Bounding_Volumes
                bounding_volumes_for_penumbras = construct_shape_penumbras_volumes(
                    clipped_edge_in_ls,
                    self.light.influence_radius,
                    self.light.inner_radius,
                    sf.Color.BLUE
                )
                bvs['penumbras'] += bounding_volumes_for_penumbras
        return bvs
