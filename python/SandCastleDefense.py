import pygame, sys
from characters.Jenai import Jenai

pygame.init()

# castles = [
# 	pygame.image.load('castle_01.PNG'),
# 	pygame.image.load('castle_02.PNG'),
# 	pygame.image.load('castle_03.PNG'),
# 	pygame.image.load('castle_04.PNG')
# ]


beach = pygame.image.load('beach.jpg')

size = (width, height) = beach.get_size()
speed = [2, 2]
black = 0, 0, 0
white = 255,255,255
screen = pygame.display.set_mode(size)
jenai = Jenai()

beachlady = pygame.image.load('beachlady_01.PNG')
driftwood = pygame.image.load('driftwood_01.PNG')
allsprites = pygame.sprite.RenderPlain(jenai)
screen.blit(beach, (0,0))
pygame.display.flip()
clock = pygame.time.Clock()
while 1:

	clock.tick(60)
	for event in pygame.event.get():
		if event.type == pygame.QUIT: sys.exit()

	mouseState = leftClick, middleClick, rightClick = pygame.mouse.get_pressed()

	if leftClick:
		mousePosition = pygame.mouse.get_pos()
		print mousePosition
		jenai.setDestination(mousePosition)
	allsprites.update()
	screen.blit(beach, (0, 0))
	for i in range(0,height, 64):
		pygame.draw.line(beach, (0,0,0), (0, i), (width, i))
	for i in range(0,width, 64):
		pygame.draw.line(beach, (0,0,0), (i, 0), (i, height))
	screen.blit(beachlady, (128, 192))
	screen.blit(driftwood, (640, 256))
	allsprites.draw(screen)
	pygame.display.flip()

