import numpy as np


class Winds:
    def get_wind(self, x, y):
        raise NotImplementedError


class OnlyEastwardWinds(Winds):
    def __init__(self, width, height):
        # it's all "0",
        # because "0 degrees" is on the right hand side / eastwards
        self.data = np.zeros((width, height))

    def get_wind(self, x, y):
        return self.data[x][y]
