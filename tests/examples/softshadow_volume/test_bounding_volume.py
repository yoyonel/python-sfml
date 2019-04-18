from sfml import sf

from softshadow_volume.bounding_volume import (
    BoundingVolume,
    Edge,
    TypeVertexComparedCircle
)


def test_edge_default_values():
    edge = Edge()
    assert edge.start == sf.Vector2(0, 0)
    assert edge.end == sf.Vector2(0, 0)
    assert edge.type_edge == TypeVertexComparedCircle.OUTSIDE_CIRCLE


def test_bounding_volume_default_values():
    bv = BoundingVolume(shape=None)
    default_edge = Edge(
        sf.Vector2(0, 0),
        sf.Vector2(0, 0),
        TypeVertexComparedCircle.OUTSIDE_CIRCLE
    )
    assert bv.edge == default_edge
    assert bv.intersection == default_edge
    assert bv.shape is None
