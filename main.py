from environment import spaces, winds


def main():
    maps = spaces.Map((256, 256), False, 400, 2)
    wind = winds.OnlySouthwardWinds(256, 256)
    maps.create_biomes(wind)
    maps.displayCell(8)

if __name__ == "__main__":
    main()
