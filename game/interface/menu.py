# Panda3D imports
from panda3d.core import TextNode
from direct.gui.DirectGui import *

WHITE = (1, 1, 1, 1)
BLACK = (0, 0, 0, 1)
TRANSPARENT = (0, 0, 0, 0)

left_rel_x = 0.05
edge_rel_x = 0.2
edge_rel_y = 0.75
title_rel_y = 0.70
subtitle_rel_y = 0.65

hidden_left_rel_x = 0.01
hidden_left_rel_y = 0.8

title_scale = 0.08
subtitle_scale = 0.06
label_scale = 0.05
button_scale = 0.06

INTERIOR_COLOR = (0, 0.1, 0, 0.2)
MAIN_FRAME_COLOR = (0, 0, 0, 0.1)
BUTTON_COLOR = (1, 1, 1, 0.3)
STORE_COLOR = (0, 0, 0, 0.2)

class MainMenu:

	def __init__(self):
		self.main_frame = DirectFrame(
			frameSize=rel_size(x_rel=1, y_rel=1),
			frameColor=TRANSPARENT)

	def show(self):
		self.main_frame.show()

	def hide(self):
		self.main_frame.hide()

class HiddenLeftMenu:

	def __init__(self):
		self.main_frame = main_frame(x_rel=left_rel_x, color=TRANSPARENT)
		self.show_button = show_left_button(parent=self.main_frame)
		self.hide()

	def show(self):
		self.main_frame.show()

	def hide(self):
		self.main_frame.hide()

class ControlMenu:

	hidden_menu = None # load on first creating
	controler_rel_y = 0.725

	def __init__(self):
		self.main_frame = main_frame()
		self.title = title(parent=self.main_frame, text="Control menu", y_rel=edge_rel_y)
		self.hide_left_button = hide_left_button(parent=self.main_frame)
		if ControlMenu.hidden_menu is None:
			ControlMenu.hidden_menu = HiddenLeftMenu()

		self.build_button = message_text_button(
			parent=self.main_frame,
			text="Build",
			x_rel=left_rel_x,
			y_rel=ControlMenu.controler_rel_y,
			message="Build-Show")
		self.statistics_button = message_text_button(
			parent=self.main_frame,
			text="Statistics",
			x_rel=left_rel_x + 0.04,
			y_rel=ControlMenu.controler_rel_y,
			message="Statistics-Show")
		self.settings_button = message_text_button(
			parent=self.main_frame,
			text="Settings",
			x_rel=left_rel_x + 0.10,
			y_rel=ControlMenu.controler_rel_y,
			message="Settings-Show")

		self.hide()

	def show(self):
		ControlMenu.hidden_menu.hide()
		self.main_frame.show()

	def hide(self):
		self.main_frame.hide()
		ControlMenu.hidden_menu.show()

class StandardMenu:

	def __init__(self, title_text):
		self.main_frame = main_frame()
		self.title = title(parent=self.main_frame, text=title_text)
		# self.hide()

	def show(self):
		self.main_frame.show()

	def hide(self):
		self.main_frame.hide()

class BuildMenu(StandardMenu):

	def __init__(self):
		StandardMenu.__init__(self, title_text="Constructions")
		self.construct_storage_button = message_text_button(
			parent=self.main_frame,
			text="Construct storage",
			n=1,
			message="Construct-Storage")
		self.construct_school_button = message_text_button(
			parent=self.main_frame,
			text="Construct school",
			n=2,
			message="Construct-School")
		self.construct_farm_button = message_text_button(
			parent=self.main_frame,
			text="Construct farm",
			n=3,
			message="Construct-Farm")
		self.construct_obstacle_button = message_text_button(
			parent=self.main_frame,
			text="Construct obstacle",
			n=4,
			message="Construct-Obstacle")
		self.hide()

class StatisticsMenu(StandardMenu):

	def __init__(self):
		StandardMenu.__init__(self, title_text="Statistics")
		self.orders_button = message_text_button(
			parent=self.main_frame,
			text="Print booked orders",
			n=1,
			message="Print-Orders")
		self.queue_button = message_text_button(
			parent=self.main_frame,
			text="Print queue of deliveries",
			n=2,
			message="Print-Deliveries")
		self.free_valets_button = message_text_button(
			parent=self.main_frame,
			text="Print free valets",
			n=3,
			message="Print-Free-Valets")
		self.building_dict_button = message_text_button(
			parent=self.main_frame,
			text="Print buildings in the town",
			n=4,
			message="Print-Buildings")
		self.hide()

class SettingMenu(StandardMenu):

	def __init__(self):
		StandardMenu.__init__(self, title_text="Settings")
		self.remove_obstacles_button = message_text_button(
			parent=self.main_frame,
			text="Remove all obstacles on the map",
			n=1,
			message="Remove-Obstacles")
		self.ralph_spawner_button = message_text_button(
			parent=self.main_frame,
			text="Spawn ralph",
			n=2,
			message="Spawn-Ralph")
		self.hide()

def interior_size():
	return rel_size(y_rel=under_rel_y(n=1.5))

def store_size():
	return rel_size(y0_rel=under_rel_y(n=1.5), y_rel=under_rel_y(n=7))

class ItemMenu:

	def __init__(self, title_text):
		self.main_frame = main_frame()
		self.title = title(parent=self.main_frame, text=title_text)
		self.subtitle = subtitle(parent=self.main_frame)
		# self.hide()

	def show(self):
		self.main_frame.show()
		self.show_inner()

	def show_inner(self):
		pass

	def hide(self, unload=False):
		self.main_frame.hide()
		self.hide_inner(unload=unload)

	def hide_inner(self, unload=False):
		pass

class BuildingMenu(ItemMenu):

	def __init__(self, building=None):
		ItemMenu.__init__(self, title_text="Building menu")
		self.building = building

		self.interior_frame = DirectFrame(
			parent=self.main_frame,
			frameSize=interior_size(),
			frameColor=INTERIOR_COLOR)

		self.pos_label = label(parent=self.main_frame, n=12)
		self.health_label = label(parent=self.main_frame, text="_ / _", n=1)
		self.hide()

	def set(self, building):
		self.building = building
		self.building.menu = self
		self.subtitle['text'] = "{} of {}".format(building.kind.capitalize(), building.flag.name.capitalize())

		self.interior_frame.destroy()
		self.interior_frame = DirectFrame(
			parent=self.main_frame,
			frameSize=interior_size(),
			frameColor=INTERIOR_COLOR)
		self.store_frame = DirectFrame(
			parent=self.interior_frame,
			frameSize=store_size(),
			frameColor=STORE_COLOR)
		self.store_label = label(parent=self.interior_frame, text="", n=2)

		if self.building.kind == 'school':
			self.valet_button = command_text_button(
				parent=self.interior_frame,
				text="Study valet",
				n=7,
				command=lambda: self.building.order('valet'))
			self.builder_button = command_text_button(
				parent=self.interior_frame,
				text="Study builder",
				n=8,
				command=lambda: self.building.order('builder'))
			self.recruiting_label = label(parent=self.interior_frame, text="Recruiting: None", n=9)
			self.queue_label = label(parent=self.interior_frame, text="Queue: ", n=10)

		if 1 in self.building.store:
			self.add_gold_button = command_text_button(
				parent=self.interior_frame,
				text="+4 wood",
				n=3,
				command=lambda: self.building.add_to_store({1: 4}))
		if 2 in self.building.store:
			self.add_gold_button = command_text_button(
				parent=self.interior_frame,
				text="+4 stone",
				n=4,
				command=lambda: self.building.add_to_store({2: 4}))
		if 3 in self.building.store:
			self.add_gold_button = command_text_button(
				parent=self.interior_frame,
				text="+4 iron",
				n=5,
				command=lambda: self.building.add_to_store({3: 4}))
		if 10 in self.building.store:
			self.add_gold_button = command_text_button(
				parent=self.interior_frame,
				text="+4 gold",
				n=6,
				command=lambda: self.building.add_to_store({10: 4}))
		if 19 in self.building.store:
			self.add_wheat_button = command_text_button(
				parent=self.interior_frame,
				text="+4 wheat",
				n=7,
				command=lambda: self.building.add_to_store({19: 4}))
		self.pos_label['text'] = "{}".format(building.grid_pos)

		self.update()

	def update(self):
		self.health_label['text'] = "{} / {}".format(int(self.building.health), self.building.max_health)
		if self.building.kind == 'storage':
			self.store_label['text'] = str({key: self.building.store[key] for key in self.building.store if self.building.store[key] != 0})
		else:
			self.store_label['text'] = str(self.building.store)
		if self.building.kind == 'school':
			self.queue_label['text'] = "Queue: {}".format(', '.join([str(x) for x in self.building.queue]))
			if self.building.recruiting:
				self.recruiting_label['text'] = "Recruiting: {0[1]} ({0[0]}/{1})".format(self.building.recruiting, self.building.recruiting_time)
			else:
				self.recruiting_label['text'] = "Recruiting: None"

	def show_inner(self):
		pass

	def hide_inner(self, unload=False):
		if unload:
			self.building.menu = None
			self.building = None

class ConstructionMenu(ItemMenu):

	def __init__(self, construction=None):
		ItemMenu.__init__(self, title_text="Construction menu")
		self.construction = construction

		self.pos_label = label(parent=self.main_frame, text="_", n=12)
		self.store_label = label(parent=self.main_frame, text="_", n=2)
		self.health_label = label(parent=self.main_frame, text="_ / _", n=3)
		self.hide()

	def set(self, construction):
		self.construction = construction
		self.construction.menu = self
		self.subtitle['text'] = "{} of {}".format(construction.kind.capitalize(), construction.flag.name.capitalize())
		self.pos_label['text'] = "{}".format(construction.grid_pos)
		self.update()

	def update(self):
		self.store_label['text'] = str(self.construction.price)
		self.health_label['text'] = "{} / {}".format(int(self.construction.health), self.construction.max_health)		

	def show_inner(self):
		pass

	def hide_inner(self, unload=False):
		if unload:
			self.construction.menu = None
			self.construction = None

class SquadMenu(ItemMenu):

	def __init__(self, squad=None):
		ItemMenu.__init__(self, title_text="Squad menu")
		self.squad = squad

		self.stop_button = command_text_button(
			parent=self.main_frame,
			text="Stop",
			n=1,
			command=lambda: self.squad.stop())
		self.add_row_button = command_geom_button(
			parent=self.main_frame,
			name="add-row",
			scale=0.075,
			n=2,
			command=lambda: self.squad.add_row())
		self.remove_row_button = command_geom_button(
			parent=self.main_frame,
			name="remove-row",
			scale=0.075,
			n=3,
			command=lambda: self.squad.remove_row())
		self.add_column_button = command_geom_button(
			parent=self.main_frame,
			name="remove-column",
			scale=0.075,
			n=4,
			command=lambda: self.squad.add_column())
		self.remove_column_button = command_geom_button(
			parent=self.main_frame,
			name="remove-column",
			scale=0.075,
			n=5,
			command=lambda: self.squad.remove_column())

		self.lrc_title_label = label(parent=self.main_frame, text="length : rows : columns", n=6)
		self.lrc_label = label(parent=self.main_frame, text="_ : _ : _", n=7)
		self.pos_label = label(parent=self.main_frame, text="_", n=12)
		self.hide()

	def set(self, squad):
		self.squad = squad
		self.squad.menu = self
		self.subtitle['text'] = "Squad of {}".format(self.squad.flag.name.capitalize())
		self.update()

	def update(self):
		self.lrc_label['text'] = "{} : {} : {}".format(self.squad.length, self.squad.n_rows, self.squad.n_columns)
		self.pos_label['text'] = "{}".format(self.squad.ringleader.grid_pos)
		if self.squad.n_columns == 1:
			self.add_row_button['state'] = DGG.DISABLED
			self.remove_column_button['state'] = DGG.DISABLED
		else:
			self.add_row_button['state'] = DGG.NORMAL
			self.remove_column_button['state'] = DGG.NORMAL
		if self.squad.n_rows == 1:
			self.remove_row_button['state'] = DGG.DISABLED
			self.add_column_button['state'] = DGG.DISABLED
		else:
			self.remove_row_button['state'] = DGG.NORMAL
			self.add_column_button['state'] = DGG.NORMAL

	def show_inner(self):
		pass

	def hide_inner(self, unload=False):
		if unload:
			self.squad.menu = None
			self.squad = None

class WarriorMenu(ItemMenu):

	def __init__(self, warrior=None):
		ItemMenu.__init__(self, title_text="Warrior menu")
		self.warrior = warrior
		self.hide()

	def set(self, warrior):
		self.warrior = warrior
		self.warrior.menu = self
		self.subtitle['text'] = "{} of {}".format(warrior.kind.capitalize(), warrior.flag.name.capitalize())
		self.update()

	def update(self):
		pass

	def show_inner(self):
		pass

	def hide_inner(self, unload=False):
		if unload:
			self.warrior.menu = None
			self.warrior = None

class CitizenMenu(ItemMenu):

	def __init__(self, citizen=None):
		ItemMenu.__init__(self, title_text="Citizen menu")
		self.citizen = citizen

		self.path_label = label(parent=self.main_frame, text="path: [_]", n=10)
		self.motion_label = label(parent=self.main_frame, text="motion: _", n=11)
		self.pos_label = label(parent=self.main_frame, text="_ (_)", n=12)
		self.health_label = label(parent=self.main_frame, text="_ / _ | _%", n=2)
		self.labels = dict()
		self.hide()

	def set(self, citizen):
		for l in self.labels.values():
			l.destroy()
		self.citizen = citizen
		self.citizen.menu = self
		self.subtitle['text'] = "{} of {}".format(citizen.kind.capitalize(), citizen.flag.name.capitalize())
		if self.citizen.kind == 'valet':
			self.labels["delivery"] = label(parent=self.main_frame, text="...", n=3)
		elif self.citizen.kind == 'builder':
			self.labels["construction"] = label(parent=self.main_frame, text="_", n=3)
		self.update()

	def update(self):
		self.pos_label['text'] = "{} (auto: {})".format(self.citizen.grid_pos, self.citizen.auto)
		if not self.citizen.has_interval():
			motion = 'stop'
		elif self.citizen.interval.is_playing():
			motion = 'moving'
		else:
			motion = 'idle'
		self.motion_label['text'] = "motion: {}".format(motion)
		self.path_label['text'] = "path: {}".format(self.citizen.path)
		self.health_label['text'] = "{} / {} | {}%".format(int(self.citizen.health), self.citizen.max_health, self.citizen.satiety)
		if self.citizen.kind == 'valet':
			self.labels["delivery"]['text'] = str(self.citizen.delivery)
		elif self.citizen.kind == 'builder':
			self.labels["construction"]['text'] = str(self.citizen.construction)

	def show_inner(self):
		pass

	def hide_inner(self, unload=False):
		if unload:
			self.citizen.menu = None
			self.citizen = None

# functions

def x_pos(rel):
	"""left [0; 1] right"""
	return base.a2dLeft + 1.0*rel*(base.a2dRight - base.a2dLeft)

def y_pos(rel):
	"""bottom [0; 1] top"""
	return base.a2dBottom + 1.0*rel*(base.a2dTop - base.a2dBottom)

def rel_pos(x_rel, y_rel):
	"""right-top = (1.0, 1.0)"""
	return (x_pos(x_rel), 0, y_pos(y_rel))

def rel_size(x0_rel=0, x_rel=edge_rel_x, y0_rel=0, y_rel=edge_rel_y):
	return (x_pos(x0_rel), x_pos(x_rel), y_pos(y0_rel), y_pos(y_rel))

def under_rel_y(n=1, dy=0.05):
	"""n in [1; 13]"""
	return subtitle_rel_y - dy*n


def main_frame(x0_rel=0, x_rel=edge_rel_x, y0_rel=0, y_rel=edge_rel_y, color=MAIN_FRAME_COLOR):
	return DirectFrame(
		frameSize=rel_size(x0_rel=x0_rel, x_rel=x_rel, y0_rel=y0_rel, y_rel=y_rel),
		frameColor=color)

def label(parent, text="", n=None, x_rel=left_rel_x, y_rel=edge_rel_y, scale=label_scale):
	if n is not None:
		y_rel = under_rel_y(n=n)
	return DirectLabel(
		scale=scale,
		pos=rel_pos(x_rel, y_rel),
		frameColor=TRANSPARENT,
		text=text,
		text_align = TextNode.ALeft,
		text_fg=WHITE,
		parent=parent)

def title(parent, text="", x_rel=left_rel_x, y_rel=title_rel_y, scale=title_scale):
	return label(
		parent=parent,
		text=text,
		x_rel=x_rel,
		y_rel=y_rel,
		scale=scale)

def subtitle(parent, text="", x_rel=left_rel_x, y_rel=subtitle_rel_y, scale=subtitle_scale):
	return label(
		parent=parent,
		text=text,
		x_rel=x_rel,
		y_rel=y_rel,
		scale=scale)

def message_text_button(parent, message, text="", n=None, x_rel=left_rel_x, y_rel=under_rel_y(n=1), frameColor=BUTTON_COLOR, scale=button_scale, text_fg=BLACK, text_bg=TRANSPARENT):
	if n is not None:
		y_rel = under_rel_y(n=n)
	return DirectButton(
		text=text,
		text_align = TextNode.ALeft,
		text_fg=text_fg,
		text_bg=text_bg,
		frameColor=frameColor,
		scale=scale,
		pos=rel_pos(x_rel, y_rel),
		parent=parent,
		command=base.messenger.send,
		extraArgs=[message],
		# relief='raised',
		rolloverSound=None,
		clickSound=None)

def command_text_button(parent, text="", n=None, x_rel=left_rel_x, y_rel=under_rel_y(n=1), command=lambda: None, frameColor=BUTTON_COLOR, scale=button_scale, text_fg=BLACK, text_bg=TRANSPARENT):
	if n is not None:
		y_rel = under_rel_y(n=n)
	return DirectButton(
		text=text,
		text_align = TextNode.ALeft,
		text_fg=text_fg,
		text_bg=text_bg,
		frameColor=frameColor,
		scale=scale,
		pos=rel_pos(x_rel, y_rel),
		parent=parent,
		command=command,
		# relief='raised',
		rolloverSound=None,
		clickSound=None)

def message_geom_button(parent, message, geom=None, name=None, n=None, x_rel=left_rel_x, y_rel=under_rel_y(n=1), scale=button_scale):
	if n is not None:
		y_rel = under_rel_y(n=n)
	if geom is None:
		model = loader.loadModel("./lib/menu/{}_maps".format(name))
		geom = (
			model.find("**/{}_ready".format(name)),
			model.find("**/{}_click".format(name)),
			model.find("**/{}_rollover".format(name)),
			model.find("**/{}_disabled".format(name)))
	return DirectButton(
		scale=scale,
		geom=geom,
		pos=rel_pos(x_rel, y_rel),
		parent=parent,
		command=base.messenger.send,
		extraArgs=[message],
		# relief='raised',
		rolloverSound=None,
		clickSound=None,
		pressEffect=0)

def command_geom_button(parent, n=None, geom=None, name=None, x_rel=left_rel_x, y_rel=under_rel_y(n=1), command=lambda: None, scale=button_scale):
	if n is not None:
		y_rel = under_rel_y(n=n)
	if geom is None:
		model = loader.loadModel("./lib/menu/{}_maps".format(name))
		geom = (
			model.find("**/{}_ready".format(name)),
			model.find("**/{}_click".format(name)),
			model.find("**/{}_rollover".format(name)),
			model.find("**/{}_disabled".format(name)))
	return DirectButton(
		geom=geom,
		scale=scale,
		pos=rel_pos(x_rel, y_rel),
		parent=parent,
		command=command,
		# relief='raised',
		rolloverSound=None,
		clickSound=None,
		pressEffect=0)

def hide_left_button(parent):
	return message_text_button(
		parent=parent,
		text="<",
		x_rel=hidden_left_rel_x,
		y_rel=hidden_left_rel_y,
		message="Left-Hide")

def show_left_button(parent):
	return message_text_button(
		parent=parent,
		text=">",
		x_rel=hidden_left_rel_x,
		y_rel=hidden_left_rel_y,
		message="Left-Show")

def execute(*sequence):
	"""execute sequence of functions:
	execute({'func': func1, 'arg1': arg1, 'arg2': arg2, ...}, {...}, ...)
	--> func1(arg1=arg1, arg2=arg2, ...); func2(...); ..."""
	for d in sequence:
		d.pop('func')(**d)