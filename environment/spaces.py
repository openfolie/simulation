from mesa.discrete_space import OrthogonalMooreGrid
from environment.winds import Winds
from random import randint
from environment.rainfall import generate_rainfall_patterns
from environment.tiles import Tile
from commons.noise import (
    generate_noisemap,
    save_noise_image,
    grayscale_to_color,
    save_3dnoise_image,
)
import numpy as np

# np.set_printoptions(
#     threshold=np.inf,  # show all elements
#     precision=1,  # decimal places
#     suppress=True,  # suppress scientific notation like 1e-5
#     linewidth=200,  # wider lines before wrapping
# )


class Map(OrthogonalMooreGrid):
    def __init__(self, dimensions, torus, capacity, random=None, cell_klass=Tile):
        if random is None:
            random = randint(0, 100000)
        """<Up> self,
        dimensions: Sequence[int],
        torus: bool = False,            #wether it warps.. may be used for round worlds
        capacity: float | None = None,  #how many cells
        random: Random | None = None,   #seed
        cell_klass: type[T] = Cell,"""  # cells
        super().__init__(dimensions, torus, capacity, random, cell_klass)

    def create_biomes(self, wind: Winds):
        elevation = generate_noisemap(
            self.dimensions[0], self.dimensions[1], self.random, 50
        )

        for tile in self.all_cells:
            tile.elevation = elevation[tile.coordinate]

        rainfall, og = generate_rainfall_patterns(elevation, wind)

        save_3dnoise_image(grayscale_to_color(elevation), "elevation.png")
        save_noise_image(rainfall, "rainfall.png")
        save_noise_image(og, "rainfallog.png")

    def displayCell(
        self, n
    ):  # helper functino checking mapping consistency with the map
        arr = np.array([cell.elevation for cell in self.all_cells])
        for i in range(0, 256, n):
            for j in range(0, 256, n):
                print(round(arr[i], 2), end=" ")
            print("\n")
