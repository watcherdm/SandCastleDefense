# map engine

class Map:
	def __init__(self, map, tiles):
		self.tiles = pygame.image.load(tiles)
		l = [line.strip() for line in open(map).readlines()]
        self.map = [[None]*len(l[0]) for j in range(len(l))]
        for i in range(len(l[0])):
            for j in range(len(l)):
                tile = l[j][i]
