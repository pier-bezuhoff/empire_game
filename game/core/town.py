# Python imports
from itertools import chain
# Panda3d imports
from panda3d.core import LPoint3 as Point
# Game imports
from .map import Map
from .flag import Flag
from .transport import Transport
from ..creatures.citizen import Valet, Builder
from ..creatures.squad import Squad
from ..buildings.building import Building, Storage, School, Farm
from ..buildings.construction import Construction

class Town(object):
	"""a town contains buildings, constructions, squads and citizens and updates them"""
	building_kinds = ('storage', 'school', 'tavern', 'farm', 'bakery', 'mill', 'hut forester', 'sawmill', 'carpentry', 'quarry')

	def __init__(self, flag=None):
		self.flag = flag or Flag.flags['player']
		self.buildings = []
		self.building_dict = {kind: [] for kind in Town.building_kinds}
		self.squads = []
		self.citizens = []
		self.constructions = []
		self.construction = None # current construction
		self.transport = Transport(town=self)
		Map.map.add_town(self)

	def __repr__(self):
		return "Town({})".format(self.flag)

	def __str__(self):
		return "<Town of {}>".format(self.flag.name)

	def update(self, dt=1):
		self.transport.update(dt=dt)
		if len(self.constructions) > 0:
			self.construction = self.constructions[0]
		for x in chain(self.buildings, self.squads, self.citizens, self.constructions):
			x.update(dt=dt)

	def show_unit(self, x):
		"""display the unit"""
		x.model.reparent_to(Map.map.render)
		x.model.set_z(Map.map.model.get_z())
		x.grid = Map.map.grid
		x.grid_pos = x.grid.get_xy(x.pos)
		x.grid.add(x)
		# x.adjust_z(Map.map.model.evaluate(x.pos.x, x.pos.y))

	def hide_unit(self, x):
		"""hide the unit"""
		x.model.remove_node()
		x.grid.remove(x)
		x.grid = None

	def add_construction(self, construction):
		self.constructions.append(construction)
		self.show_unit(construction)

	def remove_construction(self, construction):
		self.hide_unit(construction)
		self.constructions.remove(construction)

	def add_building(self, building):
		self.buildings.append(building)
		self.building_dict[building.kind].append(building)
		self.show_unit(building)

	def remove_building(self, building):
		self.hide_unit(building)
		self.building_dict[building.kind].remove(building)
		self.buildings.remove(building)

	def add_squad(self, squad, show=True):
		self.squads.append(squad)
		if show:
			for x in squad.composition:
				x.town = self
				self.show_unit(x)
		squad.town = self

	def remove_squad(self, squad, hide=True):
		if hide:
			for x in squad.composition:
				self.hide_unit(x)
		self.squads.remove(squad)

	def add_citizen(self, citizen):
		self.citizens.append(citizen)
		self.show_unit(citizen)

	def remove_citizen(self, citizen):
		self.hide_unit(citizen)
		self.citizens.remove(citizen)

	def has_construction(self):
		return self.construction is not None

	def create_construction(self, kind, pos, direction):
		cls = Building.building_table[kind]
		Construction(cls=cls, pos=pos, town=self, direction=direction)

	def create_test_town(self):
		Storage(pos=Point(0, 0, 0), town=self).add_to_store({1: 100, 2:100, 3: 150, 10: 200})
		School(pos=Point(-5, -5, 0), town=self, direction=180)
		# School(pos=Point(0, -5, 0), town=self, direction=90)
		# School(pos=Point(5, -5, 0), town=self, direction=180)
		Farm(pos=Point(7, -1, 0), town=self)
		Valet(pos=Point(3, -3, 0), town=self)
		Valet(pos=Point(3, -4, 0), town=self)
		Builder(pos=Point(1, -4, 0), town=self)
		Squad.create(kind='ralph', pos=Point(0, 5, 0), town=self, n=4)

	def destroy(self):
		Map.map.remove_town(self)