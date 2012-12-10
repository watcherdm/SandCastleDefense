import sys, pygame

class SelectableGroup(pygame.sprite.RenderUpdates):
	def checkSelected(self, pos):
		for sprite in self.sprites():
			sprite.checkSelected(pos)
