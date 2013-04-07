import pygame, sys
from base import World
from Structures import Tile
import random
# map engine
BEACHCOLOR = pygame.Color(255, 222, 73, 1)
BLOCKSIZE = 50

class Map:
	def __init__(self, world, map, tiles = None):
		self.world = world
		world.map = self
		l = [line.strip() for line in open(map).readlines()]
		l1 = len(l[0])
		rol = range(len(l))
		self.map = []
		self.tiles = pygame.sprite.LayeredDirty()

		for j in rol:
			self.map.append([None] * l1)
		for j in rol:
			for i in range(l1):
				self.map[j][i] = Tile(j, i, world)
				self.tiles.add(self.map[j][i])

	def draw(self, surf):
		self.tiles.draw(surf)

	def dirtyTiles(self):
		for sprite in self.tiles.sprites():
			sprite.dirty = 1

	def addStructure(self, structure):
		rect = structure.rect
		if hasattr(structure, 'orig_rect'):
			rect = structure.orig_rect
		sprites = self.tiles.get_sprites_at(rect.center)
		layer = len(sprites)
		if layer > 6:
			raise "Cannot build higher than 6 layers"
		tile = sprites[0]
		for sprite in sprites[1:]:
			sprite.dirty = 1
			if hasattr(sprite, 'height'):
				structure.height += sprite.height
		self.tiles.add(structure, layer = layer)
		structure.tile = tile
		structure.tile.addStructure(structure)
		structure.layer = layer

	def getRandomTile(self):
		row = random.choice(self.map)
		tile = random.choice(row)
		return tile.rect.topleft