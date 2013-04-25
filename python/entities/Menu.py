import pygame
from math import sin, cos, floor, radians
from base import *
from Structures import *
from pallette import *
from dimensions import *

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
			if self.structure.can_build_at(pos):
				self.active = True
				self.position = ((pos[0] / BLOCKSIZE) * BLOCKSIZE, (pos[1] / BLOCKSIZE) * BLOCKSIZE)
				return True
			else:
				print "Can't build at ::"
				print pos

	def get_position(self):
		return self.position

	def set_structure(self, structure):
		self.structure = structure

	def get_structure(self):
		return self.structure

	def can_build_on(self, tile):
		return self.structure.can_build_on(tile)

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
		self.ghost = None
		self.image = pygame.Surface((BLOCKSIZE, BLOCKSIZE))

	def set_color(self, color):
		self._color = color

	def get_color(self):
		return self._color

	def update(self, events):
		pos = pygame.mouse.get_pos()
		pos = ((pos[0] / self.bs) * self.bs, (pos[1] / self.bs) * self.bs)
		top = pos[1]
		left = pos[0]
		bottom = self.bs
		right = self.bs
		self.block_rect = pygame.Rect((left, top, right, bottom))
		center = self.block_rect.center
		self.last_tile = self.tile
		self.tile = self.world.map.get_bottom_sprite_at(self.block_rect.center)
		EventedSurface.update(self, events)
		# determine if currently placing a project
		self.set_color(WHITE)
		if self.tile != None:
			self.rect = self.tile.rect
		if self.world.has_selected():
			if self.world.get_selected().has_project():
				if not self.world.get_selected().get_project().has_position():
					self.ghost = self.world.get_selected().get_project().structure
					tile = self.world.map.get_top_sprite_at(self.block_rect.center)
					if self.world.get_selected().get_project().can_build_on(tile):
						self.set_color(GREEN)
					else:
						self.set_color(RED)
				else:
					self.ghost = None
			else:
				self.ghost = None
		else:
			self.ghost = None
		self.alpha = 64

	def draw(self, surf):

		self.image.fill(self.get_color())
		if self.ghost != None:
			self.image.blit(self.ghost.image, (0,0))
		self.image.set_alpha(self.alpha)
		tile = self.tile
		if self.last_tile != None:
			self.last_tile.make_dirty()
		if self.block_rect:
			surf.blit(self.image, self.block_rect.topleft)



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
			tile = self.world.map.get_bottom_sprite_at(self.rect.center)
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
		self.add_button(PauseButton())

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
				self.project.xp = self.xp
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
	xp = 20
	def __init__(self):
		StructureButton.__init__(self, '')

class MoundButton(StructureButton):
	image_base = 'mound_'
	project_type = 'mound'
	project_structure = Mound
	xp = 20
	def __init__(self):
		StructureButton.__init__(self, '')

class PauseButton(StructureButton):
	image_base = 'pause_'
	project_type = 'pause'
	project_structure = None
	def __init__(self):
		StructureButton.__init__(self, '')

	def on_click(self, event):
		self.world.state = 3
		return

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


class Control(EventedSprite):
	def __init__(self):
		EventedSprite.__init__(self)
		self.world = World(SCREENSIZE)

class Label(pygame.sprite.Sprite):
	color = BLACK
	def __init__(self, position = (0, 0), size = (100, 100), targetAttr = "name"):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface(size)
		if not pygame.font.get_init():
			pygame.font.init()
		fontname = pygame.font.get_default_font()
		self.font = pygame.font.Font(fontname, 30)
		self.rect = pygame.Rect(position + size)
		self.attr = targetAttr
		self.rect.topleft = position
	
	def update(self, events):
		self.text = str(getattr(self.pane.target, self.attr))
		text = self.font.render(self.text, True, self.color)
		self.image = text

class CloseButton(Control):
	def __init__(self, position = (0, 0), size = (40, 40)):
		self.width = 40
		self.height = 40
		Control.__init__(self)
		pygame.font.init()
		self.font = pygame.font.SysFont('arial', 20)
		self.image = pygame.Surface(size)
		self.rect = self.image.get_rect()
		self.rect.topleft = position

	def update(self, events):
		Control.update(self, events)
		label = self.font.render('X', True, BLACK)
		self.image = label

	def on_click(self, event):
		self.world.state = 2

class AddButton(Control):
	width = 40
	height = 40
	# 5 px margin on all sides?
	def __init__(self, binding = None, pos = (0, 0)):
		self.binding = binding
		self.image = pygame.Surface((self.width, self.height))
		self.rect = pos + (self.width, self.height)
		Control.__init__(self)
		self.image.fill(GREEN, pygame.Rect(8, 16, 24, 8))
		self.image.fill(GREEN, pygame.Rect(16, 8, 8, 24))

class Pane(EventedSprite):
	target = None
	def __init__(self, position = (0, 0), size = (40, 40)):
		EventedSprite.__init__(self)
		self.color = OCEANCOLOR
		self.left = position[0]
		self.top = position[1]
		self.width = size[0]
		self.height = size[1]
		self.labels = pygame.sprite.OrderedUpdates()
		self.controls = pygame.sprite.OrderedUpdates()
		self.image = pygame.Surface((self.width, self.height))
		self.rect = pygame.Rect((self.top, self.left, self.width, self.height))

	def setTarget(self, target):
		self.target = target

	def addControl(self, control):
		control.pane = self
		self.controls.add(control)

	def addLabel(self, label):
		label.pane = self
		self.labels.add(label)

	def update(self, events):
		self.image.fill(self.color, (0,0, self.width, self.height))
		if len(self.labels.sprites()) > 0:
			print "Draw the " + str(len(self.labels.sprites())) + " labels"
			self.labels.update(events)
			self.labels.draw(self.image)
		if len(self.controls.sprites()) > 0:
			print "Draw the " + str(len(self.controls.sprites())) + " controls"
			self.controls.update(events)
			self.controls.draw(self.image)

class PicturePane(Pane):
	def __init__(self, position = (0, 0), size = (40, 40), target = None):
		Pane.__init__(self, position, size)
		self.target = target

	def update(self, events):
		Pane.update(self, events)
		if self.target != None:
			image = pygame.transform.scale(self.target.image, (300, 300))
			self.image.blit(image, (0, 100))
			self.target.update(events)

class CharacterScreen(pygame.sprite.Sprite):
	active = False
	def __init__(self, world):
		self.color = BLACK
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface(world.sand.get_size())
		self.rect = pygame.Rect(world.sand.get_rect())
		self.panes = pygame.sprite.OrderedUpdates()

	def setTarget(self, target):
		for pane in self.panes.sprites():
			pane.setTarget(target)

	def addPane(self, pane):
		self.panes.add(pane)

	def update(self, events):
		if self.active:
			self.panes.update(events)

	def draw(self, surf):
		if self.active:
			self.image.fill(self.color)
			self.panes.draw(self.image)
			surf.blit(self.image, self.rect)
