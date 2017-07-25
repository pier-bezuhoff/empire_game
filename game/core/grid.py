# Python imports
from math import floor, ceil
from itertools import chain
# Game imports
from core import get_angle, to_pos, to_vector, vicinity, square, dist

class Grid(object):

	max_path_length = 1e3
	max_path_verticies = 1e2

	def __init__(self):
		self.list_grid = {} # dict of lists of objects on occupied pos
		self.static_grid = {} # dict for stable objects
		self.dynamic_grid = {} # dict for moving objects

	def __repr__(self):
		return "Grid()"

	def __str__(self):
		return "<Grid>"

	def is_free(self, pos, static=False):
		"""check if the pos/Point3 is free, not [from] static ==> [from] all"""
		if not static: # all
			return pos not in self.static_grid and pos not in self.dynamic_grid
		else: # buildings
			return pos not in self.static_grid

	def area_is_free(self, center_pos, size=0, static=False):
		"""check if
		square (2*size+1)x(2*size+1)
		with center in center_pos is free"""
		return all(self.is_free(p, static=static) for p in square(center_pos, size))

	def segment_is_free(self, start_pos, end_pos, static=False):
		"""check if segment with given ends is free, borrowed from self.get_obstacles()"""
		if start_pos == end_pos:
			return True
		start_x, start_y = start_pos
		end_x, end_y = end_pos
		dx = (start_x - end_x)
		dy = (start_y - end_y)
		if abs(dy) >= abs(dx):
			k = dx/dy
			if start_y > end_y:
				start_x, end_x = end_x, start_x
				start_y, end_y = end_y, start_y
			for y in xrange(end_y - start_y + 1):
				p1 = (int(floor(start_x + k*y)), start_y + y)
				p2 = (int(ceil(start_x + k*y)), start_y + y)
				if not all([self.is_free(pos, static=static) for pos in (p1, p2)]):
					return False
		else:
			k = dy/dx
			if start_x > end_x:
				start_x, end_x = end_x, start_x
				start_y, end_y = end_y, start_y
			for x in xrange(end_x - start_x + 1):
				p1 = (start_x + x, int(floor(start_y + k*x)))
				p2 = (start_x + x, int(ceil(start_y + k*x)))
				if not all([self.is_free(pos, static=static) for pos in (p1, p2)]):
					return False
		return True

	def path_is_free(self, start_pos, end_pos, static=False):
		"""check if path with given ends is free, borrowed from self.get_obstacles()"""
		if start_pos == end_pos:
			return True
		start_x, start_y = start_pos
		end_x, end_y = end_pos
		dx = (start_x - end_x)
		dy = (start_y - end_y)
		if abs(dy) >= abs(dx):
			k = dx/dy
			if start_y > end_y:
				start_x, end_x = end_x, start_x
				start_y, end_y = end_y, start_y
			for y in xrange(end_y - start_y + 1):
				p1 = (int(floor(start_x + k*y)), start_y + y)
				p2 = (int(ceil(start_x + k*y)), start_y + y)
				if not self.is_free(p1, static=static) and not self.is_free(p2, static=static):
					return False
		else:
			k = dy/dx
			if start_x > end_x:
				start_x, end_x = end_x, start_x
				start_y, end_y = end_y, start_y
			for x in xrange(end_x - start_x + 1):
				p1 = (start_x + x, int(floor(start_y + k*x)))
				p2 = (start_x + x, int(ceil(start_y + k*x)))
				if not self.is_free(p1, static=static) and not self.is_free(p2, static=static):
					return False
		return True

	def add(self, a):
		"""add to **dynamic/static/list** grid"""
		static = a.static
		if static:
			for p in square(a.grid_pos, a.grid_size):
				if p in self.static_grid:
					self.static_grid[p] += 1
				else:
					self.static_grid[p] = 1
				if p in self.list_grid:
					self.list_grid[p].append(a)
				else:
					self.list_grid[p] = [a]
		else:
			for p in square(a.grid_pos, a.grid_size):
				if p in self.dynamic_grid:
					self.dynamic_grid[p] += 1
				else:
					self.dynamic_grid[p] = 1
				if p in self.list_grid:
					self.list_grid[p].append(a)
				else:
					self.list_grid[p] = [a]

	def remove(self, a):
		"""remove from **dynamic/static/list** grid"""
		static = a.static
		if static:
			for p in square(a.grid_pos, a.grid_size):
				if self.static_grid[p] == 1:
					del self.static_grid[p]
				else:
					self.static_grid[p] -= 1
				if len(self.list_grid[p]) == 1:
					del self.list_grid[p]
				else:
					self.list_grid[p].remove(a)
		else:
			for p in square(a.grid_pos, a.grid_size):
				if self.dynamic_grid[p] == 1:
					del self.dynamic_grid[p]
				else:
					self.dynamic_grid[p] -= 1
				if len(self.list_grid[p]) == 1:
					del self.list_grid[p]
				else:
					self.list_grid[p].remove(a)

	def update(self, a):
		static = a.static
		grid_pos = self.get_xy(a.pos)
		if grid_pos != a.grid_pos:
			self.remove(a)
			self.grid_pos = grid_pos
			self.add(a)

	def get_xy(self, v):
		"""object with obj.x and obj.y attributes --> (x, y) on the grid"""
		return (int(round(v.x)), int(round(v.y)))

	def get_obstacle(self, pos, s=None, static=False):
		"""recursive, return set;
		obstacle is set of adjacent non-free points"""
		if s is None:
			s = set()
		if self.is_free(pos, static=static):
			return s
		else:
			s.add(pos)
			check_list = [(pos[0] - 1, pos[1]), (pos[0] + 1, pos[1]), (pos[0], pos[1] - 1), (pos[0], pos[1] + 1)]
			return set().union(*[self.get_obstacle(pos=p, s=s) for p in check_list if p not in s])

	def get_obstacles(self, pos1, pos2, more=True, static=False):
		"""return list of obstacles between the INT points"""
		if pos1 == pos2:
			return []
		points = [] # of non-free points
		dx = (pos1[0] - pos2[0])
		dy = (pos1[1] - pos2[1])
		if abs(dy) >= abs(dx):
			k = dx/dy
			if pos1[1] > pos2[1]:
				pos1, pos2 = pos2, pos1
			for y in xrange(pos2[1] - pos1[1] + 1):
				p1 = (int(floor(pos1[0] + k*y)), pos1[1] + y)
				p2 = (int(ceil(pos1[0] + k*y)), pos1[1] + y)
				if more:
					points += [p for p in (p1, p2) if not self.is_free(p)]
				elif not self.is_free(p1, static=static) and not self.is_free(p2, static=static):
					points.append(p1)
		else:
			k = dy/dx
			if pos1[0] > pos2[0]:
				pos1, pos2 = pos2, pos1
			for x in xrange(pos2[0] - pos1[0] + 1):
				p1 = (pos1[0] + x, int(floor(pos1[1] + k*x)))
				p2 = (pos1[0] + x, int(ceil(pos1[1] + k*x)))
				if more:
					points += [p for p in (p1, p2) if not self.is_free(p, static=static)]
				elif not self.is_free(p1, static=static) and not self.is_free(p2, static=static):
					points.append(p1)
		obstacles = []
		for point in points:
			# obstacle = self.get_obstacle(p, s=set())
			# if obstacle not in obstacles:
			# 	obstacles.append(obstacle)
			if all(point not in obstacle for obstacle in obstacles):
				obstacles.append(self.get_obstacle(point,static=static))
			# TODO: DEFINE fastest method (?)
		return obstacles

	def _get_contacts(self, pos, obstacle):
		"""return contact points of tangent through the point to the obstacle"""
		if len(obstacle) == 0:
			return tuple()
		angle = lambda p: get_angle(to_vector((p[0] - pos[0], p[1] - pos[1])))
		d = lambda p: dist(pos, p)
		p1 = max(obstacle, key=lambda p: (angle(p), -d(p)))
		p2 = min(obstacle, key=lambda p: (angle(p), d(p)))
		return (p1, p2)

	def get_contacts(self, pos1, pos2, obstacle, more=False, static=False):
		"""return shifted contacts"""
		x = self._get_contacts(pos1, obstacle)
		if not x:
			return tuple()
		p1, p2 = x
		if more:
			v1 = filter(lambda p: self.is_free(p, static=static) and self.path_is_free(pos1, p, static=static), vicinity(p1))
			v2 = filter(lambda p: self.is_free(p, static=static) and self.path_is_free(pos1, p, static=static), vicinity(p2))
			fv1 = filter(lambda p: self.segment_is_free(pos1, p, static=static), v1)
			if fv1:
				v1 = fv1
			fv2 = filter(lambda p: self.segment_is_free(pos1, p, static=static), v2)
			if fv2:
				v2 = fv2
			return chain(v1, v2)
		else:
			p1 = to_vector(p1) + rotated((to_vector(p1) - to_vector(pos1)).normalized(), 90)*1.45 # sqrt(2) < 1.45 < 1.5
			p2 = to_vector(p2) - rotated((to_vector(p2) - to_vector(pos1)).normalized(), 90)*1.45 # ==> always to another grid pos
			return (to_pos(p1), to_pos(p2))

	def get_bounds(self, start_pos, end_pos, static=True):
		obstacles = self.get_obstacles(start_pos, end_pos, more=True, static=static)
		max_x = max(chain(*obstacles), key=lambda p: p[0])
		min_x = min(chain(*obstacles), key=lambda p: p[0])
		max_y = max(chain(*obstacles), key=lambda p: p[1])
		min_y = min(chain(*obstacles), key=lambda p: p[1])
		return max_x, min_x, max_y, min_y

	def get_wave_path(self, pos1, pos2, bounds=False, static=False):
		"""Calculate shortest path with Wave (Lee) algorithm"""
		# TODO: ADD bounds search
		# TODO: FIX dual wave algorithm
		d = {}
		d[pos1] = i = 0
		condition = lambda p: self.is_free(p, static=static)
		if bounds:
			max_x, min_x, max_y, min_y = self.get_bounds(pos1, pos2)
			condition = lambda p: (min_x < p[0] < max_x) and (min_y < p[1] < max_y) and self.is_free(p, static=static)
		while pos2 not in d and i < Grid.max_path_length:
			for pos in [pos for pos in d if d[pos] == i]:
				for p in filter(lambda p: p not in d and condition(p), vicinity(pos)):
					d[p] = i + 1
			i += 1
		if i == Grid.max_path_length:
			return []
		path = [pos2]
		j = i
		while j > 0:
			j -= 1
			variants = filter(lambda p: p in d and d[p] == j, vicinity(path[-1]))
			if variants:
				path.append(variants[0])
			else:
				return []
		return list(reversed(path))

	def __get_dual_wave_path(self, pos1, pos2, bounds=False, static=False):
		"""Calculate shortest path with Wave (Lee) algorithm (dual wave)"""
		# TODO: ADD bounds search
		# FIXME: doesn't work
		condition = lambda p: self.is_free(p, static=static)
		if bounds:
			max_x, min_x, max_y, min_y = self.get_bounds(pos1, pos2)
			condition = lambda p: (min_x < p[0] < max_x) and (min_y < p[1] < max_y) and self.is_free(p, static=static)
		d = {}
		d[pos1] = d[pos2] = i = 0
		intercept = False
		while not intercept and 2*i < Grid.max_path_length:
			for x in (1, -1): # from start and from end
				if not intercept: # if intercept: break
					wave_front = filter(lambda p: d[p] == x*i, d)
					if not wave_front:
						return []
					for pos in wave_front:
						outskirt = filter(lambda p: -x*d.get(p, -x) > 0 and condition(p), vicinity(pos))
						for p in outskirt:
							if -x*d.get(p, x) > 0:
								intercept = True
								intercept_pos = p
							else:
								d[p] = x*(i + 1)
			i += 1
		if not intercept:
			return []
		path = [intercept_pos]
		end = False
		j = d[min(filter(lambda p: d.get(p, -1) > 0, vicinity(intercept_pos)), key=lambda p: d[p])] + 1# see path around intercept_pos
		while not end and j >= 0:
			j -= 1
			variants = filter(lambda p: d.get(p, j + 1) == j, vicinity(path[-1]))
			if variants:
				if pos1 in variants:
					end = True
				else:
					path.append(variants[0])
			else:
				return []
		path = path[::-1] # reverse --> (pos1; intercept_pos]
		end = False
		j = d[max(filter(lambda p: d.get(p, +1) < 0, vicinity(intercept_pos)), key=lambda p: d[p])] - 1 # see path around intercept_pos
		while not end and j <= 0:
			j += 1
			variants = filter(lambda p: d.get(p, j + 1) == j, vicinity(path[-1]))
			if variants:
				if pos2 in variants:
					end = True
				path.append(variants[0])
			else:
				return []
		return path

	def get_full_path(self, pos1, pos2, check=True, simplify=True, static=False):
		if self.path_is_free(pos1, pos2, static=static):
			path = [pos2]
		else:
			path = self.get_wave_path(pos1, pos2, bounds=False, static=static)
			# path, length = self.get_path(pos1, pos2, static=static)
		if path:
			if check:
				for i in xrange(len(path) - 1):
					if not self.path_is_free(path[i], path[i + 1], static=static):
						print "-broken chain: {} --> {}".format(path[i], path[i + 1])
					if not self.segment_is_free(path[i], path[i + 1], static=static):
						print "!weak chain: {} --> {}".format(path[i], path[i + 1])
			if simplify:
				j = 0
				for i in xrange(len(path) - 2):
					if self.segment_is_free(path[i-j], path[i-j+2], static=static):
						del path[i-j+1]
						j += 1
		return path

	def get_near_free(self, pos, limit=5, static=False):
		x0, y0 = pos
		return min((p for p in square(pos, limit) if self.is_free(p, static=static)), key=lambda p: dist(pos, p))