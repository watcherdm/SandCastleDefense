import os, sys, pygame, glob
from base import *
from Structures import *


BLOCKSIZE = 50


class Aspect(pygame.sprite.Sprite):
    def __init__(self, name = None, button = None):
        self.name = name
        self.button = button
        self.image, self.rect = load_image(self.name + '_hat.png', -1)

class Character(EventedSprite):

    def __init__(self, name = None, position = (0,0)):
        screen = pygame.display.get_surface()
        self.world = World(screen.get_size())
        self.direction = 1
        self.max_health = 500
        self.health = 200
        EventedSprite.__init__(self) #call Sprite intializer
        self.name = name
        self.moving = False
        self.ani_speed_init = 30
        self.ani_speed = self.ani_speed_init
        self.ani_pos = 0
        self.ani = load_sliced_sprites(self, BLOCKSIZE, BLOCKSIZE, 'walk/' + self.name + '_0.png')
        self.ani_max = len(self.ani[0]) - 1
        self.image = self.ani[0][self.ani_pos]
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        self.time_building = 0
        self.destinations = []
        self.aspect = None
        self.aspects = []
        self.xp = 400
        self._callbacks = {}

    def face_direction(self):
        if self.direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def add_callback(self, name, context, method):
        if not self._callbacks[name]:
            self._callbacks[name] = []
        handler = {
            "fn": method,
            "context": context
        }
        self._callbacks.append(handler)

    def call_handler(self, name, *args):
        if self._callbacks.get(name, False):
            for handler in self._callbacks[name]:
                handler["method"](handler["context"], *args)

    def on_collide(self, collisions):
        print str(len(collisions)) + " Collisions detected"
        return False

    def update(self, events):
        self.ani_speed -= 1
        if self.ani_speed == 0:
            self.ani_speed = self.ani_speed_init
            self.ani_pos += 1
            if self.ani_pos > self.ani_max:
                self.ani_pos = 0

        self.checkState(events)
        if self.moving:
            coll = self.check_collision()
            if len(coll) > 0:
                self.moving = False
                self.on_collide(coll)
            self.image = self.ani[1][self.ani_pos]
            self._walk()
        else:
            if self.health < self.max_health:
                self.health += 0.1
            self.image = self.ani[0][self.ani_pos]
        if self.aspect != None:
            # draw the hat.
            self.aspect.rect.top = - 10
            self.aspect.rect.left = 0
            self.image.blit(self.aspect.image, self.aspect.rect.topleft)
        self.face_direction()
        self.debug_draw()

    def check_collision(self):
        structures = self.world.map.tiles.get_sprites_from_layer(1)
        collisions = pygame.sprite.spritecollide(self, structures, False, pygame.sprite.collide_rect)
        return collisions

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
            self.move_done()

        movePosition = fromLeft * self.move_speed, fromTop * self.move_speed

        self.direction = fromLeft

        newpos = self.rect.move(movePosition)
        self.rect = newpos

    def move_done(self):
        return

    def clear_destination(self):
        self.destinations = []

    def set_destination(self, position):
        self.ani_speed_init = 10
        self.moving = True
        self.destinations.append(((position[0] / BLOCKSIZE) * BLOCKSIZE, (position[1] / BLOCKSIZE) * BLOCKSIZE))

                
class SelectableCharacter(Character):
    "A selectable controllable character"
    def __init__(self, name, position = (10,10)):
        Character.__init__(self, name, position)
        screen = pygame.display.get_surface()
        self.project = None
        self.area = screen.get_rect()
        self.building = False
        self.stepSize = 1
        self.selected = False
        self.move_speed = 1
        self.build_speed = 1
        self._sand = 0

    def check_collision(self):
        return []

    def add_sand(self, grains):
        self._sand += grains
        self.sand_changed()

    def spend_sand(self, grains):
        self._sand -= grains
        self.sand_changed()

    def get_sand(self):
        return self._sand

    def sand_changed(self):
        self.call_handler("sand_changed", self, self._sand)

    def select(self):
        self.selected = True
        self.world.set_selected(self)

    def deselect(self):
        self.selected = False
        self.world.set_selected(None)


    def imagine_aspect(self, aspect):
        self.aspect = aspect

    def has_project(self):
        return self.project != None

    def set_project(self, project):
        self.project = project

    def on_click(self, event):
        self.select()

    def selected_update(self, event):
        if not self.world._supress:
            if self.has_project() and not self.project.has_position():
                self.project.set_position(event.pos)
            elif not self.building:
                self.set_destination(event.pos)

    def set_destination(self, position):
        if not self.building:
            Character.set_destination(self, position)

    def finish_project(self):
        self.time_building = 0
        self.xp += 100
        self.building = False
        self.project.set_structure(None)
        self.set_project(None)

    def move_done(self):
        if self.project != None:
            self.building = True

    def update(self, events):
        Character.update(self, events)
        if not self.moving and self.building:
            self.image = self.ani[2][self.ani_pos]
            position = self.project.get_position()
            structure = self.project.get_structure()
            structure.build(self, position)



class Critter(Character):
    def __init__(self, type, pos):
        Character.__init__(self, type, pos)
        self.range = 50
        self.target = None
        self._targets = []
        self.damage = 0
        self.attacking = False

    def in_range(self, target):
        # In general, x and y must satisfy (x-center_x)^2 + (y - center_y)^2 < radius^2
        x = target.rect.center[0]
        y = target.rect.center[1]
        cx = self.rect.center[0]
        cy = self.rect.center[1]
        r = self.range
        return pow(x - cx, 2) + pow(y - cy, 2) < pow(r, 2)

    def on_collide(self, collisions):
        if self.target in collisions:
            self.attacking = True
        return False

    def get_targets(self):
        if hasattr(self, 'world'):
            self._targets = self.world.map.tiles.get_sprites_from_layer(1)
        return self._targets

    def update(self, events):
        Character.update(self, events)
        if self.attacking == False:
            for target in self.get_targets():
                print "Checking " + str(len(self.get_targets())) + " for range"
                if self.in_range(target) and isinstance(target, Structure) and self.target == None:
                    print "Target selected"
                    self.target = target
                    if self.moving:
                        self.clear_destination()
                    self.set_destination(self.target.rect.topleft)
        else:
            self.target.health -= self.damage
        if self.target == 0:
            self.target = None

        if self.target == None and self.moving == False:
            self.set_destination(self.world.map.getRandomTile())


class Jenai(SelectableCharacter):
    def __init__(self):
        SelectableCharacter.__init__(self, 'jenai', (0,0))
        self.health = 200
        self.max_health = 200
        self.build_speed = 5
        self.move_speed = 2
        self.ani_speed_init = 30
        self.add_sand(10000)

class Steve(SelectableCharacter):
    def __init__(self):
        SelectableCharacter.__init__(self, 'steve', (0, 128))
        self.health = 200
        self.max_health = 200
        self.build_speed = 3.75
        self.move_speed = 2.5
        self.ani_speed_init = 20
        self.add_sand(10000)

class Crab(Critter):
    def __init__(self, pos):
        Critter.__init__(self, 'crab', pos)
        self.health = 50
        self.max_health = 50
        self.move_speed = 2.5
        self.ani_speed_init = 20
        self.damage = 1
