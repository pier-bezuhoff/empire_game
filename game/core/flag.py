# Python imports
# Panda3d imports
# Game imports
class Flag(object):
	"""class for nation flags"""
	flags = {}
	def __init__(self, name, color):
		self.name = name
		self.color = color
		Flag.flags[name] = self

	def __repr__(self):
		return "Flag({}, {})".format(self.name, self.color)

	def __str__(self):
		return "<Flag of {} ({})>".format(self.name, self.color)

Flag(name='player', color='green')