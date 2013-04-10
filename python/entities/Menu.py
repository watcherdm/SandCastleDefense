import pygame
from math import sin, cos, floor, radians
from base import *
from Structures import *

HIGHLIGHTCOLOR = pygame.Color(255, 255, 255)
ENERGYCOLOR = pygame.Color(0, 231, 255)
LIFECOLOR = pygame.Color(255, 0, 0)
BLOCKSIZE = 50

class Project:
	xp = 0
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
		self.last_tile = None
		self.tile = None

	def on_mousemove(self, event):
		pos = ((event.pos[0] / self.bs) * self.bs, (event.pos[1] / self.bs) * self.bs)
		top = pos[1] + 1
		left = pos[0] + 1
		bottom = self.bs - 2
		right = self.bs - 2
		self.block_rect = pygame.Rect((left, top, right, bottom))
		center = self.block_rect.center
		self.last_tile = self.tile
		self.tile = self.world.map.tiles.get_sprites_at(self.block_rect.center)[0]
		self.tile.make_dirty()
		if self.tile != None:
			for t in self.tile.get_surrounding():
				t.make_dirty()
			if self.block_rect:
				pygame.draw.rect(self.tile.image, HIGHLIGHTCOLOR, self.block_rect, 2)
			self.tile.make_dirty()
		for t in self.tile.get_surrounding():
			t.make_dirty()

	def update(self, events):
		EventedSurface.update(self, events)

	def draw(self, surf):
		tile = self.tile
		if self.last_tile != None:
			self.last_tile.make_dirty()


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
		self.world.map.tiles

	def on_click(self, event):
		print "SHOULD NEVER GET CALLED"
		return 1


class Ring(EventedSurface):
	value = 0
	radius = 50
	collide_method = "CIRC"
	def __init__(self, target = None):
		EventedSurface.__init__(self, (self.radius * 2, self.radius * 2))
		self.world = World(pygame.display.get_surface().get_size())
		self.target = target
		self.alpha = 128
		self.value = 0
		self.max = 0

	def get_angle(self):
		return (self.value * 360) / self.max

	def circle_point(self, angle):
		x = self.radius * cos(angle) + self.center[0]
		y = self.radius * sin(angle) + self.center[1]
		return (x, y)

	def update(self, events):
		EventedSurface.update(self, events)
		if self.target != None:
			self.rect = self.target.rect
			self.value = self.target.health
			self.max = self.target.max_health
			self.left = self.rect.left
			self.top = self.rect.top
			targetCenter = (self.rect.width / 2, self.rect.height / 2)
			self.center = (self.left + (targetCenter[0]),  self.top + (targetCenter[1]))
			self.radius = self.rect.width / 2
			tile = self.world.map.tiles.get_sprites_at(self.rect.center)[0]
			tile.make_dirty()
			for t in tile.get_surrounding():
				t.make_dirty()




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

	def on_click(self, event):
		if self.world.has_selected():
			if not self.world.get_selected().has_project():
				self.project = Project(self.project_type)
				self.project.new = True
				structure = self.project_structure()
				self.project.set_structure(structure)
				self.world.get_selected().set_project(self.project)


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
			if not hasattr(self, "center"):
				self.center = self.rect.center
			Button.draw(self, surf)
			self.image, rect = self.get_image()
			surf.blit(self.image, (self.rect.left, self.rect.top))


class FireTowerButton(StructureButton):
	project_type = 'firetower'
	project_structure = ArcherTower
	xp = 100
	def __init__(self):
		StructureButton.__init__(self, 'fire')


class IceTowerButton(StructureButton):
	project_type = 'icetower'
	project_structure = WizardTower
	xp = 100
	def __init__(self):
		StructureButton.__init__(self, 'ice')

class LightningTowerButton(StructureButton):
	project_type = 'lightningtower'
	project_structure = BomberTower
	xp = 100
	def __init__(self):
		StructureButton.__init__(self, 'lightning')

class PitButton(StructureButton):
	image_base = 'pit_'
	project_type = 'pit'
	project_structure = Pit
	def __init__(self):
		StructureButton.__init__(self, '')

	def on_mousedown(self, event):
		print "Mouse down"

	def on_mouseup(self, event):
		print "Mouse up"

class MoundButton(StructureButton):
	image_base = 'mound_'
	project_type = 'mound'
	project_structure = Mound
	def __init__(self):
		StructureButton.__init__(self, '')

class CharacterDisk(EventedSurface):
	def __init__(self):
		EventedSurface.__init__(self)

if __name__ == '__main__':
	# run some tests
	test = Button()
	menuring = MenuRing(test)
	menuring.update()
	menuring.add_button(test)
	test.draw(pygame.Surface((90,90)))