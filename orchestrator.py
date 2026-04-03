import numpy as np
import pandas as pd
import seaborn as sns
import mesa
import agents
from environment import Tile
import environment
from mesa.discrete_space import Cell


class World(mesa.model):
    def __init__(self, width=256, height=256, num_agents=400, rng=None):
        super().__init__(rng=rng)
        self.grid = environment.Map(
            (width, height), False, num_agents, 2, self.random
        )  # add class of agents as well but well rn nah

        for cell in self.grid.all_cells:
            Tile(
                self,
                cell,
                init_state=(
                    Cell.ALIVE
                    if self.random.random() < initial_fraction_alive
                    else Cell.DEAD
                ),
            )

    if __name__ == "__main__":
        World()
