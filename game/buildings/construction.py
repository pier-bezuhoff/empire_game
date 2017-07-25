# Python imports
from math import ceil
from copy import copy
# Game imports
from .standing import Standing
from .building import Building

class Construction(Standing):

	priority = 70
	in_time = 0
	grid_size = 1

	def __init__(self, cls, pos, town, health=1, direction=0):
		self._kind = cls.__name__.lower()
		Standing.__init__(self, kind=self._kind, pos=pos, have_door=True, direction=direction)
		self.cls = cls
		self.kind = "Constructing {}".format(self._kind)
		self.town = town
		self.flag = self.town.flag
		self.menu = None
		self.in_time = Construction.in_time
		self.priority = Construction.priority
		self.price = copy(self.cls.price)
		self.health = health
		self.max_health = self.cls.health
		self.dhealth = ceil((self.max_health)/sum(self.price.values()))
		self.price_length = sum(self.price.values())
		self.max_h = self.h = -1.5
		self.grid = None
		self.grid_pos = None
		self.grid_size = Construction.grid_size
		self.town.add_construction(self)
		self.ask()
		self.change_health(0)

	def __repr__(self):
		return "Construction({}, {}, {}, {}, {})".format(self.cls, self.pos, self.town, self.health, self.angle)

	def __str__(self):
		return "<{} in {} at {}>".format(self.kind, self.town, self.pos)

	def update(self, dt=1):
		if self.health <= 0:
			self.demolish()
		elif self.health >= self.max_health:
			self.build()

	def enter(self, x): pass
	def leave(self, x): pass

	def ask(self):
		for i in self.price:
			for _ in xrange(self.price[i]):
				self.town.transport.book_delivery(i, self, self.priority)

	def receive(self, i, count=1):
		self.price[i] -= count
		self.update_menu()

	def change_health(self, dhp):
		if dhp > 0:
			self.health = min(self.health + dhp, 1 + (self.price_length - sum(self.price.values()))*self.dhealth, self.max_health)
		else:
			self.health += dhp
		if self.health < self.max_health:
			self.h = self.max_h*(1.0 - self.health/self.max_health)
			self.model.set_z(self.h)
		self.update_menu()

	def can_change_health(self):
		# TODO: UPGRADE formula
		return self.health < (self.price_length - sum(self.price.values()))*self.dhealth and self.health < self.max_health

	def build(self):
		self.demolish()
		self = Building.create(kind=self._kind, pos=self.pos, town=self.town)

	def demolish(self):
		self.town.remove_construction(self)
		if self.has_menu():
			base.messenger.send("Item-Hide") # CHECK: global var?!

	def has_menu(self):
		return self.menu is not None

	def update_menu(self):
		if self.has_menu():
			self.menu.update()