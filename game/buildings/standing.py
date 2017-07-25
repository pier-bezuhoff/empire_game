# Panda3D imports
from panda3d.core import LPoint3 as Point, BitMask32
# Game imports
from ..core.core import rotated, vicinity, to_pos, to_point
from ..core.unit import Unit
from ..core.map import Map

model_paths = {
	'storage': "./lib/buildings/storage/storage",
	'school': "./lib/buildings/school/school",
	'tavern': "./lib/buildings/cube/cube",
	'farm': "./lib/buildings/farm/farm",
	'construction': "./lib/buildings/cube/cube"}

class Standing(Unit):

	static = True

	def __init__(self, kind, pos, direction=0, have_door=False):
		Unit.__init__(self, kind=kind, pos=pos, model=Map.map.loader.loadModel(model_paths[kind]))
		self._pos = pos
		self.model.set_h(direction)
		self.direction = direction
		if have_door:
			door_pos = rotated(Point(self.model.find("**/Door").get_pos()), direction) + self.pos
			self.door_pos = to_point(filter(lambda pos: True, vicinity(to_pos(door_pos), small=True))[0], z=door_pos.z)
			self.pos = Point(door_pos.x, door_pos.y, door_pos.z)
		self.model.find("**/Collide").node().set_from_collide_mask(BitMask32.all_off())
		self.model.find("**/Collide").node().set_into_collide_mask(BitMask32.bit(1))
		self.model.find("**/Collide").node().set_python_tag('host', self)