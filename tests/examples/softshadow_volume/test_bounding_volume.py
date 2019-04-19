from sfml import sf

from softshadow_volume.bounding_volume import BoundingVolume


def test_bounding_volume_default_values():
    bv = BoundingVolume(shape=None)

    assert bv.bv_sv_vertex_0 == sf.Vector2()
    assert bv.bv_sv_vertex_1 == sf.Vector2()
    assert bv.proj_clipped_vertex_0 == sf.Vector2()
    assert bv.proj_clipped_vertex_1 == sf.Vector2()
    assert bv.shape is None
