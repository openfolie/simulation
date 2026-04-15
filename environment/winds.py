import numpy as np
from math import pi, sqrt, acos


def from_config(s):
    return {
        "north": OnlyNorthwardWinds,
        "south": OnlySouthwardWinds,
        "east": OnlyEastwardWinds,
        "west": OnlyWestwardWinds,
        "clockwise": ClockwiseWinds,
        "anticlockwise": AntiClockwiseWinds,
    }[s]


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
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[x][y]
        else:
            return 0


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


class ClockwiseWinds(Winds):
    def __init__(self, width, height):
        self.data = np.zeros((width, height))
        self.width = width
        self.height = height

        for i in range(self.width):
            for j in range(self.height):
                base = i - width // 2
                height = j - height // 2
                if base == 0 and height == 0:
                    self.data[i][j] = 0
                    continue

                radius = sqrt(base**2 + height**2)
                self.data[i][j] = acos(height / radius)

    def get_wind(self, x, y):
        x, y = int(x), int(y)
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[x][y]
        else:
            return 0


class AntiClockwiseWinds(Winds):
    def __init__(self, width, height):
        self.data = np.zeros((width, height))
        self.width = width
        self.height = height

        for i in range(self.width):
            for j in range(self.height):
                base = i - width // 2
                height = j - height // 2
                if base == 0 and height == 0:
                    self.data[i][j] = 0
                    continue

                radius = sqrt(base**2 + height**2)
                self.data[i][j] = pi - acos(height / radius)

    def get_wind(self, x, y):
        x, y = int(x), int(y)
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[x][y]
        else:
            return 0
