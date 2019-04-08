"""
"""
from dataclasses import dataclass, field
from random import randint
from sfml import sf

from .screen import Screen


@dataclass
class Player:
    speed: float = 0.0

    height: int = 43
    width: int = 40

    maxOffroadSpeed: float = 150.0
    maxForwardSpeed: float = 400.0
    maxBackwardSpeed: float = -200.0

    y: int = 1500
    z: float = 0.0
    x: float = 0.0

    scale: float = 3.0

    tex_coord_s: int = 407
    tex_coord_t: int = 0

    speedIdlingResistance: float = -.8
    speedOffroadResistance: float = -1.0
    speedAcceleration: float = .4 * 2
    speedBraking: float = -2.0

    sprite: sf.Sprite = field(init=False)

    def create_sprite(self, screen: Screen):
        fp = "data/mercedesspritesheets.png"
        tex = sf.Texture.from_file(fp)  # type: sf.Texture
        tex.smooth = False
        self.sprite = sf.Sprite(texture=tex)
        self.steer_straight()
        self.sprite.position = screen.half_width - self.width * 2, 500
        self.sprite.scale((self.scale, self.scale))

    def turn_right(self, turn_weight: float):
        self.x += turn_weight

        self.sprite.texture_rectangle = (self.tex_coord_s + self.height,
                                         self.tex_coord_t,
                                         self.width, self.height)

    def turn_left(self, turn_weight: float):
        self.x -= turn_weight

        self.sprite.texture_rectangle = (self.tex_coord_s - self.height,
                                         self.tex_coord_t,
                                         self.width, self.height)

    def steer_straight(self):
        self.sprite.texture_rectangle = (self.tex_coord_s, self.tex_coord_t,
                                         self.width, self.height)

    @property
    def is_driving_forward(self):
        return self.speed > 0.0

    @property
    def has_reached_max_forward_speed(self):
        return self.speed >= self.maxForwardSpeed

    @property
    def is_driving_backward(self):
        return self.speed < 0.0

    @property
    def has_reached_max_backward_speed(self):
        return self.speed <= self.maxBackwardSpeed

    @property
    def is_stopped(self):
        return not abs(self.speed)

    @property
    def is_player_offroad(self):
        return self.x < -1.2 or self.x > 1.0

    def per_loop_idling_resistance(self):
        if self.is_driving_forward and self.speed < self.speedAcceleration:
            self.speed = 0.0
        elif self.is_driving_forward:
            self.speed += self.speedIdlingResistance
        elif self.is_driving_backward and self.speed > -self.speedAcceleration:
            self.speed = 0.0
        elif self.is_driving_backward:
            self.speed -= self.speedIdlingResistance

    def per_loop_forward_braking(self):
        self.speed += self.speedBraking

    def per_loop_backward_braking(self):
        self.speed -= self.speedBraking

    def per_loop_forward_acceleration(self):
        self.speed += self.speedAcceleration

    def per_loop_backward_acceleration(self):
        self.speed -= self.speedAcceleration

    def per_loop_forward_acceleration_offroad(self):
        # player max speed off-road
        self.y = 1500

        if self.speed > self.maxOffroadSpeed:
            self.speed += self.speedOffroadResistance
        else:
            self.per_loop_forward_acceleration()

        # causes the ground to shake
        self.y += (1 + randint(0, 298))
