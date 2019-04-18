"""
"""
from sfml import sf


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


if __name__ == "__main__":
    # create the main window
    window = sf.RenderWindow(sf.VideoMode(800, 600),
                             "pySFML - 2D Soft Shadow Volume")
    window.vertical_synchronization = True

    # create the effects
    effects = ()
    current = 0

    # initialize them
    for effect in effects:
        effect.load()

    # load the messages font
    try:
        font = sf.Font.from_file("data/sansation.ttf")
    except IOError as error:
        raise RuntimeError("An error occured: {0}".format(error))

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

        # finally, display the rendered frame on screen
        window.display()
