#! /usr/bin/python

import cProfile
import pygame, sys, random
from entities.base import *
from entities.Characters import *
from entities.Structures import *
from entities.Menu import *
from entities.map import *

version = '0.0.3'
SCREENHEIGHT = 600
SCREENWIDTH  = 1000
SCREENSIZE   = (SCREENWIDTH, SCREENHEIGHT)
BEACHCOLOR   = pygame.Color(255, 222, 73)
OCEANCOLOR   = pygame.Color(73, 130, 255)
WETSANDCOLOR = pygame.Color(94,82,69, 50)
WHITE        = pygame.Color(255,255,255)
BLACK        = pygame.Color(0,0,0)
RED          = pygame.Color(255, 0, 0)
BLUE         = pygame.Color(0, 0, 255)
GREEN        = pygame.Color(0, 255, 0)
critters = {
	"Crab": Crab,
	"Turtle": Turtle,
	"Snake": Snake,
	"Seagull": Seagull
}

def startGame():
	world = World(SCREENSIZE)
	world.debug = False
	world.state = 1
	world.currentLevel = 0

def exit():
	sys.exit()

callbacks = {
	"Start Game": startGame,
	"Exit": exit
}

class Control(EventedSprite):
	def __init__(self):
		EventedSprite.__init__(self)
		self.world = World(SCREENSIZE)

class Label(pygame.sprite.Sprite):
	def __init__(self, position = (0, 0), size = (100, 100), text = ""):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface(size)
		self.font = pygame.font.SysFont('arial', 20)
		self.rect = self.image.get_rect()
		self.text = text
		self.rect.topleft = position



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
		self.image.blit(label, self.rect)

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

class Pane(pygame.sprite.Sprite):
	def __init__(self, position = (0, 0), size = (40, 40)):
		pygame.sprite.Sprite.__init__(self)
		self.color = OCEANCOLOR
		self.left = position[0]
		self.top = position[1]
		self.width = size[0]
		self.height = size[1]
		self.labels = pygame.sprite.LayeredDirty()
		self.controls = pygame.sprite.OrderedUpdates()
		self.image = pygame.Surface((self.width, self.height))
		self.rect = pygame.Rect((self.top, self.left, self.width, self.height))

	def addControl(self, control):
		self.controls.add(control)

	def update(self, events):
		self.image.fill(self.color, (0,0, self.width, self.height))
		self.labels.update(events)
		self.controls.update(events)
		self.labels.draw(self.image)
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

def show_character_screen():
	world = World(SCREENSIZE)
	if world.cs == None:
		
		surf = CharacterScreen(world)

		pic = PicturePane((0,0), (300, 500), world.get_selected())
		pic.color = pygame.Color(255,0,0)
		# get pic of character
		info = Pane((0, 300), (700, 100))
		info.color = BEACHCOLOR
		# render text here for name, level, xp
		stats = Pane((100, 300), (700, 200))
		stats.color = WETSANDCOLOR
		# build and move speed, maybe health and magic as stats too?
		abilities = Pane((300, 300), (700, 200))
		abilities.color = BLUE
		# the abilities the characters has available
		aspects = Pane((500, 0),(900, 100))
		aspects.color = GREEN
		# currently selected and selectable aspects

		close = CloseButton((960,0), (40, 40))
		info.addControl(close)

		surf.addPane(pic)
		surf.addPane(info)
		surf.addPane(stats)
		surf.addPane(abilities)
		surf.addPane(aspects)
		world.cs = surf
	world.cs.active = True
	events = pygame.event.get()
	world.cs.update(events)
	world.cs.draw(world.sand)

def show_splash_screen():
	# start new game
	# continue game
	# exit
	world = World(SCREENSIZE)
	world.sand.fill(BEACHCOLOR)
	if world.cs != None:
		world.cs.active = False
	titlefont = pygame.font.SysFont('arial', 72)
	menufont = pygame.font.SysFont('arial', 24)
	title = titlefont.render("Sand Castle Defense", True, OCEANCOLOR)
	titleposition = (world.sand.get_width() / 2 - title.get_width() / 2, 100)
	world.sand.blit(title, titleposition)
	hitrects = []
	itemtop = 300
	for item in ['Start Game', 'Exit']:
		surf = menufont.render(item, True, OCEANCOLOR)
		itemleft = world.sand.get_width() / 2 - surf.get_width() / 2
		world.sand.blit(surf, (itemleft, itemtop))
		button = {
			"rect": pygame.Rect(itemleft, itemtop, surf.get_width(), surf.get_height()),
			"name": item
		}
		hitrects.append(button)
		itemtop += surf.get_height() * 2

	events = pygame.event.get()
	for event in events:
		if event.type == pygame.QUIT:
			exit()
		if event.type == pygame.MOUSEBUTTONDOWN:
			pos = pygame.mouse.get_pos()
			# see if they hit a box
			for button in hitrects:
				if button["rect"].collidepoint(pos):
					callbacks[button["name"]]()
					# do what the button says

def init():
	world = World(SCREENSIZE)	
	world.wave = get_line(world.i, WAVEPRECISION)
	world.wave_count = 0
	world.structures = pygame.sprite.OrderedUpdates()

	menuitems = {
		"fire": FireTowerButton(), 
		"ice": IceTowerButton(), 
		"lit": LightningTowerButton(), 
		"pit": PitButton(), 
		"mound": MoundButton()
	}

	world.aspects = {
		"wizard": Aspect("wizard", menuitems['ice']),
		"knight": Aspect("knight", menuitems['fire']),
		"pirate": Aspect("pirate", menuitems['lit'])
	}

	world.gameLevels = [
		{
			"tiles": 20,
			"waves": 4,
			"critters": ["Crab","Turtle"],
			"completed": 0
		},
		{
			"tiles": 40,
			"waves": 5,
			"critters": ["Crab", "Turtle", "Snake"],
			"completed": 0
		},
		{
			"tiles": 72,
			"waves": 6,
			"critters": ["Crab", "Turtle", "Snake", "Seagull"],
			"completed": 0
		}
	]

	world.levels = {
		"steve": {
			"lvl": {
				400: "knight",
				1200: "wizard",
				4000: "pirate"			
			},
			"obj": None
		},
		"jenai": {
			"lvl": {
				400: "wizard",
				1200: "pirate",
				4000: "knight"
			},
			"obj": None
		}
	}

	world.selectable = pygame.sprite.OrderedUpdates()
	world.hl_block = HighlightBlock()
	initCritters()
	loadPlayer(Jenai, (100, 100))
	loadPlayer(Steve, (100, 300))
	loadMusic()
	sandmap = Map(world, 'assets/maps/allsand.map')

	world.menuring = MenuRing()
	fast = 9
	med = 6
	slow = 3
	initialPosition = (400, 200)
	world.critter_level = 5
	pygame.FASTFIRE = 25
	pygame.MEDFIRE = 26
	pygame.SLOWFIRE = 27
	pygame.time.set_timer(pygame.FASTFIRE, 1000 / fast)
	pygame.time.set_timer(pygame.MEDFIRE, 1000 / med)
	pygame.time.set_timer(pygame.SLOWFIRE, 1000 / slow)
	goal = Goal()
	world.set_goal(goal)
	goal.set_position(initialPosition)
	goal.add_to_world()
	world.state = 2

def loadMusic():
	pygame.mixer.music.load('assets/sounds/music.wav')

def startMusic():
	if pygame.mixer.music.get_pos() > 0:
		pygame.mixer.music.unpause()
	else:
		pygame.mixer.music.play(100)

def pauseMusic():
	pygame.mixer.music.pause()

def stopMusic():
	pygame.mixer.music.pause()
	
def loadPlayer(cls, pos):
	world = World(SCREENSIZE)
	character = cls()
	character.rect.topleft = pos
	world.selectable.add(character)
	world.levels[character.name]["obj"] = character

def initCritters():
	world = World(SCREENSIZE)
	critters = pygame.sprite.OrderedUpdates()
	world.critters = critters


def runLevel(currentLevel):
	startMusic()
	world = World(SCREENSIZE)
	if world.cs != None:
		world.cs.active = False
	level = world.gameLevels[currentLevel]
	events = pygame.event.get()
	world.ocean.update(events)
	points_per_wave = (level["tiles"] / level["waves"])
	levels_in_play = (level["completed"] + 1)
	wave_points = (points_per_wave * levels_in_play)
	if len(world.structures.sprites()) >=  wave_points:
		#send wave
		points = wave_points + (len(world.map.tiles.get_sprites_from_layer(1)) / level["waves"])
		while points > 0:
			critterConstructor = critters[random.choice(level["critters"])]
			critter = critterConstructor(world.map.getRandomTile())
			world.critters.add(critter)
			points-= critter.cost
		for critter in world.critters:
			critter.update(events)
		level["completed"] += 1
	if level["completed"] > level["waves"] + 1:
		#level completed
		world.currentLevel += 1
		print "Level Completed, moving on"

		# start a sound
	
	world.hl_block.update(events)

	for name in world.levels:
		for level in world.levels[name]["lvl"]:
	 		if world.levels[name]["obj"].xp >= level:
	 			world.levels[name]["obj"].imagine_aspect(world.aspects[world.levels[name]["lvl"][level]])

	world.menuring.update(events)
	for m in world.menuring.get_buttons():
		m.update(events)
	world.selectable.update(events)
	world.critters.update(events)
	world.map.tiles.update(events)
	world.map.tiles.draw(world.sand)
	world.hl_block.draw(world.sand)
	# if WETSANDCOLOR.a > 0:
	# 	WETSANDCOLOR.a = WETSANDCOLOR.a - 1
	# 	oosurf = pygame.Surface((world.oldocean.right - world.oldocean.left, world.oldocean.bottom - world.oldocean.top))
	# 	oosurf.set_alpha(WETSANDCOLOR.a)
	# 	oosurf.fill(WETSANDCOLOR)
	# 	world.sand.blit(oosurf, (world.oldocean.left, world.oldocean.top))
	world.selectable.draw(world.sand)
	world.critters.draw(world.sand)
	world.update(events)
	world.ocean.draw(world.sand)
	for sprite in world.map.tiles.sprites():
		if hasattr(sprite, 'cannon'):
			sprite.cannon.draw(world.sand)
	world.menuring.draw(world.sand)

def initializeWorld():
	sand = pygame.display.set_mode(SCREENSIZE)
	world = World(SCREENSIZE)
	world.sand = sand
	world.i = 1
	images = load_sliced_sprites(100, 100, 'wavetip.png')
	wavetip = pygame.sprite.Sprite()
	wavetip.ani = images
	world.wavetip = wavetip
	world.ocean = Ocean()
	return world

def main():
	pygame.init()
	pygame.display.set_caption('Sand Castle Defense ' + version)
	sand = pygame.display.set_mode(SCREENSIZE)
	world = World(SCREENSIZE)
	world.sand = sand
	world.i = 1
	world.clock = pygame.time.Clock()
	initializeWorld()
	# print len(images)
	# print len(images[0])

	while True:
		if world.state == 0: #game start
			show_splash_screen()
		if world.state == 1: #initialize game
			init()
		if world.state == 2: #play level
			runLevel(world.currentLevel)
		if world.state == 3: #pause level
			stopMusic()
			show_character_screen()
		if world.state == 99:
			stopMusic()
			world = initializeWorld()
			show_splash_screen()

		pygame.display.flip()
		world.clock.tick(24)
		world.i+= 1

def build_wet_sand():
	return False

if __name__ == '__main__':
	main()
