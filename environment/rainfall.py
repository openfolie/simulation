import numpy as np
from math import sin, cos, pi
from environment.winds import Winds
from scipy.ndimage import gaussian_filter

# import pygame


FPS = 60


class Ball:
    DT = 1 / FPS
    SPEED = 10

    def __init__(self, position, world_size):
        self.x = position[0]
        self.y = position[1]
        self.world_size = world_size
        self.velocityX = 0
        self.velocityY = 0
        self.wetness = 0

    def tick(self):
        self.x += self.velocityX * self.DT
        self.y += self.velocityY * self.DT
        return (0 < self.x < self.world_size[0]) and (0 < self.y < self.world_size[1])

    def set_direction(self, direction):
        self.velocityX = cos(direction) * self.SPEED
        self.velocityY = sin(direction) * self.SPEED


def generate_rainfall_patterns(elevation: np.array, wind: Winds):
    def get_elevation_below(ball: Ball):
        return elevation[int(ball.y)][int(ball.x)]

    rainfall = np.zeros(elevation.shape)
    balls = list(map(lambda x: Ball(x, elevation.shape), wind.get_starting_points()))
    iters = 0
    while iters < 2000:
        if iters % 1000 == 0:
            print(iters)
        iters += 1

        empty_verticals = {}

        for ball in balls:
            elevationbelow = get_elevation_below(ball)
            if elevationbelow < -0.04:
                ball.wetness -= elevationbelow * 2
            else:
                ball.wetness = max(0, ball.wetness - 0.5)
            direction = wind.get_wind(ball.x, ball.y)
            if elevationbelow > 0.75:
                direction = pi - direction

            xballi = int(ball.x)
            if xballi not in empty_verticals:
                emptyline = list(i for i in range(elevation.shape[1]))
                for otherball in balls:
                    if xballi != int(otherball.x):
                        continue
                    yball = int(otherball.y)
                    if yball in emptyline:
                        emptyline.remove(yball)
                empty_verticals[xballi] = np.array(emptyline)

            ball.set_direction(direction)
            vaccumm = empty_verticals[xballi]
            if len(vaccumm) > 0:
                towards = np.mean(vaccumm)
                power = np.sum(vaccumm - ball.y) / len(vaccumm) ** 2
                ball.velocityY += power * 800 / (towards - ball.y) ** 2

            if not ball.tick():
                balls.remove(ball)
                continue
            rainfall[int(ball.y)][int(ball.x)] += ball.wetness

    std = np.std(rainfall)
    rainfall = np.clip(rainfall / std, 0, np.mean(rainfall) + 3 * std)
    rainfall = gaussian_filter(rainfall, sigma=2)
    # pygame.init()
    # screen = pygame.display.set_mode(elevation.shape)
    # running = True
    #
    # flat = rainfall.flatten()
    # colors = np.array([(0, 0, x) for x in flat])
    #
    # rgb = colors.reshape(rainfall.shape[0], rainfall.shape[1], 3)
    # rgb = (rgb * 255).astype(np.uint8)
    # rgb = np.transpose(rgb, (1, 0, 2))
    #
    # background = pygame.surfarray.make_surface(rgb)
    #
    # while running:
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             running = False
    #
    #     screen.blit(background, (0, 0))
    #     pygame.display.flip()
    #
    # pygame.quit()
    return rainfall
