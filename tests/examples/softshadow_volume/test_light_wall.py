from sfml import sf

from softshadow_volume.light_wall import LightWall


def test_light_wall_default_values():
    light_wall = LightWall()
    assert light_wall.pos == sf.Vector2()
    assert light_wall.influence_radius == 1.0
    assert light_wall.inner_radius == 0.0
    assert light_wall.vertex_wall_0 == sf.Vector2()
    assert light_wall.vertex_wall_1 == sf.Vector2()
    assert light_wall.list_bv == []
