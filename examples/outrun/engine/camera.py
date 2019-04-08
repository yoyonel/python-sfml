"""
"""
from dataclasses import dataclass


@dataclass
class Camera:
    # TODO: think about this parameter (maybe field of view)
    depth: float = 0.84
