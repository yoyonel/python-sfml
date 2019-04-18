"""
"""
from collections import defaultdict

from examples.mariokart.engine.effect import Effect
from examples.mariokart.engine.mode7 import Mode7
from examples.mariokart.engine.mode7_wit_sat import Mode7WithSAT
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

    Effect.video_mode = sf.VideoMode(screen.width, screen.height)
    effect_mode7 = Mode7WithSAT()
    # effect_mode7 = Mode7()
    effect_mode7.load()

    clock = sf.Clock()

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

            mouse_position = sf.Mouse.get_position(app)
            x = mouse_position.x / app.size.x
            y = mouse_position.y / app.size.y
            effect_mode7.update(clock.elapsed_time.seconds, x, y)

            # clear the window
            app.clear(sf.Color(0, 137, 196))

            @profile_gpu(func_exit_condition=lambda: app.is_open)
            def _render_circuit():
                app.draw(effect_mode7)
            _render_circuit()

        _main_loop()

        # GPU Profiling
        render_profiling(screen, app)

        # finally, display the rendered frame on screen
        app.display()
