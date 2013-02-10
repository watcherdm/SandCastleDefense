import pygame, sys
from base import World
from Structures import Tile
# map engine

class Map:
	def __init__(self, map, tiles):
		self.world = World(pygame.display.get_surface().get_size())
		l = [line.strip() for line in open(map).readlines()]
        self.map = [[None]*len(l[0]) for j in range(len(l))]
        for i in range(len(l[0])):
            for j in range(len(l)):
                tile = l[j][i]
                self.world.tiles
