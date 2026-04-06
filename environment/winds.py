import numpy as np
from math import pi


class Winds:
    def get_wind(self, x, y):
        raise NotImplementedError


class OnlyEastwardWinds(Winds):
    def __init__(self, width, height):
        # it's all "0",
        # because "0 degrees" is on the right hand side / eastwards
        self.data = np.zeros((width, height))
        self.width = width
        self.height = height

    def get_wind(self, x, y):
        x, y = int(x), int(y)
        assert 0 <= x < self.width and 0 <= y < self.height
        return self.data[x][y]


class OnlyWestwardWinds(Winds):
    def __init__(self, width, height):
        self.data = np.full((width, height), pi)
        self.width = width
        self.height = height

    def get_wind(self, x, y):
        x, y = int(x), int(y)
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[x][y]
        else:
            return 0


class OnlyNorthwardWinds(Winds):
    def __init__(self, width, height):
        # it's all "0",
        # because "0 degrees" is on the right hand side / eastwards
        self.data = np.full((width, height), pi / 2)
        self.width = width
        self.height = height

    def get_wind(self, x, y):
        x, y = int(x), int(y)
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[x][y]
        else:
            return 0


class OnlySouthwardWinds(Winds):
    def __init__(self, width, height):
        self.data = np.full((width, height), -pi / 2)
        self.width = width
        self.height = height

    def get_wind(self, x, y):
        x, y = int(x), int(y)
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[x][y]
        else:
            return 0
