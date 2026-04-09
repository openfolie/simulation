from environment.biome import biome_blueprint_factory
from commons.materials import Material


def test_biomeselection():
    elevation = 0.69
    temperature = 50
    rainfall = 0.6

    biomeblueprint = biome_blueprint_factory(elevation, temperature, rainfall)
    for materialinfo in biomeblueprint.get_spawnable_materials():
        assert materialinfo.probability <= 1
        assert materialinfo.material.value < Material.COUNT.value
