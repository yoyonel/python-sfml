"""
"""
from dataclasses import dataclass, field

from sfml import sf


@dataclass
class Background:
    tex_filename: str = "data/bg.png"

    texture: sf.Texture = field(init=False)
    sprite: sf.Sprite = field(init=False)

    def __post_init__(self):
        try:
            self.texture = sf.Texture.from_file(self.tex_filename)
        except IOError as error:
            raise RuntimeError("An error occured: {0}".format(error))

        # Background
        self.texture.repeated = True
        self.sprite = sf.Sprite(self.texture)
        self.sprite.texture_rectangle = (0, 0, 5000, 411)
        self.sprite.position = (-2000, 0)

    def update_position(self, road_curve: float, player_speed: float):
        # sprite_bg.move((lines[start_pos].curve * (player.speed / 100.0), 0))
        if player_speed > 0:
            self.sprite.move((-road_curve * 2, 0))
        if player_speed < 0:
            self.sprite.move((+road_curve * 2, 0))
