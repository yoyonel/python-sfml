"""
"""
import functools
from typing import Dict
# http://pyopengl.sourceforge.net/documentation/
from OpenGL.GL import glGenQueries, glQueryCounter, GL_TIMESTAMP, \
    glGetQueryObjectiv, GL_QUERY_RESULT_AVAILABLE, glGetInteger64v, GLint64

from sfml import sf

from . line import Line
from . background import Background
from . camera import Camera
from . circuit import Circuit
from . player import Player
from . screen import Screen

nb_lines_in_screen = 300


timeit_gpu_results = {}


def profile_gpu(func_exit_condition=lambda: True):
    """
    http://pyopengl.sourceforge.net/documentation/manual-3.0/glGet.html
    http://pyopengl.sourceforge.net/documentation/manual-3.0/glGenQueries.html

    :param func_exit_condition:
    """
    def decorator_timeit_gpu(func):
        # TODO: cache this variables
        id_query_timer = next(iter(glGenQueries(1)))
        timer1 = GLint64()
        timer2 = GLint64()

        @functools.wraps(func)
        def wrapper_timeit_gpu(*args, **kwargs):
            glQueryCounter(id_query_timer, GL_TIMESTAMP)

            glGetInteger64v(GL_TIMESTAMP, timer1)

            result = func(*args, **kwargs)

            done = False
            while not done and func_exit_condition():
                done = glGetQueryObjectiv(id_query_timer,
                                          GL_QUERY_RESULT_AVAILABLE)
            glGetInteger64v(GL_TIMESTAMP, timer2)

            timeit_gpu_results[func.__name__] = timer2.value - timer1.value
            return result
        return wrapper_timeit_gpu
    return decorator_timeit_gpu


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
    profiling_text = sf.Text(string="gpu", font=font, character_size=30)
    profiling_text.position = 0, screen.height - 80

    acc_elapsed_time_in_ms = 0.0
    elapsed_time_in_ms = 0.0
    nb_elapsed_time = 0

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

            # clear the window
            app.clear(sf.Color(105, 205, 4))
            app.draw(background.sprite)

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
                # part that forces the car to stray from track when the road cruves
                # if player.is_driving_forward:
                #     player.x -= (lines[start_pos].curve * (player.speed / 8000.0))
                # elif player.is_driving_backward:
                #     player.x += (lines[start_pos].curve * (player.speed / 8000.0))

            # draw grass, rumble, road
            circuit.update_and_draw(nb_lines_in_screen, player, screen, app)

            # Reverse order (painter depth technique)
            # https://en.wikipedia.org/wiki/Painter%27s_algorithm
            for line in circuit.lines[
                        start_pos: start_pos + nb_lines_in_screen][::-1]:
                line.draw_sprite(app, screen)

            app.draw(player.sprite)

            speed_text.string = "{:.0f} kmh".format(player.speed)
            app.draw(speed_text)

        _main_loop()

        acc_elapsed_time_in_ms += timeit_gpu_results['_main_loop'] / 1000000.0
        nb_elapsed_time += 1
        if not(nb_elapsed_time % 60):
            elapsed_time_in_ms = acc_elapsed_time_in_ms / 60.0
            nb_elapsed_time = 0
            acc_elapsed_time_in_ms = 0
        profiling_text.string = "gpu = {:4.4} ms".format(elapsed_time_in_ms)
        app.draw(profiling_text)

        # finally, display the rendered frame on screen
        app.display()
