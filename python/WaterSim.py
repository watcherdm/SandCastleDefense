import pygame, sys, os
from pygame import *
import random
from scipy.ndimage import gaussian_filter1d
import numpy as np

wave_image = pygame.image.load(os.path.join('assets', 'images', 'wavetip.png'))
print wave_image

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

pygame.init()

screen = pygame.display.set_mode(SCREEN_SIZE)
obstructions = pygame.sprite.OrderedUpdates()

def smooth_line(l):
	a = np.array(l)
	x, y = a.T
	t = np.linspace(0, 1, len(x))
	t2 = np.linspace(0, 1, len(x))

	x2 = np.interp(t2, t, x)
	y2 = np.interp(t2, t, y)
	sigma = 10
	x3 = gaussian_filter1d(x2, sigma)
	y3 = gaussian_filter1d(y2, sigma)

	return y3

class Wave():
	points = []
	color = pygame.Color(0, 0, 255)
	y = 100
	low = 100
	high = 300
	direction = 1

	def __init__(self):
		for i in range(SCREEN_WIDTH):
			self.points.append([i, self.y])

	def move(self):
		if self.y > self.high:
			print "reversing direction, going down"
			self.direction = -1
		if  self.y < self.low:
			print "reversing direction, going up"
			self.direction = 1
		self.set_y(self.y + self.direction)

	def set_y(self, y):
		self.y = y
		for point in self.points:
			if y > point[1]:
				if self.can_go(point[0] + 1, point[1] + 1):
					point[1] = y
			else:
				point[1] = y

	def can_go(self, x, y):
		can_go = True
		for obstruction in obstructions:
			can_go = obstruction.rect.collidepoint(x, SCREEN_HEIGHT - y) != True
			if not can_go:
				break
		return can_go

	def draw(self, surf):
		ys = list(smooth_line(self.points))
		for idx, point in enumerate(self.points):
			x = point[0] + 1
			y = ys[idx]
			pygame.draw.line(surf, self.color, (x, SCREEN_HEIGHT - y), (x, SCREEN_HEIGHT), 1)

ocean = Wave()

def make_rock(pos = (300, 200)):
	rock = pygame.sprite.Sprite()
	rock.image = pygame.Surface((50,50))
	rock.image.fill(pygame.Color(255,0,0))
	rock.rect = rock.image.get_rect()
	rock.rect.topleft = pos
	return rock

obstructions.add(make_rock())
obstructions.add(make_rock((100, 200)))
obstructions.add(make_rock((250, 200)))

while True:
	events = pygame.event.get()
	for event in events:
		if event.type == pygame.QUIT:
			exit()
	screen.fill(pygame.Color(0,0,0))
	ocean.move()
	obstructions.draw(screen)
	ocean.draw(screen)
	pygame.display.update()