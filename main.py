from environment import spaces, winds
from configuration import load_config
import time


def wind_factory(wind_str):
    return winds.OnlyWestwardWinds


def main():
    start = time.time()
    config = load_config("configuration/world.nix")
    end = time.time()
    print(config, end - start)
    maps = spaces.Map(
        config["map"]["size"],
        False,
        config["map"]["cellcapacity"],
        config["map"]["seed"],
    )
    Wind = wind_factory(config["map"]["wind"])
    wind = Wind(*config["map"]["size"])
    maps.create_biomes(wind)
    # maps.displayCell(8)


if __name__ == "__main__":
    main()
