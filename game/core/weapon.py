# Game imports
from ..core.unit import Unit
from ..core.map import Map

model_paths = {}
model_scales = {}

class Weapon(Unit):

	def __init__(self, kind, host, place, damage=1):
		Unit.__init__(self, kind=kind, pos=host.pos, model=Map.map.loader.loadModel(model_paths[kind]), model_scale=model_scales[kind])
		self.host = host
		self.place = place
		self.v = V3(0, 0, 0)
		self.damage = damage

	def update(self, dt=1):
		pass

	def throw(self):
		# ProjectileInterval
		pass