# Game imports
from .creature import Creature
from .squad import Squad

class Warrior(Creature):

	warrior_table = {}

	def __init__(self, kind, pos, town, squad=None, health=None, equipment=None, satiety=Creature.full_satiety):
		Creature.__init__(self, kind=kind, pos=pos, town=town, health=health, satiety=satiety)
		if squad is None:
			Squad(composition=[self], town=town, load=True)
		else:
			squad.join(self, load=True)
		if equipment is not None:
			self.left_hand, self.right_hand, self.body, self.head = equipment
		else:
			self.left_hand = self.right_hand = self.body = self.head = None

	@staticmethod
	def create(kind, pos, town, squad=None, health=None, equipment=None, satiety=Creature.full_satiety):
		return Warrior.warrior_table[kind](pos=pos, town=town, squad=squad, health=health, equipment=equipment, satiety=satiety)

	def attack(self):
		# self.free_grid()
		if self.animation is not None: # != 'attack':
			self.new_animation(None) # ('attack')
		# self.occupy_grid()
		# --> self.target

	@staticmethod
	def register(cls):
		Warrior.warrior_table[cls.kind] = cls
		return cls

@Warrior.register
class Ralph(Warrior): # TO BE: deleted

	kind = 'ralph'
	health = 10

	def __init__(self, pos, town, squad=None, health=None, equipment=None, satiety=None):
		health = health or Ralph.health
		Warrior.__init__(
			self,
			kind=Ralph.kind,
			pos=pos,
			town=town,
			squad=squad,
			health=health,
			equipment=equipment,
			satiety=satiety)