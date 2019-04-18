"""
http://pyopengl.sourceforge.net/documentation/
"""
from collections import defaultdict
import functools
from OpenGL.GL import glGenQueries, glGetInteger64v, glGetQueryObjectiv
from OpenGL.raw.GL.ARB.timer_query import glQueryCounter, GL_TIMESTAMP
from OpenGL.raw.GL.VERSION.GL_1_5 import GL_QUERY_RESULT_AVAILABLE
from OpenGL.raw.GL._types import GLint64
from sfml import sf

from examples.mariokart.engine.utils import truncate_middle

timeit_gpu_results = {}
acc_elapsed_time_in_ms = defaultdict(float)
elapsed_time_in_ms = defaultdict(float)
nb_elapsed_time = defaultdict(int)
font = sf.Font.from_file('data/resources/sansation.ttf')
profiling_text = defaultdict(lambda: sf.Text(font=font, character_size=20))


@functools.lru_cache(maxsize=10)
def get_query_and_timers(_func_name):
    return next(iter(glGenQueries(1))), GLint64(), GLint64()


def profile_gpu(func_exit_condition=lambda: True):
    """
    http://pyopengl.sourceforge.net/documentation/manual-3.0/glGet.html
    http://pyopengl.sourceforge.net/documentation/manual-3.0/glGenQueries.html

    :param func_exit_condition:
    """
    def decorator_timeit_gpu(func):
        id_query_timer, timer1, timer2 = get_query_and_timers(func.__name__)

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
            screen.height - (
                    profiling_text[func_name].font.get_line_spacing(
                        profiling_text[func_name].character_size) * (i + 1 / 3))
        )
        app.draw(profiling_text[func_name])
