import pygame, sys
from base import World
from Structures import Tile
# map engine
BEACHCOLOR = pygame.Color(255, 222, 73, 1)

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
				self.map[j][i] = Tile(j, i)
				self.tiles.add(self.map[j][i])

	def draw(self, surf):
		self.tiles.draw(surf)

	def dirtyTiles(self):
		for sprite in self.tiles.sprites():
			sprite.dirty = 1

	def addStructure(self, structure):
		sprites = self.tiles.get_sprites_at(structure.rect.center)
		layer = len(sprites)
		if layer > 6:
			raise "Cannot build higher than 6 layers"
		tile = sprites[0]
		for sprite in sprites:
			sprite.dirty = 1
		self.tiles.add(structure, layer = layer)
		structure.tile = tile
		structure.layer = layer