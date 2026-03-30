from mesa.discrete_space import OrthogonalMooreGrid
from pynoise.noisemodule import Perlin
from pynoise.noiseutil import (
    noise_map_plane,
    RenderImage,
    terrain_gradient,
    grayscale_gradient,
)
from environment.winds import Winds
from random import randint
from environment.rainfall import generate_rainfall_patterns


class Map(OrthogonalMooreGrid):
    def __init__(self, dimensions, torus, capacity, random=None, cell_klass=0):
        if random is None:
            random = randint(0, 100000)
        """<Up> self,
        dimensions: Sequence[int],
        torus: bool = False,            #wether it warps.. may be used for round worlds
        capacity: float | None = None,  #how many cells
        random: Random | None = None,   #seed
        cell_klass: type[T] = Cell,"""  # cells
        super().__init__(dimensions, torus, capacity, random)

    def create_biomes(self, wind: Winds):
        perlin = Perlin(2, seed=self.random)
        elevation = noise_map_plane(
            width=self.dimensions[0],
            height=self.dimensions[1],
            lower_x=1,
            upper_x=3,
            lower_z=1,
            upper_z=3,
            source=perlin,
        ).reshape(self.dimensions)
        rainfall = generate_rainfall_patterns(elevation, wind)

        render = RenderImage()
        render.render(
            self.dimensions[0],
            self.dimensions[1],
            elevation.flatten(),
            "terrain.png",
            terrain_gradient(),
        )
        render.render(
            self.dimensions[0],
            self.dimensions[1],
            (2 * rainfall - 1).flatten(),
            "rainfall.png",
            grayscale_gradient(),
        )
