#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python imports
from __future__ import division
from functools import wraps
from sys import exit as sys_exit
from time import time

# Panda3D imports
from direct.showbase.ShowBase import ShowBase
from direct.fsm.FSM import FSM
from panda3d.core import (
	CollisionTraverser,
	AntialiasAttrib, TransparencyAttrib,
	CollisionHandlerQueue, CollisionRay, CollisionNode,
	loadPrcFileData, loadPrcFile,
	AmbientLight, DirectionalLight, LightAttrib,
	LPoint3 as Point, LVector3 as V3,
	BitMask32)

from game.core import core
from game.core.map import Map, Obstacle
from game.core.town import Town
from game.creatures.squad import Squad
from game.creatures.citizen import Citizen
from game.creatures.warrior import Warrior
from game.buildings.building import Building
from game.buildings.construction import Construction
from game.interface import menu, hud

app_name = "Empire Game"
loadPrcFileData("",
"""
	window-title {}
	# fullscreen 1
	win-size 1366 600
	cursor-hidden 0
	show-frame-rate-meter 1
""".format(app_name)) # 768

def setup_wrapper(f):
	"""wrap setup-functions"""
	@wraps(f)
	def wrapper(*args, **kwargs):
		name = f.__name__
		print "Setting up {}...".format(name.split('_')[-1]),
		t = time()
		f(*args, **kwargs)
		print "Done ({} s)".format(round(time() - t, 4))
	return wrapper

class Game(ShowBase, FSM):

	def __init__(self):
		"""create the game"""
		ShowBase.__init__(self)
		# FSM.__init__(self, "FSM-Game")
		self.disableMouse()
		self.setBackgroundColor(0, 0, 0)
		render.setAntialias(AntialiasAttrib.MAuto)
		# render.setShaderAuto()
		# DGG.getDefaultFont().setPixelsPerUnit(100)
		self.accept('escape', self.escape_from_game)
		self.setup_actions()
		# self.setup_lights()
		self.setup_units()
		self.setup_pointers()
		self.setup_collisions()
		self.setup_menus()
		taskMgr.add(self.camera_task, "camera_task")
		taskMgr.add(self.update, "update_task")
		print "Game has loaded now"

	@setup_wrapper
	def setup_actions(self):
		"""setup camera steering, keyboard and mouse event handling"""
		self.camera_dx = 0.05 # camera motion speed
		self.camera_dr = 0.3 # camera rotation speed
		self.rel_camera_motion = V3(0, 0, 0)
		self.abs_camera_motion = V3(0, 0, 0)
		self.camera_rotation = V3(0, 0, 0)
		self.accept('=', self.add_rel_camera_motion, [(0, self.camera_dx, 0)])
		self.accept('=-up', self.add_rel_camera_motion, [(0, -self.camera_dx, 0)])
		self.accept('-', self.add_rel_camera_motion, [(0, -self.camera_dx, 0)])
		self.accept('--up', self.add_rel_camera_motion, [(0, self.camera_dx, 0)])
		# TODO setup wheel and pressed wheel
		# self.accept('wheel_up', self.add_rel_camera_motion, [(0, self.camera_dx, 0), True])
		# self.accept('wheel_up-up', self.add_rel_camera_motion, [(0, -self.camera_dx, 0)])
		# self.accept('wheel_down', self.add_rel_camera_motion, [(0, -self.camera_dx, 0), True])
		# self.accept('wheel_down-up', self.add_rel_camera_motion, [(0, self.camera_dx, 0)])
		self.accept('arrow_right', self.add_rel_camera_motion, [(self.camera_dx, 0, 0)])
		self.accept('arrow_right-up', self.add_rel_camera_motion, [(-self.camera_dx, 0, 0)])
		self.accept('arrow_left', self.add_rel_camera_motion, [(-self.camera_dx, 0, 0)])
		self.accept('arrow_left-up', self.add_rel_camera_motion, [(self.camera_dx, 0, 0)])
		self.accept('arrow_up', self.add_abs_camera_motion, [(0, self.camera_dx, 0), True])
		self.accept('arrow_up-up', self.add_abs_camera_motion, [(0, -self.camera_dx, 0), True])
		self.accept('arrow_down', self.add_abs_camera_motion, [(0, -self.camera_dx, 0), True])
		self.accept('arrow_down-up', self.add_abs_camera_motion, [(0, self.camera_dx, 0), True])
		self.accept('w', self.add_abs_camera_motion, [(0, 0, self.camera_dx)])
		self.accept('w-up', self.add_abs_camera_motion, [(0, 0, -self.camera_dx)])
		self.accept('s', self.add_abs_camera_motion, [(0, 0, -self.camera_dx)])
		self.accept('s-up', self.add_abs_camera_motion, [(0, 0, self.camera_dx)])
		self.accept('a', self.add_camera_rotation, [(self.camera_dr, 0, 0)])
		self.accept('a-up', self.add_camera_rotation, [(-self.camera_dr, 0, 0)])
		self.accept('d', self.add_camera_rotation, [(-self.camera_dr, 0, 0)])
		self.accept('d-up', self.add_camera_rotation, [(self.camera_dr, 0, 0)])
		self.accept('alt', self.stop_camera)
		self.accept('mouse1', self.left_click)
		self.accept('mouse1-up', self.left_release)
		self.accept('mouse2', self.middle_click)
		self.accept('mouse3', self.right_click)
		self.accept('mouse3-up', self.right_release)
		self.accept('delete', self.clean)
		self.accept('backspace', self.clean)
		# debug
		self.accept('f', self.wireframeOn)
		self.accept('f-up', self.wireframeOff)

		self.camera_min_h = 1.0
		self.camera.set_pos_hpr(0, -12, 8, 0, -35, 0)
		self.mode = ""

	@setup_wrapper
	def setup_lights(self):
		"""setup directional and ambient light"""
		ambientLight = AmbientLight("ambientLight")
		ambientLight.set_color((0.8, 0.8, 0.8, 1))
		directionalLight = DirectionalLight("directionalLight")
		directionalLight.set_direction(V3(0, 45, -45))
		directionalLight.set_color((0.2, 0.2, 0.2, 1))
		render.set_light(render.attach_new_node(directionalLight))
		render.set_light(render.attach_new_node(ambientLight))

	@setup_wrapper
	def setup_units(self):
		"""load units"""
		self.map = Map(kind='flat', render=render, loader=loader)
		self.town = Town()
		self.town.create_test_town()
		self.selected = None

	@setup_wrapper
	def setup_pointers(self):
		"""load pointers"""
		self.selection = loader.loadModel("./lib/other/selection")
		self.selection.reparent_to(render)
		self.selection.set_transparency(TransparencyAttrib.MAlpha)
		self.selection.set_alpha_scale(0.8)
		self.selection.hide()
		self.selection_h = 0.01
		self.selections = {}

		self.pos_pointer = loader.loadModel("./lib/other/pos-pointer")
		self.pos_pointer.reparent_to(render)
		self.pos_pointer.set_transparency(TransparencyAttrib.MAlpha)
		self.pos_pointer.set_alpha_scale(0.2)
		self.pos_pointer.hide()
		self.pos_pointer_h = 0.0

		self.direction_pointer = loader.loadModel("./lib/other/direction-pointer")
		self.direction_pointer.reparent_to(render)
		self.direction_pointer.set_transparency(TransparencyAttrib.MAlpha)
		self.direction_pointer.set_alpha_scale(0.5)
		self.direction_pointer.hide()
		self.direction_pointer_h = 0.75

		self.construction_pointer = loader.loadModel("./lib/other/construction-pointer")
		self.construction_pointer.reparent_to(render)
		self.construction_pointer.set_transparency(TransparencyAttrib.MAlpha)
		self.construction_pointer.set_alpha_scale(0.5)
		self.construction_pointer.hide()
		self.construction_pointer_h = 0.01
		self.construction_pointer_size = 1.0

		self.pointers = []

	@setup_wrapper
	def setup_collisions(self):
		"""setup mouse unit selector and mouse pos picker"""
		Map.map.model.find("**/Grid").node().set_into_collide_mask(BitMask32.bit(0))
		# self.traverser = CollisionTraverser()
		# self.queue = CollisionHandlerQueue()
		# self.traverser.show_collisions(render)

		# mouse unit selector
		self.selector = CollisionTraverser()
		self.selector_queue = CollisionHandlerQueue()
		self.mouse_node = CollisionNode("mouse_ray")
		self.mouse_node.set_from_collide_mask(BitMask32.bit(1))
		self.mouse_node.set_into_collide_mask(BitMask32.all_off())
		self.selector_ray = CollisionRay()
		self.mouse_node.add_solid(self.selector_ray)
		self.selector.add_collider(camera.attach_new_node(self.mouse_node), self.selector_queue)
		# self.selector.show_collisions(render)

		# mouse pos picker
		self.pos_picker = CollisionTraverser()
		self.pos_picker_queue = CollisionHandlerQueue()
		self.mouse_ground_node = CollisionNode("mouse_ground_ray")
		self.mouse_ground_node.set_from_collide_mask(BitMask32.bit(0))
		self.mouse_ground_node.set_into_collide_mask(BitMask32.all_off())
		self.mouse_ground_node.add_solid(self.selector_ray)
		self.pos_picker.add_collider(camera.attach_new_node(self.mouse_ground_node), self.pos_picker_queue)
		# self.pos_picker.show_collisions(render)

	@setup_wrapper
	def setup_menus(self):
		"""create all menus"""
		self.control_menu = menu.ControlMenu()
		self.build_menu = menu.BuildMenu()
		self.statistics_menu = menu.StatisticsMenu()
		self.setting_menu = menu.SettingMenu()
		self.item_menus = {}
		self.item_menus[Building] = menu.BuildingMenu()
		self.item_menus[Construction] = menu.ConstructionMenu()
		self.item_menus[Squad] = menu.SquadMenu()
		self.item_menus[Warrior] = menu.WarriorMenu()
		self.item_menus[Citizen] = menu.CitizenMenu()
		self.opened_menus = [self.control_menu, None]
		self.left_hidden = True
		self.enter_control_menu()
		self.enter_left_menu()
		self.accept("Item-Hide", lambda: self.exit_submenu())

	def left_click(self):
		"""on left click"""
		if self.mode == "":
			self.select_by_mouse()
		elif self.mode == "pick free pos":
			clicked_pos = self.clicked_pos()
			if clicked_pos is not None:
				pos = Map.map.grid.get_xy(clicked_pos)
				if Map.map.grid.area_is_free(pos, size=1):
					self.construction_pos = Point(pos[0], pos[1], 0.0)
					self.construction_pointer.set_pos(pos[0], pos[1], self.construction_pointer_h)
					self.direction_pointer.set_pos(pos[0], pos[1], self.direction_pointer_h)
					self.direction_pointer.set_h(0.0)
					self.mode = "pick door direction"
					self.direction_pointer.show()
		elif self.mode == "pick free pos for obstacle":
			clicked_pos = self.clicked_pos()
			if clicked_pos is not None:
				pos = Map.map.grid.get_xy(clicked_pos)
				if Map.map.grid.is_free(pos):
					Obstacle(pos=V3(pos[0], pos[1], 0.0))

	def left_release(self):
		"""on left release"""
		if self.mode == "pick door direction":
			clicked_pos = self.clicked_pos()
			if clicked_pos is not None:
				v = clicked_pos - self.construction_pos
				angle = core.get_main_angle(v) # 90*[-1, 0, 1, 2]
			else:
				angle = self.direction_pointer.get_h()
			self.construction_pointer.hide()
			self.direction_pointer.hide()
			self.mode = ""
			self.town.create_construction(kind=self.construction_kind, pos=self.construction_pos, direction=angle)

	def middle_click(self):
		"""on middle click"""
		pass

	def right_click(self):
		"""on right click"""
		clicked_pos = self.clicked_pos()
		if (isinstance(self.selected, Squad) or isinstance(self.selected, Citizen)) and clicked_pos is not None:
			self.mode = "catch direction"
			pos = self._clicked_pos = clicked_pos
			if isinstance(self.selected, Squad):
				self.selected.new_goal(Point(pos.x, pos.y, 0.0))
				self.direction_pointer.set_h(self.selected.ringleader.direction)
			elif isinstance(self.selected, Citizen):
				self.selected.new_goal(Point(pos.x, pos.y, 0.0))
				self.direction_pointer.set_h(self.selected.direction)
			self.pos_pointer.set_pos(pos.x, pos.y, self.pos_pointer_h)
			self.direction_pointer.set_pos(pos.x, pos.y, self.direction_pointer_h)
			self.pos_pointer.show()
			self.direction_pointer.show()

	def right_release(self):
		"""on right release"""
		clicked_pos = self.clicked_pos()
		if self.mode == "catch direction" and (isinstance(self.selected, Squad) or isinstance(self.selected, Citizen)):
			angle = None
			if clicked_pos is not None:
				angle = core.get_angle(clicked_pos - self._clicked_pos)
			elif angle is None:
				angle = self.direction_pointer.get_h()
			if isinstance(self.selected, Squad):
				if angle is not None:
					self.selected.set_direction(angle)
					pos = self.selected.ringleader.goal.pos if self.selected.ringleader.has_goal() else self.selected.ringleader.pos
					self.selected.new_goal(pos)
			elif isinstance(self.selected, Citizen):
				if angle is not None:
					self.selected.direction = angle
			self.mode = ""
			self.pos_pointer.hide()
			self.direction_pointer.hide()

	def clean(self):
		"""cancel selection and item menu, clean mode"""
		self.unselect()
		self.clean_mode()

	def clicked_pos(self, mouse_pos=None):
		"""return clicked point or None"""
		if mouse_pos is None:
			if base.mouseWatcherNode.has_mouse():
				mouse_pos = base.mouseWatcherNode.get_mouse()
			else:
				return None
		self.selector_ray.set_from_lens(base.camNode, mouse_pos.get_x(), mouse_pos.get_y())
		self.pos_picker.traverse(render)
		if self.pos_picker_queue.get_num_entries() > 0:
			self.pos_picker_queue.sort_entries()
			pos = self.pos_picker_queue.get_entry(0).get_surface_point(Map.map.model)
			return pos

	def add_rel_camera_motion(self, v, delay=False):
		"""stored in self.rel_camera_motion"""
		self.rel_camera_motion += V3(*v)

	def add_abs_camera_motion(self, v, rotate=False):
		"""stored in self.abs_camera_motion"""
		if rotate:
			self.abs_camera_motion += core.rotated(V3(*v), self.camera.get_h())
		else:
			self.abs_camera_motion += V3(*v)

	def add_camera_rotation(self, v):
		"""stored in self.camera_rotation"""
		self.camera_rotation += V3(*v)

	def stop_camera(self):
		"""clear camera motion and rotation"""
		self.camera_rotation = V3(0, 0, 0)
		self.abs_camera_motion = V3(0, 0, 0)
		self.rel_camera_motion = V3(0, 0, 0)

	def camera_task(self, task):
		"""update camera"""
		self.camera.set_pos(self.camera, self.rel_camera_motion)
		pos = self.camera.get_pos()
		self.camera.set_pos(pos + self.abs_camera_motion)
		if self.camera.get_z() < self.camera_min_h:
			self.camera.set_z(self.camera_min_h)
		self.camera.set_hpr(self.camera.get_hpr() + self.camera_rotation)
		return task.cont

	def update_pointers(self):
		"""update helpful pointers"""
		if self.mode == "catch direction" and (isinstance(self.selected, Squad) or isinstance(self.selected, Citizen)):
			clicked_pos = self.clicked_pos()
			if clicked_pos is not None:
				angle = core.get_angle(clicked_pos - self._clicked_pos)
				if angle is not None:
					self.direction_pointer.set_h(angle)
		elif self.mode == "pick free pos":
			clicked_pos = self.clicked_pos()
			if clicked_pos is not None:
				pos = Map.map.grid.get_xy(clicked_pos)
				if Map.map.grid.area_is_free(pos, size=1):
					self.construction_pointer.set_pos(pos[0], pos[1], self.construction_pointer_h)
		elif self.mode == "pick free pos for obstacle":
			clicked_pos = self.clicked_pos()
			if clicked_pos is not None:
				pos = Map.map.grid.get_xy(clicked_pos)
				if Map.map.grid.is_free(pos):
					self.construction_pointer.set_pos(pos[0], pos[1], self.construction_pointer_h)
		elif self.mode == "pick door direction": # choose 1 of 4 direction: nsew
			clicked_pos = self.clicked_pos()
			if clicked_pos is not None:
				v = clicked_pos - self.construction_pos
				angle = core.get_main_angle(v) # 90*[-1, 0, 1, 2]
				self.direction_pointer.set_h(angle)


	def update(self, task):
		"""main update function"""
		self.update_pointers()
		self.map.update(dt=globalClock.getDt())
		# self.adjust_z() # ? traverse ground collisions ?
		# @HEIGHT_MAP('{'<"[!]">'}')
		# If you're using GeoMipTerrain to generate the terrain from the heightmap,
		# then you can use get_elevation(x, y) to get the elevation at a specific point.
		# It does bilinear interpolation between pixels for you.
		return task.cont

	def spawn_ralph(self, pos=(0, 5)):
		"""create ralph on free pos"""
		x, y = pos
		while not Map.map.grid.is_free((x, y)):
			x += 1
		Warrior(kind='ralph', pos=Point(x, y, 0), town=self.town)

	def clean_mode(self):
		"""clean mode and hide pointers"""
		self.mode = ""
		self.construction_pointer.hide()
		self.pos_pointer.hide()
		self.direction_pointer.hide()

	def select_by_mouse(self, mouse_pos=None):
		"""on mouse selection"""
		self.unselect()
		if mouse_pos is None:
			mouse_pos = base.mouseWatcherNode.get_mouse()
		self.selector_ray.set_from_lens(base.camNode, mouse_pos.get_x(), mouse_pos.get_y())
		self.selector.traverse(render)
		if self.selector_queue.get_num_entries() > 0:
			self.selector_queue.sort_entries()
			pos = self.selector_queue.get_entry(0).get_surface_point(Map.map.model)
			host = self.selector_queue.get_entry(0).get_into_node().get_python_tag('host')
			selected = self.select_by_type(host)
		else:
			selected = None
		self.show_selected_menu(selected)

	def show_selection(self, x, scale=1):
		"""attach selection to x"""
		self.selection.set_scale(scale)
		placeholder = x.model.attach_new_node("selection_placeholder")
		placeholder.set_pos(0.0, 0.0, self.selection_h)
		placeholder.set_scale(1.0/x.model_scale)
		self.selection.instance_to(placeholder)
		self.selections[placeholder] = x
		self.selection.show()

	def show_squad_selection(self, squad, scale=1):
		"""attach selections to squad"""
		self.selection.set_scale(scale)
		for x in squad.composition:
			placeholder = x.model.attach_new_node("selection_placeholder")
			placeholder.set_pos(0.0, 0.0, self.selection_h)
			placeholder.set_scale(1.0/x.model_scale)
			self.selection.instance_to(placeholder)
			self.selections[placeholder] = x
		placeholder = squad.ringleader.model.attach_new_node("big_selection_placeholder")
		placeholder.set_pos(0.0, 0.0, self.selection_h)
		placeholder.set_scale(1.5/x.model_scale)
		self.selection.instance_to(placeholder)
		self.selections[placeholder] = squad.ringleader
		self.selection.show()

	def create_construction(self, kind):
		"""enter construction creating mode"""
		self.mode = "pick free pos"
		self.construction_pointer.show()
		self.construction_kind = kind

	def create_obstacle(self):
		"""enter obstacle creating mode"""
		self.mode = "pick free pos for obstacle"
		self.construction_pointer.show()

	def unselect(self):
		"""cancel selctions and item menu"""
		if self.has_selected():
			if self.selected.has_menu():
				self.opened_menus[1].hide(unload=True)
				self.opened_menus[1] = None
			self.selected = None
			self.selection.hide()
			for x in self.selections:
				x.remove_node()
			self.selections = {}

	def show_selected_menu(self, selected):
		"""show corresponding menu"""
		if selected is not None:
			suitable_classes = [cls for cls in self.item_menus if isinstance(selected, cls)]
			if len(suitable_classes) == 1:
				self.selected = selected
				self.selected.cls = suitable_classes[0]
				self.enter_submenu(self.item_menus[self.selected.cls])

	def select_by_type(self, host):
		"""host --> selected"""
		if isinstance(host, Building) or isinstance(host, Construction):
			selected = host
			self.show_selection(selected, 10)
		elif isinstance(host, Citizen):
			selected = host
			self.show_selection(selected)
		elif isinstance(host, Warrior):
			selected = host.squad
			self.show_squad_selection(selected)
		else:
			selected = None
		return selected

	def select(self, x):
		"""show selections and corresponding menu"""
		self.unselect()
		selected = self.select_by_type(x)
		self.show_selected_menu(selected)

	def has_selected(self):
		"""if self.selected is not None"""
		return self.selected is not None

	def enter_left_menu(self):
		"""show all previously hidden menus"""
		self.accept("Left-Hide", lambda: self.exit_left_menu())
		self.ignore("Left-Show")
		for m in self.opened_menus:
			if m is not None:
				m.show()
		self.left_hidden = False

	def exit_left_menu(self):
		"""hide all left menus"""
		self.accept("Left-Show", lambda: self.enter_left_menu())
		self.ignore("Left-Hide")
		for m in self.opened_menus:
			if m is not None:
				m.hide()
		self.left_hidden = True

	def enter_control_menu(self):
		"""show control menu and accept control menu events"""
		self.accept("Build-Show", lambda: self.enter_submenu(self.build_menu))
		self.accept("Statistics-Show", lambda: self.enter_submenu(self.statistics_menu))
		self.accept("Settings-Show", lambda: self.enter_submenu(self.setting_menu))

		self.accept("Construct-Storage", lambda: self.create_construction('storage'))
		self.accept("Construct-School", lambda: self.create_construction('school'))
		self.accept("Construct-Farm", lambda: self.create_construction('farm'))
		self.accept("Construct-Obstacle", lambda: self.create_obstacle())

		self.accept("Print-Orders", lambda: _print_d(self.town.transport.orders))
		self.accept("Print-Deliveries", lambda: _print(self.town.transport.queue))
		self.accept("Print-Free-Valets", lambda: _print(self.town.transport.free_valets))
		self.accept("Print-Buildings", lambda: _print_d(self.town.building_dict))

		self.accept("Remove-Obstacles", lambda: Map.map.remove_obstacles())
		self.accept("Spawn-Ralph", lambda: self.spawn_ralph())
		self.control_menu.show()

	def enter_submenu(self, m):
		"""exit last and enter new submenu (under ControlMenu)"""
		self.exit_submenu()
		m.show()
		if isinstance(m, menu.ItemMenu) and self.has_selected():
			m.set(self.selected)
		self.opened_menus[1] = m
		if self.left_hidden:
			self.enter_left_menu()

	def exit_submenu(self):
		"""hide and unload opened submenu"""
		submenu = self.opened_menus[1]
		if submenu is not None:
			if isinstance(submenu, menu.ItemMenu):
				self.unselect()
			else:
				submenu.hide()
		self.opened_menus[1] = None

	def escape_from_game(self):
		"""escape function"""
		# autosave etc...
		sys_exit()

def _print(x):
	"""print function"""
	print x

def _print_d(d):
	"""print sorted non-empty items of dict"""
	for i in sorted(d.keys()):
		if d[i]:
			print "{}: {}".format(str(i), str(d[i]))

def execute(*sequence):
	"""execute sequence of functions:
	execute({'func': func1, 'arg1': arg1, 'arg2': arg2, ...}, {...}, ...)
	--> func1(arg1=arg1, arg2=arg2, ...); func2(...); ..."""
	for d in sequence:
		d.pop('func')(**d)

def main():
	"""main function"""
	game = Game()
	game.run()

if __name__ == '__main__':
	main()