"""
"""
from dataclasses import dataclass, field

from math import sin
from typing import Callable, Iterator

from . circular_list import CircularList
from . line import Line
from sfml import sf


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
