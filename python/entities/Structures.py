import pygame, sys
from math import fabs
from base import *

BLOCKSIZE = 50

class Structure(EventedSprite):
	def __init__(self):
		EventedSprite.__init__(self)
		self.tile_position = {
			'x': 0, 
			'y': 0
		}
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
				self.tile_position[0] = position[0] / BLOCKSIZE
				self.tile_position[1] = position[1] / BLOCKSIZE
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


tower_mask = {
	'single': 0,
	'top': 1,
	'bottom': 2,
	'topright': 3,
	'bottomright': 4,
	'bottomleft': 5,
	'topleft': 6,
	'right': 7,
	'left': 8
}

class TowerSegment(Structure):
	def __init__(self):
		Structure.__init__(self)
		self.states = load_sliced_sprites(self, 50, 50, 'tower_short.png')
		self.image = self.states[0][0]
		self.rect = pygame.Rect((0, 0, BLOCKSIZE, BLOCKSIZE))
		self.time_to_build = 300

	def update(self, events):
		mask_item = ''
		for structure in self.world.structures:
			# check tile_position to ensure get adjacents
			if structure == self:
				continue
			struct_x = structure.tile_position[0] == self.tile_position[0]
			struct_y = structure.tile_position[1] == self.tile_position[1]
			struct_y_rel = structure.tile_position[1] - self.tile_position[1]
			struct_x_rel = structure.tile_position[0] - self.tile_position[0]
			if struct_x and fabs(struct_y_rel) == 1:
				if struct_y_rel > 0:
					mask_item += 'bottom'
				else:
					mask_item += 'top'
			if struct_y and fabs(struct_x_rel) == 1:
				if struct_x_rel > 0:
					mask_item += 'right'
				else:
					mask_item += 'left'
		if mask_item == '':
			mask_item = 'single'
		print mask_item
		self.image = self.states[0][tower_mask[mask_item]]