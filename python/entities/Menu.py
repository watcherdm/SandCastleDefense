import pygame
from math import sin, cos, floor
from base import *

class Button(EventedSurface):
	def __init__(self):
		self.radius = 12
		EventedSurface.__init__(self, (self.radius * 2, self.radius * 2))
		self.rect = self.get_rect()

	def set_center_position(self, pos):
		self.rect.center = [floor(x) for x in pos]

	def draw(self, surf):
		pygame.draw.circle(surf, ENERGYCOLOR, self.rect.center, self.radius, 0)

	def on_click(self, event):
		print "TEST"
		return 1

ENERGYCOLOR = pygame.Color(0, 231, 255)

class MenuRing:
	def __init__(self, target):
		self.target = target
		self.buttons = []

	def update(self):
		self.left = self.target.rect.left
		self.top = self.target.rect.top
		targetCenter = (self.target.rect.width / 2, self.target.rect.height / 2)
		self.center = (self.left + (targetCenter[0]),  self.top + (targetCenter[1]))
		self.radius = self.target.rect.width
		self.update_buttons()

	def update_buttons(self):
		degrees = 360
		count = len(self.buttons)
		if count > 0:
			radians = (degrees / count) * 180
			angle = 0
			for button in self.buttons:
				button.set_center_position(self.button_center(angle))
				angle += radians 


	def button_center(self, angle):
		x = self.radius * cos(angle) + self.center[0]
		y = self.radius * sin(angle) + self.center[1]
		return (x, y)

	def draw(self, surf):
		pygame.draw.circle(surf, ENERGYCOLOR, self.center, self.radius, 4)


	def add_button(self, button):
		self.buttons.append(button)

class StructureButton(Button):
	def __init__(self, type):
		Button.__init__(self)

class FireTowerButton(StructureButton):
	def __init__(self):
		StructureButton.__init__(self, 'FireTower')
		self.rect.left = 300

	def on_click(event):
		print "Fire Tower Selected"

class IceTowerButton(StructureButton):
	def __init__(self):
		StructureButton.__init__(self, 'IceTower')
		self.rect.left = 330

	def on_click(event):
		print "Ice Tower Selected"

class LightningTowerButton(StructureButton):
	def __init__(self):
		StructureButton.__init__(self, 'LightningTower')
		self.rect.left = 360

	def on_click(event):
		print "Lightning Tower Selected"

class TrenchButton(StructureButton):
	def __init__(self):
		StructureButton.__init__(self, 'Trench')

if __name__ == '__main__':
	# run some tests
	test = Button()
	menuring = MenuRing(test)
	menuring.update()
	print menuring.button_center(90)
	menuring.add_button(test)
	test.draw(pygame.Surface((90,90)))