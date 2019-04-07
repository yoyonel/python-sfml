"""
https://en.wikipedia.org/wiki/Tetromino

TODO:
- alpha blending for clipping objects
- filtering (anti-aliasing) on grass, rumble, road rendering
- LODs on textures objects (for filtering/anti-aliasing)
- handle textures for grass, rumble, road
- refactor the code (OO, dataclass, helpers/func/methods, typing, ...)
- [HARD] Using Fixed-point arithmetic :p
"""
from dataclasses import dataclass, field
from typing import Optional, Dict

from math import sin
import operator
from sfml import sf

width = 1024  # type: int
height = 768  # type: int
road_width = 2000  # type: int
seg_length = 200  # type: int
cam_depth = 0.84  # type: float


# https://stackoverflow.com/a/47606550
class CircularList(list):
    def __getitem__(self, x):
        if isinstance(x, slice):
            return [self[x] for x in self._rangeify(x)]

        index = operator.index(x)
        try:
            return super().__getitem__(index % len(self))
        except ZeroDivisionError:
            raise IndexError('list index out of range')

    def _rangeify(self, slice_):
        start, stop, step = slice_.start, slice_.stop, slice_.step
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is None:
            step = 1
        return range(start, stop, step)


@dataclass
class ProjectedPoint:
    x: float = 0.0
    y: float = 0.0
    w: float = 0.0


@dataclass
class Line:
    center_of_line: sf.Vector3 = sf.Vector3()

    screen_coord: ProjectedPoint = field(default_factory=ProjectedPoint)
    scale: float = field(default_factory=float)
    curve: float = field(default_factory=float)

    clip: int = 0

    sprite_x: int = 0
    tex_object: Optional[sf.Texture] = None

    def project(self, cam: sf.Vector3) -> None:
        x, y, z = self.center_of_line

        self.scale = cam_depth / (z - cam.z)
        scale = self.scale

        self.screen_coord = ProjectedPoint(
            (1 + scale * (x - cam.x)) * width / 2,
            (1 - scale * (y - cam.y)) * height / 2,
            scale * road_width * width / 2,
        )

    def draw_sprite(self, app: sf.RenderWindow):
        if self.tex_object:
            # new instance of Sprite
            # TODO: really needed ?
            sprite_object = sf.Sprite(texture=self.tex_object)

            tex_w = sprite_object.texture_rectangle.width
            tex_h = sprite_object.texture_rectangle.height

            sc_w = self.screen_coord.w
            scale = self.scale
            sprite_x = self.sprite_x

            dest_x = self.screen_coord.x + scale * sprite_x * width / 2
            dest_y = self.screen_coord.y + 4
            # TODO: Understand this magical factor => 266
            dest_w = tex_w * sc_w / (266 * 1)
            dest_h = tex_h * sc_w / (266 * 1)

            dest_x += dest_w * sprite_x  # offsetX
            dest_y += dest_h * (-1)  # offsetY

            # clippings
            #
            clip_h = max(0, dest_y + dest_h - self.clip)
            if clip_h >= dest_h:
                return
            # scissor
            rect = (0, 0, tex_w, tex_h - tex_h * clip_h / dest_h)
            sprite_object.texture_rectangle = rect

            scale = (dest_w / tex_w, dest_h / tex_h)
            sprite_object.scale(scale)
            sprite_object.position = dest_x, dest_y

            app.draw(sprite_object)


def draw_quad(w: sf.RenderWindow, c: sf.Color, p1: ProjectedPoint, p2: ProjectedPoint) -> None:
    shape = sf.ConvexShape(4)
    shape.fill_color = c
    shape.set_point(0, sf.Vector2(p1.x - p1.w, p1.y))
    shape.set_point(1, sf.Vector2(p2.x - p2.w, p2.y))
    shape.set_point(2, sf.Vector2(p2.x + p2.w, p2.y))
    shape.set_point(3, sf.Vector2(p1.x + p1.w, p1.y))
    w.draw(shape)


def main():
    # create the main window
    app = sf.RenderWindow(sf.VideoMode(width, height), "Outrun racing!")
    app.framerate_limit = 60

    try:
        tex_bg = sf.Texture.from_file("data/bg.png")  # type: sf.Texture
        tex_objects = {
            i: sf.Texture.from_file("data/{}.png".format(i))
            for i in range(1, 8)
        }  # type: Dict[int, sf.Texture]
    except IOError as error:
        raise RuntimeError("An error occured: {0}".format(error))
    # Activate smooth attribute for all textures objects
    for tex_object in tex_objects.values():
        tex_object.smooth = True
    tex_bg.repeated = True
    sprite_bg = sf.Sprite(tex_bg)
    sprite_bg.texture_rectangle = (0, 0, 5000, 411)
    sprite_bg.position = (-2000, 0)

    nb_lines = 1600
    nb_lines_in_screen = 300

    player = sf.Vector3(0, 1500, 0)

    # Define circuit with parametric equations for y,z components and the road's curvature
    lines = CircularList([
        Line(center_of_line=sf.Vector3(y=(i > 750) * (sin(i / 30) * 1500),
                                       z=i * seg_length + 1),
             curve=(300 > i < 700) * 0.5 + (i > 1100) * (-0.7), )
        for i in range(nb_lines)
    ])

    def select_lines(func_select_id_line):
        for i in filter(func_select_id_line, range(nb_lines)):
            yield lines[i]

    def set_object_to_lines(func_select_id_line, sprite_x: float, id_tex_object: int):
        for select_line in filter(lambda l: l.tex_object is None,
                                  select_lines(func_select_id_line)):
            select_line.sprite_x += sprite_x
            select_line.tex_object = tex_objects[id_tex_object]

    set_object_to_lines(lambda i: i < 300 and i % 20 == 0, -2.5, 5)
    set_object_to_lines(lambda i: i % 17 == 0, 2.0, 6)
    set_object_to_lines(lambda i: i > 300 and i % 20 == 0, -0.7, 4)
    set_object_to_lines(lambda i: i > 800 and i % 20 == 0, -1.2, 1)
    set_object_to_lines(lambda i: i == 400, -1.2, 7)

    # start the game loop
    while app.is_open:
        # process events
        for event in app.events:

            # close window: exit
            if event == sf.Event.CLOSED:
                app.close()

            if event == sf.Event.KEY_PRESSED:
                # escapte key: exit
                if event['code'] == sf.Keyboard.ESCAPE:
                    app.close()

        speed = 0

        if sf.Keyboard.is_key_pressed(sf.Keyboard.RIGHT):
            player.x += 0.1
        if sf.Keyboard.is_key_pressed(sf.Keyboard.LEFT):
            player.x -= 0.1
        if sf.Keyboard.is_key_pressed(sf.Keyboard.UP):
            speed = 200
        if sf.Keyboard.is_key_pressed(sf.Keyboard.DOWN):
            speed = -200
        if sf.Keyboard.is_key_pressed(sf.Keyboard.R_CONTROL):
            speed *= 3
        if sf.Keyboard.is_key_pressed(sf.Keyboard.W):
            player.y += 100
        if sf.Keyboard.is_key_pressed(sf.Keyboard.S):
            player.y -= 100

        player.z += speed
        while player.z >= nb_lines * seg_length:
            player.z -= nb_lines * seg_length
        while player.z < 0:
            player.z += nb_lines * seg_length

        # clear the window
        app.clear(sf.Color(105, 205, 4))
        app.draw(sprite_bg)

        start_pos = (player.z // seg_length) % nb_lines  # type: int
        cam_h = player.y + lines[start_pos].center_of_line.y

        # Background parallax link to road curve
        if speed > 0:
            sprite_bg.move((-lines[start_pos].curve * 2, 0))
        if speed < 0:
            sprite_bg.move((+lines[start_pos].curve * 2, 0))

        maxy = height
        x = 0
        dx = 0

        # draw grass, rumble, road
        for n, (cur_line, prev_line) in enumerate(zip(lines[start_pos:start_pos + nb_lines_in_screen],
                                                      lines[(start_pos - 1):(start_pos - 1) + nb_lines_in_screen]),
                                                  start=start_pos):
            cur_line.project(
                cam=sf.Vector3(player.x * road_width - x,
                               cam_h,
                               (start_pos - (n >= nb_lines) * nb_lines) * seg_length)
            )

            x += dx
            dx += cur_line.curve

            # clip y-screen_coordinate
            cur_line.clip = maxy
            if cur_line.screen_coord.y > maxy:
                continue
            maxy = cur_line.screen_coord.y

            sc_cur_line = cur_line.screen_coord
            sc_prev_line = prev_line.screen_coord

            n_modulo_3 = (n // 3) % 2

            grass = sf.Color(16, 200, 16) if n_modulo_3 else sf.Color(0, 154, 0)
            rumble = sf.Color.WHITE if n_modulo_3 else sf.Color.BLACK
            road = sf.Color(107, 107, 107) if n_modulo_3 else sf.Color(105, 105, 105)

            draw_quad(app, grass,
                      ProjectedPoint(0, sc_prev_line.y, width),
                      ProjectedPoint(0, sc_cur_line.y, width))
            draw_quad(app, rumble,
                      ProjectedPoint(sc_prev_line.x, sc_prev_line.y, sc_prev_line.w * 1.2),
                      ProjectedPoint(sc_cur_line.x, sc_cur_line.y, sc_cur_line.w * 1.2))
            draw_quad(app, road,
                      ProjectedPoint(sc_prev_line.x, sc_prev_line.y, sc_prev_line.w),
                      ProjectedPoint(sc_cur_line.x, sc_cur_line.y, sc_cur_line.w))

        # Reverse order (painter depth technique)
        # https://en.wikipedia.org/wiki/Painter%27s_algorithm
        for line in lines[start_pos: start_pos + nb_lines_in_screen][::-1]:
            line.draw_sprite(app)

        # finally, display the rendered frame on screen
        app.display()


if __name__ == "__main__":
    main()
