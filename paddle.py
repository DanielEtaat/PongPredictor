import numpy as np
import pygame


class Paddle:

    def __init__(self, x, y, color):
        self.pos = np.array([x, y])
        self.color = color
        self.width = 12
        self.height = 120

    def move(self, dy):
        self.pos[1] += dy

    def bound(self, max_height, min_height):
        if self.pos[1] > max_height - self.height:
            self.pos[1] = max_height - self.height
        elif self.pos[1] < min_height:
            self.pos[1] = min_height

    def render(self, screen):
        full_pos = list(self.pos.astype("int")) + [self.width, self.height *  0.99]
        full_pos[0] -= self.width / 2
        full_pos[0] *= 0.99
        pygame.draw.rect(screen, self.color, full_pos)
