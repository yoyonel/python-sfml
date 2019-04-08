"""
"""
from typing import Dict
from sfml import sf

from . background import Background
from . camera import Camera
from . circuit import Circuit
from . player import Player
from . project_point import ProjectedPoint
from . rendering import draw_quad
from . road import road_width
from . screen import Screen

nb_lines_in_screen = 300


def main():
    screen = Screen()
    camera = Camera()

    # create the main window
    app = sf.RenderWindow(sf.VideoMode(*screen.resolution), "Outrun racing!")
    app.framerate_limit = 60

    try:
        tex_objects = {
            i: sf.Texture.from_file("data/{}.png".format(i))
            for i in range(1, 8)
        }  # type: Dict[int, sf.Texture]
    except IOError as error:
        raise RuntimeError("An error occured: {0}".format(error))
    # Activate smooth attribute for all textures objects
    for tex_object in tex_objects.values():
        tex_object.smooth = True

    # Background
    background = Background()
    circuit = Circuit()

    circuit.build()

    circuit.set_object(lambda i: i < 300 and i % 20 == 0, -2.5, tex_objects[5])
    circuit.set_object(lambda i: i % 17 == 0, 2.0, tex_objects[6])
    circuit.set_object(lambda i: i > 300 and i % 20 == 0, -0.7, tex_objects[4])
    circuit.set_object(lambda i: i > 800 and i % 20 == 0, -1.2, tex_objects[1])
    circuit.set_object(lambda i: i == 400, -1.2, tex_objects[7])

    player = Player(tex_coord_t=98)
    player.create_sprite(screen)

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

        if sf.Keyboard.is_key_pressed(sf.Keyboard.UP) or \
                sf.Keyboard.is_key_pressed(sf.Keyboard.DOWN):

            if sf.Keyboard.is_key_pressed(sf.Keyboard.UP) and \
                    player.is_driving_forward and player.is_player_offroad:
                player.per_loop_forward_acceleration_offroad()
            elif sf.Keyboard.is_key_pressed(sf.Keyboard.UP) and \
                    not player.is_driving_backward and \
                    not player.has_reached_max_forward_speed:
                player.per_loop_forward_acceleration()
            elif sf.Keyboard.is_key_pressed(sf.Keyboard.UP) and \
                    player.is_driving_backward:
                player.per_loop_backward_braking()

            if sf.Keyboard.is_key_pressed(sf.Keyboard.DOWN) and \
                    not player.is_driving_forward and \
                    not player.has_reached_max_backward_speed:
                player.per_loop_backward_acceleration()
            elif sf.Keyboard.is_key_pressed(sf.Keyboard.DOWN) and \
                    player.is_driving_forward:
                player.per_loop_forward_braking()

        player.z += player.speed
        while player.z >= circuit.nb_lines * circuit.seg_length:
            player.z -= circuit.nb_lines * circuit.seg_length
        while player.z < 0:
            player.z += circuit.nb_lines * circuit.seg_length

        # clear the window
        app.clear(sf.Color(105, 205, 4))
        app.draw(background.sprite)

        start_pos = int(player.z / circuit.seg_length) % circuit.nb_lines
        cam_h = player.y + circuit.lines[start_pos].center_of_line.y

        if not player.is_stopped:
            turn_weight = min(player.speed * .0005, 0.04)

            if (sf.Keyboard.is_key_pressed(sf.Keyboard.RIGHT) and
                player.is_driving_forward) or \
                    (sf.Keyboard.is_key_pressed(sf.Keyboard.LEFT) and
                     player.is_driving_backward):
                player.turn_right(turn_weight)
            elif (sf.Keyboard.is_key_pressed(sf.Keyboard.LEFT) and
                  player.is_driving_forward) or \
                    (sf.Keyboard.is_key_pressed(sf.Keyboard.RIGHT) and
                     player.is_driving_backward):
                player.turn_left(turn_weight)
            else:
                player.steer_straight()

            # Background parallax link to road curve
            background.update_position(circuit.lines[start_pos].curve,
                                       player.speed)

            # TODO: régler la sensibilité de ce parametre physique
            # part that forces the car to stray from track when the road cruves
            # if player.is_driving_forward:
            #     player.x -= (lines[start_pos].curve * (player.speed / 8000.0))
            # elif player.is_driving_backward:
            #     player.x += (lines[start_pos].curve * (player.speed / 8000.0))

        maxy = screen.height
        x = 0
        dx = 0

        # draw grass, rumble, road
        cur_prev_lines = zip(
            circuit.lines[start_pos:start_pos + nb_lines_in_screen],
            circuit.lines[(start_pos - 1):(start_pos - 1) + nb_lines_in_screen])
        for n, (cur_line, prev_line) in enumerate(cur_prev_lines,
                                                  start=start_pos):
            cam_x = player.x * road_width - x
            cam_z = (start_pos - (n >= circuit.nb_lines) * circuit.nb_lines
                     ) * circuit.seg_length
            cur_line.project(cam=sf.Vector3(cam_x, cam_h, cam_z),
                             screen=screen, cam_depth=camera.depth)

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
            road = sf.Color(107, 107, 107) if n_modulo_3 else sf.Color(105, 105,
                                                                       105)

            draw_quad(app, grass,
                      ProjectedPoint(0, sc_prev_line.y, screen.width),
                      ProjectedPoint(0, sc_cur_line.y, screen.width))
            draw_quad(app, rumble,
                      ProjectedPoint(sc_prev_line.x, sc_prev_line.y,
                                     sc_prev_line.w * 1.2),
                      ProjectedPoint(sc_cur_line.x, sc_cur_line.y,
                                     sc_cur_line.w * 1.2))
            draw_quad(app, road,
                      ProjectedPoint(sc_prev_line.x, sc_prev_line.y,
                                     sc_prev_line.w),
                      ProjectedPoint(sc_cur_line.x, sc_cur_line.y,
                                     sc_cur_line.w))

        # Reverse order (painter depth technique)
        # https://en.wikipedia.org/wiki/Painter%27s_algorithm
        for line in circuit.lines[
                    start_pos: start_pos + nb_lines_in_screen][::-1]:
            line.draw_sprite(app, screen)

        app.draw(player.sprite)

        # finally, display the rendered frame on screen
        app.display()
