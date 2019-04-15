"""
"""
from collections import defaultdict
from math import pi, cos, sin

from examples.mariokart.engine.profiling import (
    timeit_gpu_results,
    profile_gpu
)
from sfml import sf

from examples.mariokart.engine.screen import Screen
from examples.mariokart.engine.utils import truncate_middle


font = sf.Font.from_file('data/sansation.ttf')
profiling_text = defaultdict(lambda: sf.Text(font=font, character_size=20))

acc_elapsed_time_in_ms = defaultdict(float)
elapsed_time_in_ms = defaultdict(float)
nb_elapsed_time = defaultdict(int)


def render_profiling(screen, app):
    for i, func_name in enumerate(timeit_gpu_results, start=1):
        acc_elapsed_time_in_ms[func_name] += timeit_gpu_results[
                                                 func_name] / 1000000.0
        nb_elapsed_time[func_name] += 1
        if not (nb_elapsed_time[func_name] % 60):
            elapsed_time_in_ms[func_name] = acc_elapsed_time_in_ms[
                                                func_name] / 60.0
            nb_elapsed_time[func_name] = 0
            acc_elapsed_time_in_ms[func_name] = 0
            # https://stackoverflow.com/questions/5676646/how-can-i-fill-out-a-python-string-with-spaces/38505737
        profiling_text[func_name].string = f"[gpu] {truncate_middle(func_name.ljust(15), 15)} = {elapsed_time_in_ms[func_name]:4.4} ms"
        profiling_text[func_name].position = (
            0,
            screen.height - (profiling_text[func_name].font.get_line_spacing(profiling_text[func_name].character_size) * (i + 1 / 3))
        )
        app.draw(profiling_text[func_name])


def main():
    screen = Screen(1024, 768)

    # create the main window
    app = sf.RenderWindow(sf.VideoMode(*screen.resolution), "Mario Kart")
    app.framerate_limit = 60
    app.vertical_synchronization = True

    try:
        circuit_texture = sf.Texture.from_file("data/mariocircuit-1.png")   # type: sf.Texture
    except IOError as error:
        raise RuntimeError("An error occured: {0}".format(error))
    # Activate smooth attribute for all textures objects
    circuit_texture.smooth = True

    circuit_sprite = sf.Sprite(circuit_texture)
    circuit_sprite.texture_rectangle = (0, 0, 1024, 1024)

    screen_texture = sf.Texture.create(screen.width, screen.half_height)

    fWorldX = 1000.0
    fWorldY = 1000.0
    fWorldA = 0.1
    fNear = 0.005
    fFar = 0.03
    fFoVHalf = pi
    nMapSize = 1024

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

            # clear the window
            app.clear(sf.Color.BLACK)

            @profile_gpu(func_exit_condition=lambda: app.is_open)
            def _render_circuit():
                # app.draw(circuit_sprite)
                # Create Frustum corner points
                fFarX1 = fWorldX + cos(fWorldA - fFoVHalf) * fFar
                fFarY1 = fWorldY + sin(fWorldA - fFoVHalf) * fFar
                fNearX1 = fWorldX + cos(fWorldA - fFoVHalf) * fNear
                fNearY1 = fWorldY + sin(fWorldA - fFoVHalf) * fNear
                fFarX2 = fWorldX + cos(fWorldA + fFoVHalf) * fFar
                fFarY2 = fWorldY + sin(fWorldA + fFoVHalf) * fFar
                fNearX2 = fWorldX + cos(fWorldA + fFoVHalf) * fNear
                fNearY2 = fWorldY + sin(fWorldA + fFoVHalf) * fNear
            _render_circuit()

        _main_loop()

        # GPU Profiling
        render_profiling(screen, app)

        # finally, display the rendered frame on screen
        app.display()
