# Python imports
from math import ceil
# Panda3D imports
from panda3d.core import LVector3 as V3
# Game imports
from ..core.core import Goal, rotated
# from .warrior import Warrior
from .creature import Creature
from ..buildings.building import Building

class Squad(object):

	interval = 1.0 # distance between warriors (in row and in column)

	def __init__(self, composition, town, n_rows=1, name=None, load=False):
		self.composition = []
		self.flag = town.flag
		town.add_squad(self)
		self.n_rows = n_rows
		self.menu = None
		self.join_list(composition, load=load)
		# ringleader is left top warrior when the squad is directed up (nw)
		self.target = None
		self.name = name
		self.update_logic()
		self.stop()

	def __iter__(self):
		return iter(self.composition)

	@staticmethod
	def create(kind, pos, town, n=1):
		assert n >= 1, "min squad length is 1"
		from .warrior import Warrior
		squad = Warrior.create(kind=kind, pos=pos, town=town).squad
		for i in xrange(n - 1):
			Warrior.create(kind=kind, pos=pos + V3(0, i, 0), town=town, squad=squad)
		return squad

	def get_order_map(self):
		"""Return list of rows of numbers"""
		return [[i + j*self.n_columns for i in xrange(self.n_columns)] for j in xrange(self.n_rows)]

	def update(self, dt=1):
		if self.target is not None:
			self.attack(dt=dt)
		for x in self.composition:
			x.update(dt=dt)
		self.pos = self.ringleader.pos
		if not self.composition:
			self.destroy()

# TODO: columns!
	def update_logic(self, n_rows=None, n_columns=None, drows=0, dcolumns=0):
		"""recalculate number of columns and rows
		(usually after changing the squad length)"""
		n_rows = self.n_rows + drows
		self.ringleader = self.composition[0]
		self.pos = self.ringleader.pos
		self.direction = self.ringleader.direction
		self.length = len(self.composition)
		if n_rows is not None:
			self.n_rows = n_rows
		if self.n_rows > self.length:
			self.n_rows = self.length
		if self.n_rows <= 0:
			self.n_rows = 1
		self.n_columns = int(ceil(self.length/self.n_rows))
		self.update_menu()

	def direct(self, goal=None):
		"""direct the squad to the goal"""
		goal = goal or self.ringleader.goal # ringleader is 'nw'
		direction = self.ringleader.direction = self.direction
		for i in xrange(len(self.composition)):
			column = i%self.n_columns
			row = i//self.n_columns
			self.composition[i].direction = direction
			self.composition[i].new_goal(goal.pos + rotated(V3(column, row, 0)*Squad.interval, direction))
		self.update_menu()

	def attack(self, dt=1):
		"""for every warrior set squad target as target
		(target might be Creature, Squad, Construction or Building)"""
		if isinstance(self.target, Squad):
			for x in self.composition:
				x.target = self.target.get_nearest_to(x.pos)
		elif isinstance(self.target, Creature) or isinstance(self.target, Building):
			for x in self.composition:
				x.target = self.target

	def stop(self):
		"""stop the squad ringleader;
		other warriors in the squad go to their positions"""
		self.ringleader.direction = self.direction # ringleader is 'nw'
		self.direct(goal=Goal(self.ringleader.pos, to_int=False))
		self.ringleader.stop()

	def set_direction(self, direction):
		self.direction = direction
		for x in self.composition:
			x.direction = direction

	def turn(self, angle, in_degrees=True):
		"""turn & stop squad"""
		if not in_degrees:
			angle = 180.0*angle/pi
		self.ringleader.direction = angle
		self.stop()

	def new_goal(self, pos):
		self.direct(goal=Goal(pos, to_int=False))

	def new_target(self, target):
		self.target = target

	def add_column(self):
		self.update_logic(dcolumns=+1)
		self.stop()

	def remove_column(self):
		self.update_logic(dcolumns=-1)
		self.stop()

	def add_row(self):
		self.update_logic(drows=+1)
		self.stop()

	def remove_row(self):
		self.update_logic(drows=-1)
		self.stop()

	def join(self, x, update=True, load=False):
		"""join warrior to the squad"""
		if x.has_squad():
			x.squad.destroy(unload=False)
		x.squad = self
		x.town = self.town
		x.flag = self.flag
		self.composition.append(x)
		if load:
			self.town.show_unit(x)
		if update:
			self.update_logic()

	def join_list(self, composition, update=True, load=False):
		"""join list to the squad"""
		for x in composition:
			if x.has_squad():
				x.squad.destroy(unload=False)
			x.squad = self
			x.town = self.town
			x.flag = self.flag
			if load:
				self.town.show_unit(x)
		self.composition += composition
		if update:
			self.update_logic()

	def join_squad(self, squad):
		"""join given squad to the squad"""
		self.join_list(squad.composition)

	def unjoin_list(self, composition, unload=True):
		"""unjoin list from the squad"""
		for x in composition:
			self.composition.remove(x)
			if unload and self.has_town():
				self.town.hide_unit(x)
		self.update_logic()

	def unjoin(self, x, unload=True):
		"""unjoin list from the squad"""
		self.composition.remove(x)
		if unload and self.has_town():
			self.town.hide_unit(x)
		self.update_logic()

	def has_town(self):
		return self.town is not None

	def has_menu(self):
		return self.menu is not None

	def update_menu(self):
		if self.has_menu():
			self.menu.update()

	def get_nearest_to(self, pos):
		"""return nearest to given position warrior in the squad"""
		return min(self.composition, key=lambda x: (x.pos - pos).length())

	def destroy(self, unload=True):
		if self.has_town():
			self.town.remove_squad(self, hide=unload)
		if self.has_menu():
			base.messenger.send("Item-Hide") # CHECK: global var?!