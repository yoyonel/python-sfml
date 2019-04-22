"""
"""
from sfml import sf


def to_vec2(v: sf.Vector3) -> sf.Vector2:
    return sf.Vector2(v.x, v.y)


def to_vec3(v: sf.Vector2, z: float = 0) -> sf.Vector3:
    """

    :param v:
    :param z:
    :return:

    >>> to_vec3(sf.Vector2())
    Vector3(x=0, y=0, z=0)
    >>> to_vec3(sf.Vector2(1, 1))
    Vector3(x=1, y=1, z=0)
    >>> to_vec3(sf.Vector2(-2, 3), -1)
    Vector3(x=-2, y=3, z=-1)
    """
    return sf.Vector3(*v, z)


def prod_vec(v0: sf.Vector3, v1: sf.Vector3) -> sf.Vector3:
    """
    
    :param v0: 
    :param v1: 
    :return:

    >>> prod_vec(sf.Vector3(), sf.Vector3())
    Vector3(x=0, y=0, z=0)
    >>> prod_vec(sf.Vector3(1, 0, 0), sf.Vector3(0, 1, 0))
    Vector3(x=0, y=0, z=1)
    >>> prod_vec(sf.Vector3(0, 1, 0), sf.Vector3(0, 0, 1))
    Vector3(x=1, y=0, z=0)
    >>> prod_vec(sf.Vector3(0, 0, 1), sf.Vector3(1, 0, 0))
    Vector3(x=0, y=1, z=0)
    >>> prod_vec(sf.Vector3(1, 0, 0), sf.Vector3(0, 0, 1))
    Vector3(x=0, y=-1, z=0)
    """
    return sf.Vector3(v0.y * v1.z - v0.z * v1.y,
                      v0.z * v1.x - v0.x * v1.z,
                      v0.x * v1.y - v0.y * v1.x)
