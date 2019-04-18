"""
"""
import logging
from collections import defaultdict

from math import cos, sin
from sfml import sf

from examples.mariokart.engine.effect import Effect

logger = logging.getLogger(__name__)


class Mode7(Effect):
    """
    https://en.wikipedia.org/wiki/Mode_7
    https://www.coranac.com/tonc/text/mode7.htm
    """

    def __init__(self):
        Effect.__init__(self, 'Mode 7')

        self.fWorldX = 0.0
        self.fWorldY = 0.0
        self.fWorldA = 0.1
        self.fNear = 0.005
        self.fFar = 0.03
        self.fFoVHalf = 3.14159 / 4.0

        self.fFarX1 = 0.0
        self.fFarY1 = 0.0
        self.fFarX2 = 0.0
        self.fFarY2 = 0.0
        self.fNearX1 = 0.0
        self.fNearY1 = 0.0
        self.fNearX2 = 0.0
        self.fNearY2 = 0.0

        self.last_time = 0.0
        self.ellapsed_time = 0.0

        self.list_fn_img = defaultdict(
            lambda: "data/resources/mariocircuit-1.png",
            {
                'mariocircuit-1': "data/resources/mariocircuit-1.png",
            }
        )

        self.texture = None
        self.sprite = None
        self.shader = None

        print("Press ARROW (← → ↑ ↓) keys to move")
        print("Press Q/A to increase/decrease: Near plane")
        print("Press W/S to increase/decrease: Far plane")
        print("Press Z/X to increase/decrease: FOV")

    def on_load(self):
        try:
            fn_img = self.list_fn_img['mariocircuit-1']

            # load the texture and initialize the sprite
            self.texture = sf.Texture.from_file(fn_img)
            self.texture.smooth = False

            self.sprite = sf.Sprite(self.texture)
            self.sprite.position = (0, (self.video_mode.height // 2))
            self.sprite.scale(
                (self.video_mode.width / self.texture.width,
                 (self.video_mode.height // 2) / self.texture.height)
            )

            # load the shader
            self.shader = sf.Shader.from_file(
                vertex="data/shader/mode7.vert",
                fragment="data/shader/mode7.frag"
            )
            self.shader.set_parameter("texture")
        except IOError as error:
            logger.error("An error occured: {0}".format(error))
            exit(1)

        return True

    def on_update(self, time, x, y):
        self.ellapsed_time = ellapsed_time = time - self.last_time
        self.shader.set_parameter("time", time)

        if sf.Keyboard.is_key_pressed(sf.Keyboard.Q):
            self.fNear += 0.1 * ellapsed_time
            logger.debug(f"+fNear={self.fNear}")
        if sf.Keyboard.is_key_pressed(sf.Keyboard.A):
            self.fNear -= 0.1 * ellapsed_time
            logger.debug(f"-fNear={self.fNear}")
        if sf.Keyboard.is_key_pressed(sf.Keyboard.W):
            self.fFar += 0.1 * ellapsed_time
            logger.debug(f"+fFar={self.fFar}")
        if sf.Keyboard.is_key_pressed(sf.Keyboard.S):
            self.fFar -= 0.1 * ellapsed_time
            logger.debug(f"-fFar={self.fFar}")
        if sf.Keyboard.is_key_pressed(sf.Keyboard.Z):
            self.fFoVHalf += 0.1 * ellapsed_time
            logger.debug(f"+fFoVHalf={self.fFoVHalf}")
        if sf.Keyboard.is_key_pressed(sf.Keyboard.X):
            self.fFoVHalf -= 0.1 * ellapsed_time
            logger.debug(f"-fFoVHalf={self.fFoVHalf}")

        if sf.Keyboard.is_key_pressed(sf.Keyboard.RIGHT):
            self.fWorldA += 1.0 * ellapsed_time
            logger.debug(f"+fWorldA={self.fWorldA}")
        if sf.Keyboard.is_key_pressed(sf.Keyboard.LEFT):
            self.fWorldA -= 1.0 * ellapsed_time
            logger.debug(f"-fWorldA={self.fWorldA}")
        if sf.Keyboard.is_key_pressed(sf.Keyboard.UP):
            self.fWorldX += cos(self.fWorldA) * 0.2 * ellapsed_time
            self.fWorldY += sin(self.fWorldA) * 0.2 * ellapsed_time
            logger.debug(f"+fWorldXY=({self.fWorldX},{self.fWorldY})")
        if sf.Keyboard.is_key_pressed(sf.Keyboard.DOWN):
            self.fWorldX -= cos(self.fWorldA) * 0.2 * ellapsed_time
            self.fWorldY -= sin(self.fWorldA) * 0.2 * ellapsed_time
            logger.debug(f"-fWorldXY=({self.fWorldX},{self.fWorldY})")

        # TODO: can be done in Vertex Shader [gpu side] with matrix
        # Create Frustum corner points
        fFarX1 = self.fWorldX + cos(
            self.fWorldA - self.fFoVHalf) * self.fFar
        fFarY1 = self.fWorldY + sin(
            self.fWorldA - self.fFoVHalf) * self.fFar
        fNearX1 = self.fWorldX + cos(
            self.fWorldA - self.fFoVHalf) * self.fNear
        fNearY1 = self.fWorldY + sin(
            self.fWorldA - self.fFoVHalf) * self.fNear
        fFarX2 = self.fWorldX + cos(
            self.fWorldA + self.fFoVHalf) * self.fFar
        fFarY2 = self.fWorldY + sin(
            self.fWorldA + self.fFoVHalf) * self.fFar
        fNearX2 = self.fWorldX + cos(
            self.fWorldA + self.fFoVHalf) * self.fNear
        fNearY2 = self.fWorldY + sin(
            self.fWorldA + self.fFoVHalf) * self.fNear

        self.shader.set_parameter("fFarX1", fFarX1)
        self.shader.set_parameter("fFarY1", fFarY1)
        self.shader.set_parameter("fNearX1", fNearX1)
        self.shader.set_parameter("fNearY1", fNearY1)
        self.shader.set_parameter("fFarX2", fFarX2)
        self.shader.set_parameter("fFarY2", fFarY2)
        self.shader.set_parameter("fNearX2", fNearX2)
        self.shader.set_parameter("fNearY2", fNearY2)

        self.last_time = time

    def on_draw(self, target, states):
        states.shader = self.shader
        target.draw(self.sprite, states)
