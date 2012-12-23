import pygame, sys
from pygame.local import *

class Structure(pygame.sprites.Sprite):
	def __init__(self):
		self.toughness = 0 # this should be influenced by builder level
		self.height = 0 # this should be influenced by structure type
		self.habiation = 0 # this should be influenced by structure material?
		self.power = 0 # attack power
		self.range = 0 # attack range

