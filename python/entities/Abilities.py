import pygame
from base import World
import dimensions

class Ability(pygame.sprite.Sprite):
	def __init__(self, user = None, ):
		pygame.sprite.Sprite.__init__(self)
		self.world = World(SCREENSIZE)
		self.targets = []
		self.user = user
		self.state = "ready"
		self.active = False
		self.params = {
			"level": 0
		}
		self.timeoutTime = 0
		self.cooldownTime = 1000
		self.timeSinceCast = 0

	def cooldown(self, t):
		if t > self.cooldownTime and self.state == "cooling":
			self.state = "ready"

	def timeout(self, t):
		if self.active and t > self.timeoutTime:
			self.active = False

	def effect(self, world):
		if len(self.targets) > 0:
			for target in self.targets:
				self.effect_tick(self, target, world)

	def effect_tick(self, target, world):
		target.health -= 1

	def activate(self):
		self.timeSinceCast = 0
		self.targets = self.get_targets()
		self.active = True
		self.state = "cooling"

	def deactivate(self):
		self.targets = []
		self.active = False

	def update(self, events):
		self.timeSinceCast += 1
		if self.active:
			self.effect(self.world)
		self.timeout(self.timeSinceCast)
		self.cooldown(self.timeSinceCast)
