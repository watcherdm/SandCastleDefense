import os, sys, pygame, glob
from base import EventedSprite, load_image

class Character(EventedSprite):
    def __init__(self, name = None, position = (0,0)):
        if not name: raise 1
        EventedSprite.__init__(self) #call Sprite intializer
        self.name = name
        self.ani_speed_init = 10
        self.ani_speed = self.ani_speed_init
        self.ani = glob.glob("walk/" + self.name + "*.png")
        self.ani.sort()
        self.ani_pos = 0
        self.ani_max = len(self.ani) - 1
        self.image = pygame.image.load(self.ani[self.ani_pos])
        self.image = pygame.transform.scale(self.image, (50,50))
        self.rect = self.image.get_rect()
        self.rect.topleft = position

    def update(self, events):
        self.ani_speed -= 1
        if self.ani_speed == 0:
            self.ani_speed = self.ani_speed_init
            self.ani_pos += 1
            if self.ani_pos > self.ani_max:
                self.ani_pos = 0

        self.checkState(events)
        if self.moving:
            self.image = pygame.image.load(self.ani[self.ani_pos])
            self.image = pygame.transform.scale(self.image, (50, 50))
            self._walk()

class SelectableCharacter(Character):
    "A selectable controllable character"
    def __init__(self, name, position = (10,10)):
        Character.__init__(self, name, position)
        screen = pygame.display.get_surface()
        self.destinations = []
        self.structures = []
        self.area = screen.get_rect()
        self.moving = False
        self.building = False
        self.stepSize = 1
        self.selected = False

    def _walk(self):
        current_destination = self.destinations[0];
        if  not current_destination:
            print "removing the current destination"
            self.moving = False
            self.destinations.remove(current_destination)

        distance = fromLeft, fromTop = cmp(current_destination[0] - self.rect.left, 0), cmp(current_destination[1] - self.rect.top, 0)

        if self.rect.left == current_destination[0]:
            fromLeft = 0
        if self.rect.top == current_destination[1]:
            fromTop = 0

        if fromLeft == 0 and fromTop == 0:
            self.moving = False
            self.destinations.remove(current_destination)

        movePosition = fromLeft, fromTop

        if (movePosition == (0, 0)):
            self.direction = None
        elif (movePosition == (1, 0)):
            self.direction = 'right'
        elif (movePosition == (0, 1)):
            self.direction = 'down'
        elif (movePosition == (-1, 0)):
            self.direction = 'left'
        elif (movePosition == (0, -1)):
            self.direction = 'up'

        newpos = self.rect.move(movePosition)
        self.rect = newpos

    def select(self):
        self.selected = True

    def deselect(self):
        self.selected = False

    def setDestination(self, position):
        self.moving = True
        self.destinations.append(((position[0] / 64) * 64, (position[1] / 64) * 64))

    def setProject(self, structure):
        self.building = True
        self.structures.append(structure)

    def on_click(self, event):
        self.select()
        print self.name + " selected"

class Jenai(SelectableCharacter):
    def __init__(self):
        SelectableCharacter.__init__(self, 'jenai', (0,0))

class Steve(SelectableCharacter):
    def __init__(self):
        SelectableCharacter.__init__(self, 'steve', (0, 128))