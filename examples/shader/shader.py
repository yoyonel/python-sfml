import logging
from dataclasses import dataclass, field
from typing import Tuple

from math import cos
from random import randint
from sfml import sf

from examples.outrun.engine.game import render_profiling
from examples.outrun.engine.profiling import profile_gpu

logger = logging.getLogger(__name__)


class Effect(sf.Drawable):
    video_mode = sf.VideoMode(800, 600)

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


@dataclass
class RatioVideoMode:
    origin: sf.VideoMode
    target: sf.VideoMode

    ratio: sf.Vector2 = field(init=False)

    def __post_init__(self):
        self.ratio = sf.Vector2(
            self.target.width / self.origin.width,
            self.target.height / self.origin.height
        )

    def convert_coord(self, x: float, y: float) -> Tuple[float, float]:
        return (
            x * self.ratio.x,
            y * self.ratio.y
        )

    def convert_x_coord(self, x: float) -> float:
        return x * self.ratio.x

    def convert_y_coord(self, y: float) -> float:
        return y * self.ratio.y


Effect.video_mode = sf.VideoMode(800, 600)
#
ratio = RatioVideoMode(sf.VideoMode(800, 600), Effect.video_mode)


class Pixelate(Effect):
    def __init__(self):
        Effect.__init__(self, 'pixelate')

    def on_load(self):
        try:
            # load the texture and initialize the sprite
            self.texture = sf.Texture.from_file("data/background.jpg")
            self.sprite = sf.Sprite(self.texture)
            self.sprite.scale(ratio.convert_coord(1, 1))

            # load the shader
            self.shader = sf.Shader.from_file(fragment="data/pixelate.frag")
            self.shader.set_parameter("texture")

        except IOError as error:
            print("An error occured: {0}".format(error))
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
            self.text.character_size = ratio.convert_x_coord(22)
            self.text.position = ratio.convert_coord(30, 20)

        try:
            # load the shader
            self.shader = sf.Shader.from_file("data/wave.vert",
                                              "data/blur.frag")

        except IOError as error:
            print("An error occured: {0}".format(error))
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
            x = randint(0, 32767) % int(ratio.convert_x_coord(800))
            y = randint(0, 32767) % int(ratio.convert_y_coord(600))
            r = randint(0, 32767) % 255
            g = randint(0, 32767) % 255
            b = randint(0, 32767) % 255
            self.points.append(sf.Vertex(sf.Vector2(x, y), sf.Color(r, g, b)))

        try:
            # load the shader
            self.shader = sf.Shader.from_file("data/storm.vert",
                                              "data/blink.frag")

        except IOError as error:
            print("An error occured: {0}".format(error))
            exit(1)

        return True

    def on_update(self, time, x, y):
        radius = ratio.convert_x_coord(200) + cos(time) * ratio.convert_x_coord(150)
        self.shader.set_parameter("storm_position",
                                  x * ratio.convert_x_coord(800),
                                  y * ratio.convert_y_coord(600))
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
        self.surface = sf.RenderTexture(*ratio.convert_coord(800, 600))
        self.surface.smooth = True

        # load the textures
        self.background_texture = sf.Texture.from_file("data/sfml.png")
        self.background_texture.smooth = True

        self.entity_texture = sf.Texture.from_file("data/devices.png")
        self.entity_texture.smooth = True

        # initialize the background sprite
        self.background_sprite = sf.Sprite(self.background_texture)
        self.background_sprite.position = ratio.convert_coord(135, 100)

        # load the moving entities
        self.entities = []

        for i in range(6):
            sprite = sf.Sprite(self.entity_texture,
                               (96 * i, 0, 96, 96))
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
            entity.position = ratio.convert_coord(x, y)

        # render the updated scene to the off-screen surface
        self.surface.clear(sf.Color.WHITE)
        self.surface.draw(self.background_sprite)

        for entity in self.entities:
            self.surface.draw(entity)

        self.surface.display()

    def on_draw(self, target, states):
        states.shader = self.shader
        target.draw(sf.Sprite(self.surface.texture), states)


class MainApp(object):
    def __init__(self):
        self.video_mode = Effect.video_mode

        # create the main window
        self.window = sf.RenderWindow(self.video_mode, "pySFML - Shader")
        self.window.vertical_synchronization = False

        #
        self.clock = sf.Clock()

        # create the effects
        self.effects = (Pixelate(), WaveBlur(), StormBlink(), Edge())
        self.current = 0

        # initialize them
        for effect in self.effects:
            effect.load()

        # create the message background
        try:
            self.text_background_texture = \
                sf.Texture.from_file(
                    "data/text-background.png")

        except IOError as error:
            raise RuntimeError("An error occured: {0}".format(error))

        self.text_background = sf.Sprite(self.text_background_texture)
        self.text_background.position = ratio.convert_coord(0, 520)
        self.text_background.scale(ratio.convert_coord(1, 1))
        self.text_background.color = sf.Color(255, 255, 255, 64)

        # load the messages font
        try:
            self.font = sf.Font.from_file("data/sansation.ttf")
        except IOError as error:
            raise RuntimeError("An error occured: {0}".format(error))

        # create the description text
        self.description = sf.Text(
            "Current effect: {0}".format(self.effects[self.current].name),
            self.font, 20
        )
        self.description.position = ratio.convert_coord(10, 530)
        self.description.color = sf.Color(80, 80, 80)

        # create the instructions text
        self.instructions = sf.Text(
            "Press left and right arrows to change the current shader",
            self.font, 20)
        self.instructions.position = ratio.convert_coord(280, 555)
        self.instructions.color = sf.Color(80, 80, 80)

    def process_events(self):
        for event in self.window.events:
            # close window: exit
            if event == sf.Event.CLOSED:
                self.window.close()

            if event == sf.Event.KEY_PRESSED:
                # escapte key: exit
                if event['code'] == sf.Keyboard.ESCAPE:
                    self.window.close()

                # left arrow key: previous shader
                elif event['code'] == sf.Keyboard.PAGE_DOWN:
                    self.current = (self.current - 1) % len(self.effects)

                    self.description.string = "Current effect: {0}".format(
                        self.effects[self.current].name)

                # right arrow key: next shader
                elif event['code'] == sf.Keyboard.PAGE_UP:
                    self.current = (self.current + 1) % len(self.effects)

                    self.description.string = "Current effect: {0}".format(
                        self.effects[self.current].name)

    def update_effect(self):
        mouse_position = sf.Mouse.get_position(self.window)
        x = mouse_position.x / self.window.size.x
        y = mouse_position.y / self.window.size.y
        self.effects[self.current].update(self.clock.elapsed_time.seconds, x, y)

    def draw_texts(self):
        self.window.draw(self.text_background)
        self.window.draw(self.instructions)
        self.window.draw(self.description)

    def run(self):
        def _func_exit_condition():
            return self.window.is_open

        # start the game loop
        while self.window.is_open:
            @profile_gpu(_func_exit_condition)
            def loop():
                # update the current example
                self.update_effect()

                # process events
                self.process_events()

                # clear the window
                self.window.clear(sf.Color(0, 137, 196))

                # draw the current example
                @profile_gpu(_func_exit_condition)
                def _render_effect():
                    self.window.draw(self.effects[self.current])

                _render_effect()

                # draw the text
                self.draw_texts()

            loop()

            # GPU Profiling
            render_profiling(self.video_mode, self.window,
                             color=sf.Color(0, 255, 0, 128))

            # finally, display the rendered frame on screen
            self.window.display()


def main():
    logging.basicConfig(
        level=logging.INFO,
        # format='[%(relativeCreated)6d ms] %(threadName)s %(message)s'
        format='%(asctime)s %(threadName)s %(message)s'
    )
    app = MainApp()
    app.run()


if __name__ == "__main__":
    main()
