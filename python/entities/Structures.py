import pygame, sys
from base import EventedSprite, load_image, World

class Structure(EventedSprite):
	def __init__(self):
		EventedSprite.__init__(self)
		self.ring = None
		self.health = 0
		self.max_health = 0 # this should be influenced by builder level
		self.height = 0 # this should be influenced by structure type
		self.habitation = 0 # this should be influenced by structure material?
		self.power = 0 # attack power
		self.range = 0 # attack range
		self.age = 0
		self.built = False
		self.world = World(pygame.display.get_surface().get_size())
		self.rendered = False

	def build(self, builder, position):
		if self.time_to_build >= builder.time_building:
			self.health = builder.time_building
			self.max_health = self.time_to_build
			builder.time_building += builder.build_speed
		else:
			if self.rect != None and position != None:
				self.rect.topleft = position
			self.health = self.time_to_build
			self.max_health = self.time_to_build
			self.world.structures.add(self)
			builder.finish_project()

	def update(self, events):
		if self.built and not self.rendered:
			self.rendered = True
			self.world.structures.add(self)
		if self.health > 0:
			self.health -= 0.1
		else:
			self.world.structures.remove(self)
		if self.ring != None:
			self.ring.update(events)
		
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