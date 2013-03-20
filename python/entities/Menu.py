import pygame
from math import sin, cos, floor, radians
from base import *
from Structures import *

HIGHLIGHTCOLOR = pygame.Color(255, 255, 255)
ENERGYCOLOR = pygame.Color(0, 231, 255)
LIFECOLOR = pygame.Color(255, 0, 0)
BLOCKSIZE = 50

class Project:
	def __init__(self, type = 'idle'):
		self.type = type
		self.position = None
		self.active = False
		self.structure = None

	def has_position(self):
		return self.position != None

	def set_position(self, pos = None):
		if pos == None:
			self.active = False
		else:
			self.active = True
		self.position = ((pos[0] / BLOCKSIZE) * BLOCKSIZE, (pos[1] / BLOCKSIZE) * BLOCKSIZE)

	def get_position(self):
		return self.position

	def set_structure(self, structure):
		self.structure = structure

	def get_structure(self):
		return self.structure

class HighlightBlock(EventedSurface):
	def __init__(self):
		self.world = World(pygame.display.get_surface().get_size())
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
		print "SHOULD NEVER GET CALLED"
		return 1


class Ring:
	value = 0
	def __init__(self, target = None):
		self.world = World(pygame.display.get_surface().get_size())
		self.target = target
		self.alpha = 128
		self.value = 0
		self.max = 0
		self.rect = None

	def get_angle(self):
		return (self.value * 360) / self.max

	def circle_point(self, angle):
		x = self.radius * cos(angle) + self.center[0]
		y = self.radius * sin(angle) + self.center[1]
		return (x, y)

	def update(self, events):
		if self.target != None:
			self.rect = self.target.rect
			self.value = self.target.health
			self.max = self.target.max_health
			self.left = self.rect.left
			self.top = self.rect.top
			targetCenter = (self.rect.width / 2, self.rect.height / 2)
			self.center = (self.left + (targetCenter[0]),  self.top + (targetCenter[1]))
			self.radius = self.rect.width / 2



class HealthRing(Ring):
	def draw(self, surf):
		if self.target == None or self.rect == None:
			return
		pygame.draw.circle(surf, pygame.Color('black'), self.center, self.radius, 4)
		pygame.draw.arc(surf, LIFECOLOR, self.rect, radians(270), radians(self.get_angle() - 270), 4)

	def update(self, events):
		if self.world.has_selected():
			self.target = self.world.get_selected()
		if self.target == None:
			return
		Ring.update(self, events)
		self.rect = self.rect.inflate(20, 20)
		self.radius = self.rect.width / 2


class StructureRing(Ring):
	def draw(self, surf):
		if self.target == None or self.rect == None:
			return
		pygame.draw.circle(surf, pygame.Color('black'), self.center, self.radius, 4)
		pygame.draw.arc(surf, LIFECOLOR, self.rect, radians(270), radians(self.get_angle()), 4)

	def update(self, events):
		if self.target == None:
			return
		Ring.update(self, events)
		self.rect = self.rect.inflate(20, 20)
		self.radius = self.rect.width / 2

class MenuRing(Ring):
	angleSoFar = 0
	def __init__(self, target = None):
		Ring.__init__(self, target)
		self.buttons = []
	
	def is_active(self):
		return self.target != None

	def set_target(self, target):
		self.empty()
		self.target = target
		self.add_target_buttons(target)

	def update_target_buttons(self):
		self.empty()
		self.add_target_buttons(self, self.target)

	def add_target_buttons(self, target):
		self.add_button(PitButton())
		if target.get_sand() > 0:
			self.add_button(MoundButton())
		if target.aspect != None:
			self.add_button(target.aspect.button)

	def update(self, events):
		selected = self.world.get_selected()
		if selected != self.target:
			self.set_target(selected)
		elif selected:
			self.update_buttons()
		Ring.update(self, events)
		if self.target == None:
			return
		self.radius = self.rect.width
		self.update_buttons()

	def update_buttons(self):
		degrees = 360
		count = len(self.buttons)
		if count > 0:
			points = (degrees / count)
			angle = self.angleSoFar
			for button in self.buttons:
				button.set_center_position(self.circle_point(radians(angle)))
				angle += points
			if self.angleSoFar == 360:
				self.angleSoFar = -1

	def draw(self, surf):
		if self.target == None:
			return
		pygame.draw.circle(surf, ENERGYCOLOR, self.center, self.radius, 4)
		for b in self.buttons:
			b.draw(surf)


	def add_button(self, button):
		button.ring = self
		self.buttons.append(button)

	def get_buttons(self):
		return self.buttons

	def empty(self):
		self.buttons = []

class StructureButton(Button):
	image_base = 'shovel_'
	extension = '.png'
	enabled = False

	def __init__(self, type):
		self.type = type
		if type != '':
			self.image_base = 'tower_'
		self.images = {
			'enabled': None,
			'disabled': None
		}
		Button.__init__(self)

	def on_mouseenter(self, event):
		self.enable()

	def on_mousemove(self, event):
		self.enable()

	def on_mouseover(self):
		self.enable()

	def on_mouseout(self, event):
		self.disable()

	def state(self):
		return 'enabled' if self.enabled == True else 'disabled'

	def enable(self):
		self.enabled = True

	def disable(self):
		self.enabled = False

	def get_image_path(self):
		prefix = self.type + '_' if self.state() == 'enabled' and self.type else ''
		return prefix + self.image_base + self.state() + self.extension

	def get_image(self):
		state = self.state()
		img = self.images[state]
		if img == None:
			self.images[state] = load_image(self.get_image_path(), -1)
		return self.images[state]

	def draw(self, surf):
		if self.ring.is_active():
			Button.draw(self, surf)
			self.image, rect = self.get_image()
			surf.blit(self.image, (self.rect.left, self.rect.top))


class FireTowerButton(StructureButton):
	def __init__(self):
		StructureButton.__init__(self, 'fire')

	def on_click(self, event):
		if self.world.has_selected():
			if not self.world.get_selected().has_project():
				self.project = Project('firetower')
				structure = ArcherTower()
				self.project.set_structure(structure)
				StructureButton.on_click(self, event)
				self.world.get_selected().set_project(self.project)

class IceTowerButton(StructureButton):
	def __init__(self):
		StructureButton.__init__(self, 'ice')

	def on_click(self, event):
		self.project = Project('icetower')
		structure = WizardTower()
		self.project.set_structure(structure)
		StructureButton.on_click(self, event)
		if self.world.has_selected():
			self.world.get_selected().set_project(self.project)

class LightningTowerButton(StructureButton):
	def __init__(self):
		StructureButton.__init__(self, 'lightning')

	def on_click(self, event):
		self.project = Project('lightningtower')
		structure = BomberTower()
		self.project.set_structure(structure)
		StructureButton.on_click(self, event)
		if self.world.has_selected():
			self.world.get_selected().set_project(self.project)

class PitButton(StructureButton):
	image_base = 'pit_'

	def __init__(self):
		StructureButton.__init__(self, '')

	def on_mousedown(self, event):
		print "Mouse down"

	def on_mouseup(self, event):
		print "Mouse up"

	def on_click(self, event):
		print "Starting Pit Project"
		self.project = Project('pit')
		self.project.set_structure(Pit())
		StructureButton.on_click(self, event)
		if self.world.has_selected():
			self.world.get_selected().set_project(self.project)

class MoundButton(StructureButton):
	image_base = 'mound_'

	def __init__(self):
		StructureButton.__init__(self, '')

	def on_click(self, event):
		self.project = Project('mound')
		self.project.set_structure(Mound())
		StructureButton.on_click(self, event)
		if self.world.has_selected():
			self.world.get_selected().set_project(self.project)

if __name__ == '__main__':
	# run some tests
	test = Button()
	menuring = MenuRing(test)
	menuring.update()
	print menuring.button_center(90)
	menuring.add_button(test)
	test.draw(pygame.Surface((90,90)))