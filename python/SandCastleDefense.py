#! /usr/bin/python

import pygame, sys, random
from entities.base import *
from entities.Characters import *
from entities.Structures import *
from entities.Menu import *
from engines.wave import *

version = '0.0.1'
SCREENHEIGHT = 600
SCREENWIDTH = 1000
SCREENSIZE = (SCREENWIDTH, SCREENHEIGHT)
TIDELEVELS = (.5, 1, 1.5, 2, 3, 4, 6)
WAVELEVELS = (10, 20, 50, 100)
BEACHCOLOR = pygame.Color(255, 222, 73, 1)
OCEANCOLOR = pygame.Color(73, 130, 255)
WETSANDCOLOR = pygame.Color(94,82,69, 50)
WAVEPRECISION = 100
def main():
	pygame.init()
	world = World(SCREENSIZE)
	pygame.mixer.music.load('sounds/oceanwave.wav')
	pygame.mixer.music.play(100)
	pygame.display.set_caption('Sand Castle Defense ' + version)
	current_tide_level = TIDELEVELS[0]

	sand = pygame.display.set_mode(SCREENSIZE)


	speed = [2, 2]

	jenai = Jenai()

	# TODO: get player positions from map
	jenai.rect.top = 100
	jenai.rect.left = 100

	steve = Steve()
	# TODO: get player positions from map
	steve.rect.top = 100
	steve.rect.left = 300

	selectable = pygame.sprite.OrderedUpdates()
	structures = pygame.sprite.OrderedUpdates()
	selectable.add(jenai, steve)
	oldocean = None

	world.structures = structures

	menuitems = FireTowerButton(), IceTowerButton(), LightningTowerButton(), TrenchButton(), TrenchButton()

	hl_block = HighlightBlock()

	clock = pygame.time.Clock()

	i = 1
	wave = get_line(i, WAVEPRECISION)
	wave_count = 0
	ocean = None
	menuring = MenuRing()
	for m in menuitems:
		menuring.add_button(m)

	healthring = HealthRing()

	while True:
		events = pygame.event.get()
		if i % 100 == 0:
			if random.randint(0,100) % 2 == 0:
				current_tide_level += .01
			else:
				current_tide_level -= .01

		if wave_count >= len(wave):
			wave_count = 0
			wave = get_line(wave_count + 1, WAVEPRECISION)
		
		hl_block.update(events)
		sand.fill(BEACHCOLOR)


		ocean = build_ocean(wave[wave_count], current_tide_level)
		if oldocean == None or oldocean.top > ocean.top or WETSANDCOLOR.a == 0:
			oldocean = ocean
			WETSANDCOLOR.a = 255
		hl_block.draw(sand)
		if (i % 3 == 0):
			wave_count += 1

		if WETSANDCOLOR.a > 0:
			WETSANDCOLOR.a = WETSANDCOLOR.a - 1
			oosurf = pygame.Surface((oldocean.right - oldocean.left, oldocean.bottom - oldocean.top))
			oosurf.set_alpha(WETSANDCOLOR.a)
			oosurf.fill(WETSANDCOLOR)
			sand.blit(oosurf, (oldocean.left, oldocean.top))

		menuring.update(events)
		healthring.update(events)
		for m in menuitems:
			m.update(events)
		structures.update(events)
		selectable.update(events)
		structures.draw(sand)
		for structure in structures:
			if structure.ring != None:
				structure.ring.draw(sand)
		selectable.draw(sand)
		world.update(events)
		sand.fill(OCEANCOLOR, ocean)
		menuring.draw(sand)
		healthring.draw(sand)

		pygame.display.flip()
		clock.tick(60)
		i+= 1

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
