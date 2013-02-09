import os, sys, pygame, glob
from base import *


BLOCKSIZE = 50

class Character(EventedSprite):
    def __init__(self, name = None, position = (0,0)):
        self.direction = 1
        self.max_health = 500
        self.health = 200
        EventedSprite.__init__(self) #call Sprite intializer
        self.name = name
        self.ani_speed_init = 30
        self.ani_speed = self.ani_speed_init
        self.ani_pos = 0
        self.ani = load_sliced_sprites(self, BLOCKSIZE, BLOCKSIZE, 'walk/' + self.name + '_0.png')
        self.ani_max = len(self.ani[0]) - 1
        self.image = self.ani[0][self.ani_pos]
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        self.time_building = 0

    def face_direction(self):
        if self.direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)


    def update(self, events):
        self.ani_speed -= 1
        if self.ani_speed == 0:
            self.ani_speed = self.ani_speed_init
            self.ani_pos += 1
            if self.ani_pos > self.ani_max:
                self.ani_pos = 0

        self.checkState(events)
        if self.moving:
            self.image = self.ani[1][self.ani_pos]
            self._walk()
        elif self.building:
            self.image = self.ani[2][self.ani_pos]
            position = self.project.get_position()
            structure = self.project.get_structure()
            structure.build(self, position)
        else:
            if self.health < self.max_health:
                self.health += 0.1
            self.image = self.ani[0][self.ani_pos]
        self.face_direction()

    def finish_project(self):
        self.time_building = 0
        self.building = False
        self.project.set_structure(None)
        self.set_project(None)
                
class SelectableCharacter(Character):
    "A selectable controllable character"
    def __init__(self, name, position = (10,10)):
        Character.__init__(self, name, position)
        screen = pygame.display.get_surface()
        self.world = World(screen.get_size())
        self.destinations = []
        self.project = None
        self.area = screen.get_rect()
        self.moving = False
        self.building = False
        self.stepSize = 1
        self.selected = False
        self.build_speed = 1

    def _walk(self):
        current_destination = self.destinations[0]

        distance = fromLeft, fromTop = cmp(current_destination[0] - self.rect.left, 0), cmp(current_destination[1] - self.rect.top, 0)

        if self.rect.left == current_destination[0]:
            fromLeft = 0
        if self.rect.top == current_destination[1]:
            fromTop = 0

        if fromLeft == 0 and fromTop == 0:
            self.ani_speed_init = 30
            self.moving = False
            self.destinations = []
            # you reached the destination, now build if you have a project
            if self.project != None:
                self.building = True

        movePosition = fromLeft, fromTop

        self.direction = fromLeft

        newpos = self.rect.move(movePosition)
        self.rect = newpos

    def select(self):
        self.selected = True
        self.world.set_selected(self)

    def deselect(self):
        self.selected = False
        self.world.set_selected(None)

    def set_destination(self, position):
        if not self.building:
            self.ani_speed_init = 10
            self.moving = True
            self.destinations.append(((position[0] / BLOCKSIZE) * BLOCKSIZE, (position[1] / BLOCKSIZE) * BLOCKSIZE))

    def has_project(self):
        return self.project != None

    def set_project(self, project):
        self.project = project

    def on_click(self, event):
        self.select()
        print self.name + " selected"

    def selected_update(self, event):
        if not self.world._supress:
            if self.has_project() and not self.project.has_position():
                self.project.set_position(event.pos)
            elif not self.building:
                self.set_destination(event.pos)

class Jenai(SelectableCharacter):
    def __init__(self):
        SelectableCharacter.__init__(self, 'jenai', (0,0))
        self.health = 200
        self.max_health = 200
        self.build_speed = 1.25

class Steve(SelectableCharacter):
    def __init__(self):
        SelectableCharacter.__init__(self, 'steve', (0, 128))
        self.health = 200
        self.max_health = 200
        self.build_speed = .75