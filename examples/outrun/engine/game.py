"""
"""
from collections import defaultdict
from typing import Dict
from examples.outrun.engine.profiling import (
    timeit_gpu_results,
    profile_gpu
)
from sfml import sf

from . line import Line
from . background import Background
from . camera import Camera
from . circuit import Circuit
from . player import Player
from . screen import Screen
from . utils import truncate_middle

nb_lines_in_screen = 300


def main():
    screen = Screen(1024, 768)
    camera = Camera()

    # create the main window
    app = sf.RenderWindow(sf.VideoMode(*screen.resolution), "Outrun racing!")
    app.framerate_limit = 60
    app.vertical_synchronization = True

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

    id_car = 1
    player = Player(tex_coord_t=(43 + 6)*(id_car*2),
                    maxForwardSpeed=400*3,
                    scale=3.0)
    player.create_sprite(screen)

    Line.screen = screen
    Line.cam_depth = camera.depth

    speed_text = sf.Text(string="0", font=screen.font, character_size=50)
    speed_text.position = screen.width - 250, screen.height - 80

    font = sf.Font.from_file('data/sansation.ttf')
    profiling_text = defaultdict(lambda: sf.Text(font=font, character_size=20))

    acc_elapsed_time_in_ms = defaultdict(float)
    elapsed_time_in_ms = defaultdict(float)
    nb_elapsed_time = defaultdict(int)

    # start the game loop
    while app.is_open:
        @profile_gpu(func_exit_condition=lambda: app.is_open)
        def _main_loop():
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

            start_pos = int(player.z / circuit.seg_length) % circuit.nb_lines

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
                player.per_loop_drift(circuit.lines[start_pos].curve)

            # clear the window
            app.clear(sf.Color(105, 205, 4))

            @profile_gpu(func_exit_condition=lambda: app.is_open)
            def _render_background():
                app.draw(background.sprite)
            _render_background()

            # draw grass, rumble, road
            @profile_gpu(func_exit_condition=lambda: app.is_open)
            def _render_road():
                circuit.update_and_draw(nb_lines_in_screen, player, screen, app)
            _render_road()

            @profile_gpu(func_exit_condition=lambda: app.is_open)
            def _render_objects():
                # Reverse order (painter depth technique)
                # https://en.wikipedia.org/wiki/Painter%27s_algorithm
                for line in circuit.lines[
                            start_pos: start_pos + nb_lines_in_screen][::-1]:
                    line.draw_sprite(app, screen)
            _render_objects()

            @profile_gpu(func_exit_condition=lambda: app.is_open)
            def _render_car():
                app.draw(player.sprite)
            _render_car()

            # render text with car speed
            speed_text.string = "{:.0f} kmh".format(player.speed)
            app.draw(speed_text)

        _main_loop()

        # GPU Profiling
        for i, func_name in enumerate(timeit_gpu_results, start=1):
            acc_elapsed_time_in_ms[func_name] += timeit_gpu_results[func_name] / 1000000.0
            nb_elapsed_time[func_name] += 1
            if not(nb_elapsed_time[func_name] % 60):
                elapsed_time_in_ms[func_name] = acc_elapsed_time_in_ms[func_name] / 60.0
                nb_elapsed_time[func_name] = 0
                acc_elapsed_time_in_ms[func_name] = 0
                # https://stackoverflow.com/questions/5676646/how-can-i-fill-out-a-python-string-with-spaces/38505737
            profiling_text[func_name].string = f"[gpu] {truncate_middle(func_name.ljust(15), 15)} = {elapsed_time_in_ms[func_name]:4.4} ms"
            profiling_text[func_name].position = (
                0,
                screen.height - (profiling_text[func_name].font.get_line_spacing(profiling_text[func_name].character_size) * (i + 1/3))
            )
            app.draw(profiling_text[func_name])

        # finally, display the rendered frame on screen
        app.display()
