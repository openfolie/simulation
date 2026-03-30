import numpy as np
from math import pi


class Winds:
    def get_wind(self, x, y):
        raise NotImplementedError

    def get_starting_points(self):
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

    def get_starting_points(self):
        output = []
        for i in range(self.height):
            output.append((0, i))
        return output


class OnlyWestwardWinds(Winds):
    def __init__(self, width, height):
        self.data = np.full((width, height), pi)
        self.width = width
        self.height = height

    def get_wind(self, x, y):
        x, y = int(x), int(y)
        assert 0 <= x < self.width and 0 <= y < self.height
        return self.data[x][y]

    def get_starting_points(self):
        output = []
        for i in range(self.height):
            output.append((self.width - 1, i))
        return output


class OnlyNorthwardWinds(Winds):
    def __init__(self, width, height):
        # it's all "0",
        # because "0 degrees" is on the right hand side / eastwards
        self.data = np.full((width, height), pi / 2)
        self.width = width
        self.height = height

    def get_wind(self, x, y):
        x, y = int(x), int(y)
        assert 0 <= x < self.width and 0 <= y < self.height
        return self.data[x][y]

    def get_starting_points(self):
        output = []
        for i in range(self.height):
            output.append((i, 0))
        return output


class OnlySouthwardWinds(Winds):
    def __init__(self, width, height):
        self.data = np.full((width, height), -pi / 2)
        self.width = width
        self.height = height

    def get_wind(self, x, y):
        x, y = int(x), int(y)
        assert 0 <= x < self.width and 0 <= y < self.height
        return self.data[x][y]

    def get_starting_points(self):
        output = []
        for i in range(self.height):
            output.append((i, self.height - 1))
        return output
