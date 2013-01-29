from base import EventedSprite, load_image

class Button(EventedSprite):
	def __init__(self, name):
		EventedSprite.__init__(self)
		self.image, self.rect = load_image('button.png', -1)


	def on_click(self, event):
		return 1

class StructureButton(Button):
	def __init__(self, type):
		Button.__init__(self, 'Structure' + type)

class FireTowerButton(StructureButton):
	def __init__(self):
		StructureButton.__init__(self, 'FireTower')

	def on_click(event):
		print "Fire Tower Selected"

class IceTowerButton(StructureButton):
	def __init__(self):
		StructureButton.__init__(self, 'IceTower')

	def on_click(event):
		print "Ice Tower Selected"

class LightningTowerButton(StructureButton):
	def __init__(self):
		StructureButton.__init__(self, 'LightningTower')

	def on_click(event):
		print "Lightning Tower Selected"

class TrenchButton(StructureButton):
	def __init__(self):
		StructureButton.__init__(self, 'Trench')