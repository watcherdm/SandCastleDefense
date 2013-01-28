import pygame, os, sys

class EventedSprite(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    self.selected = False
    self.mouse = {
      'down': False,
      'over': False
    }

  def update(self, events):
    self.checkState(events)

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
          self.mouseup(event)        

  def on_mousedown(self, event):
    return 0
  def on_mouseup(self, event):
    return 0
  def on_mouseover(self, event):
    return 0
  def on_mouseout(self, event):
    return 0
  def on_click(self, event):
    return 0



def load_image(name, colorkey=None):
  fullname = os.path.join(name)
  try:
    image = pygame.image.load(fullname)
  except pygame.error, message:
    print 'Cannot load image:', name
    raise SystemExit, message
  return image, image.get_rect()