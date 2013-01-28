import pygame, sys
from base import EventedSprite, load_image

class Structure(EventedSprite):
	def __init__(self):
		EventedSprite.__init__(self)
		self.toughness = 0 # this should be influenced by builder level
		self.height = 0 # this should be influenced by structure type
		self.habiation = 0 # this should be influenced by structure material?
		self.power = 0 # attack power
		self.range = 0 # attack range
		self.age = 0

	def update(self, events):
		self.age += 1

	def on_click(self, event):
		"""report on damage etc and give upgrade options"""
		return

class WallSegment(EventedSprite):
	def __init__(self, direction = 0):
		EventedSprite.__init__(self)
		self.direction = direction
		img = 'wall_segment_0.png'
		if self.direction == 1:
			img = 'wall_segment_1.png'
		self.image, self.rect = load_image(img, -1)

class TowerSegment(EventedSprite):
	def __init__(self):
		EventedSprite.__init__(self)
		self.image, self.rect = load_image('tower_segment_0.png', -1)

class World(EventedSprite):
	def __init__(self, name = "beach", grid_size = 50):
		EventedSprite.__init__(self)
		self.image, self.rect = load_image(name + '.jpg', -1)
		self.grid_size = grid_size
		self.selected = None
	def draw(self, surfaceObj):
		surfaceObj.blit(self.image, (0, 0))

	def setSelected(self, sprite):
		if self.selected:
			self.selected.deselect() #this should only allow one selection at a time
		self.selected = sprite

	def on_click(self, event):
		if self.selected:
			self.selected.setDestination(pygame.mouse.get_pos())