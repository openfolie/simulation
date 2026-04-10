from environment import spaces, winds
from configuration import load_config


def wind_factory(wind_str):
    return winds.OnlySouthwardWinds


def main():
    config = load_config()
    print(config)
    maps = spaces.Map(
        config['map']['size'],
        False,
        config['map']['cellcapacity'],
        config['map']['seed']
    )
    Wind = wind_factory(config['map']['wind'])
    wind = Wind(*config['map']['size'])
    maps.create_biomes(wind)
    maps.displayCell(8)


if __name__ == "__main__":
    main()
