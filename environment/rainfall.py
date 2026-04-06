import numpy as np
from math import sin, cos
from environment.winds import Winds
from scipy.ndimage import gaussian_filter
from random import randrange


FPS = 60
DT = 1 / FPS


def vectorize(x):
    return np.array([cos(x), sin(x)])


class Particle:
    SPEED = 10

    def __init__(self, position, world_size):
        self.x = position[0]
        self.y = position[1]
        self.world_size = world_size
        self.velocity_x = 0
        self.velocity_y = 0
        self.moisture = 0

    def tick(self):
        self.x += self.velocity_x * DT
        self.y += self.velocity_y * DT
        if self.x < 0:
            self.x = self.world_size[0] + self.x
            self.moisture = 0
        elif self.x > self.world_size[0]:
            self.x -= self.world_size[0]
            self.moisture = 0

        if self.y < 0:
            self.y = self.world_size[1] + self.y
            self.moisture = 0
        elif self.y > self.world_size[1]:
            self.y -= self.world_size[1]
            self.moisture = 0

    def set_direction(self, direction):
        self.velocity_x, self.velocity_y = vectorize(direction) * self.SPEED


def sample_bilinear(wind: Winds, x, y):
    x0, y0 = int(x), int(y)
    x1, y1 = x0 + 1, y0 + 1
    tx, ty = x - x0, y - y0

    v00 = vectorize(wind.get_wind(x0, y0))
    v10 = vectorize(wind.get_wind(x1, y0))
    v01 = vectorize(wind.get_wind(x0, y1))
    v11 = vectorize(wind.get_wind(x1, y1))

    return (
        v00 * (1 - tx) * (1 - ty)
        + v10 * tx * (1 - ty)
        + v01 * (1 - tx) * (1 - ty)
        + v11 * tx * ty
    )


def splat(density: np.array, x, y, weight):
    x0, y0 = int(x), int(y)
    tx, ty = x - x0, y - y0

    density[y0][x0] += weight * (1 - tx) * (1 - ty)
    if x0 < 255:
        density[y0][x0 + 1] += weight * tx * (1 - ty)
    if y0 < 255:
        density[y0 + 1][x0] += weight * (1 - tx) * ty
    if x0 < 255 and y0 < 255:
        density[y0 + 1][x0 + 1] += weight * tx * ty


def generate_rainfall_patterns(elevation: np.array, wind: Winds):
    rainfall = np.zeros(elevation.shape)
    particles = []
    density = np.zeros(elevation.shape)
    SPARCITY = 5
    rho = 1

    for i in range(0, elevation.shape[0], SPARCITY):
        for j in range(0, elevation.shape[1], SPARCITY):
            particles.append((i, j))
            density[j][i] += 1

    particles = list(map(lambda x: Particle(x, elevation.shape), particles))
    iters = 0

    ITER_COUNT = 2000
    while iters < ITER_COUNT:
        if iters % 20 == 0:
            print(
                "Simulating rainfall:",
                round(100 * iters / ITER_COUNT, 2),
                "% completed",
            )
        iters += 1

        def process_particle(p):
            elevationbelow = elevation[int(p.y)][int(p.x)]
            if elevationbelow < -0.04:
                p.moisture -= elevationbelow * 2
                p.moisture = max(10, p.moisture)
            else:
                p.moisture = max(0, p.moisture - randrange(0, 5)/10)

            px, py = int(p.x), int(p.y)
            dpdx = (density[py][min(255, px + 1)] - density[py][max(0, px - 1)]) / 2
            dpdy = (density[min(255, py + 1)][px] - density[max(0, py - 1)][px]) / 2

            p.velocity_x -= (dpdx / rho) * DT
            p.velocity_y -= (dpdy / rho) * DT

            wind_dir = 20 * sample_bilinear(wind, p.x, p.y)
            drag = 0.1
            p.velocity_x += (wind_dir[0] - p.velocity_x) * drag * DT
            p.velocity_y += (wind_dir[1] - p.velocity_y) * drag * DT

            if elevationbelow > 0.75:
                p.velocity_x *= -1
                p.velocity_y *= -1
            p.tick()

            density[py][px] -= 1
            density[int(p.y)][int(p.x)] += 1
            rainfall[py][px] += p.moisture

        for p in particles:
            process_particle(p)

    std = np.std(rainfall)
    rainfall = np.clip(rainfall / std, 0, np.mean(rainfall) + 3 * std)
    rainfall = gaussian_filter(rainfall, sigma=2)

    return rainfall
