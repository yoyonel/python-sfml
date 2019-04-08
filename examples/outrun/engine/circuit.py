"""
"""
from dataclasses import dataclass, field
from math import sin
from sfml import sf
from typing import Callable, Iterator

from . circular_list import CircularList
from . line import Line
from . project_point import ProjectedPoint
from . rendering import draw_quad
from . road import Road


@dataclass
class Circuit:
    nb_lines: int = 1600
    seg_length: int = 200

    lines: CircularList = field(init=False)

    def build(self):
        """Define circuit with parametric equations for y,z components
        and the road's curvature.
        """
        self.lines = CircularList([
            Line(center_of_line=sf.Vector3(y=(i > 750) * (sin(i / 30) * 1500),
                                           z=i * self.seg_length + 1),
                 curve=(300 > i < 700) * 0.5 + (i > 1100) * (-0.7))
            for i in range(self.nb_lines)
        ])

    def select_lines(
            self,
            func_select_id_line: Callable[[int], bool]
    ) -> Iterator[Line]:
        for i in filter(func_select_id_line, range(self.nb_lines)):
            yield self.lines[i]

    def set_object(
            self,
            func_select_id_line: Callable[[int], bool],
            sprite_x: float,
            tex_object: sf.Texture
    ):
        for select_line in filter(lambda l: l.tex_object is None,
                                  self.select_lines(func_select_id_line)):
            select_line.sprite_x += sprite_x
            select_line.tex_object = tex_object

    def update_and_draw(
            self,
            nb_lines_in_screen,
            player,
            screen,
            app
    ):
        start_pos = int(player.z / self.seg_length) % self.nb_lines
        cam_h = player.y + self.lines[start_pos].center_of_line.y

        x = 0
        dx = 0
        maxy = screen.height

        cur_prev_lines = zip(
            self.lines[start_pos:start_pos + nb_lines_in_screen],
            self.lines[(start_pos - 1):(start_pos - 1) + nb_lines_in_screen])
        for n, (cur_line, prev_line) in enumerate(cur_prev_lines,
                                                  start=start_pos):
            cam_x = player.x * Road.width - x
            cam_z = (start_pos - (n >= self.nb_lines) * self.nb_lines
                     ) * self.seg_length
            cur_line.project(cam=sf.Vector3(cam_x, cam_h, cam_z))

            x += dx
            dx += cur_line.curve

            # clip y-screen_coordinate
            cur_line.clip = maxy
            if cur_line.screen_coord.y > maxy:
                continue
            maxy = cur_line.screen_coord.y

            sc_cur_line = cur_line.screen_coord
            sc_prev_line = prev_line.screen_coord

            n_modulo_3 = (n // 3) % 2

            grass = sf.Color(16, 200, 16) if n_modulo_3 else sf.Color(0, 154, 0)
            rumble = sf.Color.WHITE if n_modulo_3 else sf.Color.BLACK
            road = sf.Color(107, 107, 107) if n_modulo_3 else sf.Color(105, 105,
                                                                       105)

            draw_quad(app, grass,
                      ProjectedPoint(0, sc_prev_line.y, screen.width),
                      ProjectedPoint(0, sc_cur_line.y, screen.width))
            draw_quad(app, rumble,
                      ProjectedPoint(sc_prev_line.x, sc_prev_line.y,
                                     sc_prev_line.w * 1.2),
                      ProjectedPoint(sc_cur_line.x, sc_cur_line.y,
                                     sc_cur_line.w * 1.2))
            draw_quad(app, road,
                      ProjectedPoint(sc_prev_line.x, sc_prev_line.y,
                                     sc_prev_line.w),
                      ProjectedPoint(sc_cur_line.x, sc_cur_line.y,
                                     sc_cur_line.w))
