#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
https://en.wikipedia.org/wiki/Tetromino

TODO:
- alpha blending for clipping objects
- filtering (anti-aliasing) on grass, rumble, road rendering
- LODs on textures objects (for filtering/anti-aliasing)
- handle textures for grass, rumble, road
- refactor the code (OO, dataclass, helpers/func/methods, typing, ...)
- [HARD] Using Fixed-point arithmetic :p
- real speed (km/hour)
- GPGPU - Ray-casting + Point Sprites Rendering
- separate update and draw for road
"""

from examples.mariokart.engine.game import main

if __name__ == "__main__":
    main()
