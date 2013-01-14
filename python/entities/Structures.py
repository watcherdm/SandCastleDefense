import pygame, sys
from base import EventedSprite, load_image

class Structure(EventedSprite):
	def __init__(self):
		EventedSprite.__init__(self)
		self.toughness = 0 # this should be influenced by builder level
		self.height = 0 # this should be influenced by structure type
		self.habiation = 0 # this should be influenced by structure material?
		self.power = 0 # attack power
		self.range = 0 # attack range
		self.age = 0

	def update(self, events):
		self.age += 1

	def on_click(self, event):
		"""report on damage etc and give upgrade options"""
		return

class World(EventedSprite):
	def __init__(self, name = "beach", grid_size = 64):
		EventedSprite.__init__(self)
		self.image, self.rect = load_image(name + '.jpg', -1)
		self.grid_size = grid_size
		self.selected = None
	def draw(self, surfaceObj):
		width = self.rect.width
		height = self.rect.height
		for i in range(0, height, self.grid_size):
			pygame.draw.line(self.image, (0,0,0), (0, i), (width, i))
		for i in range(0, width, self.grid_size):
			pygame.draw.line(self.image, (0,0,0), (i, 0), (i, height))
		surfaceObj.blit(self.image, (0, 0))

	def setSelected(self, sprite):
		if self.selected:
			self.selected.deselect() #this should only allow on selection at a time
		self.selected = sprite

	def on_click(self, event):
		if self.selected:
			self.selected.setDestination(pygame.mouse.get_pos())