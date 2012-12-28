from base import EventedSprite, load_image

class Button(EventedSprite):
	def __init__(self, name):
		self.rect, self.image = load_image(self.name + '.PNG', -1)