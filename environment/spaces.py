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
import math

# np.set_printoptions(
#     threshold=np.inf,  # show all elements
#     precision=1,  # decimal places
#     suppress=True,  # suppress scientific notation like 1e-5
#     linewidth=200,  # wider lines before wrapping
# )


def dist(point, i, j, elevation, rainfall, temperature):
    return math.sqrt(
        (point[0] - elevation[i][j]) ** 2 +
        (point[1] - rainfall[i][j]) ** 2 +
        (point[2] - temperature[i][j]) ** 2
    )


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

    def create_biomes(self, wind: Winds, biomes):
        elevation = generate_noisemap(
            self.dimensions[0], self.dimensions[1], self.random, 50
        )

        for tile in self.all_cells:
            tile.elevation = elevation[tile.coordinate]

        rainfall = generate_rainfall_patterns(elevation, wind) * 100
        # rainfall = np.full(self.dimensions, 100)

        # save_3dnoise_image(grayscale_to_color(elevation), "imgs/elevation.png")
        temperature = generate_noisemap(
            self.dimensions[0], self.dimensions[1], self.random + 1, 100
        )
        # save_noise_image(rainfall, "imgs/rainfall.png")
        # save_noise_image(temperature, "imgs/temperature.png")

        biome_map = np.zeros(self.dimensions)
        points = []
        for i, biome in enumerate(biomes.values()):
            for point in biome['points']:
                points.append((point, i))

        for i in range(self.dimensions[0]):
            for j in range(self.dimensions[1]):
                min_dist = math.inf
                closest_biome = None
                for point in points:
                    d = dist(point[0], i, j, elevation, rainfall, temperature)
                    if d >= min_dist:
                        continue
                    min_dist = d
                    closest_biome = point[1]
                # print(min_dist, closest_biome)
                biome_map[i][j] = closest_biome
       
        print(biome_map)
        save_noise_image(biome_map / len(biomes), "imgs/biome.png")


    def displayCell(
        self, n
    ):  # helper functino checking mapping consistency with the map
        arr = np.array([cell.elevation for cell in self.all_cells])
        for i in range(0, 256, n):
            for j in range(0, 256, n):
                print(round(arr[i], 2), end=" ")
            print("\n")
