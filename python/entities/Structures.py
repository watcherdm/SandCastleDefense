import pygame, sys
from base import EventedSprite, load_image, World

class Structure(EventedSprite):
	def __init__(self):
		EventedSprite.__init__(self)
		self.toughness = 0 # this should be influenced by builder level
		self.height = 0 # this should be influenced by structure type
		self.habitation = 0 # this should be influenced by structure material?
		self.power = 0 # attack power
		self.range = 0 # attack range
		self.age = 0
		self.built = False
		self.world = World(pygame.display.get_surface().get_size())
		self.rendered = False

	def update(self, events):
		if self.built and not self.rendered:
			self.rendered = True
			self.world.structures.add(self)


	def on_click(self, event):
		"""report on damage etc and give upgrade options"""
		return

class WallSegment(Structure):
	def __init__(self, direction = 0):
		Structure.__init__(self)
		self.direction = direction
		img = 'wall_segment_0.png'
		if self.direction == 1:
			img = 'wall_segment_1.png'
		self.image, self.rect = load_image(img, -1)
		self.time_to_build = 150


class TowerSegment(Structure):
	def __init__(self):
		Structure.__init__(self)
		self.image, self.rect = load_image('tower_segment_0.png', -1)
		self.time_to_build = 300