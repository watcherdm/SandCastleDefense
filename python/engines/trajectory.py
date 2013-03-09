from math import cos, sin, sqrt, asin, pow, tan, pi, atan, atan2,degrees,radians
import pygame, sys
from itertools import combinations
from entities.Characters import *
gravity = 9.81
view_angle = 30
black = pygame.Color(0, 0, 0)
grey = pygame.Color(128,128,128)
red = pygame.Color(255,0,0)
white = pygame.Color(255, 255, 255)
FRAMERATE = 60

def time_of_flight(distance, velocity, angle):
	angle = 180 * angle / pi
	return distance / velocity * cos(angle)

def to_angle(radians): #use math.degrees
	return 180 * radians / pi

def to_radians(angle): #use math.radians
	return pi * angle / 180

def get_distance_traveled(velocity, height, angle):
	radians = to_radians(angle)
	return velocity * cos(radians) / gravity * (velocity * sin(radians) + sqrt(velocity * sin(radians) + 2 * gravity * height))

def y_velocity(velocity, angle):
	radians = to_radians(angle)
	vy = 0
	x = (velocity * cos(radians)) * 0.1
	vx = velocity * cos(radians)
	if vx > 0:
		vy = velocity * sin(radians) - gravity * x / velocity * cos(radians)
	return vy


def x_velocity(velocity, angle):
	radians = to_radians(angle)
	return velocity * cos(radians)
	
def velocity_at_x(x, velocity, angle):
	return sqrt(pow(x_velocity(velocity, angle), 2) + pow(y_velocity(velocity, angle), 2))

def height_at_x(x, orig_height, angle, velocity):
	radians = to_radians(angle) * 2
	rtan = tan(radians)
	rcos = cos(radians)
	val = orig_height + (x * rtan) - gravity * (x**2) / (2 * (velocity * rcos) ** 2)
	return val

def get_trajectory(x, h, a, vel):
	trajectory = []
	v = vel
	while h >= 0.0 and h <= 1000:
		v = velocity_at_x(x, vel, a)
		h = height_at_x(x, h, a, v)
		if h > 0.0:
			trajectory.append(h)
		else:
			trajectory.append(0)
		x += vel
	return trajectory

def angle_line(start, angle, distance):
	radians = to_radians(angle)
	return start[0] + distance * cos(radians), start[1] + distance * sin(radians)

def angle_between_points(x1, y1, x2, y2):
	dx = x2 - x1
	dy = y2 - y1
	rads = atan2(-dy, dx)
	rads %= 2*pi
	return  to_angle(rads)

def distance_between_points(x1, y1, x2, y2):
	return sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2))

def angular_trajectory(start, angle, direction, velocity):
	shadow = []
	path = []
	x = start[0]
	y = start[1]
	ms = 1000 / FRAMERATE
	counter = 0
	t = get_trajectory(0, start[2], angle, velocity)
	for z in t:
		x, y = angle_line((x, y), direction, counter)
		shadow.append((x, y, 0))
		path.append((x, y, z))
		if (z > 0):
			shadow.append((x, y, 0))
			path.append((x, y, 0))			
		counter += velocity
	return path, shadow

def time_in_air(distance):
	return sqrt((2 * distance) / gravity)


class Cannon:
	def __init__(self):
		print "Initializing cannon"
		self._targets = []
		self.aof = 45
		self.rof = 10
		self.vel = 3
		self.ang = 180
		self.height = 0
		self.hits = []
		self.projectiles = []
		self.center = [0, 0]
		self.fireTrigger = pygame.MEDFIRE
		self.shotRequested = False
		self.canvas = pygame.Surface(pygame.display.get_surface().get_size())
		self.canvas.set_colorkey(black)
		self.projectile_radius = 2
		self.yOrigin = pygame.display.get_surface().get_rect().height
		self.range = 50

	def setPosition(self, pos):
		screen_height = pygame.display.get_surface().get_rect().height
		left = pos[0]
		top = screen_height - pos[1]
		self.center = [left, top]

	def yFla(self, x, y, z, angle):
		yCart = y+(z)*sin(to_radians(angle));
		yI = -yCart + self.yOrigin;
		return (yI);

	def to3d(self, point, angle):
		return (int(point[0]), int(self.yFla(point[0], point[1], point[2], angle)))

	def convert_y(self):
		return pygame.display.get_surface().get_rect().height - self.center[1]

	def get_3d_point(self):
		return (self.center[0], self.center[1], self.height)

	def get_targets(self):
		if hasattr(self, 'world'):
			self._targets = self.world.critters
		return self._targets

	def set_target(self, target):
		self._targets.append(target)

	def remove_target(self, target):
		self._targets.remove(target)

	def angle_to_target(self, target, for_z = False):
		x1 = self.center[0]
		if for_z:
			y1 = self.height
			y2 = 0 #hit the ground
		else:
			y1 = self.convert_y()
			y2 = target.rect.center[1]
		x2 = target.rect.center[0]
		val = angle_between_points(x1, y1, x2, y2)
		return val

	def distance_to(self, target):
		p1 = x1, y1 = self.center
		p2 = x2, y2 = target.rect.center
		return distance_between_points(x1, y1, x2, y2)

	def real_distance_to(self, target):
		p1 = x1, y1, z1 = self.center[0], self.center[1], self.height
		p2 = x2, y2, z2 = target.rect.center[0], target.rect.center[1], 0
		return distance_between_points(0,  z1, self.distance_to(target), 0)


	def angle_to_go_distance(self, distance, velocity):
		print ' :: '.join([str(gravity), str(distance), str(velocity)])
		rate = (gravity*distance)/(velocity**2)
		if rate < 45 and rate > 0:
			return to_angle(.5*asin(to_radians(rate)))
		return 0

	def aof_to_target(self, velocity, target):
		r = self.real_distance_to(target)
		x = r
		y = - self.height
		v = velocity
		g = gravity
		#
		rads = atan(v ** 2 - sqrt(abs(v ** 4 - g * (g * x ** 2 + 2 * y * v ** 2)))/ g * x)
		return abs(rads)

	def in_range(self, target):
		# In general, x and y must satisfy (x-center_x)^2 + (y - center_y)^2 < radius^2
		x = target.rect.center[0]
		y = target.rect.center[1]
		cx = self.center[0]
		cy = self.convert_y()
		r = self.range + self.height
		return pow(x - cx, 2) + pow(y - cy, 2) < pow(r, 2)

	def update(self, events):
		range = self.range + self.height
		to_attack = []
		for target in self.get_targets():
			if self.in_range(target):
				self.ang = self.angle_to_target(target)
				distance_x = self.distance_to(target)
				distance = self.real_distance_to(target)
				if distance_x < self.height:
					self.vel = distance_x / 12
				else:
					self.vel = distance / 12
				aof = self.aof_to_target(self.vel, target)
				self.aof = aof
				self.shotRequested = True

		self.canvas = pygame.Surface(pygame.display.get_surface().get_size())
		self.canvas.set_colorkey(black)
		for event in events:
			if event.type == self.fireTrigger:
				if self.shotRequested:
					projectile = angular_trajectory(self.get_3d_point(), self.aof, self.ang, self.vel)
					self.projectiles.append([projectile[0], projectile[1]])
					self.shotRequested = False	
		if self.ang < -180:
			self.ang = 180
		if self.ang > 180:
			self.ang = -180
		if self.aof > 180:
			self.aof = -180
		if self.aof < -180:
			self.aof = 180

		for projectile in self.projectiles:
			t = projectile[0]
			s = projectile[1]
			if len(t) != 0:
				pos = self.to3d(t[0], view_angle)
				spos = self.to3d(s[0], view_angle)
				projectile[0] = t[1:]
				projectile[1] = s = s[1:]
				if len(projectile[0]) == 0:
					self.hits.append(pos)
				pygame.draw.circle(self.canvas, black, pos, self.projectile_radius)
				# pygame.draw.circle(self.canvas, grey, spos, self.projectile_radius)
			else:
				self.projectiles.remove(projectile)

		if len(self.hits) > 20:
			self.hits = self.hits[1:]

		for hit in self.hits:
			pygame.draw.circle(self.canvas, grey, hit, 3)

	def draw_debug(self):
		p = self.to3d(self.get_3d_point(), view_angle)
		spoint = (self.center[0], self.center[1], 0)
		pygame.draw.circle(self.canvas, red, p, 4, 2)
		pygame.draw.circle(self.canvas, grey, self.to3d(spoint, view_angle) , 4, 2)
		pygame.draw.circle(self.canvas, grey, self.to3d(spoint, view_angle) , self.range + self.height, 1)

	def draw(self, surf):
		self.draw_debug()
		surf.blit(self.canvas, (0,0))

pygame.FASTFIRE = 25
pygame.MEDFIRE = 26
pygame.SLOWFIRE = 27

def test():
	fast = 10
	med = 5
	slow = 2
	pygame.init()
	pygame.font.init()
	f = pygame.font.SysFont('arial', 12)	
	screen = pygame.display.set_mode((640, 480))
	clock = pygame.time.Clock()
	pygame.time.set_timer(pygame.FASTFIRE, 1000 / fast)
	pygame.time.set_timer(pygame.MEDFIRE, 1000 / med)
	pygame.time.set_timer(pygame.SLOWFIRE, 1000 / slow)

	keysHeld = {
		276: False,
		275: False,
		274: False,
		273: False,
		122: False, # aof down
		120: False, # aof up
		101: False, # elevation down
		113: False, # elevation up
		119: False, # position y up
		115: False, # position y down
		100: False, # position x up
		97: False, # position x down
		32: False,
		27: False,
		9: False
	}		

	cannon = Cannon()
	targets = pygame.sprite.RenderUpdates()
	target = Crab((0, 0))
	cannon.set_target(target)
	moveCannon = True
	targets.add(target)
	while True:

		distance = get_distance_traveled(cannon.vel, cannon.height, cannon.aof)
		currentAngle = f.render("direction " + str(cannon.ang), False, black)
		currentAof = f.render("angle " + str(cannon.aof), False, black)
		currentVelocity = f.render("velocity " + str(cannon.vel), False, black)
		currentPoint = f.render("location " + str(cannon.get_3d_point()), False, black)
		currentRange = f.render("range " + str(distance), False, black)
		currentFps = f.render("fps " + str(clock.get_fps()), False, black)
		screen.fill(white)
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				sys.exit()
			if event.type == pygame.KEYDOWN:
				keysHeld[event.key] = True
				print event.key
			if event.type == pygame.KEYUP:
				keysHeld[event.key] = False

		targets.update(events)
		cannon.update(events)
		if keysHeld[9]:
			# swith target
			moveCannon = not moveCannon
		if keysHeld[276]:
			cannon.ang += 2
		if keysHeld[275]:
			cannon.ang -= 2
		if keysHeld[274]:
			cannon.vel -= 0.1
		if keysHeld[273]:
			cannon.vel += 0.1
		if keysHeld[120]:
			cannon.aof += 0.1
		if keysHeld[122]:
			cannon.aof -= 0.1
		if keysHeld[113]:
			if moveCannon:
				cannon.height += 1
				if cannon.height > 120:
					cannon.height = 120
			else:
				pass
		if keysHeld[101]:
			if moveCannon:
				cannon.height -= 1
				if cannon.height < 1:
					cannon.height = 1
			else:
				pass
		if keysHeld[119]:
			if moveCannon:
				cannon.center[1] += 2
				if cannon.center[1] > 480:
					cannon.center[1] = 480
			else:
				target.rect.top -= 2

		if keysHeld[115]:
			if moveCannon:
				cannon.center[1] -= 2
				if cannon.center[1] < 0:
					cannon.center[1] = 0
			else:
				target.rect.top += 2

		if keysHeld[100]:
			if moveCannon:
				cannon.center[0] += 2
				if cannon.center[0] > 640:
					cannon.center[0] = 640
			else:
				target.rect.left += 2

		if keysHeld[97]:
			if moveCannon:
				cannon.center[0] -= 2
				if cannon.center[0] < 0:
					cannon.center[0] = 0
			else:
				target.rect.left -= 2

		if keysHeld[32]:
			if moveCannon:
				if cannon.shotRequested == False:
					print "Shot Requested"
					cannon.shotRequested = True

		if keysHeld[27]:
			cannon.hits = []

		
		cannon.draw(screen)
		targets.draw(screen)
		screen.blit(currentAngle, (10, 10))
		screen.blit(currentAof, (10, 20))
		screen.blit(currentVelocity, (10, 30))
		screen.blit(currentPoint, (10, 40))
		screen.blit(currentRange, (10, 50))
		screen.blit(currentFps, (10, 60))
		clock.tick(60)

		pygame.display.flip()

if __name__ == "__main__":
	test()