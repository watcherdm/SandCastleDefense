import os, sys, pygame

def load_image(name, colorkey=None):
    fullname = os.path.join(name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    return image, image.get_rect()

class BeachLady(pygame.sprite.Sprite):
    "A lady laying on the beach"
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('beachlady_01.PNG', -1);
class Character(pygame.sprite.Sprite):
    def __init__(self, name = None, position = (0,0)):
        if not name: raise 1
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.image, self.rect = load_image(name + '_01.PNG', -1)
        self.name = name;
        self.rect.topleft = position

    def update(self, events):
        "Characters can be udpated"
        self.checkState(events)
        self.beforeUpdate()
        self.performUpdate()
        self.afterUpdate()
    def checkState(self, *args, **kwargs):
        return
    def beforeUpdate(self, *args, **kwargs):
        return
    def performUpdate(self, *args, **kwargs):
        return
    def afterUpdate(self, *args, **kwargs):
        return

class SelectableCharacter(Character):
    "A little girl ready to build a sand castle"
    def __init__(self, name, position = (10,10)):
        Character.__init__(self, name, position)
        screen = pygame.display.get_surface()
        self.destinations = []
        self.castles = []
        self.area = screen.get_rect()
        self.moving = False
        self.building = False
        self.stepSize = 1
        self.mouse = {
            'down': False,
            'over': False
        }
    def mouseover(self, event):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if not self.mouse['over']:
                self.on_mouseover(event)
            self.mouse['over'] = True
        else:
            if self.mouse['over']:
                self.on_mouseout(event)
            self.mouse['over'] = False
        
    def click(self, event):
        self.on_click(event)
    def mousedown(self, event):
        if self.mouse['over']:
            self.on_mousedown(event)
            self.mouse['down'] = True
    def mouseup(self, event):
        if self.mouse['over']:
            if self.mouse['down']:
                self.on_mouseup(event)
                self.click(event)
        self.mouse['down'] = False
    def mousehold(self, event):
        if self.mouse['over'] and self.mouse['down']:
            self.on_mousehold(event)
    def checkState(self, events = []):
        for event in events:
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.MOUSEMOTION:
                self.mouseover(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mousedown(event)
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mousedown(event)                

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

    def selected(self):
        self.selected = True

    def setDestination(self, position):
        print self.name + "has been set to moving and should be going to "
        print position
        self.moving = True
        self.destinations.append(((position[0] / 64) * 64, (position[1] / 64) * 64))

    def setProject(self, castle):
        self.building = True
        self.castles.append(castle)

    def on_mousedown(self, event):
        print "HELLO DOWN"
    def on_mouseup(self, event):
        print "HELLO UP"
    def on_mouseover(self, event):
        print "HELLO OVER"
    def on_mouseout(self, event):
        print "HELLO OUT"
    def on_click(self, event):
        print "HELLO CLICK"

class Jenai(SelectableCharacter):
    def __init__(self):
        SelectableCharacter.__init__(self, 'jenai', (0,0))

class Steve(SelectableCharacter):
    def __init__(self):
        SelectableCharacter.__init__(self, 'steve', (0, 128))