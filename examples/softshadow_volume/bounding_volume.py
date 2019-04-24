"""
https://github.com/yoyonel/holyspirit-softshadow2d/blob/version-juin2015/src/Bounding_Volume.h
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Iterator, Tuple

import numpy as np
from sfml import sf

from softshadow_volume.vector2_tools import norm2


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


def _compare_distances(d0, d1):
    if np.isclose(d0, d1):
        return TypeVertexComparedCircle.ON_CIRCLE
    elif d0 > d1:
        return TypeVertexComparedCircle.OUTSIDE_CIRCLE
    else:
        return TypeVertexComparedCircle.INSIDE_CIRCLE


def compute_type_vertex(r: float,
                        vertex: sf.Vector2) -> TypeVertexComparedCircle:
    return _compare_distances(norm2(vertex), r)


def compute_types_vertex(
        r: float,
        list_vertex: List[sf.Vector2]
) -> Iterator[TypeVertexComparedCircle]:
    return map(lambda v: compute_type_vertex(r, v), list_vertex)


@dataclass
class BoundingVolume:
    shape: Optional[sf.Shape]
    proj_clipped_vertex_0: sf.Vector2 = field(default_factory=sf.Vector2)
    proj_clipped_vertex_1: sf.Vector2 = field(default_factory=sf.Vector2)
    bv_sv_vertex_0: sf.Vector2 = field(default_factory=sf.Vector2)
    bv_sv_vertex_1: sf.Vector2 = field(default_factory=sf.Vector2)


@dataclass
class BoundingVolumePenumbra:
    # TODO: rename variables members
    # Points on unit light circle for generating penumbras volumes
    p_light: List[List[sf.Vector2]]
    # edge's point
    clipped_edge_in_ls: List[sf.Vector2]
    # edge's centers proj (for penumbras volumes)
    proj_edge_with_projs_light: List[List[sf.Vector2]]
    # points for bounding volumes (for penumbras volumes)
    bv: List[sf.Vector2]
    #
    shapes_inner_penumbras: Optional[List[sf.Shape]]
    shapes_outer_penumbras: Optional[List[sf.Shape]]
