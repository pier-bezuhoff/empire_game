# Python imports
from time import time
from itertools import chain
# Game imports
from core import Goal, distance

class Transport(object):
	"""distribute deliveries and manage valets"""
	kind_table = {i: ['storage'] for i in xrange(100)} # where any resource might be
	kind_table[1] += ['sawmill'] # planks
	kind_table[2] += ['quarry'] # stones
	kind_table[3] += []
	kind_table[4] += []
	kind_table[5] += []
	kind_table[6] += ['bakery'] # bread
	kind_table[7] += []
	kind_table[8] += []
	kind_table[9] += []
	kind_table[10] += []
	kind_table[11] += []
	kind_table[12] += []
	kind_table[13] += []
	kind_table[14] += []
	kind_table[15] += []
	kind_table[16] += []
	kind_table[17] += []
	kind_table[18] += ['hut forester'] # wood
	kind_table[19] += ['farm'] # wheat
	kind_table[20] += ['mill'] # flour
	k = 0.1 # priority += k per second

	def __init__(self, town):
		self.town = town
		self.orders = {i: [] for i in xrange(100)} # queue of orders to become delivery
		self.queue = [] # queue of deliveries
		self.free_valets = []

	def __repr__(self):
		return "Transport({})".format(self.town)

	def __str__(self):
		return "<Transport in {}>".format(self.town)

	def update(self, dt=1):
		t = time()
		for i in self.orders:
			self.candidates = list(chain(*[[[b, b._store[i]] for b in self.town.building_dict[kind] if b._store[i] > 0] for kind in Transport.kind_table[i]]))
			self.orders[i].sort(key=lambda o: o[2] + Transport.k*(t  -o[1]), reverse=True)
			while len(self.orders[i]) > 0 and len(self.candidates) > 0:
				self.make_delivery(i)
			self.candidates = [c for c in self.candidates if not c[0].kind == 'storage']
			while len(self.candidates) > 0:
				self.make_delivery_to_storage(i)
		self.queue.sort(key=lambda x: x.priority + Transport.k*(x.time - t), reverse=True)
		while len(self.free_valets) > 0 and len(self.queue) > 0: # distribute deliveries
			self.start_delivery()

	def book_delivery(self, product, goal_to, priority):
		"""remember order"""
		self.orders[product].append((goal_to, time(), priority))

	def make_delivery(self, i):
		"""order --> delivery (set goal_from)"""
		order = self.orders[i].pop(0)
		goal_to = order[0]
		candidate = min(self.candidates, key=lambda c: distance(c[0], goal_to))
		Delivery(product=i, goal_from=candidate[0], goal_to=goal_to, priority=order[2] + Transport.k*(time() - order[1]))
		candidate[0]._store[i] -= 1
		if candidate[1] >= 2:
			self.candidates[self.candidates.index(candidate)][1] -= 1
		else:
			self.candidates.remove(candidate)

	def make_delivery_to_storage(self, i):
		"""rest to storage --> delivery"""
		candidate = self.candidates[0]
		storage = min(self.town.building_dict['storage'], key=lambda storage: distance(candidate[0], storage))
		Delivery(product=i, goal_from=candidate[0], goal_to=storage, priority=storage.priority)
		candidate[0]._store[i] -= 1
		if candidate[1] >= 2:
			self.candidates[self.candidates.index(candidate)][1] -= 1
		else:
			self.candidates.remove(candidate)

	def add_delivery(self, delivery):
		self.queue.append(delivery)

	def get_delivery(self):
		return self.queue.pop(0)

	def start_delivery(self):
		"""self.queue --> delivery --> valet <-- self.free_valets"""
		delivery = self.get_delivery()
		goal_from = Goal(delivery.goal_from.door_pos)
		valet = min(self.free_valets, key=lambda x: distance(x, goal_from))
		self.free_valets.remove(valet)
		valet.new_delivery(delivery)
		valet.update_menu()

class Delivery(object):

	def __init__(self, product, goal_from, goal_to, priority):
		self.product = product
		self.goal_from = goal_from
		self.goal_to = goal_to
		self.priority = priority
		self.time = time()
		assert goal_from != goal_to, "cycling delivery (on {} of {})".format(goal_to, product)
		self.goal_to.town.transport.add_delivery(self)

	def __repr__(self):
		return "Delivery({}, {}, {}, {})".format(self.product, self.goal_from, self.goal_to, self.priority)

	def __str__(self):
		return "<Delivery of {} from {}\nto {} with priority {}>".format(self.product, self.goal_from, self.goal_to, self.priority)

def Order(product, goal_to, priority):
	goal_to.town.transport.book_delivery(product, goal_to, priority)
