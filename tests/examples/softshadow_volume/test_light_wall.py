from sfml import sf

from softshadow_volume.light import Light
from softshadow_volume.light_wall import LightWall


def test_light_wall_default_values():
    light_wall = LightWall(Light(sf.Vector2()))
    assert light_wall.v0 == sf.Vector2()
    assert light_wall.v1 == sf.Vector2()
