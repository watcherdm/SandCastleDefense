#! /usr/bin/python

import cProfile
import pygame, sys, random
from entities.base import *
from entities.Characters import *
from entities.Structures import *
from entities.Menu import *
from engines.wave import *
from entities.map import *

version = '0.0.2'
SCREENHEIGHT = 600
SCREENWIDTH = 1000
SCREENSIZE = (SCREENWIDTH, SCREENHEIGHT)
TIDELEVELS = (.5, 1, 1.5, 2, 3, 4, 6)
WAVELEVELS = (10, 20, 50, 100)
BEACHCOLOR = pygame.Color(255, 222, 73, 1)
OCEANCOLOR = pygame.Color(73, 130, 255)
WETSANDCOLOR = pygame.Color(94,82,69, 50)
WAVEPRECISION = 100
currentLevel = 0

g = {
	"world": None,
	"sand": None
}

def startGame():
	world = World(SCREENSIZE)
	world.state = 1

def exit():
	sys.exit()

callbacks = {
	"Start Game": startGame,
	"Exit": exit
}

def show_splash_screen():
	# start new game
	# continue game
	# exit
	world = World(SCREENSIZE)
	world.sand.fill(BEACHCOLOR)
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

	world.current_tide_level = TIDELEVELS[0]
	world.selectable = pygame.sprite.OrderedUpdates()
	world.hl_block = HighlightBlock()
	initCritters()
	world.oldocean = None
	world.ocean = None
	loadPlayer(Jenai, (100, 100))
	loadPlayer(Steve, (100, 300))
	loadMusic()
	sandmap = Map(world, 'maps/allsand.map')

	world.menuring = MenuRing()
	fast = 10
	med = 5
	slow = 2
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
	pygame.mixer.music.load('sounds/music.wav')
	pygame.mixer.music.play(100)

def stopMusic():
	pygame.mixer.music.stop()
	
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
	world = World(SCREENSIZE)
	world.map.dirtyTiles()
	events = pygame.event.get()
	#adjust tide
	if world.wave_count == len(world.wave) / 2:
		if len(world.critters.sprites()) < world.critter_level:
			critter = Crab(world.map.getRandomTile())
			world.critters.add(critter)
		for critter in world.critters:
			critter.update(events)
		# place some critters

	if world.wave_count >= len(world.wave):
		world.wave_count = 0
		world.wave = get_line(world.wave_count + 1, WAVEPRECISION)
		pygame.mixer.Sound("sounds/oceanwave.wav").play()
		# start a sound
	
	world.hl_block.update(events)

	world.ocean = build_ocean(world.wave[world.wave_count], world.current_tide_level)
	if world.oldocean == None or world.oldocean.top > world.ocean.top or WETSANDCOLOR.a == 0:
		world.oldocean = world.ocean
		WETSANDCOLOR.a = 255
	if (world.i % 3 == 0):
		world.wave_count += 1

	for name in world.levels:
		for level in world.levels[name]["lvl"]:
	 		if world.levels[name]["obj"].xp >= level:
	 			world.levels[name]["obj"].imagine_aspect(world.aspects[world.levels[name]["lvl"][level]])

	world.menuring.update(events)
	for m in world.menuring.get_buttons():
		m.update(events)
	world.map.tiles.update(events)
	world.selectable.update(events)
	world.critters.update(events)
	world.map.tiles.draw(world.sand)
	world.hl_block.draw(world.sand)
	if WETSANDCOLOR.a > 0:
		WETSANDCOLOR.a = WETSANDCOLOR.a - 1
		oosurf = pygame.Surface((world.oldocean.right - world.oldocean.left, world.oldocean.bottom - world.oldocean.top))
		oosurf.set_alpha(WETSANDCOLOR.a)
		oosurf.fill(WETSANDCOLOR)
		world.sand.blit(oosurf, (world.oldocean.left, world.oldocean.top))
	world.selectable.draw(world.sand)
	world.critters.draw(world.sand)
	world.update(events)
	for sprite in world.map.tiles.sprites():
		if hasattr(sprite, 'cannon'):
			sprite.cannon.draw(world.sand)
	world.sand.fill(OCEANCOLOR, world.ocean)
	world.menuring.draw(world.sand)

def initializeWorld():
	sand = pygame.display.set_mode(SCREENSIZE)
	world = World(SCREENSIZE)
	world.sand = sand
	world.i = 1
	world.clock = pygame.time.Clock()
	return world

def main():
	pygame.init()
	pygame.display.set_caption('Sand Castle Defense ' + version)
	sand = pygame.display.set_mode(SCREENSIZE)
	g["world"] = World(SCREENSIZE)
	world = g["world"]
	world.sand = sand
	world.i = 1
	world.clock = pygame.time.Clock()

	while True:
		if world.state == 0: #game start
			show_splash_screen()
		if world.state == 1: #initialize game
			init()
		if world.state == 2: #play level
			runLevel(currentLevel)
		if world.state == 3: #pause level
			showPause()
		if world.state == 99:
			stopMusic()
			world = initializeWorld()
			show_splash_screen()

		pygame.display.flip()
		world.clock.tick(60)
		world.i+= 1


def build_ocean(wave_point, tide_level=.5):
	oceanbase = 100
	oceanrange = 100
	waveheight = (oceanrange * tide_level) * (1 + wave_point)
	height = oceanbase + waveheight
	ocean = pygame.Rect((0, SCREENHEIGHT - height) + SCREENSIZE)
	return ocean

def build_wet_sand():
	return False

if __name__ == '__main__':
	main()
