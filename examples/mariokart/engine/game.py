"""
"""
from sfml import sf

from examples.mariokart.engine.effect import Effect
# from examples.mariokart.engine.mode7 import Mode7
from examples.mariokart.engine.mode7_wit_sat import Mode7WithSAT
from examples.mariokart.engine.profiling import (
    profile_gpu,
    render_profiling
)
from examples.mariokart.engine.screen import Screen


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
