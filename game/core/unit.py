class Unit(object):

	def __init__(self, kind, pos, model, model_scale=None):
		self.kind = kind
		self.pos = pos
		self.model = model
		self.model.set_pos(self.pos)
		self.model_scale = model_scale or 1
		if model_scale is not None:
			self.model.set_scale(model_scale)

	def __repr__(self):
		return "Unit({}, {}, {}, {}, {})".format(self.kind, self.pos, self.model, self.model_scale, self.town)

	def __str__(self):
		return "<{} '{}' at {}>".format(self.__class__.__name__, self.kind, self.pos)