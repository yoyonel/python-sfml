"""
"""
import logging
from math import cos, sin
import numpy as np
from OpenGL.GL import *
from pathlib import Path
from random import randint
from sfml import sf
from tifffile import tifffile
from typing import Tuple

from examples.outrun.engine.game import render_profiling
from examples.outrun.engine.profiling import profile_gpu

# video_mode = sf.VideoMode(1024, 768)
# https://fr.wikipedia.org/wiki/Super_Nintendo
video_mode = sf.VideoMode(512, 448)
clock = sf.Clock()

logger = logging.getLogger(__name__)


class Effect(sf.Drawable):
    def __init__(self, name):
        sf.Drawable.__init__(self)

        self._name = name
        self.is_loaded = False

    def _get_name(self):
        return self._name

    def load(self):
        self.is_loaded = sf.Shader.is_available() and self.on_load()

    def update(self, time, x, y):
        if self.is_loaded:
            self.on_update(time, x, y)

    def draw(self, target, states):
        if self.is_loaded:
            self.on_draw(target, states)
        else:
            error = sf.Text("Shader not\nsupported")
            error.font = sf.Font.from_file("data/sansation.ttf")
            error.position = (320, 200)
            error.character_size = 36
            target.draw(error, states)

    name = property(_get_name)


class Pixelate(Effect):
    def __init__(self):
        Effect.__init__(self, 'pixelate')

    def on_load(self):
        try:
            # load the texture and initialize the sprite
            self.texture = sf.Texture.from_file("data/background.jpg")
            self.sprite = sf.Sprite(self.texture)

            # load the shader
            self.shader = sf.Shader.from_file(fragment="data/pixelate.frag")
            self.shader.set_parameter("texture")

        except IOError as error:
            logger.error("An error occured: {0}".format(error))
            exit(1)

        return True

    def on_update(self, time, x, y):
        self.shader.set_parameter("pixel_threshold", (x + y) / 30)

    def on_draw(self, target, states):
        states.shader = self.shader
        target.draw(self.sprite, states)


class WaveBlur(Effect):
    def __init__(self):
        Effect.__init__(self, 'wave + blur')

    def on_load(self):
        with open("data/text.txt") as file:
            self.text = sf.Text(file.read())
            self.text.font = sf.Font.from_file("data/sansation.ttf")
            self.text.character_size = 22
            self.text.position = (30, 20)

        try:
            # load the shader
            self.shader = sf.Shader.from_file("data/wave.vert",
                                              "data/blur.frag")

        except IOError as error:
            logger.error("An error occured: {0}".format(error))
            exit(1)

        return True

    def on_update(self, time, x, y):
        self.shader.set_parameter("wave_phase", time)
        self.shader.set_parameter("wave_amplitude", x * 40, y * 40)
        self.shader.set_parameter("blur_radius", (x + y) * 0.008)

    def on_draw(self, target, states):
        states.shader = self.shader
        target.draw(self.text, states)


class StormBlink(Effect):
    def __init__(self):
        Effect.__init__(self, 'storm + blink')

        self.points = sf.VertexArray()

    def on_load(self):
        # create the points
        self.points.primitive_type = sf.PrimitiveType.POINTS

        for i in range(40000):
            x = randint(0, 32767) % 800
            y = randint(0, 32767) % 600
            r = randint(0, 32767) % 255
            g = randint(0, 32767) % 255
            b = randint(0, 32767) % 255
            self.points.append(sf.Vertex(sf.Vector2(x, y), sf.Color(r, g, b)))

        try:
            # load the shader
            self.shader = sf.Shader.from_file("data/storm.vert",
                                              "data/blink.frag")

        except IOError as error:
            logger.error("An error occured: {0}".format(error))
            exit(1)

        return True

    def on_update(self, time, x, y):
        radius = 200 + cos(time) * 150
        self.shader.set_parameter("storm_position", x * 800, y * 600)
        self.shader.set_parameter("storm_inner_radius", radius / 3)
        self.shader.set_parameter("storm_total_radius", radius)
        self.shader.set_parameter("blink_alpha", 0.5 + cos(time * 3) * 0.25)

    def on_draw(self, target, states):
        states.shader = self.shader
        target.draw(self.points, states)


class Edge(Effect):
    def __init__(self):
        Effect.__init__(self, "edge post-effect")

    def on_load(self):
        # create the off-screen surface
        self.surface = sf.RenderTexture(800, 600)
        self.surface.smooth = True

        # load the textures
        self.background_texture = sf.Texture.from_file("data/sfml.png")
        self.background_texture.smooth = True

        self.entity_texture = sf.Texture.from_file("data/devices.png")
        self.entity_texture.smooth = True

        # initialize the background sprite
        self.background_sprite = sf.Sprite(self.background_texture)
        self.background_sprite.position = (135, 100)

        # load the moving entities
        self.entities = []

        for i in range(6):
            sprite = sf.Sprite(self.entity_texture, (96 * i, 0, 96, 96))
            self.entities.append(sprite)

        # load the shader
        self.shader = sf.Shader.from_file(fragment="data/edge.frag")
        self.shader.set_parameter("texture")

        return True

    def on_update(self, time, x, y):
        self.shader.set_parameter("edge_threshold", 1 - (x + y) / 2)

        # update the position of the moving entities
        for i, entity in enumerate(self.entities):
            x = cos(0.25 * (time * i + (len(self.entities) - i))) * 300 + 350
            y = cos(0.25 * (time * (len(self.entities) - i) + i)) * 200 + 250
            entity.position = (x, y)

        # render the updated scene to the off-screen surface
        self.surface.clear(sf.Color.WHITE)
        self.surface.draw(self.background_sprite)

        for entity in self.entities:
            self.surface.draw(entity)

        self.surface.display()

    def on_draw(self, target, states):
        states.shader = self.shader
        target.draw(sf.Sprite(self.surface.texture), states)


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

        self.last_time = clock.elapsed_time.seconds

    def on_load(self):
        try:
            list_fn_img = [
                "data/81343.png",
                "data/84993_track.png",
                "data/battlecourse-1.png",
                "data/mariocircuit-2.png",
                "data/vanillalake-1.png",
                "data/bowsercastle-1.png"
            ]
            fn_img = list_fn_img[2]

            # load the texture and initialize the sprite
            self.texture = sf.Texture.from_file(fn_img)
            self.texture.smooth = False

            self.sprite = sf.Sprite(self.texture)
            self.sprite.position = (0, (video_mode.height // 2))
            self.sprite.scale((video_mode.width / self.texture.width,
                               (video_mode.height // 2) / self.texture.height))

            # load the shader
            self.shader = sf.Shader.from_file(
                vertex="data/mode7.vert",
                fragment="data/mode7.frag"
            )
            self.shader.set_parameter("texture")
        except IOError as error:
            logger.error("An error occured: {0}".format(error))
            exit(1)

        return True

    def on_update(self, time, x, y):
        ellapsed_time = time - self.last_time
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


class Mode7WithSAT(Effect):
    """
    https://en.wikipedia.org/wiki/Mode_7
    https://www.coranac.com/tonc/text/mode7.htm
    """

    def __init__(self):
        Effect.__init__(self, 'Mode 7 with SAT')

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

        self.last_time = clock.elapsed_time.seconds

    def on_load(self):
        try:
            list_fn_img = [
                "data/81343.png",
                "data/84993_track.png",
                "data/battlecourse-1.png",
                "data/mariocircuit-2.png",
                "data/vanillalake-1.png",
                "data/bowsercastle-1.png"
            ]
            fn_img = list_fn_img[2]

            # SAT
            path_sat, pixel_average = generate_sat(fn_img)
            img = sf.Image.from_file(fn_img)
            self.texture = sf.Texture.create(width=img.width, height=img.height)
            self.texture.smooth = True

            self.sprite = sf.Sprite(self.texture)
            self.sprite.position = (0, (video_mode.height // 2))
            self.sprite.scale((video_mode.width / self.texture.width,
                               (video_mode.height // 2) / self.texture.height))

            # load the shader
            self.shader = sf.Shader.from_file(
                vertex="data/mode7.vert",
                fragment="data/mode7_with_sat.frag"
            )
            self.shader.set_parameter("tex_sat")
            self.shader.set_parameter("tex_width", self.texture.width)
            self.shader.set_4float_parameter("pixel_average", *pixel_average)

            sat = tifffile.imread(str(path_sat))
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

    def on_update(self, time, x, y):
        ellapsed_time = time - self.last_time
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
        # TODO: use OpenGL primitives directly instead of using sf::Sprite
        # glEnable(GL_TEXTURE_2D)
        # glBindTexture(GL_TEXTURE_2D, self.sat_tex_id)
        target.draw(self.sprite, states)


def generate_sat(fn_img: str) -> Tuple[Path, np.array]:
    # http://developer.amd.com/wordpress/media/2012/10/GDC2005_SATEnvironmentReflections.pdf
    # https://developer.nvidia.com/gpugems/GPUGems3/gpugems3_ch39.html
    # "Fast Summed-Area Table Generation and its Applications"
    # http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.90.8836&rep=rep1&type=pdf

    image = sf.Image.from_file(fn_img)
    logger.info(
        f"Generate Summed Area Table from: '{fn_img}' ({image.width}, "
        f"{image.height}) ...")
    nparray_image = np.array(
        np.ndarray(
            (image.width, image.height, 4),
            buffer=image.pixels,
            dtype=np.uint8
        )
    )
    normed_image = nparray_image / 255.0
    pixel_average = np.average(normed_image, axis=(0, 1))
    normed_image = np.add(normed_image, pixel_average * -1.0)
    sat = normed_image.cumsum(axis=0).cumsum(axis=1)

    assert all(np.isclose(
        (sat[512][512] + sat[511][511]) - (sat[511][512] + sat[512][511]),
        normed_image[512][512]))

    # https://stackoverflow.com/questions/52490653/saving-float-numpy-images
    path_img = Path(fn_img)
    path_sat = path_img.with_name(path_img.stem + '.sat.tif')
    logger.info(f"export SAT: {path_sat}")
    tifffile.imsave(str(path_sat), sat)

    return path_sat, pixel_average


def main():
    # create the main window
    context_settings = sf.ContextSettings()
    context_settings.antialiasing_level = 1
    window = sf.RenderWindow(
        video_mode,
        "pySFML - Mode 7 (SNES)",
        sf.Style.DEFAULT, context_settings
    )
    window.vertical_synchronization = True

    # create the effects
    # effects = (Pixelate(), WaveBlur(), StormBlink(), Edge())
    # TODO: don't work with the two effects in the same time ...
    # problem with setting shader texture
    effects = (
        # Mode7(),
        Mode7WithSAT(),
    )
    current = 0

    # initialize them
    for effect in effects:
        effect.load()

    # create the message background
    try:
        text_background_texture = sf.Texture.from_file(
            "data/text-background.png")
    except IOError as error:
        raise RuntimeError("An error occured: {0}".format(error))

    text_background = sf.Sprite(text_background_texture)
    text_background.position = (0, 520)
    text_background.color = sf.Color(255, 255, 255, 200)

    # load the messages font
    try:
        font = sf.Font.from_file("data/sansation.ttf")
    except IOError as error:
        raise RuntimeError("An error occured: {0}".format(error))

    # create the description text
    description = sf.Text("Current effect: {0}".format(effects[current].name),
                          font, 20)
    description.position = (10, 530)
    description.color = sf.Color(80, 80, 80)

    # create the instructions text
    instructions = sf.Text(
        "Press left and right arrows to change the current shader", font, 20)
    instructions.position = (280, 555)
    instructions.color = sf.Color(80, 80, 80)

    # start the game loop
    while window.is_open:
        @profile_gpu(func_exit_condition=lambda: window.is_open)
        def _render_loop(current: int):
            # update the current example
            x = sf.Mouse.get_position(window).x / window.size.x
            y = sf.Mouse.get_position(window).y / window.size.y
            effects[current].update(clock.elapsed_time.seconds, x, y)

            # process events
            for event in window.events:

                # close window: exit
                if event == sf.Event.CLOSED:
                    window.close()

                if event == sf.Event.KEY_PRESSED:
                    # escapte key: exit
                    if event['code'] == sf.Keyboard.ESCAPE:
                        window.close()

                    # left arrow key: previous shader
                    elif event['code'] == sf.Keyboard.PAGE_DOWN:
                        if current == 0:
                            current = len(effects) - 1
                        else:
                            current -= 1

                        description.string = "Current effect: {0}".format(
                            effects[current].name)

                    # right arrow key: next shader
                    elif event['code'] == sf.Keyboard.PAGE_UP:
                        if current == len(effects) - 1:
                            current = 0
                        else:
                            current += 1

                        description.string = "Current effect: {0}".format(
                            effects[current].name)

            # clear the window
            window.clear(sf.Color(0, 137, 196))

            # draw the current example
            @profile_gpu(func_exit_condition=lambda: window.is_open)
            def _render_effect(e):
                window.draw(e)

            _render_effect(effects[current])

            # draw the text
            # window.draw(text_background)
            # window.draw(instructions)
            window.draw(description)

        _render_loop(current)

        # GPU Profiling
        render_profiling(video_mode, window)

        # finally, display the rendered frame on screen
        window.display()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(relativeCreated)6d %(threadName)s %(message)s'
    )
    main()
