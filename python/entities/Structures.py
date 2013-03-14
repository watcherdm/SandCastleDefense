import pygame, sys
from math import fabs
from base import *
from engines import trajectory

BLOCKSIZE = 50
BEACHCOLOR = pygame.Color(255, 222, 73, 1)

class Tile(pygame.sprite.DirtySprite):
	layer = 0
	x = 0
	y = 0
	def __init__(self, y, x):
		pygame.sprite.DirtySprite.__init__(self)
		self.x = x;
		self.y = y;
		self.image = pygame.Surface((BLOCKSIZE, BLOCKSIZE))
		self.rect = pygame.Rect((x * BLOCKSIZE, y * BLOCKSIZE, BLOCKSIZE, BLOCKSIZE));
		self.image.fill(BEACHCOLOR)

class Structure(EventedSprite):
	def __init__(self):
		EventedSprite.__init__(self)
		self.tile = None
		self.ring = None
		self.health = 0
		self.max_health = 0 # this should be influenced by builder level
		self.height = 0 # this should be influenced by structure type
		self.habitation = 0 # this should be influenced by structure material?
		self.age = 0
		self.built = False
		self.world = World(pygame.display.get_surface().get_size())
		self.rendered = False

	def on_buildfinish(self, builder):
		print builder.name + " finished building " + self.__class__.__name__

	def build(self, builder, position):
		if self.time_to_build >= builder.time_building:
			self.health = builder.time_building
			self.max_health = self.time_to_build
			builder.time_building += builder.build_speed
		else:
			if self.rect != None and position != None:
				self.rect.topleft = position
			# determine vertical offset by height
			self.health = self.time_to_build
			self.max_health = self.time_to_build
			self.world.map.addStructure(self)
			self.orig_rect = pygame.Rect(self.rect)
			self.adjustToLayer()
			builder.finish_project()
			self.on_buildfinish(builder)

	def adjustToLayer(self):
		self.rect.top = self.rect.top - ((self.layer - 1) * 10)

	def update(self, events):
		EventedSprite.update(self, events)
		if self.health == 0:
			self.kill()
		self.debug_draw()

	def kill(self):
		self.world.map.tiles.get_at()
		EventedSprite.kill(self)


class JoiningStructure(Structure):
	def update(self, events):
		Structure.update(self, events)
		mask_hash = ['', '', '', '']
		mask_item = ''
		for structure in self.world.map.tiles.sprites():
			# check tile_position to ensure get adjacents
			if structure == self or not isinstance(structure, self.__class__):
				continue
			if structure.tile == None:
				print "No tile associated with structure"
				continue
			if structure.layer != self.layer:
				continue
			struct_x = structure.tile.x == self.tile.x
			struct_y = structure.tile.y == self.tile.y
			struct_y_rel = structure.tile.y - self.tile.y
			struct_x_rel = structure.tile.x - self.tile.x
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

class Pit(JoiningStructure):
	def __init__(self):
		Structure.__init__(self)
		self.height = 10
		self.map_set = 1
		self.states = load_sliced_sprites(self, 50, 50, 'tower_short.png')
		self.image = self.states[self.map_set][0]
		self.rect = pygame.Rect((0, 0, BLOCKSIZE, BLOCKSIZE))
		self.time_to_build = 300

	def adjustToLayer(self):
		self.rect.top = self.rect.top + ((self.layer - 1) * 10)


	def on_buildfinish(self, builder):
		builder.add_sand(self.health)
		print "Finished building pit +1 sand"

class Mound(JoiningStructure):
	def __init__(self):
		Structure.__init__(self)
		self.height = 10
		self.map_set = 0
		self.states = load_sliced_sprites(self, 50, 50, 'tower_short.png')
		self.image = self.states[0][0]
		self.rect = pygame.Rect((0, 0, BLOCKSIZE, BLOCKSIZE))
		self.time_to_build = 300

	def on_buildfinish(self, builder):
		builder.spend_sand(self.health)

class ArcherTower(Structure):
	sprite_file = "archer_tower.png"
	def __init__(self):
		Structure.__init__(self)
		self.height = 40
		self.map_set = 0
		self.states = load_sliced_sprites(self, 50, 50, self.sprite_file)
		self.image = self.states[0][0]
		self.rect = pygame.Rect((0,0, BLOCKSIZE, BLOCKSIZE))
		self.time_to_build = 300
		self.rate_of_fire = 10
		self.attack_power = 10
		self.cannon = trajectory.Cannon()
		self.cannon.world = self.world
		self.cannon.fireTrigger = pygame.FASTFIRE
		self.cannon.height = self.height
	def update(self, events):
		Structure.update(self, events)
		center = self.rect.center
		if hasattr(self, "orig_rect"):
			center = self.orig_rect.center
		self.cannon.setPosition(center)
		self.cannon.height = self.height
		for event in events:
			if event.type == pygame.KEYDOWN:
				self.cannon.shotRequested = True
		self.cannon.update(events)


class WizardTower(Structure):
	sprite_file = "mage_tower.png"
	def __init__(self):
		Structure.__init__(self)
		self.height = 40
		self.map_set = 0
		self.states = load_sliced_sprites(self, 50, 50, self.sprite_file)
		self.image = self.states[0][0]
		self.rect = pygame.Rect((0,0, BLOCKSIZE, BLOCKSIZE))
		self.time_to_build = 300
		self.rate_of_fire = 10
		self.attack_power = 10
		self.cannon = trajectory.Cannon()
		self.cannon.world = self.world
		self.cannon.fireTrigger = pygame.MEDFIRE
		self.cannon.height = self.height
	def update(self, events):
		Structure.update(self, events)
		center = self.rect.center
		if hasattr(self, "orig_rect"):
			center = self.orig_rect.center
		self.cannon.setPosition(center)
		self.cannon.height = self.height
		for event in events:
			if event.type == pygame.KEYDOWN:
				self.cannon.shotRequested = True
		self.cannon.update(events)


class BomberTower(Structure):
	sprite_file = "bomber_tower.png"
	def __init__(self):
		Structure.__init__(self)
		self.height = 40
		self.map_set = 0
		self.states = load_sliced_sprites(self, 50, 50, self.sprite_file)
		self.image = self.states[0][0]
		self.rect = pygame.Rect((0,0, BLOCKSIZE, BLOCKSIZE))
		self.time_to_build = 300
		self.rate_of_fire = 10
		self.attack_power = 10
		self.cannon = trajectory.Cannon()
		self.cannon.world = self.world
		self.cannon.fireTrigger = pygame.SLOWFIRE
	def update(self, events):
		Structure.update(self, events)
		center = self.rect.center
		if hasattr(self, "orig_rect"):
			center = self.orig_rect.center
		self.cannon.setPosition(center)
		self.cannon.height = self.height
		for event in events:
			if event.type == pygame.KEYDOWN:
				self.cannon.shotRequested = True
		self.cannon.update(events)

class Stairs(Structure):
	sprite_file = "stairs_left.png"
	def __init__(self):
		Structure.__init__(self)
		self.height = 40
		self.map_set = 0
		self.states = load_sliced_sprites(self, 50, 50, self.sprite_file)
		self.image = self.states[0][0]
		self.rect = pygame.Rect((0,0, BLOCKSIZE, BLOCKSIZE))
		self.time_to_build = 300
		self.rate_of_fire = 10
		self.attack_power = 10
