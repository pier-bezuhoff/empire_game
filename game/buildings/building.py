# Python imports
from copy import copy
# Game imports
from .standing import Standing
from ..core.core import to_pos, to_point
from ..creatures.citizen import Citizen

class Building(Standing):

	building_table = {}
	in_time = 1
	grid_size = 1 # 3x3

	def __init__(self, kind, pos, town, direction=0, store=None, health=2, in_product=None, out_product=None, priority=0):
		Standing.__init__(self, kind=kind, pos=pos, direction=direction, have_door=True)
		self.flag = town.flag
		self.town = town
		self.menu = None
		self.store = copy(store)
		self._store = copy(store) # for calculating ('imaginary')
		self.in_people = []
		self.in_time = Building.in_time
		self.attendant = None # kind of worker
		self.max_health = self.health = health
		self.priority = priority
		self.in_product = copy(in_product) or []
		self.out_product = copy(out_product) or []
		self.grid_size = Building.grid_size
		self.town.add_building(self)

	def __repr__(self):
		return "Building({}, {}, {}, {}, {}, {}, {}, {})".format(self.kind, self.pos, self.town, self.direction, self.store, self.health, self.in_product, self.out_product)

	def __str__(self):
		return "<{} in {} at {}>".format(self.__class__.__name__, self.town, self._pos)

	@staticmethod
	def create(kind, pos, town):
		return Building.building_table[kind](pos=pos, town=town)

	def update(self, dt=1):
		if self.health <= 0:
			self.demolish()
		# elif self.health < self.max_health:
		# 	Repair(self)

	def change_health(self, dhealth):
		self.health += dhealth
		self.update_menu()

	def receive(self, i, count=1):
		"""to real store"""
		self.store[i] += count
		self.update_menu()

	def add_to_store(self, dict_):
		"""to both real and imaginary store"""
		for product, count in dict_.items():
			self.store[product] += count
			self._store[product] += count
		self.update_menu()

	def provide(self, i, count=1, imaginary=False):
		"""from real store"""
		self.store[i] -= count
		assert self.store[i] >= 0, "Negative product count in {} at {}".format(self.kind, self.pos)
		if imaginary:
			self._store[i] -= count
			assert self._store[i] >= 0, "Negative product count in {} at {}".format(self.kind, self.pos)
		self.update_menu()

	def ask(self):
		for product in self.in_product:
			for _ in xrange(self.max_volume - self._store[product]):
				self.town.transport.book_delivery(product, self, self.priority)
				self._store[product] += 1

	def produce(self, product): pass
	def craft(self, subject): pass
	def equip(self, creature): pass

	def enter(self, x):
		self.in_people.append(x)

	def leave(self, x):
		self.in_people.remove(x)

	def has_menu(self):
		return self.menu is not None

	def update_menu(self):
		if self.has_menu():
			self.menu.update()

	def demolish(self):
		self.town.remove_building(self)
		self.grid.remove(self.grid_pos, self)
		if self.has_menu():
			base.messenger.send("Item-Hide") # CHECK: global var?!

	@staticmethod
	def register(cls):
		Building.building_table[cls.kind] = cls
		return cls

@Building.register
class Storage(Building):

	kind = 'storage'
	price = {1: 10, 2: 10, 3: 4}
	health = 100
	priority = 1
	store = {i: 0 for i in xrange(100)}

	def __init__(self, pos, town, direction=0):
		Building.__init__(
			self,
			kind=Storage.kind,
			pos=pos,
			direction=direction,
			store=Storage.store,
			town=town,
			health=Storage.health,
			in_product=[x for x in xrange(100)],
			priority=Storage.priority)

@Building.register
class School(Building):

	kind = 'school'
	prices = {'valet': 1, 'builder': 1}
	recruiting_time = 10
	price = {1: 6, 2: 5, 3: 2}
	health = 100
	max_volume = 5 # 10
	priority = 40
	store = {10: 0}

	def __init__(self, pos, town, direction=0): # gold under #10
		Building.__init__(
			self,
			kind=School.kind,
			pos=pos,
			direction=direction,
			store=School.store,
			town=town,
			health=School.health,
			in_product=[10],
			priority=School.priority)
		self.max_volume = School.max_volume
		self.prices = copy(School.prices)
		self.queue = []
		self.recruiting = False
		self.recruiting_time = School.recruiting_time

	def update(self, dt=1):
		Building.update(self, dt=dt)
		self.ask()
		if self.recruiting:
			self.recruiting = (self.recruiting[0] + dt, self.recruiting[1])
			if self.recruiting[0] >= self.recruiting_time:
				self.recruit(self.recruiting[1])
			self.update_menu()
		elif self.queue and self.store[10]:
			assert self.queue[0] in self.prices, "unknown kind '{}' has been tried to be recruited".format(self.queue[0])
			if self.prices[self.queue[0]] <= self.store[10]:
				self.book(self.queue.pop(0))
				self.update_menu()

	def book(self, kind):
		self.provide(10, count=self.prices[kind], imaginary=True)
		self.recruiting = (0, kind)

	def recruit(self, kind):
		Citizen.create(kind=kind, pos=to_point(self.grid.get_near_free(to_pos(self.pos))), town=self.town)
		self.recruiting = False

	def order(self, kind):
		self.queue.append(kind)
		self.update_menu()

class CollectorBuilding(Building):

	def __init__(self, kind, pos, town, store=None, priority=0, health=2, max_volume=1, in_product=None, out_product=None, direction=0):
		Building.__init__(
			self,
			kind=kind,
			pos=pos,
			direction=direction,
			store=store,
			town=town,
			health=health,
			in_product=in_product,
			out_product=out_product,
			priority=priority)
		self.max_volume = max_volume
	
	def update(self, dt=1):
		Building.update(self, dt=dt)
		self.ask()

@Building.register
class Farm(CollectorBuilding):

	kind = 'farm'
	price = {1: 5, 2: 1}
	health = 75
	max_volume = 5
	store = {19: 0} # wheat
	priority = 10

	def __init__(self, pos, town, direction=0):
		CollectorBuilding.__init__(
			self,
			kind=Farm.kind,
			pos=pos,
			direction=direction,
			store=Farm.store,
			town=town,
			priority=Farm.priority,
			health=Farm.health,
			max_volume=Farm.max_volume,
			out_product=[19])