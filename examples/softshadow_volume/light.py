"""
"""
from dataclasses import dataclass

from sfml import sf


@dataclass
class Light:
    pos: sf.Vector2
    inner_radius: float = 1.0
    influence_radius: float = 1.0
    intensity: float = 1.0
    color: sf.Color = sf.Color.WHITE