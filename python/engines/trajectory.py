from math import cos, sin, sqrt, asin, pow

gravity = 9.81

def get_distance_traveled(velocity, height, angle):
	return velocity * cos(angle) / gravity * (velocity * sin(angle) + sqrt(velocity * sin(angle) + 2 * gravity * height))

def time_of_flight(distance, velocity, angle):
	return distance / velocity * cos(angle)

def angle_of_reach(distance, velocity):
	m = (1/2) * (asin((gravity*distance) / (pow(velocity, 2))))
	return m

if __name__ == "__main__":
	a = 45
	v = 20
	h = 0
	d = get_distance_traveled(v, h, a)
	print d
	print time_of_flight(d, v, a)
	print angle_of_reach(15, v)