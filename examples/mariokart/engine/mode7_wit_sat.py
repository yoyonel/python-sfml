"""
"""
import logging
from OpenGL.GL import (
    glGenTextures, glBindTexture, GL_TEXTURE_2D, glTexImage2D,
    GL_RGBA32F, GL_RGBA, GL_FLOAT,
    glEnable)
from sfml import sf
from tifffile import tifffile

from examples.mariokart.engine.mode7 import Mode7
from examples.mariokart.engine.sat import generate_sat

logger = logging.getLogger(__name__)


class Mode7WithSAT(Mode7):
    def __init__(self):
        Mode7.__init__(self)
        self._name = 'Mode 7 with Summed Area Table'

    def on_load(self):
        try:
            list_fn_img = [
                "data/mariocircuit-1.png",
            ]
            fn_img = list_fn_img[-1]

            # SAT
            path_sat, pixel_average = generate_sat(fn_img)
            img = sf.Image.from_file(fn_img)
            self.texture = sf.Texture.create(width=img.width, height=img.height)
            self.texture.smooth = True

            self.sprite = sf.Sprite(self.texture)
            self.sprite.position = (0, (self.video_mode.height // 2))
            self.sprite.scale(
                (self.video_mode.width / self.texture.width,
                 (self.video_mode.height // 2) / self.texture.height)
            )

            # load the shader
            self.shader = sf.Shader.from_file(
                vertex="data/mode7.vert",
                fragment="data/mode7_with_sat.frag"
            )
            self.shader.set_parameter("tex_sat")
            self.shader.set_parameter("tex_width", self.texture.width)
            self.shader.set_4float_parameter("pixel_average", *pixel_average)

            logger.info("Load SAT ...")
            sat = tifffile.imread(str(path_sat))
            logger.info("Generate Float Texture RGBA32F ...")
            self.sat_tex_id = 1
            glGenTextures(1, self.sat_tex_id)
            glBindTexture(GL_TEXTURE_2D, self.sat_tex_id)
            # # https://www.khronos.org/registry/OpenGL-Refpages/gl4/html/glTexImage2D.xhtml
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, sat.shape[0],
                         sat.shape[1], 0, GL_RGBA, GL_FLOAT, sat)

        except IOError as error:
            logger.error("An error occured: {0}".format(error))
            exit(1)

        return True

    def on_draw(self, target, states):
        states.shader = self.shader
        # TODO: use OpenGL primitives directly instead of using sf::Sprite
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.sat_tex_id)
        target.draw(self.sprite, states)
