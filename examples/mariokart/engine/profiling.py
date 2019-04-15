"""
http://pyopengl.sourceforge.net/documentation/
"""
import functools
from OpenGL.GL import glGenQueries, glGetInteger64v, glGetQueryObjectiv
from OpenGL.raw.GL.ARB.timer_query import glQueryCounter, GL_TIMESTAMP
from OpenGL.raw.GL.VERSION.GL_1_5 import GL_QUERY_RESULT_AVAILABLE
from OpenGL.raw.GL._types import GLint64

timeit_gpu_results = {}


@functools.lru_cache(maxsize=10)
def get_query_and_timers(func_name):
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
