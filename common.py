from enum import Enum, IntEnum
from types import FunctionType, MethodType


class Event:
    def __init__(self):
        self._callbacks = []

    def add(self, other):
        if not isinstance(other, FunctionType) and not isinstance(other, MethodType):
            raise TypeError('invalid function or method')
        self._callbacks.append(other)

    def remove(self, other):
        try:
            self._callbacks.remove(other)
        except ValueError:
            pass

    def notify(self, *args, **kwargs):
        for callback in self._callbacks:
            callback(*args, **kwargs)


class GameError(Exception):
    pass


class Result(Enum):
    OK = 0
    Win = 1
    Loss = 2


class Content(IntEnum):
    BlownMine = -5
    Mine = -4
    QuestionMark = -3
    Flag = -2
    Unknown = -1
    NoMine = 0
    M1 = 1
    M2 = 2
    M3 = 3
    M4 = 4
    M5 = 5
    M6 = 6
    M7 = 7
    M8 = 8
