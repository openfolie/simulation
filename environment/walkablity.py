from commons.actions import FundamentalActions
from random import randint


class Walkability:
    def __init__(self, slopes, base_level):
        self.slopes = slopes
        self.diffs = []
        old = [base_level] * len(slopes[0])
        for i, slope in enumerate(slopes):
            self.diffs.append([0] * len(slopes[0]))
            for j in range(len(slopes[0])):
                self.diffs[i][j] = slope[j] - old[j]
            old = slope
        print(self.diffs)


class FlatPlain(Walkability):
    def __init__(self, level):
        # just assumming a 3x5 for testing
        super().__init__(
            [
                [level, level],
                [level, level],
                [level, level],
                [level, level],
                [level, level],
            ],
            level,
        )


class RugidSurface(Walkability):
    def __init__(self, level, max_height, min_height):
        def x():
            return randint(min_height, max_height)
        super().__init__(
            [
                [level + x(), level + x()],
                [level + x(), level + x()],
                [level + x(), level + x()],
                [level + x(), level + x()],
                [level + x(), level + x()],
            ],
            level,
        )
