import pygame, sys
from characters.Characters import Jenai, Steve, BeachLady
from characters.SelectableGroup import SelectableGroup
from structures.Structures import World

pygame.init()
beach = World('beach')

size = (width, height) = beach.image.get_size()
speed = [2, 2]
black = 0, 0, 0
white = 255,255,255
screen = pygame.display.set_mode(size)
jenai = Jenai()
steve = Steve()
beachlady = BeachLady()
driftwood = pygame.image.load('driftwood_01.PNG')

selectablecharacters = SelectableGroup(jenai, steve)
allsprites = pygame.sprite.RenderPlain(jenai, steve, beachlady)
imoveablesprites = pygame.sprite.RenderPlain(beachlady)
pygame.display.flip()
clock = pygame.time.Clock()

while 1:

	clock.tick(60)
	events = pygame.event.get()

	beach.draw(screen)
	allsprites.update(events)
	allsprites.draw(screen)
	
	screen.blit(driftwood, (640, 256))
	pygame.display.flip()
