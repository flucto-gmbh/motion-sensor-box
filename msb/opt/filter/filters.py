from types import FunctionType
from collections.abc import Generator
import numpy as np

_filters = []


def add_filter_func(func):
    _filters.append(func)


def filter_generator(source: Generator[np.ndarray, None, None]) -> np.ndarray:
    for img in source:
        for filter in _filters:
            img = filter(img)

        yield img
