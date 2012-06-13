#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pySFML2 - Cython SFML Wrapper for Python
# Copyright 2012, Jonathan De Wachter <dewachter.jonathan@gmail.com>
#
# This software is released under the GPLv3 license.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sfml as sf
from rendertarget import test_rendertarget

window = sf.RenderWindow(sf.VideoMode(640, 480), "pySFML - sf.Shape")
window.clear(sf.Color.WHITE)
window.display()
input()

test_rendertarget(window)

image = window.capture()
assert type(image) == sf.Image
image.save_to_file("result/renderwindow-capture.png")
input()
