import pygame
from math import sin, cos, floor, radians
from base import *

HIGHLIGHTCOLOR = pygame.Color('white')

class HighlightBlock(EventedSurface):
	def __init__(self):
		surf = pygame.display.get_surface()
		EventedSurface.__init__(self, surf.get_size())
		self.rect = self.get_rect()
		self.bs = 50
		self.block_rect = None

	def on_mousemove(self, event):
		pos = ((event.pos[0] / self.bs) * self.bs, (event.pos[1] / self.bs) * self.bs)
		top = pos[1]
		left = pos[0]
		bottom = self.bs
		right = self.bs
		self.block_rect = pygame.Rect((left, top, right, bottom))

	def draw(self, surf):
		if self.block_rect:
			pygame.draw.rect(surf, HIGHLIGHTCOLOR, self.block_rect, 3)


class Button(EventedSurface):
	def __init__(self):
		self.world = World(pygame.display.get_surface().get_size())
		self.radius = 16
		EventedSurface.__init__(self, (self.radius * 2, self.radius * 2))
		self.rect = self.get_rect()
		self.ring = None

	def set_center_position(self, pos):
		self.rect.center = [floor(x) for x in pos]

	def draw(self, surf):
		if self.ring == None:
			return
		if self.ring.is_active():
			pygame.draw.circle(surf, ENERGYCOLOR, self.rect.center, self.radius, 0)


	def on_click(self, event):
		print "TEST"
		return 1

ENERGYCOLOR = pygame.Color(0, 231, 255)


class MenuRing:
	angleSoFar = 0
	def __init__(self, target = None):
		self.world = World(pygame.display.get_surface().get_size())
		self.target = target
		self.buttons = []
		self.is_animating = True

	def is_active(self):
		return self.target != None

	def set_target(self, target):
		self.target = target;

	def update(self):
		if self.world.has_selected():
			self.target = self.world.get_selected()
		if self.target == None:
			return
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
			points = (degrees / count)
			angle = self.angleSoFar
			for button in self.buttons:
				button.set_center_position(self.button_center(radians(angle)))
				angle += points
			if self.angleSoFar == 360:
				self.angleSoFar = -1
			if self.is_animating:
				self.angleSoFar += 1

	def button_center(self, angle):
		x = self.radius * cos(angle) + self.center[0]
		y = self.radius * sin(angle) + self.center[1]
		return (x, y)

	def draw(self, surf):
		if self.target == None:
			return
		pygame.draw.circle(surf, ENERGYCOLOR, self.center, self.radius, 4)


	def add_button(self, button):
		button.ring = self
		self.buttons.append(button)

class StructureButton(Button):
	image_base = 'shovel_'
	extension = '.png'
	enabled = False

	def __init__(self, type):
		self.type = type
		self.image_base = type + '_'
		self.images = {
			'enabled': None,
			'disabled': None
		}
		Button.__init__(self)

	def on_mouseenter(self, event):
		self.enable()
		self.ring.is_animating = False

	def on_mousemove(self, event):
		self.enable()
		self.ring.is_animating = False

	def on_mouseout(self, event):
		self.disable()
		self.ring.is_animating = True

	def on_click(self, event):
		self.world.stop_event_propogation()
		print self.type + "Trench Tool Selected"
	
	def state(self):
		return 'enabled' if self.enabled == True else 'disabled'

	def enable(self):
		self.enabled = True

	def disable(self):
		self.enabled = False

	def get_image_path(self):
		return self.image_base + self.state() + self.extension

	def get_image(self):
		state = self.state()
		img = self.images[state]
		if img == None:
			self.images[state] = load_image(self.get_image_path(), -1)
		return self.images[state]

	def draw(self, surf):
		Button.draw(self, surf)
		self.image, rect = self.get_image()
		surf.blit(self.image, (self.rect.left, self.rect.top))


class FireTowerButton(StructureButton):
	def __init__(self):
		StructureButton.__init__(self, 'tower')

class IceTowerButton(StructureButton):
	def __init__(self):
		StructureButton.__init__(self, 'tower')

class LightningTowerButton(StructureButton):
	def __init__(self):
		StructureButton.__init__(self, 'tower')

class TrenchButton(StructureButton):

	def __init__(self):
		StructureButton.__init__(self, 'shovel')


if __name__ == '__main__':
	# run some tests
	test = Button()
	menuring = MenuRing(test)
	menuring.update()
	print menuring.button_center(90)
	menuring.add_button(test)
	test.draw(pygame.Surface((90,90)))