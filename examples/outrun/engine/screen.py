"""
"""
from dataclasses import dataclass, field
from typing import Tuple

from sfml import sf


@dataclass
class Screen:
    width: int = 1024
    height: int = 768
    font_fn: str = "data/Road_Rage.otf"

    font: sf.Font = field(init=False)
    half_width: int = field(init=False)
    half_height: int = field(init=False)

    def __post_init__(self):
        self.font = sf.Font.from_file(self.font_fn)
        self.half_width = self.width // 2
        self.half_height = self.height // 2

    @property
    def resolution(self) -> Tuple[int, int]:
        return self.width, self.height
