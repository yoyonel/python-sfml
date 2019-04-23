"""
"""
from math import cos, sin
from sfml import sf

from softshadow_volume.graphical.light import build_shapes_for_light
from softshadow_volume.graphical.light_wall import build_shapes_for_light_wall
from softshadow_volume.light import Light
from softshadow_volume.light_wall import LightWall


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


half_width = 800 // 2
half_height = 600 // 2


class DemoShadowVolume(Effect):
    def __init__(self):
        Effect.__init__(self, 'demo shadow volumes')

    def on_load(self):
        # create the light

        self.light = Light(
            pos=sf.Vector2(half_width, half_height - half_height // 2),
            inner_radius=20,
            influence_radius=400,
        )

        self.ligth_wall = LightWall(
            self.light,
            v0=sf.Vector2(half_width - half_height / 2.0,
                          half_height + half_height // 6),
            v1=sf.Vector2(half_width + half_height / 2.0,
                          half_height + half_height // 6),
        )

        self.light_shapes = build_shapes_for_light(self.light)
        self.light_wall_shapes = build_shapes_for_light_wall(self.ligth_wall,
                                                             sv_alpha=0.05)

        return True

    def on_update(self, time, x, y):
        self.light.pos = sf.Vector2(
            # half_width + cos(time) * 300,
            # half_height - half_height // 2 + sin(time) * 300
            # half_width - 10,
            # half_height - half_height // 2 + 50
            700,
            150
        )
        # self.ligth_wall.update()

        self.light_shapes = build_shapes_for_light(self.light)
        self.light_wall_shapes = build_shapes_for_light_wall(self.ligth_wall,
                                                             sv_alpha=0.15)

    def on_draw(self, target, states):
        target.draw(self.light_shapes['inner'], states)
        target.draw(self.light_shapes['outer'], states)
        for shape in self.light_wall_shapes['vertex']:
            target.draw(shape, states)
        target.draw(self.light_wall_shapes['edge'], states)
        for shape in self.light_wall_shapes["shadow_volumes"]:
            target.draw(shape, states)
        for shape in self.light_wall_shapes["penumbras"]:
            target.draw(shape, states)


if __name__ == "__main__":
    # create the main window
    window = sf.RenderWindow(sf.VideoMode(800, 600),
                             "pySFML - 2D Soft Shadow Volume")
    window.vertical_synchronization = True

    # create the effects
    effects = (DemoShadowVolume(),)
    current = 0

    # initialize them
    for effect in effects:
        effect.load()

    # load the messages font
    try:
        font = sf.Font.from_file("data/sansation.ttf")
    except IOError as error:
        raise RuntimeError("An error occured: {0}".format(error))

    # create the message background
    try:
        text_background_texture = sf.Texture.from_file(
            "data/text-background.png")
    except IOError as error:
        raise RuntimeError("An error occured: {0}".format(error))

    text_background = sf.Sprite(text_background_texture)
    text_background.position = (0, 520)
    text_background.color = sf.Color(255, 255, 255, 100)

    # create the description text
    description = sf.Text(
        "Current effect: {0}".format(effects[current].name), font, 20)
    description.position = (10, 530)
    description.color = sf.Color(80, 80, 80)

    # create the instructions text
    instructions = sf.Text(
        "Press left and right arrows to change the current shader", font,
        20)
    instructions.position = (280, 555)
    instructions.color = sf.Color(80, 80, 80)

    clock = sf.Clock()

    # start the game loop
    while window.is_open:

        # update the current example
        x = sf.Mouse.get_position(window).x / window.size.x
        y = sf.Mouse.get_position(window).y / window.size.y

        if effects:
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

        # clear the window
        window.clear(sf.Color.BLACK)

        # draw the current example
        if effects:
            window.draw(effects[current])

        # draw the text
        window.draw(text_background)
        window.draw(instructions)
        window.draw(description)

        # finally, display the rendered frame on screen
        window.display()
