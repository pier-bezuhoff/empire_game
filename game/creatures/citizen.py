# Game imports
from .creature import Creature
from ..core.core import Goal, distance, to_point, to_pos

class Citizen(Creature):

	citizen_table = {}
	speed = 1.0
	health = 1
	enter_distance = 0.1

	def __init__(self, kind, pos, town, satiety=Creature.full_satiety):
		Creature.__init__(
			self,
			kind=kind,
			pos=pos,
			town=town,
			direction=Creature.direction,
			speed=Citizen.speed,
			health=Citizen.health,
			satiety=satiety)
		self.auto = True
		self.building = None
		self.inside = False
		self.enter_distance = Citizen.enter_distance
		self.in_time = 0
		town.add_citizen(self)

	def __repr__(self):
		return "Citizen({}, {}, {}, {})".format(self.kind, self.pos, self.town, self.satiety)

	def __str__(self):
		return "<{} in {} at {}>".format(self.__class__.__name__, self.town, self.pos)

	@staticmethod
	def create(kind, pos, town, satiety=Creature.full_satiety):
		return Citizen.citizen_table[kind](pos=pos, town=town, satiety=satiety)

	def update(self, dt=1):
		if self.auto:
			self.auto_update(dt=dt)
		elif self.has_goal() and not self.inside:
			self.move(dt=dt)
		else:
			self.auto = True
			self.new_auto()
		if self.health == 0 or self.satiety <= 0:
			self.die()

	def auto_update(self, dt=1): pass

	def new_auto(self): pass

	def new_manual(self): pass

	def new_goal(self, pos):
		self.stop()
		self.auto = False
		self.new_manual()
		self.goal = Goal(pos, to_int=False)

	def enter(self, building):
		self.free_grid()
		self.model.hide()
		building.enter(self)
		self.building = building
		self.inside = True
		self.in_time = 0

	def leave(self, building=None):
		building = building or self.building
		self.pos = to_point(self.grid.get_near_free(to_pos(building.pos), static=True))
		self.model.set_pos(self.pos)
		self.occupy_grid()
		self.model.show()
		building.leave(self)
		self.inside = False
		self.in_time = 0

	def move_by_road(self, dt=1):
		# TODO: ADD roads structure
		self.move(dt=dt)

	def free_road(self, dt=1):
		# TODO: ...roads...
		self.stop()

	def die(self):
		self.town.remove_citizen(self)
		if self.has_menu():
			base.messenger.send("Item-Hide") # CHECK: global var?!

	@staticmethod
	def register(cls):
		Citizen.citizen_table[cls.kind] = cls
		return cls

@Citizen.register
class Valet(Citizen):

	kind = 'valet'

	def __init__(self, pos, town, satiety=None):
		Citizen.__init__(self, kind=Valet.kind, pos=pos, town=town, satiety=satiety)
		self.product = None
		self.delivery = None
		self.town.transport.free_valets.append(self)

	def auto_update(self, dt=1):
		if self.has_delivery():
			if not self.inside:
				if distance(self, self.goal) > self.enter_distance:
					self.move_by_road(dt=dt)
				else:
					self.enter(self.goal)
					self.serve()
			else:
				if self.in_time >= self.building.in_time:
					self.leave()
				self.in_time += dt
		else:
			self.free_road(dt=dt)
		
	def serve(self):
		if not self.has_product():
			self.product = self.delivery.product
			self.building.provide(self.product)
			self.goal = self.delivery.goal_to
		else:
			self.building.receive(self.product)
			self.product = None
			self.goal = None
			self.delivery = None
			self.town.transport.free_valets.append(self)
		self.update_menu()

	def new_delivery(self, delivery):
		self.delivery = delivery
		self.goal = self.delivery.goal_from

	def new_auto(self):
		self.town.transport.free_valets.append(self)

	def new_manual(self):
		if self.has_delivery():
			self.town.transport.add_delivery(self.delivery)
			self.delivery = None
			self.product = None
		else:
			self.town.transport.free_valets.remove(self)

	def cancel_goal(self):
		if self.auto and self.has_delivery():
			self.town.transport.add_delivery(self.delivery)
			self.delivery = None
			self.product = None

	def has_delivery(self):
		return self.delivery is not None

	def has_product(self):
		return self.product is not None

	def die(self):
		Citizen.die(self)
		if self.auto:
			if self.has_delivery():
				self.town.transport.add_delivery(self.delivery)
			else:
				self.town.transport.free_valets.remove(self)

@Citizen.register
class Builder(Citizen):

	kind = 'builder'
	building_speed = 1
	build_distance = 2.0

	def __init__(self, pos, town, satiety=None):
		Citizen.__init__(self, kind=Builder.kind, pos=pos, town=town, satiety=satiety)
		self.construction = None

	def auto_update(self, dt=1):
		if not self.has_construction() and self.town.has_construction() and self.town.construction.can_change_health():
			self.construction = self.goal = self.town.construction
			self.update_menu()
		if self.has_construction():
			if self.construction.can_change_health():
				if distance(self, self.construction) > Builder.build_distance:
					self.move_by_road(dt=dt)
				else:
					self.build(dt=dt)
			else:
				self.construction = None
				self.update_menu()
		else:
			self.free_road(dt=dt)

	def build(self, dt=1):
		self.construction.change_health(dt*Builder.building_speed)
		self.rotate(10)
		# if self.animation != 'build':
		# 	self.new_animation('build')
		self.update_menu()

	def has_construction(self):
		return self.construction is not None

class CollectorCitizen(Citizen):
	pass

class Worker(Citizen):
	pass

@Citizen.register
class Recruit(Citizen):

	kind = 'recruit'