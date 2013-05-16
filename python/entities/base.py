import pygame, os, sys
import random
from engines.wave import *
from dimensions import *
from scipy.ndimage import gaussian_filter1d
import numpy as np

RED = pygame.Color(255, 0, 0, 255)
ASSETDIR = "assets/images/"
WAVEPRECISION = 100
TIDELEVELS = (.5, 1, 1.2, 1.5, 1.7, 2.2, 2.5)
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
  _goal = None
  i = 0
  structures = None
  state = 0
  initialized = False
  debug = False
  cs = None
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
    self.clock = pygame.time.Clock()
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
    if self.ani_frame >= len(self.ani[0]):
      self.ani_frame = 0
    self.image = self.ani[0][self.ani_frame]
    self.ani_frame += 1

def smooth_line(l):
  a = np.array(l)
  x, y = a.T
  t = np.linspace(0, 1, len(x))
  t2 = np.linspace(0, 1, len(x))

  x2 = np.interp(t2, t, x)
  y2 = np.interp(t2, t, y)
  sigma = 1
  x3 = gaussian_filter1d(x2, sigma)
  y3 = gaussian_filter1d(y2, sigma)

  return zip(x3, y3)

class Ocean(pygame.sprite.Sprite):
  base = 100
  range = 50
  direction = 1
  wave_count = 0
  i = 0
  points = []
  wave = []
  current_tide_level = TIDELEVELS[0]
  rect = None
  y = 0
  ne = False
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    self.screen = pygame.display.get_surface()
    self.world = World(self.screen.get_size())
    self.wave = get_line(self.wave_count + 1, WAVEPRECISION)
    self.image = pygame.Surface(SCREENSIZE)
    self.rect = self.image.get_rect()
    self.tips = pygame.sprite.OrderedUpdates()
    for i in range(0, self.screen.get_size()[0], 100):
      wave_tip = WaveTip(self)
      self.tips.add(wave_tip)
      wave_tip.rect.left = i
      wave_tip.rect.top = 0
    for i in range(0, SCREENSIZE[0], 1):
      self.points.append([i, self.y])

  def ebb(self, y):
    if self.ne:
      self.ne = False
      return

    if self.direction == 1:
      #highest point
      self.direction = -1
    set_y = True
    delta_y =  self.y - y
    for point in self.points:
      if point[1] > y:
        point[1] -= delta_y

  def flow(self, y):
    if self.direction == -1:
      self.direction = 1
      self.current_tide_level = random.choice(TIDELEVELS)
      self.ne = True
      pygame.mixer.Sound("assets/sounds/oceanwave.wav").play()
    possible_collisions = self.world.map.tiles.get_sprites_from_layer(1)
    delta_y =  y - self.y
    for point in self.points:
      set_y = True
      if y > point[1]:
        for structure in possible_collisions:
          if structure.rect.collidepoint(point[0], SCREENSIZE[1] - (point[1] + delta_y)):
            self.point_collision(point, structure)
            set_y = False
      if set_y:
        point[1] += delta_y

  def point_collision(self, point, structure):
    dmg = 0.5
    if structure.isPit():
      dmg = 0.1
    structure.health -= dmg

  def dirty_sand(self):
    colliding_tiles = pygame.sprite.spritecollide(self, self.world.map.tiles, False, pygame.sprite.collide_rect)
    for t in colliding_tiles:
      if hasattr(t, 'make_dirty'):
        t.make_dirty()
        surr = t.get_surrounding()
        for s in surr:
          s.make_dirty()

  def update(self, events):
    canvas = pygame.Surface(self.image.get_rect().size)
    wave_point = self.wave[self.wave_count]
    if (self.i % 3 == 0):
      self.wave_count += 1

    if self.wave_count >= len(self.wave):
      self.wave_count = 0
      self.wave = get_line(self.wave_count + 1, WAVEPRECISION)


    waveheight = (self.range * self.current_tide_level) * (1 + wave_point)
    new_y = self.base + waveheight
    if self.y == new_y:
      self.image.set_alpha(196)
      self.dirty_sand()
      self.i += 1
      return
    if new_y < self.y:
      self.ebb(new_y)
    elif new_y > self.y:
      self.flow(new_y)

    self.y = new_y
    self.rect.top = self.screen.get_size()[1] - self.y
    self.dirty_sand()
    self.image.fill(OCEANCOLOR)
    self.i += 1
    self.tips.update(events)
    self.tips.draw(self.image)
    last_point = None
    blocks = pygame.sprite.Group()
    block_x = [0, 0]
    building_block = False
    def closeBlock(point):
      block = pygame.sprite.Sprite()
      block.image = pygame.Surface((block_x[1], SCREENSIZE[1]))
      block.image.set_colorkey(pygame.Color(0, 0, 0))
      block.image.blit(self.image, (block_x[0], 0, block_x[1], SCREENSIZE[1]))
      block.rect = block.image.get_rect()
      block.rect.top = self.y - last_point[1]
      blocks.add(block)
      block_x[0] = point[0]
      block_x[1] = point[0]
      building_block = False
    smooth_points = smooth_line(self.points)
    for point in smooth_points:
      if last_point != None:
        if last_point[1] == point[1]:
          # continue the block
          block_x[1] = point[0]
          building_block = True
          if smooth_points.index(point) == len(smooth_points) - 1:
            closeBlock(point)
        else:
          block_x[1] += 1
          closeBlock(point)
          # finish the last block and start a new one

      last_point = point
    self.image.set_colorkey(pygame.Color(255,0,0))
    self.image.fill(pygame.Color(255,0,0))
    blocks.draw(self.image)
    self.image.set_alpha(196)
    # now that we have the full rendered image
    # break it up into 1 px strips
    # adjust the y values of the points
    # position the subsurfaces 

