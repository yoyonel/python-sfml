"""
"""
from dataclasses import dataclass
from typing import Optional
from sfml import sf

from . project_point import ProjectedPoint
from . road import road_width
from . screen import Screen


class Road(object):
    pass


@dataclass
class Line:
    center_of_line: sf.Vector3 = sf.Vector3()

    screen_coord: ProjectedPoint = ProjectedPoint()
    scale: float = 0.0
    curve: float = 0.0

    clip: int = 0

    sprite_x: int = 0
    tex_object: Optional[sf.Texture] = None

    def project(self, cam: sf.Vector3,
                screen: Screen,
                cam_depth: float) -> None:
        x, y, z = self.center_of_line

        self.scale = cam_depth / (z - cam.z)
        scale = self.scale

        self.screen_coord = ProjectedPoint(
            (1 + scale * (x - cam.x)) * screen.half_width,
            (1 - scale * (y - cam.y)) * screen.half_height,
            scale * road_width * screen.half_width,
        )

    def draw_sprite(self, app: sf.RenderWindow, screen: Screen):
        if self.tex_object:
            # new instance of Sprite
            # TODO: really needed ?
            sprite_object = sf.Sprite(texture=self.tex_object)

            tex_w = sprite_object.texture_rectangle.width
            tex_h = sprite_object.texture_rectangle.height

            sc_w = self.screen_coord.w
            scale = self.scale
            sprite_x = self.sprite_x

            dest_x = self.screen_coord.x + scale * sprite_x * screen.half_width
            dest_y = self.screen_coord.y + 4
            # TODO: Understand this magical factor => 266
            dest_w = tex_w * sc_w / (266 * 1)
            dest_h = tex_h * sc_w / (266 * 1)

            dest_x += dest_w * sprite_x  # offsetX
            dest_y += dest_h * (-1)  # offsetY

            # clippings
            #
            clip_h = max(0, dest_y + dest_h - self.clip)
            if clip_h >= dest_h:
                return
            # scissor
            rect = (0, 0, tex_w, tex_h - tex_h * clip_h / dest_h)
            sprite_object.texture_rectangle = rect

            scale = (dest_w / tex_w, dest_h / tex_h)
            sprite_object.scale(scale)
            sprite_object.position = dest_x, dest_y

            app.draw(sprite_object)
