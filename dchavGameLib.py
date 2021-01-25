def colored(text, color=31):
	"""
	30-37 - текст
	40-47 - фон
	черный
	краный
	зеленый
	желтый
	синий
	фиолетовый
	бирюзовый
	белый
	"""
	return f"\033[{color}m{text}\033[0m"

def num_len(num):
	return len(str(num))

def random_boolean():
	from random import getrandbits
	return bool(getrandbits(1))

def clear_console():
	import os
	os.system('cls' if os.name == 'nt' else 'clear')


num_to_side = {
	0: 'Up',
	1: 'Right',
	2: 'Down',
	3: 'Left',
}
side_to_num = {
	'Up': 0,
	'Right': 1,
	'Down': 2,
	'Left': 3,
}
side_inverse = {
	'Up': 'Down',
	'Right': 'Left',
	'Down': 'Up',
	'Left': 'Right',
}

class Side:
	num_to_side = {
		0: 'Up',
		1: 'Right',
		2: 'Down',
		3: 'Left',
	}
	side_to_num = {
		'Up': 0,
		'Right': 1,
		'Down': 2,
		'Left': 3,
	}
	side_inverse = {
		'Up': 'Down',
		'Right': 'Left',
		'Down': 'Up',
		'Left': 'Right',
	}

	@staticmethod
	def to_num(side):
		return Side.side_to_num[side]

	@staticmethod
	def from_num(num_of_side: int):
		return Side.num_to_side[num_of_side % 4]

	@staticmethod
	def inverse(side):
		return Side.side_inverse[side]

class Pos:
	sides = ['Up', 'Right', 'Down', 'Left']

	def __init__(self, x: int, y: int):
		self.x = x
		self.y = y

	def __eq__(self, other: 'Pos'):
		if self.x == other.x and self.y == other.y:
			return True
		else:
			return False

	def __str__(self):
		return f'{self.x}, {self.y}'

	def __add__(self, other):
		self.x += other
		self.y += other
		return self

	def __sub__(self, other):
		self.x -= other
		self.y -= other
		return self

	def __mul__(self, other):
		self.x *= other
		self.y *= other
		return self

	def __floordiv__(self, other):
		self.x //= other
		self.y //= other
		return self

	def __pow__(self, power, modulo=None):
		self.x **= power
		self.y **= power
		return self

	def get_nearby(self, side):
		if side == 'Up':
			return Pos(self.x + 0, self.y - 1)
		elif side == 'Right':
			return Pos(self.x + 1, self.y + 0)
		elif side == 'Down':
			return Pos(self.x + 0, self.y + 1)
		elif side == 'Left':
			return Pos(self.x - 1, self.y + 0)

	def get_move(self, side, move=1):
		if side == 'Up':
			return Pos(self.x + 0 * move, self.y - 1 * move)
		elif side == 'Right':
			return Pos(self.x + 1 * move, self.y + 0 * move)
		elif side == 'Down':
			return Pos(self.x + 0 * move, self.y + 1 * move)
		elif side == 'Left':
			return Pos(self.x - 1 * move, self.y + 0 * move)

	def get_list_of_nearest(self, center=True, cross=True, xform=True):
		"""
		center\n
		░░ ░░ ░░\n
		░░ >< ░░\n
		░░ ░░ ░░\n
		cross \n
		░░ >< ░░\n
		>< ░░ ><\n
		░░ >< ░░\n
		xform\n
		>< ░░ ><\n
		░░ ░░ ░░\n
		>< ░░ ><
		"""
		result_list = []
		if center is True:
			result_list.append(Pos(self.x, self.y))
		if cross is True:
			result_list.append(Pos(self.x + 1, self.y))
			result_list.append(Pos(self.x - 1, self.y))
			result_list.append(Pos(self.x, self.y + 1))
			result_list.append(Pos(self.x, self.y - 1))
		if xform is True:
			result_list.append(Pos(self.x + 1, self.y + 1))
			result_list.append(Pos(self.x + 1, self.y - 1))
			result_list.append(Pos(self.x - 1, self.y + 1))
			result_list.append(Pos(self.x - 1, self.y - 1))
		return result_list

	def relation_to(self, coordinate: 'Pos', printed=True):
		"""
		с какой стороны находится координата (coordinate) по отношению к нашей (self)
		"""
		for coordinate_nearby in self.get_list_of_nearest(center=False, xform=False):
			if coordinate == coordinate_nearby:
				for side in self.sides:
					if coordinate == self.get_nearby(side):
						return side_inverse[side]
			else:
				if printed is True:
					print('coordinate too far!')


class Cell:
	def __init__(self, field: 'Field'):
		self.field = field
		self.sprite = '  '
		self.contains = None

	def set_sprite(self, sprite):
		self.sprite = sprite

	def add(self, entity: 'Entity'):
		if self.is_empty():
			self.contains = entity
		else:
			print(f'{self} is NOT empty!')

	def is_empty(self):
		if self.contains is None:
			return True
		else:
			return False

	def contains_clear(self):
		self.contains = None

	def get_sprite(self):
		if not self.is_empty():
			if isinstance(self.contains, Entity):
				return self.contains.get_sprite()
			if len(str(self.contains)) < 2:
				return str(self.contains) + ' '
			else:
				return str(self.contains)[0:2]
		else:
			return self.sprite


class Field:
	def __init__(self, size=10):
		self.size = size
		self.cells = [[Cell(self) for _ in range(self.size)]
		              for _ in range(self.size)]

	def __call__(self, pos: Pos):
		return self.cells[pos.x][pos.y]

	@staticmethod
	def whitespace_for_nums(num, max_num_len):
		"""
		Возвращает кол-во пробелов для ровного отступа
				num - чило
				max_num_len - максимальная возможная длина числа
				напр:
				2 + whitespace(2, 2) == 2__
				10 + whitespace(10, 2) == 10_
		"""
		return ' ' * (max_num_len - len(str(num)))

	@staticmethod
	def nums_for_size(size):
		result_string = ''
		max_num_len = num_len(size - 1)
		if size < 11: max_num_len = 2
		for num in range(size):
			result_string += f'{num} ' + Field.whitespace_for_nums(num, max_num_len)
		return result_string

	def get_sprite(self, pos: Pos):
		return self(pos).get_sprite()

	def draw(self):
		print(' ' * num_len(self.size - 1), self.nums_for_size(self.size), end='')
		for i in range(self.size):
			print(f'\n{self.whitespace_for_nums(i, num_len(self.size - 1))}{i} ', end='')
			for j in range(self.size):
				print(self.get_sprite(Pos(j, i)) + ' ', end='', sep='')
		print()


class Entity:
	def __init__(self, cell_field: Field, pos: Pos):
		self.cell_field = cell_field
		self.pos = pos
		self.sprite = '{}'  # ✨
		if self.can_be_added(self.pos):
			self.cell_field(self.pos).add(self)

	def get_sprite(self):
		return self.sprite

	def set_sprite(self, sprite):
		self.sprite = sprite

	def can_be_added(self, coordinate: Pos, printed=True):
		if 0 <= coordinate.x < self.cell_field.size and 0 <= coordinate.y < self.cell_field.size:
			if self.cell_field(coordinate).is_empty():
				return True
			else:
				if printed is True:
					print(
						f'({self.pos.x}, {self.pos.y}) Can\'t be placed at ({coordinate.x}, {coordinate.y}): isn\'t empty!')
				return False
		else:
			if printed is True:
				print(
					f'({self.pos.x}, {self.pos.y}) Can\'t be placed at ({coordinate.x}, {coordinate.y}): out of sea!')
			return False

	def teleport(self, coordinate: Pos):
		if self.can_be_added(coordinate):
			self.cell_field(coordinate).add(self)
			self.cell_field(self.pos).contains_clear()
			self.pos = coordinate

	def move(self, side, move=1):
		if side == 'Up':
			self.teleport(Pos(self.pos.x + 0 * move, self.pos.y - 1 * move))
		elif side == 'Right':
			self.teleport(Pos(self.pos.x + 1 * move, self.pos.y + 0 * move))
		elif side == 'Down':
			self.teleport(Pos(self.pos.x + 0 * move, self.pos.y + 1 * move))
		elif side == 'Left':
			self.teleport(Pos(self.pos.x - 1 * move, self.pos.y + 0 * move))

	def push(self, side, move=1):
		if not self.cell_field(self.pos.get_nearby(side)).is_empty():
			self.cell_field(self.pos.get_nearby(side)).contains.push(side, move=move)
			self.cell_field(self.pos.get_nearby(side)).contains.move(side, move=move)

	def push_move(self, side, move=1):
		self.push(side, move=move)
		self.move(side, move=move)

	def pull_move(self, side, move=1, max_length=5, length_now=1):
		for _ in range(move):
			self.move(side)
			if length_now < max_length:
				if not self.cell_field(self.pos.get_move(side_inverse[side], move=2)).is_empty():
					self.cell_field(self.pos.get_move(side_inverse[side], move=2)).contains.pull_move(side,
					                                                                                  max_length=max_length,
					                                                                                  length_now=length_now + 1)

# не используется
class PuzzleEntity(Entity):
	def __init__(self, cell_field: Field, coordinate: Pos):
		super().__init__(cell_field, coordinate)
		self.puzzled_sides = {
			'Up': False,
			'Right': False,
			'Down': False,
			'Left': False
		}
		# стыкуем ближайшие пазловые существа
		# здесь нужно грамотная проверка can_be_placed
		for coordinate_nearby in coordinate.get_list_of_nearest():
			if isinstance(self.cell_field(coordinate_nearby).contains, PuzzleEntity):
				self.puzzled_sides[coordinate_nearby.relation_to(coordinate, printed=False)] = True
				self.cell_field(coordinate_nearby).contains.puzzled_sides[
					coordinate.relation_to(coordinate_nearby, printed=False)] = True

	def move(self, side, move=1, command_side=None):
		for _ in range(move):
			if isinstance(self.cell_field(self.pos.get_nearby(side)).contains, PuzzleEntity):
				self.cell_field(self.pos.get_nearby(side)).contains.move(side, command_side=side_inverse[side])
			super().move(side)
			# также передать команду всем сторонам, исключая, собственно, side и сторону, с которой пришла аналогичная команда
			for puzzled_side, value in self.puzzled_sides.items():
				if value is True:
					if puzzled_side != side and puzzled_side != command_side and not self.cell_field(
							self.pos.get_nearby(puzzled_side)).is_empty():
						self.cell_field(self.pos.get_nearby(puzzled_side).get_move(side_inverse[side])).contains.move(side,
						                                                                                              command_side=side_inverse[puzzled_side])
					break


def end_game():
	import webbrowser
	url = 'https://www.pornhub.com/'
	webbrowser.open(url, new=0, autoraise=True)