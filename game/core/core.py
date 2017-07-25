# Python imports
from __future__ import division
from math import sin, cos, pi, e, hypot

# Panda3D imports
from panda3d.core import (
	LPoint3 as Point,
	LVector3 as V3,
	LVector2 as V2)

class Goal:

	def __init__(self, pos, to_int=True):
		if to_int:
			pos = Point(int(round(pos.x)), int(round(pos.y)), int(round(pos.z)))
		else:
			pos = Point(pos.x, pos.y, pos.z)
		self.pos = pos

	def __repr__(self):
		return "Goal({})".format(self.pos)

	def __str__(self):
		return "<Goal at {}>".format(self.pos)

# functions

def distance(a, b):
	"""--> (a.pos - b.pos).length()"""
	return (a.pos - b.pos).length()

def dist(pos1, pos2):
	"""dist-ance
	(x1, y1), (x2, y2) --> hypot(x1-x2, y1-y2)"""
	return hypot(pos2[0]-pos1[0], pos2[1]-pos1[1])

def rotated(v, angle, in_degrees=True):
	"""flat rotation on angle in degrees (default)
	Point/V3 --> V3"""
	if in_degrees:
		angle = pi*angle/180.0
	# (cos_, sin_) = (cos(angle), sin(angle))
	# return V3(v.x*cos_ - v.y*sin_, v.x*sin_ + v.y*cos_, v.z)
	c = (v.x + v.y*1j)*e**(1j*angle) # complex approximately twice faster...
	return V3(c.real, c.imag, v.z)

def get_angle(v1, v2=None, in_degrees=True, default=None):
	"""v1 --> v2 [-180:+180] -- wrap for V2.signed_angle_[deg|rad] method
	default v2 = Vector3(0, 1, 0)
	+ anticlockwise"""
	if v2 is None:
		v2 = V3(0, 1, 0)
	if v1.length() == 0 or v2.length() == 0:
		return default
	if in_degrees:
		return -V2(v1.x, v1.y).signed_angle_deg(-V2(v2.x, v2.y))
	else:
		return -V2(v1.x, v1.y).signed_angle_rad(-V2(v2.x, v2.y))

def to_vector(pos, z=0, to_int=False):
	"""(x, y) --> Vector3(x, y, z[=0])"""
	if to_int:
		pos = (int(round(pos[0])), int(round(pos[1])))
	return V3(pos[0], pos[1], z)

def to_point(pos, z=0, to_int=False):
	"""(x, y) --> Point3(x, y, z[=0])"""
	if to_int:
		pos = (int(round(pos[0])), int(round(pos[1])))
	return Point(pos[0], pos[1], z)

def to_pos(v, to_int=True):
	"""object with obj.x and obj.y --> (x, y) rounded"""
	if to_int:
		return (int(round(v.x)), int(round(v.y)))
	return (v.x, v.y)

def square(pos, size):
	x0, y0 = pos
	return ((x0 + x, y0 + y) for x in xrange(-size, size + 1) for y in xrange(-size, size + 1))

def vicinity(pos, small=False):
	"""(x, y) --> ((x1, y1), (x2, y2), ...)
	bsb # b - not small (big)
	sxs # s - small
	bsb # x - pos"""
	x, y = int(round(pos[0])), int(round(pos[1]))
	if small:
		return ((x+1, y), (x, y-1), (x-1, y), (x, y+1))
	else:
		return ((x+1, y), (x, y-1), (x-1, y), (x, y+1),
			(x+1, y+1), (x+1, y-1), (x-1, y-1), (x-1, y+1))

def edge(pos, v):
	"""(x, y), Vector[2|3] --> tuple
	of 3 pos at direction of v"""
	x, y = int(round(pos[0])), int(round(pos[1]))
	dx, dy = to_pos(v.normalized()*1.45) # sqrt(2) < 1.45 < 1.5
	if dx*dy != 0:
		return ((x+dx, y), (x, y+dy), (x+dx, y+dy))
	elif dx == 0:
		return ((x+1, y+dy), (x, y+dy), (x-1, y+dy))
	elif dy == 0:
		return ((x+dx, y+1), (x+dx, y), (x+dx, y-1))

def sign(x):
	"""standard math function 'signum'"""
	return (x > 0) - (x < 0)

def get_main_ort(v):
	if abs(v.x) > abs(v.y):
		return V2(sign(v.x), 0)
	else:
		return V2(0, sign(v.y))

def get_main_angle(v):
	if abs(v.x) > abs(v.y):
		return sign(v.x)*90.0
	else:
		if v.y >= 0:
			return 180.0
		else:
			return 0.0

def co(v1, v2):
	"""xOy angle < 90"""
	return (sign(v1.x)*sign(v2.x) > 0) or (sign(v1.y)*(v2.y) > 0)
