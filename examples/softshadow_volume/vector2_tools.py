import numpy as np
from math import sqrt
from sfml import sf


def dot(p1: sf.Vector2, p2: sf.Vector2) -> float:
    """

    :param p1:
    :param p2:
    :return:

    >>> dot(sf.Vector2(), sf.Vector2())
    0
    >>> dot(sf.Vector2(1, -1), sf.Vector2(1, 1))
    0
    """
    return (p1.x * p2.x) + (p1.y * p2.y)


def norm2(p: sf.Vector2) -> float:
    """

    :param p:
    :return:

    >>> norm2(sf.Vector2())
    0
    >>> norm2(sf.Vector2(1, 1))
    2
    >>> norm2(sf.Vector2(2, 2))
    8
    """
    return dot(p, p)


def norm(p: sf.Vector2) -> float:
    """

    :param p:
    :return:

    >>> norm(sf.Vector2())
    0.0
    >>> np.isclose(norm(sf.Vector2(1, 1)), sqrt(2))
    True
    >>> np.isclose(norm(sf.Vector2(2, 2)), sqrt(8))
    True
    """
    return sqrt(norm2(p))


def inv_norm(p: sf.Vector2) -> float:
    """

    :param p:
    :return:

    >>> inv_norm(sf.Vector2())
    Traceback (most recent call last):
    ...
    ZeroDivisionError: float division by zero
    >>> np.isclose(inv_norm(sf.Vector2(1, 1)), 1.0 / sqrt(2))
    True
    >>> np.isclose(inv_norm(sf.Vector2(2, 2)), 1.0 / sqrt(8))
    True
    """
    return 1.0 / norm(p)


def normalize(p: sf.Vector2) -> sf.Vector2:
    """

    :param p:
    :return:

    >>> normalize(sf.Vector2())
    Traceback (most recent call last):
    ...
    ZeroDivisionError: float division by zero
    >>> normalize(sf.Vector2(1, 1)) == sf.Vector2(1.0 / sqrt(2), 1.0 / sqrt(2))
    True
    >>> normalize(sf.Vector2(2, 2)) == sf.Vector2(1.0 / sqrt(2), 1.0 / sqrt(2))
    True
    """
    return p * inv_norm(p)


def normal(p: sf.Vector2) -> sf.Vector2:
    """

    :param p:
    :return:

    >>> normal(sf.Vector2()) == sf.Vector2()
    True
    >>> normal(sf.Vector2(1, 1)) == sf.Vector2(-1, 1)
    True
    >>> normal(sf.Vector2(3, 2)) == sf.Vector2(-2, 3)
    True
    """
    return sf.Vector2(-p.y, p.x)


def det(v0: sf.Vector2, v1: sf.Vector2) -> float:
    return v0.x * v1.y - v1.x * v0.y


def compute_middle(v1: sf.Vector2, v2: sf.Vector2) -> sf.Vector2:
    """

    :param v1:
    :param v2:
    :return:

    >>> compute_middle(sf.Vector2(), sf.Vector2()) == sf.Vector2()
    True
    >>> compute_middle(sf.Vector2(), sf.Vector2(1, 1)) == sf.Vector2(0.5, 0.5)
    True
    >>> compute_middle(sf.Vector2(1, 1), sf.Vector2(3, 2)) == sf.Vector2(2, 1.5)
    True
    """
    return (v1 + v2) * 0.5


def min_vector2(v0: sf.Vector2, v1: sf.Vector2):
    return sf.Vector2(min(v0.x, v1.x), min(v0.y, v1.y))


def max_vector2(v0: sf.Vector2, v1: sf.Vector2):
    return sf.Vector2(max(v0.x, v1.x), max(v0.y, v1.y))
