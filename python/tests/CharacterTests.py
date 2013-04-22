from entities.base import * 
from entities.map import *
from entities.Characters import *
import pygame
import sys

SCREENSIZE = (400, 400)

class CharacterTests():
	def test(self):
		pygame.init()
		pygame.display.set_caption('Character Test Harness')
		sand = pygame.display.set_mode(SCREENSIZE)
		world = World(SCREENSIZE)	
		characters = pygame.sprite.OrderedUpdates()
		jenai = Jenai((0,0))
		steve = Steve((50, 0))
		crab = Crab((100, 0))
		turtle = Turtle((116,0))
		snake = Snake((148, 0))
		seagull = Seagull((196, 0))
		characters.add(jenai, steve, crab, turtle, snake, seagull)
		sandmap = Map(world, 'assets/maps/allsand.map')
		while True:
			sand.fill(BEACHCOLOR)
			events = pygame.event.get()
			for e in events:
				if e.type == pygame.KEYDOWN:
					if e.key == 275:
						jenai.moving = True
						steve.moving = True
						crab.moving = True
						turtle.moving = True
						snake.moving = True
					else:
						jenai.moving = False
						steve.moving = False
						crab.moving = False
						turtle.moving = False
						snake.moving = False
					if e.key == 274:
						jenai.attacking = False
						steve.attacking = False
						crab.attacking = False
						turtle.attacking = False
						snake.attacking = False
					print e.key
			characters.update(events)
			characters.draw(sand)
			pygame.display.flip()
			world.clock.tick(60)
			world.i+= 1





if __name__ == "__main__":
	CharacterTests().test()