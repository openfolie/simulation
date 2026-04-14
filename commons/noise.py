from PIL import Image
import noise
import numpy as np


def generate_noisemap(width, height, seed, scale=100.0):
    terrain = np.zeros((height, width))

    for y in range(height):
        for x in range(width):
            terrain[y][x] = noise.pnoise2(
                x / scale,
                y / scale,
                octaves=20,
                persistence=0.5,
                lacunarity=2.0,
                base=seed,
            )

    return (terrain + 1) / 2


def save_noise_image(noise, filename):
    # Convert to 0–255
    img = (noise * 255).astype(np.uint8)

    image = Image.fromarray(img, mode="L")
    image.save(filename)


def save_3dnoise_image(noise3d, filename):
    image = Image.fromarray(noise3d)
    image.save(filename)


water = np.array([0, 0, 150])
sand = np.array([240, 240, 64])
grass = np.array([50, 160, 60])
mountain = np.array([200, 200, 200])
snow = np.array([255, 255, 255])


def grayscale_to_color(terrain):
    h, w = terrain.shape
    img = np.zeros((h, w, 3), dtype=np.uint8)

    for y in range(h):
        for x in range(w):
            img[y, x] = color_from_height(terrain[y, x]) * 255

    return img


def lerp3d(a, b, t):
    return a + (b - a) * t


stops = [
    (0, np.array([0, 0, 128 / 255])),
    (.4, np.array([32 / 255, 64 / 255, 128 / 255])),
    (.48, np.array([64 / 255, 96 / 255, 192 / 255])),
    (.49, np.array([192 / 255, 192 / 255, 128 / 255])),
    (.5, np.array([0, 192 / 255, 0])),
    (.59, np.array([192 / 255, 192 / 255, 0])),
    (.6, np.array([160 / 255, 96 / 255, 64 / 255])),
    (.68, np.array([128 / 255, 1, 1])),
    (1, np.array([1, 1, 1])),
]


def color_from_height(v):
    # v assumed in [0, 1]

    for i in range(len(stops) - 1):
        v0, c0 = stops[i]
        v1, c1 = stops[i + 1]

        if v0 <= v <= v1:
            t = (v - v0) / (v1 - v0)
            return lerp3d(c0, c1, t)

    return stops[-1][1]
