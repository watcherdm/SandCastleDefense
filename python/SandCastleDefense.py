import pygame, sys
from characters.Characters import Jenai, Steve, BeachLady
from characters.SelectableGroup import SelectableGroup

pygame.init()
beach = pygame.image.load('beach.jpg')

size = (width, height) = beach.get_size()
speed = [2, 2]
black = 0, 0, 0
white = 255,255,255
screen = pygame.display.set_mode(size)
jenai = Jenai()
steve = Steve()
beachlady = BeachLady()
driftwood = pygame.image.load('driftwood_01.PNG')

selectablecharacters = SelectableGroup(jenai, steve)
allsprites = pygame.sprite.RenderPlain(jenai, beachlady, steve)
imoveablesprites = pygame.sprite.RenderPlain(beachlady)
screen.blit(beach, (0,0))
pygame.display.flip()
clock = pygame.time.Clock()

while 1:

	clock.tick(60)
	events = pygame.event.get()

	allsprites.update(events)
	screen.blit(beach, (0, 0))
	for i in range(0,height, 64):
		pygame.draw.line(beach, (0,0,0), (0, i), (width, i))
	for i in range(0,width, 64):
		pygame.draw.line(beach, (0,0,0), (i, 0), (i, height))
	screen.blit(driftwood, (640, 256))
	allsprites.draw(screen)
	pygame.display.flip()
