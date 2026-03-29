import numpy as np
from mesa.discrete_space import OrthogonalMooreGrid
from pynoise.noisemodule import Perlin
from pynoise.noiseutil import noise_map_plane
from pynoise.noiseutil import RenderImage
from pynoise.noiseutil import terrain_gradient


class Map(OrthogonalMooreGrid):
    def __init__(self, dimensions, torus, capacity, random, cell_klass=0):
        """<Up> self,
        dimensions: Sequence[int],
        torus: bool = False,            #wether it warps.. may be used for round worlds
        capacity: float | None = None,  #how many cells
        random: Random | None = None,   #seed
        cell_klass: type[T] = Cell,"""  # cells
        super().__init__(dimensions, torus, capacity, random)

    def create_biomes(self):
        perlin = Perlin(self.random)
        elevation = noise_map_plane(
            width=self.dimensions[0],
            height=self.dimensions[1],
            lower_x=1,
            upper_x=3,
            lower_z=1,
            upper_z=3,
            source=perlin,
        )
        print(elevation)
        elevation_np = np.array(elevation.reshape(self.dimensions))
        self.add_property_layer("elevation", elevation_np, True)
        render = RenderImage()
        gradient = terrain_gradient()
        render.render(
            self.dimensions[0], self.dimensions[1], elevation, "terrain.png", gradient
        )
        # read only is true for now later if we wanna let them terraform and shit  then adjust accordingly


if __name__ == "__main__":
    maps = Map((256, 256), False, 400, 2)
    maps.create_biomes()
