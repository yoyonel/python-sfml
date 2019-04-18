"""
"""
from dataclasses import dataclass, field
from typing import List

from sfml import sf

from softshadow_volume.bounding_volume import BoundingVolume


@dataclass
class LightWall:
    pos: sf.Vector2 = field(default_factory=sf.Vector2)
    inner_radius: float = 0.0
    influence_radius: float = 1.0
    vertex_wall_0: sf.Vector2 = field(default_factory=sf.Vector2)
    vertex_wall_1: sf.Vector2 = field(default_factory=sf.Vector2)
    list_bv: List[BoundingVolume] = field(default_factory=list)
