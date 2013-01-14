import pygame, sys
from entities.Characters import Jenai, Steve, BeachLady
from entities.Structures import World
from entities.Menu import *

pygame.init()

beach = World('beach')

size = (width, height) = beach.image.get_size()
speed = [2, 2]
black = 0, 0, 0
white = 255,255,255
screen = pygame.display.set_mode(size)
jenai = Jenai()
beachlady = BeachLady()
driftwood = pygame.image.load('driftwood_01.PNG')
background = pygame.sprite.RenderPlain(beach)
menu = pygame.sprite.RenderPlain(FireTowerButton(), IceTowerButton(), LightningTowerButton())
selectable = pygame.sprite.RenderPlain(jenai)
imoveablesprites = pygame.sprite.RenderPlain(beachlady)
pygame.display.flip()
clock = pygame.time.Clock()

while 1:

	clock.tick(60)
	events = pygame.event.get()

	background.draw(screen)
	selectable.update(events)
	for sprite in selectable:
		if sprite.selected:
			beach.setSelected(sprite)
	selectable.draw(screen)
	imoveablesprites.draw(screen)
	background.update(events)	
	screen.blit(driftwood, (640, 256))
	pygame.display.flip()
