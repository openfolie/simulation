from abc import ABC, abstractmethod
from commons.materials import Material
from typing import List


class MaterialInfo:
    material: Material
    probability: int

    def __init__(self, material: Material, probability: int):
        self.material = material
        self.probability = probability

    def __str__(self):
        return f"{self.material} with {self.probability * 100}% probability"

    def __repr__(self):
        return f"{self.material} with {self.probability * 100}% probability"


class BiomeBlueprint(ABC):
    def __init__(self, elevation, temperature, rainfall):
        pass

    @abstractmethod
    def get_spawnable_materials(self) -> List[MaterialInfo]:
        pass


class HotDesertBlueprint(BiomeBlueprint):
    def get_spawnable_materials(self):
        return list(
            map(
                lambda x: MaterialInfo(*x),
                [
                    (Material.SAND, 1.0),
                    (Material.GOLD, 0.04),
                ],
            )
        )


class ForestBlueprint(BiomeBlueprint):
    def get_spawnable_materials(self):
        return list(
            map(
                lambda x: MaterialInfo(*x),
                [
                    (Material.DIRT, 1.0),
                    (Material.WOOD, 0.89),
                    (Material.IRON, 0.08),
                ],
            )
        )


def biome_blueprint_factory(elevation, temperature, rainfall):
    if rainfall > 0.5:
        return ForestBlueprint(elevation, temperature, rainfall)
    return HotDesertBlueprint(elevation, temperature, rainfall)
