"""
"""
from dataclasses import dataclass, field
from typing import List

from sfml import sf

from softshadow_volume.bounding_volume import BoundingVolume
from softshadow_volume.shape_shadow_volume import construct_shape_shadow_volume
from softshadow_volume.compute_clip import (
    compute_clip_edge_with_influence_light_circle
)


@dataclass
class LightWall:
    pos: sf.Vector2 = field(default_factory=sf.Vector2)
    inner_radius: float = 0.0
    influence_radius: float = 1.0

    vertex_wall_0: sf.Vector2 = field(default_factory=sf.Vector2)
    vertex_wall_1: sf.Vector2 = field(default_factory=sf.Vector2)

    list_bv: List[BoundingVolume] = field(default_factory=list)

    sqr_inner_radius: float = field(init=False)

    def __post_init__(self):
        self.sqr_inner_radius = self.inner_radius * self.inner_radius

    def compute_shadow_volumes(self):
        # E0_LS et E1_LS sont les positions des deux extremites du mur,
        # relatives au centre de la lumiere
        E0_LS = self.vertex_wall_0 - self.pos
        E1_LS = self.vertex_wall_1 - self.pos

        # Calcul du clip du segment representant le mur avec le circle
        # d'influence de la lumière.
        clipped_wall_with_influence_circle = compute_clip_edge_with_influence_light_circle(
            self.pos, self.influence_radius,
            self.vertex_wall_0, self.vertex_wall_1)

        # Est ce que le mur est dans le cercle d'influence
        # de la lumiere (donc projete de l'ombre) ?
        if len(clipped_wall_with_influence_circle) != 0:
            # On a les deux vertex issus du clipping du segment par
            # le cercle d'influence de la lumieres

            # Est ce que le segment est à l'interieur du cercle de lumière ?
            intersections_segment_inner_circle = compute_clip_edge_with_influence_light_circle(
                self.pos, self.inner_radius,
                self.vertex_wall_0, self.vertex_wall_1)
            if len(intersections_segment_inner_circle) == 2:
                # On construit la shape englobante pour l'influence de ce
                # segment par rapport a  la lumiere en l'occurence si la segment
                # est a  l'interieur de la lumiere,
                # il influence toute la projection de la lumiere
                shape_bb_light = sf.ConvexShape(4)
                shape_bb_light.set_point(0, sf.Vector2(-self.influence_radius,
                                                       -self.influence_radius))
                shape_bb_light.set_point(1, sf.Vector2(+self.influence_radius,
                                                       -self.influence_radius))
                shape_bb_light.set_point(2, sf.Vector2(+self.influence_radius,
                                                       +self.influence_radius))
                shape_bb_light.set_point(3, sf.Vector2(-self.influence_radius,
                                                       +self.influence_radius))
                shape_bb_light.position = self.pos
                shape_bb_light.outline_color = sf.Color.WHITE
                shape_bb_light.fill_color = sf.Color.WHITE

                self.list_bv.append(
                    BoundingVolume(shape_bb_light, E0_LS, E1_LS,
                                   *intersections_segment_inner_circle)
                )
            # sinon le segment est en dehors du disque de lumiere
            else:
                # Add Bounding Volume for Hard Shadow
                # => Hard Shadow and Inner Penumbra
                # Construct_Shadow_Volume_Bounding_Volume(...)
                bv_hard_shadow = construct_shape_shadow_volume(
                        self.pos,
                        self.influence_radius,
                        clipped_wall_with_influence_circle,
                        sf.Color.BLUE
                    )
                self.list_bv.append(bv_hard_shadow)

                # Add Bounding Volumes for Penumbra (Inner Outer)
                # Construct_Penumbras_Bounding_Volumes
