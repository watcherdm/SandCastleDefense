import pygame
from base import World, load_image
from dimensions import *
from Menu import Control

class AbilityButton(Control):
	def __init__(self):
		Control.__init__(self)
		self.image, self.rect = load_image('ability_' + self.name + '.png', -1)

	def on_click(self, event):
		if not self in self.user.abilities:
			pass
		if self.user.xp > self.cost:
			self.user.abilities[self.name] = self
			self.user.xp -= self.cost


class Ability():
	def __init__(self, user = None):
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
		if len(self.targets) > 0 and self.active:
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

class Taunt(Ability):
	name = "taunt"
	timeoutTime = 100
	cooldownTime = 500
	targetRange = 150
	cost = 50
	def effect_tick(self, target, world):
		if not hasattr(target, "orig_target"):
			target.orig_target = target.target
		if target.target != self.user:
			target.orig_target = target.target
		target.target = self.user

	def get_targets(self):
		splash = pygame.sprite.Sprite()
		splash.rect = pygame.Rect(0, 0, self.targetRange * 2, self.targetRange * 2)
		splash.rect.center = self.user.rect.center
		splash.radius = self.targetRange
		splashed = pygame.sprite.spritecollide(splash, self.world.critters, False, pygame.sprite.collide_circle)
		return splashed

	def deactivate(self):
		Ability.deactivate(self)
		for target in self.targets:
			target.target = target.orig_target
