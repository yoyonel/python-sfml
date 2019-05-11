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
    construct_bounding_volume_for_shadow,
    construct_bounding_volume_for_full_influence_light)
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

        # Edge/wall inside the (inner) light's circle ?
        intersections_with_inner_circle = self.clip_wall_with_light()
        if len(intersections_with_inner_circle) == 2:
            # FIXME: we have to clip the light wall with light source
            # and generate 1 or 2 new light wall(s) => ~XOR boolean operation
            bvs['hard_shadow'] += [
                construct_bounding_volume_for_full_influence_light(
                    self.light,
                    self.v0, self.v1,
                    intersections_with_inner_circle
                )
            ]
        # otherwise edge is outside the (inner) light's circle
        else:
            # clip edge with influence light's circle
            clipped_edge = clip_edge_with_circle(
                self.v0, self.v1, self.light.pos,
                self.light.influence_radius
            )

            if len(clipped_edge) == 2:
                bvs['penumbras'] = []

                clipped_edge_in_ls = [v - self.light.pos for v in clipped_edge]
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
                bv_penumbras = construct_bounding_volumes_for_penumbras_volumes(
                    clipped_edge_in_ls,
                    self.light,
                    sf.Color.RED
                )
                bvs['penumbras'] += bv_penumbras
        return bvs
