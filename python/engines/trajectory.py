from math import cos, sin, sqrt, asin, pow, tan, pi, atan2
from math import radians as rad
import pygame, sys
from itertools import combinations
from python.entities.Characters import *
import numpy as np
gravity = 9.81
view_angle = 30
black = pygame.Color(0, 0, 0)
grey = pygame.Color(128,128,128)
red = pygame.Color(255,0,0)
white = pygame.Color(255, 255, 255)

def time_of_flight(distance, velocity, angle):
	angle = 180 * angle / pi
	return distance / velocity * cos(angle)

def to_angle(radians):
	return 180 * radians / pi

def to_radians(angle):
	return pi * angle / 180

def get_distance_traveled(velocity, height, angle):
	radians = to_radians(angle)
	return velocity * cos(radians) / gravity * (velocity * sin(radians) + sqrt(velocity * sin(radians) + 2 * gravity * height))

def y_velocity(velocity, angle):
	radians = to_radians(angle)
	x = (velocity * cos(radians)) * 0.1
	vy = velocity * sin(radians) - gravity * x / velocity * cos(radians)
	return vy

def x_velocity(velocity, angle):
	radians = to_radians(angle)
	return velocity * cos(radians)
	
def velocity_at_x(x, velocity, angle):
	return sqrt(pow(x_velocity(velocity, angle), 2) + pow(y_velocity(velocity, angle), 2))

def height_at_x(x, orig_height, angle, velocity):
	radians = to_radians(angle)
	rtan = tan(radians)
	rcos = cos(radians)
	val = orig_height + (x * rtan) - gravity * (x * x) / pow(2 * (velocity * rcos), 2)
	return val

def get_trajectory(x, h, a, v):
	trajectory = []
	val = 0
	while val >= 0.0 and val <= 1000:
		val = height_at_x(x, h, a, v)
		if val > 0:
			trajectory.append(val)
		x += 1
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
	return sqrt((x2 - x1)**2 + (y2 - y1)**2)

def angular_trajectory(start, angle, direction, velocity):
	shadow = []
	path = []
	x = start[0]
	y = start[1]
	counter = 0
	t = get_trajectory(0, start[2], angle, velocity)
	for z in t:
		x, y = angle_line((x, y), direction, counter)
		shadow.append((x, y, 0))
		path.append((x, y, z))
		if (z > 0):
			shadow.append((x, y, 0))
			path.append((x, y, 0))			
		counter += 1
	return path, shadow

def time_in_air(distance):
	return sqrt((2 * distance) / gravity)

#Universal projectile class. Is inherited by specific child projectiles such as the Cannonball.
class Projectile:  
	def __init__(self):
		self.r_set = np.array([[[0,0,0],[0,0,0]]], np.float)
		self.localtime = 0
		self.timestep = .1
		self.current_frame = 0
		self.hit_status = False
		pass
	
	def get_current_frame(self):
		return self.r_set[self.current_frame]
	
	def frame_step(self):
		if self.hit_status == False:
			if self.current_frame + 1 < np.shape(self.r_set)[0]:
				self.current_frame += 1
			else:
				self.hit_status = True
		else:
			pass
	
	def set_initial_conditions(self, position, azimuth, inclination, velocity): #rotational coordinates use standard mathematical spherical coordinate conventions (azimuth rotates about vertical axis)
		self.r_set[-1,0,:] = position
		self.r_set[-1,1,:] = [velocity*sin(inclination)*cos(azimuth), velocity*sin(inclination)*sin(azimuth), velocity*cos(inclination)]
	
	def rk4(self, diff_eqs, diff_eqs_args):
		r_next = [[[0,0,1],[0,0,0]]]		#Place-holder to satisfy the first iteration of the while loop
		while r_next[0][0][2] >= 0 and r_next[0][0][2] <= 1000:		
 			if type(r_next) == np.ndarray:			#Placing the append at the start of the loop means that the loop-breaking boundary condition doesn't get appended to r_set
 				self.r_set = np.append(self.r_set, r_next, axis = 0)
 			else:
 				pass
			k1 = diff_eqs(self.r_set[-1], self.localtime, diff_eqs_args)*self.timestep
			k2 = diff_eqs(self.r_set[-1] + .5*k1, self.localtime + .5*self.timestep, diff_eqs_args)*self.timestep
			k3 = diff_eqs(self.r_set[-1] + .5*k2, self.localtime + .5*self.timestep, diff_eqs_args)*self.timestep
			k4 = diff_eqs(self.r_set[-1] + k3, self.localtime + self.timestep, diff_eqs_args)*self.timestep			
			r_next = np.array([self.r_set[-1] + (k1 + 2*k2 + 2*k3 + k4)/6])
					
					


# Basic projectile type. Is called with a physical constants object instance so that things like
# Gravity and windspeed can be changed for different sessions through the Physics object.
class Cannonball(Projectile):  
	def __init__(self, phys_constants, *kwargs):
		Projectile.__init__(self)
		self.P = phys_constants
		self.diff_eqs_args = {}
	
	def diff_eqs(self, r, t, *kwargs):
		return np.append([r[1]],[[0, 0, self.P.gravity]], axis = 0)
	
	def calculate_trajectory(self):
		self.rk4(self.diff_eqs, self.diff_eqs_args)

class RPG(Projectile):  
	def __init__(self, phys_constants):
		Projectile.__init__(self)
		self.P = phys_constants
		self.diff_eqs_args = {}
		self.thrust = 12
		self.drag_coef = .15
	
	def diff_eqs(self, r, t, *kwargs):
		if t < 5:
			propulsion = np.array([[0,0,0], self.thrust*r[1]/np.linalg.norm(r[1])]) #Calculate thruster contribution to acceleration
		else:
			propulsion = np.array([[0,0,0],[0,0,0]])
		ASV = self.P.wind - r[1] #Air speed velocity
		wind_resistance = np.array([[0,0,0], self.drag_coef*ASV/np.linalg.norm(ASV)]) #Calculate drag contribution to acceleration
		falling = np.array([[0,0,0],[0,0,self.P.gravity]])
		momentum = np.array([r[1],[0,0,0]])
		return momentum + falling + wind_resistance + propulsion

	def calculate_trajectory(self):
		self.rk4(self.diff_eqs, self.diff_eqs_args)
	
class Homing(Projectile):
	def __init__(self, phys_constants):
		Projectile.__init__(self)
		self.P = phys_constants
		self.diff_eqs_args = {}
		self.thrust = 12
		self.target = np.array([0,0,300])
		
	def diff_eqs(self, r, t, *kwargs):
		homing_vector = self.target - r[0]
		propulsion = np.array([[0,0,0], self.thrust * homing_vector/np.linalg.norm(homing_vector)])
		falling = np.array([[0,0,0],[0,0,self.P.gravity]])
		momentum = np.array([r[1],[0,0,0]])
		return momentum + falling + propulsion
		
	def calculate_trajectory(self):
		self.rk4(self.diff_eqs, self.diff_eqs_args)
# Contains the physical constants like Gravity. Should be initialized at the start of play and issued
# as an argument to every projectile type.	
class Physics:
	def __init__(self):
		self.gravity = -9.81
		self.wind = np.array([0,0,0])
#		self.force_from_his_noodley_appendage = [0,0,0]  

	

class Cannon:
	def __init__(self):
		print "Initializing cannon"
		self.projectile_type = Cannonball
		self.physics_variables = Physics()
		self._targets = []
		self.inclination = 0
		self.azimuth = 180
		self.aof = 180
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

	def angle_to_target(self, target):
		x1 = self.center[0]
		y1 = self.convert_y()
		x2 = target.rect.center[0]
		y2 = target.rect.center[1]
		val = angle_between_points(x1, y1, x2, y2)
		self.ang = val

	def distance_to(self, target):
		p1 = x1, y1 = self.center
		p2 = x2, y2 = target.rect.center
		return distance_between_points(x1, y1, x2, y2)

	def velocity_to_distance(self, distance):
		self.vel = sqrt(distance * gravity / m)

	def in_range(self, target):
		# In general, x and y must satisfy (x-center_x)^2 + (y - center_y)^2 < radius^2
		x = target.rect.center[0]
		y = target.rect.center[1]
		cx = self.center[0]
		cy = self.convert_y()
		r = self.range + self.height
		return pow(x - cx, 2) + pow(y - cy, 2) < pow(r, 2)
	
	def fire_projectile(self, *kwargs):
		self.projectiles.append(self.projectile_type(self.physics_variables, kwargs))
		projectile = self.projectiles[-1]
		projectile.set_initial_conditions([self.center[0], self.center[1], self.height], rad(self.azimuth), rad(self.inclination), self.vel)
		projectile.calculate_trajectory()
		
		

	def update(self, events):
		range = self.range + self.height
		to_attack = []
		for target in self.get_targets():
			if self.in_range(target):
				print "Target in range"
				self.angle_to_target(target)
				distance = self.distance_to(target)
				self.velocity_to_distance(distance)
				self.shotRequested = True
				continue

		self.canvas = pygame.Surface(pygame.display.get_surface().get_size())
		self.canvas.set_colorkey(black)
		for event in events:
			if event.type == self.fireTrigger:
				if self.shotRequested:
					self.fire_projectile()
# 					projectile = angular_trajectory(self.get_3d_point(), self.aof, self.ang, self.vel)
# 					self.projectiles.append([projectile[0], projectile[1]])
					self.shotRequested = False	
# 		if self.ang < -180:
# 			self.ang = 180
# 		if self.ang > 180:
# 			self.ang = -180
# 		if self.aof > 180:
# 			self.aof = 180
		if self.aof < 90:
			self.aof = 90
		if self.inclination < 0:
			self.inclination = 0
		if self.inclination > 90:
			self.inclination = 90

		for projectile in self.projectiles:
# 			t = projectile[0]
# 			s = projectile[1]
# 			if len(t) != 0:
# 				pos = self.to3d(t[0], view_angle)
# 				spos = self.to3d(s[0], view_angle)
# 				projectile[0] = t[1:]
# 				projectile[1] = s = s[1:]
# 				if len(projectile[0]) == 0:
# 					self.hits.append(pos)
# 				pygame.draw.circle(self.canvas, red, pos, self.projectile_radius)
# 				pygame.draw.circle(self.canvas, grey, spos, self.projectile_radius)
# 			else:
# 				self.projectiles.remove(projectile)
			if projectile.hit_status == False:
				pygame.draw.circle(self.canvas, red, self.to3d(projectile.get_current_frame[0], view_angle), self.projectile_radius)
				pygame.draw.circle(self.canvas, grey, self.to3d([projectile.get_current_frame[0,0], projectile.get_current_frame[0,1], 0], view_angle), self.projectile_radius)
				projectile.frame_step()
			else:
				self.hits.append(self.to3d(projectile.get_current_frame[0], view_angle))
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
			cannon.aof += 2
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