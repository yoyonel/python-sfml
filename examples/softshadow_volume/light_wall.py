"""
"""
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Union

from sfml import sf

from softshadow_volume.bounding_volume import (
    BoundingVolume,
    BoundingVolumePenumbra
)
from softshadow_volume.light import Light
from softshadow_volume.bv_penumbra_volume import (
    construct_bounding_volumes_for_penumbras_volumes
)
from softshadow_volume.bv_shadow_volume import (
    construct_bounding_volume_for_shadow
)
from softshadow_volume.compute_clip import clip_edge_with_circle


@dataclass
class LightWall:
    light: Light

    v0: sf.Vector2 = field(default_factory=sf.Vector2)
    v1: sf.Vector2 = field(default_factory=sf.Vector2)

    def clip_wall_with_light(self):
        return clip_edge_with_circle(
            self.v0, self.v1, self.light.pos, self.light.inner_radius
        )

    def build_bounding_volumes_for_shadow_volumes(
            self,
            bv_hs_color: sf.Color = sf.Color.BLUE
    ) -> Dict[str, List[Union[BoundingVolume, BoundingVolumePenumbra]]]:
        bvs = defaultdict(list)

        # Est ce que le segment est à l'interieur du cercle de lumière ?
        intersections_with_inner_circle = self.clip_wall_with_light()
        if len(intersections_with_inner_circle) == 2:
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

            bvs['hard_shadow'] += [
                BoundingVolume(shape_bb_light,
                               self.v0 - self.light.pos,
                               self.v1 - self.light.pos,
                               *intersections_with_inner_circle)
            ]
        # sinon le segment est en dehors du disque de lumiere
        else:
            clipped_edge = clip_edge_with_circle(
                self.v0, self.v1, self.light.pos,
                self.light.influence_radius
            )

            if len(clipped_edge) == 2:
                bvs['penumbras'] = []

                clipped_edge_in_ls = [
                    v - self.light.pos
                    for v in clipped_edge
                ]
                # Add Bounding Volume for Hard Shadow
                # => Hard Shadow and Inner Penumbra
                # Construct_Shadow_Volume_Bounding_Volume(...)
                bv_hard_shadow = construct_bounding_volume_for_shadow(
                    self.light.pos,
                    self.light.influence_radius,
                    clipped_edge_in_ls,
                    bv_hs_color
                )
                bvs['hard_shadow'] = [bv_hard_shadow]

                # Add Bounding Volumes for Penumbra (Inner Outer)
                # Construct_Penumbras_Bounding_Volumes
                bounding_volumes_for_penumbras = construct_bounding_volumes_for_penumbras_volumes(
                    clipped_edge_in_ls,
                    self.light,
                    sf.Color.BLUE
                )
                bvs['penumbras'] += bounding_volumes_for_penumbras
        return bvs
