from mesa.discrete_space import Cell
import numpy as np

Coordinate = tuple[int, ...]
from random import Random


class Tile(Cell):
    def __init__(
        self,
        coordinate: Coordinate,
        position: np.ndarray | None = None,
        capacity: int | None = None,
        random: Random | None = None,
        climate: int | None = None,
        terrain: int | None = None,
        elevation: int | None = None,
    ):
        super().__init__(coordinate, position, capacity, random)
        self.elevation = elevation
        self.climate = climate
        self.terrain = terrain
