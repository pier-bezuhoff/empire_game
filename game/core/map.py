# Python imports
# Panda3d imports
from panda3d.core import LPoint3 as Point
# Game imports
from grid import Grid
from flag import Flag
from unit import Unit

model_paths = {
	'flat': "./lib/maps/flat",
	'standard': "./lib/maps/standard"}

class Map(Unit):
	"""map contains towns, obstacles and grid;
	map is single"""
	def __init__(self, kind, render, loader, pos=None):
		self.pos = pos or Point(0, 0, 0)
		self.render = render
		self.loader = loader
		Unit.__init__(self, kind=kind, pos=self.pos, model=self.loader.loadModel(model_paths[kind]))
		self.model.reparent_to(self.render)
		self.model.find("**/Grid").node().set_python_tag('host', Map)
		self.grid = Grid()
		self.towns = {flag: [] for flag in Flag.flags.values()}
		self.obstacles = []

		Map.map = self

	def __repr__(self):
		return "Map({}, {}, {}, {})".format(self.kind, self.render, self.loader, self.pos)

	def __str__(self):
		return "<Game map at {}>".format(self.pos)

	def update(self, dt=1):
		for flag in self.towns:
			for town in self.towns[flag]:
				town.update(dt=dt)

	def add_town(self, town):
		self.towns[town.flag].append(town)

	def remove_town(self, town):
		self.towns[town.flag].remove(town)

	def add_obstacle(self, obstacle):
		self.obstacles.append(obstacle)
		obstacle.model.reparent_to(self.render)
		obstacle.model.set_z(0.1)
		obstacle.grid_pos = self.grid.get_xy(obstacle.pos)
		self.grid.add(obstacle)

	def remove_obstacle(self, obstacle):
		self.obstacles.remove(obstacle)
		obstacle.model.remove_node()
		self.grid.remove(obstacle)

	def remove_obstacles(self):
		for obstacle in self.obstacles[:]:
			obstacle.destroy()

class Obstacle(Unit):

	grid_size = 0
	static = True

	def __init__(self, pos):
		Unit.__init__(self, kind='obstacle', pos=pos, model=Map.map.loader.loadModel("./lib/other/obstacle"))
		self.static = Obstacle.static
		self.grid_size = Obstacle.grid_size
		Map.map.add_obstacle(self)

	def destroy(self):
		Map.map.remove_obstacle(self)