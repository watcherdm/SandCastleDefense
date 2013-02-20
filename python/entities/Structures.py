import pygame, sys
from math import fabs
from base import *

BLOCKSIZE = 50

class Tile:
	height = 0
	def __init__(self):
		self.contents = []

	def add_contents(self, content):
		self.contents.append(content)
		self.height += content.height


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
		elif self.health <= 0:
			self.world.structures.remove(self)
		if self.ring != None:
			self.ring.update(events)
		mask_hash = ['', '', '', '']
		mask_item = ''
		for structure in self.world.structures:
			# check tile_position to ensure get adjacents
			if structure == self or not isinstance(structure, self.__class__):
				continue
			if not structure.tile_position:
				continue
			struct_x = structure.tile_position[0] == self.tile_position[0]
			struct_y = structure.tile_position[1] == self.tile_position[1]
			struct_y_rel = structure.tile_position[1] - self.tile_position[1]
			struct_x_rel = structure.tile_position[0] - self.tile_position[0]
			if struct_x and fabs(struct_y_rel) == 1:
				if struct_y_rel > 0:
					mask_hash[0] = 'bottom'
				else:
					mask_hash[1] = 'top'
			if struct_y and fabs(struct_x_rel) == 1:
				if struct_x_rel > 0:
					mask_hash[2] = 'right'
				else:
					mask_hash[3] = 'left'
		mask_item = ''.join(mask_hash)
		if mask_item == '':
			mask_item = 'single'
		self.image = self.states[self.map_set][tower_mask[mask_item]]
#TODO: Redo wall segments structure

tower_mask = {
	'single': 0,
	'top': 1,
	'bottom': 2,
	'topright': 3,
	'bottomright': 4,
	'bottomleft': 6,
	'topleft': 5,
	'right': 7,
	'left': 8,
	'bottomrightleft': 9,
	'toprightleft': 10,
	'bottomtopright': 11,
	'bottomtopleft': 12,
	'bottomtoprightleft': 13,
	'bottomtop': 14,
	'rightleft': 15
}

class Pit(Structure):
	def __init__(self):
		Structure.__init__(self)
		self.height = 10
		self.map_set = 1
		self.states = load_sliced_sprites(self, 50, 50, 'tower_short.png')
		self.image = self.states[1][0]
		self.rect = pygame.Rect((0, 0, BLOCKSIZE, BLOCKSIZE))
		self.time_to_build = 300		

class Mound(Structure):
	def __init__(self):
		Structure.__init__(self)
		self.height = 10
		self.map_set = 0
		self.states = load_sliced_sprites(self, 50, 50, 'tower_short.png')
		self.image = self.states[0][0]
		self.rect = pygame.Rect((0, 0, BLOCKSIZE, BLOCKSIZE))
		self.time_to_build = 300

