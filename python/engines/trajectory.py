from math import cos, sin, sqrt, asin, pow, tan, pi
import pygame, sys
gravity = 9.81

def get_distance_traveled(velocity, height, angle):
	angle = 180 * angle / pi
	return velocity * cos(angle) / gravity * (velocity * sin(angle) + sqrt(velocity * sin(angle) + 2 * gravity * height))

def time_of_flight(distance, velocity, angle):
	angle = 180 * angle / pi
	return distance / velocity * cos(angle)

def to_angle(radians):
	return 180 * radians / pi

def to_radians(angle):
	return pi * angle / 180

def y_velocity(velocity, angle):
	radians = to_radians(angle)
	x = (v * cos(radians)) * t
	vy = velocity * sin(radians) - gravity * x / velocity * cos(radians)
	return vy


def x_velocity(velocity, angle):
	radians = to_radians(angle)
	return velocity * cos(radians)
	
def velocity_at_x(x, velocity, angle):
	return sqrt(pow(x_velocity(velocity, angle), 2) + pow(y_velocity(x, velocity, angle), 2))

def height_at_x(x, orig_height, angle, velocity):
	radians = to_radians(angle)
	rtan = tan(radians)
	rcos = cos(radians)
	return orig_height + x * rtan - gravity * (x * x) / pow(2 * (velocity * rcos), 2)

def get_trajectory(x, h, a, v):
	print "generating trajectory for " + str(x) + " " + str(h) + " " + str(a) + " " + str(v)
	trajectory = []
	val = 0
	while val >= 0.0 and val <= 100000:
		val = height_at_x(x, h, a, v)
		if val > 0:
			trajectory.append(val)
		x += 1
	return trajectory

xOrigin = 0
yOrigin = 480

def xFla(x, y, z):
	xCart = (x-z)*cos(to_radians(90));
	xI = xCart+xOrigin;
	return (xI);
 
def yFla(x, y, z):
	yCart = y+(x+z)*sin(to_radians(30));
	yI = -yCart+yOrigin;
	return (yI);

def to3d(point):
	return (point[0], yFla(point[0], point[1], point[2]))

range_of_projectile = 100

initPoint = [320, 240, 0]
if __name__ == "__main__":
	box = ((0, 0, 0), (1, 0, 0), (1, 1, 0), (1,0,1), (0,1,1), (0, 0, 1), (0, 1, 0))
	a = 45
	v = 40
	h = 0
	black = pygame.Color(0, 0, 0)
	red = pygame.Color(255,0,0)
	white = pygame.Color(255, 255, 255)
	d = get_distance_traveled(v, h, a)
	x = 0
	r = 2
	print d
	print time_of_flight(d, v, a)
	pygame.init()
	screen = pygame.display.set_mode((640, 480))
	canvas = pygame.Surface((640, 480))
	t = get_trajectory(x, h, a, v)
	while True:
		canvas.fill(white)
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				# probably are you sure you want to quit
				sys.exit()
		if len(t) == 0:
			x = 0
			t = get_trajectory(x, 0, a, v)
			a -= 3
			if a < 0:
				a = 180

			initPoint = [320, 230, 0]
		else:
			pos = (320 + int(x), 240 + int(t[0]))
			x += 1
			t = t[1:]
			pygame.draw.circle(canvas, black, pos, r)
			i = initPoint
			p = (initPoint[0], int(yFla(i[0], i[1], i[2])))
			pygame.draw.circle(canvas, red, p, 4, 2)
			i[2] -= 2
		canvas = pygame.transform.flip(canvas, False, True)
		screen.blit(canvas, (0, 0))
		pygame.display.flip()

