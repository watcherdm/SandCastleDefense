import pygame, sys
from math import fabs
from base import *
from engines import trajectory

BLOCKSIZE = 50
BEACHCOLOR = pygame.Color(255, 222, 73, 1)

images = {
    
}

class Tile(pygame.sprite.DirtySprite):
	layer = 0
	x = 0
	y = 0
	underwater = False
	def __init__(self, y, x, world):
		self.structures = pygame.sprite.OrderedUpdates()
		pygame.sprite.DirtySprite.__init__(self)
		self.x = x;
		self.y = y;
		self.image = pygame.Surface((BLOCKSIZE, BLOCKSIZE))
		self.rect = pygame.Rect((x * BLOCKSIZE, y * BLOCKSIZE, BLOCKSIZE, BLOCKSIZE));
		self.draw()
		self.world = world

	def submerge(self):
		self.underwater = True

	def reveal(self):
		self.underwater = False

	def isUnderwater(self):
		return self.underwater

	def isStructure(self):
		return False

	def make_dirty(self):
		self.dirty = 1
		for sprite in self.structures.sprites():
			sprite.dirty = 1

	def draw(self):
		self.image.fill(BEACHCOLOR)

	def addStructure(self, structure):
		self.structures.add(structure)

	def get_surrounding(self):
		self.center = self.rect.center
		surrounding = []
		x = self.center[0] - BLOCKSIZE
		y = self.center[1] - BLOCKSIZE
		topleft = self.world.map.tiles.get_sprites_at((x,y))
		if len(topleft) > 0:
			surrounding.append(topleft[0])
		y = self.center[1]
		centerleft = self.world.map.tiles.get_sprites_at((x,y))
		if len(centerleft) > 0:
			surrounding.append(centerleft[0])
		y = self.center[1] + BLOCKSIZE
		bottomleft = self.world.map.tiles.get_sprites_at((x,y))
		if len(bottomleft) > 0:
			surrounding.append(bottomleft[0])
		x = self.center[0]
		y = self.center[1] - BLOCKSIZE
		topcenter = self.world.map.tiles.get_sprites_at((x,y))
		if len(topcenter) > 0:
			surrounding.append(topcenter[0])
		y = self.center[1] + BLOCKSIZE
		bottomcenter = self.world.map.tiles.get_sprites_at((x,y))
		if len(bottomcenter) > 0:
			surrounding.append(bottomcenter[0])
		x = self.center[0] + BLOCKSIZE
		y = self.center[1] - BLOCKSIZE
		topright = self.world.map.tiles.get_sprites_at((x,y))
		if len(topright) > 0:
			surrounding.append(topright[0])
		y = self.center[1]
		centerright = self.world.map.tiles.get_sprites_at((x,y))
		if len(centerright) > 0:
			surrounding.append(centerright[0])
		y = self.center[1] + BLOCKSIZE
		bottomright = self.world.map.tiles.get_sprites_at((x,y))
		if len(bottomright) > 0:
			surrounding.append(bottomright[0])
		return surrounding

class Structure(EventedSprite):
	w = 50
	h = 50
	height = 0
	layer = 0
	offset = {
		'x' : 0,
		'y' : 0
	}
	def isStructure(self):
		return True
	def takeDamage(self, dmg):
		self.health -= dmg

	def __init__(self):
		EventedSprite.__init__(self)
		if hasattr(images, self.sprite_file):
			self.states = images[self.sprite_file].copy()
		else:
			self.states = load_sliced_sprites(self.w, self.h, self.sprite_file)
			images[self.sprite_file] = self.states
		self.init_sprite()
		self.tile = None
		self.ring = None
		self.habitation = 0 # this should be influenced by structure material?
		self.age = 0
		self.built = False
		self.world = World(pygame.display.get_surface().get_size())
		self.rendered = False

	def init_sprite(self):
		self.image = self.states[0][0]
		self.rect = pygame.Rect((0,0, self.w, self.h))

	def can_build_at(self, pos):
		print pos
		build_on = self.world.map.get_top_sprite_at(pos)

		print build_on.__class__
		return self.can_build_on(build_on)

	def can_build_on(self, structure):
		return structure.__class__ in self.builds_on

	def apply_offset(self, position):
		return (position[0] + self.offset['x'], position[1] + self.offset['y'])

	def set_position(self, position):
		if self.rect != None and position != None:
			self.rect.topleft = position
		self.orig_rect = pygame.Rect(self.rect)
		self.rect.topleft = self.apply_offset(position)

	def add_to_world(self):
		self.world.map.addStructure(self)
		self.world.structures.add(self)

	def on_buildfinish(self, builder, position):
		self.set_position(position)
		self.add_to_world()
		self.adjustToLayer()
		self.health = self.max_health
		builder.finish_project()

	def build(self, builder, position):
		if self.time_to_build >= builder.time_building:
			self.health = builder.time_building
			self.max_health = self.time_to_build
			builder.time_building += builder.build_speed
		else:
			self.on_buildfinish(builder, position)

	def adjustToLayer(self):
		self.rect.top = self.orig_rect.top - ((self.layer - 1) * 10)

	def update(self, events):
		EventedSprite.update(self, events)
		self.adjustToLayer()
		if self.health < self.max_health:
			health_bar_x = 0
			health_bar_y = 50 - 6
			self.image.fill( pygame.Color('red'), (health_bar_x, health_bar_y, 50, 4))
			self.image.fill( pygame.Color('green'), (health_bar_x, health_bar_y, self.health * 50 / self.max_health , 4))
			if self.health <= 0:
				self.kill()

		if self.world.debug:
			self.debug_draw()

	def kill(self):
		pos = self.rect.center
		height = self.height
		EventedSprite.kill(self)
		sprites = self.world.map.tiles.get_sprites_at((pos[0], pos[1]))
		for sprite in sprites:
			if sprite.layer > 0:
				self.world.map.tiles.change_layer(sprite, sprite.layer - 1)
				sprite.height -= height

class Goal(Structure):
	builds_on = [Tile]
	sprite_file = "treasure.png"
	height = 30
	time_to_build = 500
	max_health = 500
	map_set = 0

	def __init__(self):
		Structure.__init__(self)
		self.health = self.max_health

	def kill(self):
		self.world.end_game()


class JoiningStructure(Structure):
	def __init__(self):
		Structure.__init__(self)
		self.last_structure_count = 0

	def add_to_world(self):
		self.world.map.addStructure(self)

	def update(self, events):
		Structure.update(self, events)
		sprites = self.world.map.tiles.sprites()
		i = 0
		if len(sprites) == self.last_structure_count:
			return "Nothing has changed"
		self.last_structure_count = len(sprites)
		mask_hash = ['', '', '', '']
		mask_item = ''
		for structure in sprites:
			i += 1
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
	builds_on = [Tile]
	sprite_file = 'tower_short.png'
	height = 10
	map_set = 1
	def __init__(self):
		self.builds_on.append(self.__class__) # stackable
		JoiningStructure.__init__(self)
		self.image = self.states[self.map_set][0]
		self.rect = pygame.Rect((0, 0, BLOCKSIZE, BLOCKSIZE))
		self.time_to_build = 300

	def takeDamage(self, dmg):
		self.health -= dmg * 0.2

	def isPit(self):
		return True

	def adjustToLayer(self):
		self.rect.top = self.orig_rect.top + ((self.layer - 1) * 10)


	def on_buildfinish(self, builder, position):
		JoiningStructure.on_buildfinish(self, builder, position)
		builder.add_sand(self.health)
		print "Finished building pit +1 sand"

class Mound(JoiningStructure):
	builds_on = [Tile]
	height = 10
	map_set = 0
	sprite_file = 'tower_short.png'
	def __init__(self):
		self.builds_on.append(self.__class__)
		JoiningStructure.__init__(self)
		self.image = self.states[0][0]
		self.rect = pygame.Rect((0, 0, BLOCKSIZE, BLOCKSIZE))
		self.time_to_build = 300

	def isPit(self):
		return False

	def on_buildfinish(self, builder, position):
		JoiningStructure.on_buildfinish(self, builder, position)
		builder.spend_sand(self.health)

class Tower(Structure):
	"""
	Tower abstract class handles cannon creation and range establishment
	"""
	h = 125
	offset = {
		'x': 0,
		'y': -75
	}
	builds_on = [Tile, Mound]
	def __init__(self):
		Structure.__init__(self)
		self.create_cannon()

	def isPit(self):
		return False

	def create_cannon(self):
		self.cannon = trajectory.Cannon()
		self.cannon.tower = self
		self.cannon.world = self.world
		self.cannon.height = self.height
		self.cannon.damage = self.damage
		self.cannon.fireTrigger = self.rof
		
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

class ArcherTower(Tower):
	rof = pygame.FASTFIRE
	sprite_file = "archer_tower.png"
	height = 30
	map_set = 0
	time_to_build = 200
	max_health = 200
	damage = 5

	def damage_enemy(self, target):
		target.health -= self.damage

class WizardTower(Tower):
	rof = pygame.MEDFIRE
	sprite_file = "mage_tower.png"
	height = 40
	map_set = 0
	time_to_build = 300
	max_health = 300
	damage = 5
	slowRatio = .50
	level = 1
	def upgrade(self):
		return False
		# if self.level == 1:
		# 	self.level = 2
		# 	self.slowRatio = 0.75
		# if self.level == 2:
		# 	self.level = 3
		# 	self.slowRatio = 0.5
	def damage_enemy(self, target):
		target.health -= self.damage
		if not "move" in target.modifiers:
			target.orig_move_speed = target.move_speed
			target.move_speed = target.move_speed * self.slowRatio
			target.modifiers.append("move")

class BomberTower(Tower):
	rof = pygame.SLOWFIRE
	sprite_file = "bomber_tower.png"
	height = 20
	map_set = 0
	time_to_build = 300
	max_health = 300
	damage = 5
	def damage_enemy(self, target):
		splash = pygame.sprite.Sprite()
		splash.rect = target.rect.copy()
		splash.rect.inflate(100,100)
		splash.radius = splash.rect.width / 2
		splashed = pygame.sprite.spritecollide(splash, self.world.critters, False, pygame.sprite.collide_circle)
		for i in splashed:
			i.health -= self.damage / 2
		target.health -= self.damage

class Stairs(Structure):
	sprite_file = "stairs_left.png"
	def __init__(self):
		Structure.__init__(self)
		self.height = 40
		self.map_set = 0
		self.states = load_sliced_sprites(50, 50, self.sprite_file)
		self.image = self.states[0][0]
		self.rect = pygame.Rect((0,0, BLOCKSIZE, BLOCKSIZE))
		self.time_to_build = 300
		self.rate_of_fire = 10
		self.attack_power = 10
