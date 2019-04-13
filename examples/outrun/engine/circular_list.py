"""
# https://stackoverflow.com/a/47606550
"""
import operator
from typing import _alias, T

TCircularList = _alias(list, T, inst=False)


class CircularList(list):
    def __getitem__(self, x):
        if isinstance(x, slice):
            return [self[x] for x in self._rangeify(x)]

        index = operator.index(x)
        try:
            return super().__getitem__(index % len(self))
        except ZeroDivisionError:
            raise IndexError('list index out of range')

    def _rangeify(self, slice_):
        start, stop, step = slice_.start, slice_.stop, slice_.step
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is None:
            step = 1
        return range(start, stop, step)
