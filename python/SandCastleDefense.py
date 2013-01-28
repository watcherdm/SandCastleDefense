import pygame, sys, random
from entities.Characters import *
from entities.Structures import *
from entities.Menu import *
from engines.wave import *

version = '0.0.0'
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
	pygame.mixer.music.load('sounds/oceanwave.wav')
	pygame.mixer.music.play(100)
	pygame.display.set_caption('Sand Castle Defense ' + version)
	current_tide_level = TIDELEVELS[0]

	sand = pygame.display.set_mode(SCREENSIZE)


	speed = [2, 2]

	jenai = Jenai()

	selectable = pygame.sprite.OrderedUpdates(jenai)
	oldocean = None

	#testing
	selectable = build_castle(selectable)

	menu = pygame.sprite.RenderPlain(FireTowerButton(), IceTowerButton(), LightningTowerButton())

	clock = pygame.time.Clock()

	i = 1
	wave = get_line(i, WAVEPRECISION)
	wave_count = 0
	ocean = None
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
			
		sand.fill(BEACHCOLOR)
		selectable.update(events)
		selectable.draw(sand)
		menu.draw(sand)

		ocean = build_ocean(wave[wave_count], current_tide_level)
		if oldocean == None or oldocean.top > ocean.top or WETSANDCOLOR.a == 0:
			oldocean = ocean
			WETSANDCOLOR.a = 255

		if (i % 3 == 0):
			wave_count += 1

		if WETSANDCOLOR.a > 0:
			WETSANDCOLOR.a = WETSANDCOLOR.a - 1
			oosurf = pygame.Surface((oldocean.right - oldocean.left, oldocean.bottom - oldocean.top))
			oosurf.set_alpha(WETSANDCOLOR.a)
			oosurf.fill(WETSANDCOLOR)
			sand.blit(oosurf, (oldocean.left, oldocean.top))

		sand.fill(OCEANCOLOR, ocean)
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
	

def build_castle(group):
	top = 0
	left = 200
	right = 0
	for i in range(0, 10):
		if i == 0 or i == 9:
			wall = TowerSegment()
		else:
			wall = WallSegment()
		wall.rect.topleft = (left, top)
		left += wall.rect.width
		group.add(wall)
	right = left - 50
	left = 200
	top += 50
	for i in range(0, 5):
		lwall = WallSegment(1)
		rwall = WallSegment(1)
		lwall.rect.topleft = (left, top)
		rwall.rect.topleft = (right, top)
		top += 50
		group.add(lwall, rwall)
	for i in range(0, 10):
		if i == 0 or i == 9:
			wall = TowerSegment()
		else:
			wall = WallSegment()
		wall.rect.topleft = (left, top)
		left += wall.rect.width
		group.add(wall)
	return group

if __name__ == '__main__':
	main()