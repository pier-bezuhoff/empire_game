# Panda3D imports
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
# from direct.fsm.FSM import FSM
from panda3d.core import (
	LPoint3 as Point,
	CollisionRay, CollisionTube, CollisionNode)

# Game imports
from ..core.core import Goal, to_pos, to_point, distance, get_angle
from ..core.unit import Unit

limit = 0.001 # motion accuracy

actor_paths = {
	'valet': ("./lib/units/ralph", {'walk': "./lib/units/ralph-walk", 'run': "./lib/units/ralph-run"}),
	'builder': ("./lib/units/ralph", {'walk': "./lib/units/ralph-walk", 'run': "./lib/units/ralph-run"}),
	'ralph': ("./lib/units/ralph", {'walk': "./lib/units/ralph-walk", 'run': "./lib/units/ralph-run"})} # delete
actor_scales = {
	'valet': 0.1,
	'builder': 0.1,
	'ralph': 0.1} # delete

class Creature(Unit):

	static = False
	speed = 1.0
	direction = 0.0
	full_satiety = 100 # (%)
	min_health = 1

	grid_size = 0

	r = 1.0 # TODO: add own actors
	h = 5.0

	def __init__(self, kind, pos, town, direction=None, speed=None, health=None, satiety=None):
		Unit.__init__(self, kind=kind, pos=pos, model=Actor(*actor_paths[kind]), model_scale=actor_scales[kind])
		self.animation = None
		self.collision_node = CollisionNode("creature_tube")
		self.model.attach_new_node(self.collision_node) #.show()
		scr = Creature.r # /creature.model_scale # scaled r
		sch = Creature.h # /creature.model_scale # scaled h
		pos = self.pos*self.model_scale
		self.collision_node.add_solid(CollisionTube(pos, pos + Point(0, 0, sch), scr))
		self.collision_node.set_python_tag('host', self)
		# self.from_collision_node = CollisionNode("creature_ray")
		# self.from_node_path = self.model.attach_new_node(self.from_collision_node)
		# self.from_node_path.show()
		# self.from_collision_node.add_solid(CollisionRay(pos.x, pos.y, pos.z + sch, 0, 0, -1))
		# self.from_collision_node.set_python_tag('host', self)
		self.direction = direction or Creature.direction
		self.speed = speed or Creature.speed
		self.town = town
		self.flag =town.flag
		self.max_health = self.health = health or Creature.min_health
		self.satiety = satiety or Creature.full_satiety
		self.path =[]
		self.goal = None
		self.target = None
		# self.moving = False
		self.interval = None
		self.grid = None
		self.grid_pos = None
		self.grid_size = Creature.grid_size
		self.squad = None
		self.menu = None

	def __repr__(self):
		return "Creature({}, {}, {}, {}, {}, {}, {})".format(self.kind, self.pos, self.town, self.direction, self.speed, self.health, self.satiety)

	def __str__(self):
		return "<{} in {} at {}>".format(self.__class__.__name__, self.town, self.pos)

	def update(self, dt=1):
		if self.has_goal():
			self.move(dt=dt)
		elif self.target is not None:
			self.attack(dt=dt)
		else:
			self.stop()
		if self.satiety == 0 or self.health <= 0:
			self.die()
		# self.huger()

	def free_grid(self):
		self.grid.remove(self)

	def occupy_grid(self):
		self.grid_pos = self.grid.get_xy(self.pos)
		self.grid.add(self)
		self.update_menu()

	def update_pos(self):
		self.pos = self.model.get_pos()
		self.grid.update(self)
		self.update_menu()

	def new_animation(self, animation):
		self.animation = animation
		self.model.stop()
		self.model.loop(self.animation)

	def _turn(self, direction=None):
		"""turn (in degrees)"""
		if direction is None:
			direction = self.direction
		self.direction = direction
		self.model.set_h(direction)

	def turn(self, direction):
		"""stop & turn (in degrees)"""
		self.direction = direction
		self.stop()

	def rotate(self, angle):
		"""stop & rotate (in degrees)"""
		self.direction += angle
		self.stop()

	def turn_to(self, pos):
		"""turn to the pos"""
		self.direction = get_angle(pos - self.pos)
		self.turn()

	def start_pos_interval(self, goal=None):
		self.pos = self.model.get_pos()
		goal = goal or self.goal
		angle = get_angle((goal.pos - self.pos).normalized())
		if angle is not None:
			self.model.set_h(angle)
		t = distance(self, goal)/self.speed
		self.interval = LerpPosInterval(self.model, duration=t, pos=goal.pos)
		self.interval.start()
		if self.animation != 'walk':
			self.new_animation('walk')

	def move(self, dt=1):
		if self.has_interval():
			if self.interval.is_playing():
				self.update_pos()
				# check for collisions
			else:
				if self.has_path():
					self.start_pos_interval(goal=self.path.pop(0))
					self.update_menu()
				else:
					self.stop()
		else:
			self.new_path()

	def new_path(self):
		end_pos = self.grid.get_near_free(to_pos(self.goal.pos), static=True)
		path = self.grid.get_full_path(self.grid_pos, end_pos, static=True)
		if not path:
			self.stop()
			print("No way ({})".format(self))
		else:
			self.path = [Goal(to_point(p)) for p in path[:-1]]
			self.path.append(self.goal)
			self.start_pos_interval(goal=self.path.pop(0))
			self.update_menu()

	def __move(self, dt=1, goal=None):
		# from direct.interval.IntervalGlobal import *
		# LerpPosInterval(model, duration, pos, startPos=None, other=None, blendType='noBlend', bakeInStart=1, fluid=0, name=None)
		# ProjectileInterval(<Node Path>, startPos = Point3(X,Y,Z), endPos
		# 	= Point3(X,Y,Z),
		# 	duration = <Time in seconds>, startVel = Point3(X,Y,Z), endZ = Point3(X,Y,
		# 	Z),
		# 	gravityMult = <multiplier>, name = <Name>)
		# an_actor.actorInterval
		# 	(
		# 	"Animation Name",
		# 	loop= <0 or 1>,
		# 	contrainedLoop= <0 or 1>,
		# 	duration= D,
		# 	startTime= T1,
		# 	endTime= T2,
		# 	startFrame= N1,
		# 	endFrame= N2,
		# 	playRate = R
		# 	partName = PN,
		# 	lodName = LN,
		# 	)
		# Sequence, Parallel
		# delay = Wait(2.5)
		self.free_grid()
		goal = goal or self.goal
		direction_v = (goal.pos - self.pos).normalized()
		if distance(self, goal) > self.speed*dt:
			self.model.set_pos(self.pos + direction_v*self.speed*dt)
		else:
			self.model.set_pos(goal.pos)
		self.model.set_h(get_angle(direction_v))
		# self.adjust_z()
		self.pos = self.model.get_pos()
		if self.animation != 'walk':
			self.new_animation('walk')
		self.occupy_grid()

	def move_along_path(self, dt=1):
		self.update_grid()
		self.pos = self.model.get_pos()
		if self.has_interval() and not self.interval.is_playing():
			if self.path:
				self.start_pos_interval(goal=self.path.pop(0))
			else:
				self.interval = None
		if not self.has_interval():
			if distance(self, self.goal) <= limit:
				self.stop() # end
			elif self.goal and not self.path: # and self.grid.is_free(to_pos(self.goal.pos), static=True):
				goal_pos = to_pos(self.goal.pos)
				if self.grid.is_free(goal_pos, static=True):
					free_end_pos = goal_pos
				elif 'door_pos' in dir(self.goal):
					free_end_pos = to_pos(self.goal.door_pos) #?
				else:
					free_end_pos = None
				path = []
				if free_end_pos:
					path = self.grid.get_full_path(self.grid_pos, free_end_pos, static=True)
				if not path:
					self.stop()
				else:
					self.path = [Goal(to_point(p)) for p in path][:-1] + [self.goal]
					self.start_pos_interval(goal=self.path.pop(0))

	def __move_along_path(self, dt=1):
		# TODO: LerpInterval's...
		if self.path: # go through path
			if distance(self, self.path[0]) > limit:
				self.move(dt=dt, goal=self.path[0])
			else:
				self.path.pop(0) # 1 skip on path element
		elif distance(self, self.goal) > limit: # accuracy...
			self.move(dt=dt)
		elif distance(self, self.goal) <= limit: # end path
			self.goal = None
		elif self.goal and self.grid.is_free(to_pos(self.goal.pos), static=True): # generate new path
			path = self.grid.get_full_path(self.grid_pos, self.grid.get_xy(self.goal.pos), static=True)
			if not path:
				self.stop()
			else:
				self.path = [Goal(to_point(p)) for p in path]

	def new_goal(self, pos):
		self.stop()
		self.goal = Goal(pos, to_int=False)

	def cancel_goal(self):
		pass

	def stop(self):
		if self.has_interval():
			self.interval.pause()
			self.interval = None
		self.cancel_goal()
		self.goal = None
		self.path = []
		self._turn()
		if self.has_animation():
			self.new_animation(None)
		self.update_menu()

	def adjust_z(self):
		# self.model.set_z(Map.map.model.evaluate(pos.x, pos.y))
		pass

	def attack(self, dt=1):
		if self.animation is not None: # != 'attack':
			self.new_animation(None) # ('attack')
		# new_path --> self.target

	def __hunger(self): # QUESTION: ?
		self.satiety -= 1
		if self.satiety < 10:
			self.health -= 1

	def has_path(self):
		return self.path

	def has_animation(self):
		return self.animation is not None

	def has_interval(self):
		return self.interval is not None

	def has_town(self):
		return self.town is not None

	def has_goal(self):
		return self.goal is not None

	def has_squad(self):
		return self.squad is not None

	def has_menu(self):
		return self.menu is not None

	def update_menu(self):
		if self.has_menu():
			self.menu.update()

	def die(self):
		if self.has_squad():
			self.squad.unjoin(self)
		if self.animation is not None: # != 'die':
			self.new_animation(None) # ('die')
		if self.has_menu():
			base.messenger.send("Item-Hide") # CHECK: global var?!