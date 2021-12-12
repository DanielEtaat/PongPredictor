import pygame
import numpy as np


class Ball:

	MAX_SPEED = 30

	def __init__(self, x, y, color):
		self.pos = np.array([x, y], dtype="float64")
		self.color = color
		self.vel = np.array([0, 0], dtype="float64")
		self.radius = 5

	def randomize_velocity(self, low=2, high=5):
		vy = np.random.uniform() * 2 - 1
		vx = np.random.uniform(low=low, high=high) * vy * np.sign(np.random.uniform() - 0.5)
		self.vel = np.array([vx, vy])
		self.vel *= 0.5 * Ball.MAX_SPEED / np.linalg.norm(self.vel)

	def update_pos(self):
		self.pos += self.vel

	def bound(self, width, height):
		if self.pos[0] > width:
			self.pos[0] = width
			self.vel[0] *= -1
		elif self.pos[0] < 0:
			self.pos[0]
			self.vel[0] *= -1
		if self.pos[1] > height:
			self.pos[1] = height
			self.vel[1] *= -1
		elif self.pos[1] < 0:
			self.pos[1] = 0
			self.vel[1] *= -1

	def render(self, screen):
		pygame.draw.circle(screen, self.color, self.pos.astype("int"), self.radius)
