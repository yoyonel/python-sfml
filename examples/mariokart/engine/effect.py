"""
"""
from sfml import sf


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
