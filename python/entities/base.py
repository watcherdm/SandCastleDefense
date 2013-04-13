import pygame, os, sys
from engines.wave import *

RED = pygame.Color(255, 0, 0, 255)
ASSETDIR = "assets/images/"
WAVEPRECISION = 100
TIDELEVELS = (.5, 1, 1.5, 2, 3, 4, 6)
WAVELEVELS = (10, 20, 50, 100)
OCEANCOLOR = pygame.Color(73, 130, 255)

class EventedSprite(pygame.sprite.DirtySprite):
  collide_method = "RECT"
  def get_points(self, target):
    x1 = self.rect.center[0]
    y1 = self.rect.center[1]
    x2 = target.rect.center[0]
    y2 = target.rect.center[1]
    return (x1, y1), (x2, y2)

  def angle_between_points(self, target):
    p1, p2 = self.get_points(target)
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]
    dx = x2 - x1
    dy = y2 - y1
    rads = atan2(-dy, dx)
    rads %= 2*pi
    return  to_angle(rads)

  def distance_between_points(self, target):
    p1, p2 = self.get_points(target)
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]
    return sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2))

  def debug_draw(self):
    pygame.draw.rect(self.image, RED, pygame.Rect((0,0,self.rect.width, self.rect.height)), 3)

  def __init__(self):
    pygame.sprite.DirtySprite.__init__(self)
    self.selected = False
    self.mouse = {
      'down': False,
      'over': False
    }

  def update(self, events):
    if self.collide_method == "RECT":
      method = pygame.sprite.collide_rect
    elif self.collide_method == "CIRC":
      method = pygame.sprite.collide_circle

    sprites = pygame.sprite.spritecollide(self, self.world.map.tiles, False, method)
    for sprite in self.world.map.tiles.get_sprites_at(self.rect.center):
      sprite.dirty = 1

    self.checkState(events)

  def mousemove(self, event):
    pos = pygame.mouse.get_pos()
    if self.rect.collidepoint(pos):
      self.on_mousemove(event)
    else:
      if self.mouse['over']:
        self.on_mouseout(event)
      self.mouse['over'] = False

  def mouseover(self):
    pos = pygame.mouse.get_pos()
    if self.rect.collidepoint(pos):
      self.mouse['over'] = True
      self.on_mouseover()
    
  def click(self, event):
    self.on_click(event)

  def mousedown(self, event):
    if self.mouse['over']:
      self.mouse['down'] = True
      self.on_mousedown(event)

  def mouseup(self, event):
    if self.mouse['over']:
      self.on_mouseup(event)
      if self.mouse['down']:
        self.click(event)
    self.mouse['down'] = False

  def mousehold(self, event):
    if self.mouse['over'] and self.mouse['down']:
      self.on_mousehold(event)

  def checkState(self, events = []):
    self.mouseover()
    for event in events:
      if event.type == pygame.QUIT:
        # probably are you sure you want to quit
        sys.exit()
      if event.type == pygame.MOUSEMOTION:
        self.mousemove(event)
      if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
          self.mousedown(event)
      if event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
          self.mouseup(event)

  def on_mousedown(self, event):
    return 0
  def on_mouseup(self, event):
    return 0
  def on_mousemove(self, event):
    return 0
  def on_mouseover(self):
    return 0
  def on_mouseout(self, event):
    return 0
  def on_click(self, event):
    return 0

class World(pygame.Surface, EventedSprite):
  _selected = None
  _instance = None
  _selection_changed = False
  structures = None
  state = 0
  initialized = False

  def __new__(cls, *args, **kwargs):
    if not cls._instance:
      print "creating new world"
      cls._instance = super(World, cls).__new__(
                          cls, *args, **kwargs)
    return cls._instance

  def end_game(self):
    self.state = 99

  def __init__(self, size):
    if self.initialized:
      return
    pygame.Surface.__init__(self, size)
    EventedSprite.__init__(self)
    self.selected = False
    self._supress = False
    self.rect = self.get_rect()
    self.initialized = True
  def set_goal(self, goal):
    self._goal = goal

  def get_goal(self):
    return self._goal

  def stop_event_propogation(self):
    self._supress = True

  def selection_changed(self):
    self._selection_changed = True

  def has_selected(self):
    return self._selected != None

  def set_selected(self, selectable):
    self._selected = selectable
    self.selection_changed()

  def clear_selected(self, selectable = None):
    if selectable == None or self._selected == selectable:
      self._selected = None
      self.selection_changed()

  def get_selected(self):
    return self._selected

  def update(self, events):
    if self._supress == True:
      self._supress = False
      return
    self.checkState(events)

  def on_click(self, event):
    if self._supress:
      return      
    if self._selected != None:
      self._selected.selected_update(event)
    self._selection_changed = False


class EventedSurface(pygame.Surface, EventedSprite):
  def __init__(self, size):
    pygame.Surface.__init__(self, size)
    self.selected = False
    self.mouse = {
      'down': False,
      'over': False
    }
    self.rect = self.get_rect()

class EventedShape(pygame.Surface, EventedSprite):
  def __init__(self):
    pygame.Rect.__init__(self)
    self.selected = False
    self.mouse = {
      'down': False,
      'over': False
    }
    self.rect = self


def load_image(name, colorkey=None):
  fullname = os.path.join( ASSETDIR + name)
  try:
    image = pygame.image.load(fullname)
  except pygame.error, message:
    print 'Cannot load image:', name
    raise SystemExit, message
  return image, image.get_rect()


def load_sliced_sprites(w, h, filename):
  '''
  Specs :
    Master can be any height.
    Sprites frames width must be the same width
    Master width must be len(frames)*frame.width
  Assuming you ressources directory is named "ressources"
  '''
  images = []
  master_image = pygame.image.load(os.path.join('.', ASSETDIR + filename)).convert_alpha()

  master_width, master_height = master_image.get_size()
  for j in xrange(int(master_height/h)):
    t = []
    images.append(t)
    for i in xrange(int(master_width/w)):
      position = (i*w,j*h,w,h)
      surf = master_image.subsurface(position)
      images[j].append(surf)
  return images

class WaveTip(pygame.sprite.Sprite):
  height = 100
  width = 100
  def __init__(self, ocean):
    pygame.sprite.Sprite.__init__(self)
    self.screen = pygame.display.get_surface()
    self.world = World(self.screen.get_size())
    self.ani = self.world.wavetip.ani
    self.ocean = ocean
    self.ani_frame = 0
    self.rect = pygame.Rect(0,0,100,100)

  def update(self, events):
    self.rect.top = self.ocean.rect.top
    if self.ani_frame >= len(self.ani[0]):
      self.ani_frame = 0
    self.image = self.ani[0][self.ani_frame]
    self.ani_frame += 1


class Ocean(pygame.sprite.OrderedUpdates):
  base = 100
  range = 100
  wave_count = 0
  i = 0
  wave = []
  current_tide_level = TIDELEVELS[0]
  rect = None
  def __init__(self):
    pygame.sprite.OrderedUpdates.__init__(self)
    self.screen = pygame.display.get_surface()
    self.world = World(self.screen.get_size())
    self.wave = get_line(self.wave_count + 1, WAVEPRECISION)
    for i in range(0, self.screen.get_size()[0], 100):
      wave_tip = WaveTip(self)
      self.add(wave_tip)
      wave_tip.rect.left = i

  def update(self, events):
    wave_point = self.wave[self.wave_count]
    if (self.i % 3 == 0):
      self.wave_count += 1

    if self.wave_count >= len(self.wave):
      self.wave_count = 0
      self.wave = get_line(self.wave_count + 1, WAVEPRECISION)
      pygame.mixer.Sound("assets/sounds/oceanwave.wav").play()

    waveheight = (self.range * self.current_tide_level) * (1 + wave_point)
    height = self.base + waveheight
    self.rect = pygame.Rect((0, self.screen.get_size()[1] - height) + self.screen.get_size())
    colliding_tiles = pygame.sprite.groupcollide(self.world.map.tiles, self, False, False, pygame.sprite.collide_rect)
    for t in colliding_tiles:
      t.make_dirty()
    self.i += 1
    for s in self.sprites():
      s.update(events)

  def draw(self, surf):
    surf.fill(OCEANCOLOR, self.rect)
    for s in self.sprites():
      surf.blit(s.image, s.rect)
