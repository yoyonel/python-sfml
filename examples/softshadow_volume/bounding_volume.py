"""
https://github.com/yoyonel/holyspirit-softshadow2d/blob/version-juin2015/src/Bounding_Volume.h
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from sfml import sf


class TypeBoundingVolume(Enum):
    SHADOW_VOLUME = 0
    OUTER_PENUMBRA = 1
    INNER_PENUMBRA = 2
    PENUMBRAS_WIL = 3
    PENUMBRAS_WIL_TYPE_0 = 4
    PENUMBRAS_WIL_TYPE_1 = 5
    PENUMBRAS_WIL_TYPE_2 = 6
    PENUMBRAS_WIL_TYPE_3 = 7
    PENUMBRAS_WIL_TYPE_4 = 8


class TypeVertexComparedCircle(Enum):
    OUTSIDE_CIRCLE = 0
    ON_CIRCLE = 1
    INSIDE_CIRCLE = 2


@dataclass
class Edge:
    start: sf.Vector2 = field(default_factory=sf.Vector2)
    end: sf.Vector2 = field(default_factory=sf.Vector2)
    type_edge: TypeVertexComparedCircle = TypeVertexComparedCircle.OUTSIDE_CIRCLE


@dataclass
class BoundingVolume:
    shape: Optional[sf.Shape]

    edge: Edge = field(default_factory=Edge)
    intersection: Edge = field(default_factory=Edge)
    type_bv: TypeBoundingVolume = TypeVertexComparedCircle.OUTSIDE_CIRCLE
