import os, sys, pygame

def load_image(name, colorkey=None):
    fullname = os.path.join(name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    return image, image.get_rect()

class Jenai(pygame.sprite.Sprite):
    "A little girl ready to build a sand castle"
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.image, self.rect = load_image('jenai_01.PNG', -1)
        screen = pygame.display.get_surface()
        self.destinations = []
        self.castles = []
        self.area = screen.get_rect()
        self.rect.topleft = 10, 10
        self.moving = False
        self.building = False
        self.stepSize = 1
        
    def update(self):
        "Move to her destination or build a thing"
        if self.moving:
            self._walk()
        if self.building:
            self._build()
    def _walk(self):
        "move the monkey across the screen, and turn at the ends"
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

    def _build(self):
        "Make jenai build a castle"
        center = self.rect.center
        self.dizzy += 12
        if self.dizzy >= 360:
            self.dizzy = 0
            self.image = self.original
        else:
            rotate = pygame.transform.rotate
            self.image = rotate(self.original, self.dizzy)
        self.rect = self.image.get_rect(center=center)

    def selected(self):
        "This should select jenai"
        self.selected = True

    def setDestination(self, position):
        "This will make jenai walk to the new position"
        print "Jenai has been set to moving and should be going to "
        print position
        self.moving = True
        self.destinations.append(((position[0] / 64) * 64, (position[1] / 64) * 64))

    def setProject(self, castle):
        "This will add a castle to Jenai's work queue"
        self.building = True
        self.castles.append(castle)
