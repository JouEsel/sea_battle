from dchavGameLib import colored, clear_console, num_len  # всякие полезные функции
from dchavGameLib import Side, Pos, Field, Cell, Entity  # Всякие классы: сторона света, координата, поле, клетка, существо


ship_sprites = {
	0: colored('[]', color=32),  # 0 корабль ⛴
	1: colored('><', color=31),  # 1 подбитый корабль ☠ ❌
}
sea_cell_sprites = {
	0: '░░',  #
	1: '  ',  # ▒▒
}
alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'  # 26


# CLASSES
class SeaCell(Cell):
	def __init__(self, sea: 'Sea', pos: 'Pos'):
		super().__init__(sea)
		self.hidden = True
		self.sea = sea
		self.pos = pos
		self.already_attacked = False
		self.sprite = sea_cell_sprites[0]

	def get_sprite(self):
		if not self.is_empty() and not self.hidden:
			return self.contains.get_sprite()
		else:
			return self.sprite

	def hide(self):
		if self.already_attacked is False:
			self.hidden = True
			self.set_sprite(sea_cell_sprites[0])

	def show(self):
		self.hidden = False
		self.set_sprite(sea_cell_sprites[1])
		if not self.is_empty():
			self.set_sprite(self.contains.get_sprite())

	def attacked(self):
		if not self.is_empty():
			self.contains.attacked()
		self.show()
		self.already_attacked = True
		self.sea.coefficients(self.pos).cell_attacked()


class Whitelist(Field):
	def __init__(self, sea: 'Sea', size=10):
		super().__init__(size=size)
		self.sea = sea
		for i in range(self.size):
			for j in range(self.size):
				self(Pos(i, j)).contains = True

	def get_sprite(self, pos):
		if self(pos).contains:
			return colored('T ', color=32)
		else:
			return colored('F ')

	def update(self):
		# поставить в вайтлисте False там, где нельзя ставть корабли
		for i in range(self.sea.size):
			for j in range(self.sea.size):
				if not self.sea(Pos(i, j)).is_empty():
					for pos in Pos(i, j).get_list_of_nearest():
						if 0 <= pos.x < self.sea.size and 0 <= pos.y < self.sea.size:
							self(pos).contains = False

	def random_coordinate(self):
		# вернуть рандомную True координату из вайтлиста
		whitelist_of_poses = []
		for i in range(self.sea.size):
			for j in range(self.sea.size):
				if self(Pos(i, j)):
					whitelist_of_poses.append(Pos(i, j))
		from random import choice
		return choice(whitelist_of_poses)


class CoefficientCell(Cell):
	def __init__(self, coefficients: 'Coefficients', pos: 'Pos'):
		super().__init__(coefficients)
		self.pos = pos
		self.coefficients = coefficients
		self.contains = 1

	def cell_attacked(self):
		self.contains = 0

	def ship_attacked(self, ship: 'Ship'):
		self.contains = 0
		if ship.is_alive():
			for pos in self.pos.get_list_of_nearest(xform=False, center=False, cross=True):
				if 0 <= pos.x < self.coefficients.size and 0 <= pos.y < self.coefficients.size:
					self.coefficients(pos).contains *= 2
		else:
			for pos in ship.poses_around():
				self.coefficients(pos).contains = 0


class Coefficients(Field):
	def __init__(self, sea, size=10):
		super().__init__(size=size)
		self.sea = sea
		self.cells = [[CoefficientCell(self, Pos(j, i)) for i in range(self.size)]
		              for j in range(self.size)]

	def get_sprite(self, pos):
		if self(pos).contains == 0:
			return f'{self(pos).contains} '
		elif self(pos).contains == 1:
			return colored(f'{self(pos).contains} ', color=32)
		elif self(pos).contains > 1:
			return colored(f'{self(pos).contains} ', color=31)
		elif self(pos).contains > 9:
			return colored(f'{self(pos).contains}', color=31)

	def get_pos(self):
		"""Возвращает случайную точку из точек с максимальным коэффициентом"""
		max_coefficient = 0
		result_poses = []
		for i in range(self.size):
			for j in range(self.size):
				pos = Pos(i, j)
				coefficient = self(pos).contains
				if coefficient > max_coefficient:
					result_poses = []
					max_coefficient = coefficient
				if coefficient == max_coefficient:
					result_poses.append(pos)
		from random import choice
		return choice(result_poses)


class ShipPart(Entity):
	def __init__(self, ship: 'Ship', pos: Pos):
		super().__init__(ship.sea, pos)
		self.ship = ship
		self.sprite = ship_sprites[0]
		self.alive = True

	def is_alive(self, all_ship=False):
		if all_ship is False:
			return self.alive
		else:
			return self.ship.is_alive()

	def death(self):
		self.alive = False
		self.set_sprite(ship_sprites[1])

	def attacked(self):
		self.death()
		self.ship.around_update()
		self.ship.sea.coefficients(self.pos).ship_attacked(self.ship)


class Ship:
	def __init__(self,
	             sea: 'Sea',
	             pos=Pos(0, 0),
	             random_coordinate=False,
	             length=1,
	             random_length=False,
	             side='Up',
	             random_side=False):
		self.sea = sea
		self.ship_parts = []

		if random_length is True:
			from random import randrange
			self.length = randrange(1, 5)
		else:
			self.length = length

		if random_side is True:
			from random import randrange
			self.side = Side.from_num(randrange(4))
		else:
			self.side = side

		if random_coordinate is True:
			while True:
				self.pos = self.sea.whitelist.random_coordinate()
				if self.can_be_added():
					break
		else:
			self.pos = pos

		self.add()

	def can_be_added(self, printed=True):
		for i in range(self.length):
			pos = self.pos.get_move(self.side, move=i)
			if pos.x < 0 or pos.x >= self.sea.size or pos.y < 0 or pos.y >= self.sea.size:
				if printed is True:
					print(f'Ship can\'t be placed at {self.pos.x, self.pos.y}: another Ship is in the way')
				return False
			if not self.sea.whitelist(pos).contains:
				if printed:
					print(f'Ship can\'t be placed at {self.pos.x, self.pos.y}: another Ship is in the way')
				return False
		else:
			return True

	def add(self):
		if self.can_be_added():
			for i in range(self.length):
				self.ship_parts.append(ShipPart(self, self.pos.get_move(self.side, move=i)))
				self.sea.whitelist.update()
			self.sea.ships.append(self)

	def is_alive(self):
		for ship_part in self.ship_parts:
			if ship_part.alive is True:
				return True
		return False

	def move(self, side, move=1):
		if side == self.side:
			self.ship_parts[0].push_move(side, move=move)
		elif side == Side.inverse(self.side):
			self.ship_parts[0].push(side, move=move)
			self.ship_parts[0].pull_move(side, move=move, max_length=self.length)
		else:
			for ship_part in self.ship_parts:
				ship_part.push_move(side, move=move)

	def draw(self, printed=True):
		result = ''
		for ship_part_number in range(self.length):
			result += f'{self.ship_parts[ship_part_number].get_sprite()}\n'
		if printed is True:
			print(result)
		return result

	def poses_around(self, cross=True, xform=True):
		"""
		><><><><\n
		>< [1][2] ><\n
		><><><><
		"""
		result_list_of_poses = []
		for ship_part in self.ship_parts:
			for pos in ship_part.pos.get_list_of_nearest(cross=cross, center=False, xform=xform):
				if 0 <= pos.x < self.sea.size and 0 <= pos.y < self.sea.size:
					if not pos == ship_part.pos:
						result_list_of_poses.append(pos)
		return result_list_of_poses

	def around_update(self):
		if not self.is_alive():
			for pos in self.poses_around():
				self.sea(pos).show()
				self.sea(pos).already_attacked = True

	def __str__(self):
		return f'{self.length}-deck, looking {self.side.lower()} at ({self.pos})'


class Sea(Field):
	def __init__(self, size=10):
		super().__init__(size)
		self.whitelist = Whitelist(self, size=size)  # для расстановки кораблей
		self.coefficients = Coefficients(self, size=size)  # для обстрела кораблей
		self.ships = []  # корабли, принадлежащие морю
		self.size = size
		self.cells = [[SeaCell(self, Pos(j, i)) for i in range(self.size)]
		              for j in range(self.size)]

	@staticmethod
	def whitespace_for_alphabet(num):
		"""исп. для правильного отображения буквенных координат"""
		result_string = ''
		for i in range(num):
			result_string += f'{alphabet[i]}  '
		return result_string

	def hide(self):
		for i in range(self.size):
			for cell in self.cells[i]:
				cell.hide()

	def show(self):
		for i in range(self.size):
			for cell in self.cells[i]:
				cell.show()

	def random(self):
		"""Рандомная расстановка нескольких кораблей"""
		for length in (4, 3, 3, 2, 2, 2, 1, 1, 1, 1):
			Ship(self, random_coordinate=True, length=length, random_side=True)

	def draw_ships(self, only_alive_ships=True):
		if only_alive_ships is True:
			ships = [ship for ship in self.ships if ship.is_alive()]
		else:
			ships = self.ships
		max_ship_length = 0
		for ship in ships:
			if ship.length > max_ship_length:
				max_ship_length = ship.length
		count_of_ships = [0] * max_ship_length
		for ship in ships:
			for i in range(ship.length):
				count_of_ships[i] += 1
		for i in range(max_ship_length):
			for j in range(count_of_ships[i]):
				if only_alive_ships is True:
					ship_sprite = ship_sprites[0]
				else:
					ship_sprite = ships[j].ship_parts[i].get_sprite()
				print(f'{ship_sprite}' + ' ', sep='', end='')
			print()

	def draw(self, default=False):
		"""Отрисовка моря"""
		if default is True:
			super().draw()
		else:
			print(' ' * num_len(self.size), self.whitespace_for_alphabet(self.size), end='')
			for i in range(self.size):
				print(f'\n{super().whitespace_for_nums(i + 1, num_len(self.size))}{i + 1} ', end='')
				for j in range(self.size):
					print(self(Pos(j, i)).get_sprite() + ' ', end='')
			print()


class SeaBattlePlayer:
	def __init__(self):
		self.sea = Sea()
		self.sea.random()

	@staticmethod
	def attack(player: 'SeaBattlePlayer', pos: Pos):
		player.sea(pos).attacked()

	def lose(self):
		for ship in self.sea.ships:
			if ship.is_alive():
				return False
		return True


def start_seabattle(test_mode=False):
	if test_mode is True:
		computer = SeaBattlePlayer()

		whitelist_map = False
		coefficients_map = False
		draw_ships = False
		fog_of_war = True
		computer.sea.show()
		clear_console()

		whitelist_tumbler = 'Show/' + colored('hide', color=31) + ' whitelist map'
		coefficients_tumbler = 'Show/' + colored('hide', color=31) + ' coefficients map'
		ships_tumbler = 'Show/' + colored('hide', color=31) + ' ships'
		fog_of_war_tumbler = colored('Show', color=32) + '/hide' + ' fog of war'

		while True:
			print("CONSOLE SEA BATTLE")
			print("test mode!")
			if fog_of_war is True:
				computer.sea.hide()
			else:
				computer.sea.show()
			computer.sea.draw(default=True)
			if draw_ships is True:
				computer.sea.draw_ships(only_alive_ships=False)
			if whitelist_map is True:
				computer.sea.whitelist.draw()
			if coefficients_map is True:
				computer.sea.coefficients.draw()
			print('xy: Attack\n'
			      '1. ' + whitelist_tumbler + '\n'
			      '2. ' + coefficients_tumbler + '\n'
			      '3. ' + ships_tumbler + '\n'
			      '4. ' + fog_of_war_tumbler + '\n'
			      '5. Smart attack', sep='')
			command = input()
			if command.isdigit() and len(command) == 2 and int(command) <= 99:
				computer.sea(Pos(int(command) // 10, int(command) % 10)).attacked()
			# elif command.isdigit() and int(command) == 1:
			# 	print('\'stop\' to stop command\n'
			# 				'xy: coordinate\n'
			# 	      '\'Right\' or \'Left\' or \'Up\' or \'Down\': side\n'
			# 	      'l: length')
			# 	coordinate = None
			# 	side = None
			# 	length = None
			# 	while coordinate is None or side is None or length is None:
			# 		param = input()
			# 		if param == 'Right': side = param
			# 		elif param == 'Up': side = param
			# 		elif param == 'Left': side = param
			# 		elif param == 'Down': side = param
			# 		elif param == 'stop': break
			# 		elif command.isdigit() and len(command) == 2 and int(command) <= 99:
			# 			coordinate = Coordinate(int(param) // 10, int(param) % 10)
			# 		elif param.isdigit() and 4 >= int(param) >= 1:
			# 			length = int(param)
			# 		else:
			# 			print(colored('Invalid command!'))
			# 	Ship(self.computer.sea, coordinate=coordinate, side=side, length=length)1
			elif command.isdigit() and int(command) == 1:
				if whitelist_map is False:
					whitelist_map = True
					whitelist_tumbler = colored('Show', color=32) + '/hide whitelist map'
				else:
					whitelist_map = False
					whitelist_tumbler = 'Show/' + colored('hide', color=31) + ' whitelist map'
			elif command.isdigit() and int(command) == 2:
				if coefficients_map is False:
					coefficients_map = True
					coefficients_tumbler = colored('Show', color=32) + '/hide coefficients map'
				else:
					coefficients_map = False
					coefficients_tumbler = 'Show/' + colored('hide', color=31) + ' coefficients map'
			elif command.isdigit() and int(command) == 3:
				if draw_ships is False:
					draw_ships = True
					ships_tumbler = colored('Show', color=32) + '/hide ships'
				else:
					draw_ships = False
					ships_tumbler = 'Show/' + colored('hide', color=31) + ' ships'
			elif command.isdigit() and int(command) == 4:
				if fog_of_war is False:
					fog_of_war = True
					fog_of_war_tumbler = colored('Show', color=32) + '/hide' + ' fog of war'
				else:
					fog_of_war = False
					fog_of_war_tumbler = 'Show/' + colored('hide', color=31) + ' fog of war'
			elif command.isdigit() and int(command) == 5:
				computer.attack(computer, computer.sea.coefficients.get_pos())
			else:
				clear_console()
				print(colored('Invalid command!'))
				continue
			clear_console()
	elif test_mode is False:
		from dchavGameLib import end_game
		computer = SeaBattlePlayer()
		player = SeaBattlePlayer()
		clear_console()

		while not player.lose() and not computer.lose():
			print("CONSOLE SEA BATTLE!")
			computer.sea.draw()
			print('Your ships:')
			player.sea.draw_ships(only_alive_ships=False)
			print('Enter coordinate:')
			command = input()
			# далее проверяем, соответсвует ли команда формату (A7, B3, F4, ...)
			if 2 <= len(command) <= 3 and command[0] in alphabet[0:10] and command[1:].isdigit() and int(command[1:]) <= 10:
				x = alphabet.index(command[0])
				y = int(command[1:]) - 1
				pos = Pos(x, y)
				if not computer.sea.coefficients(pos).contains == 0:  # не стреляли ли мы уже в эту точку
					player.attack(computer, Pos(x, y))
					computer.attack(player, player.sea.coefficients.get_pos())
				else:
					print('Already knocked out!')
			elif command == 'auto':
				player.attack(computer, computer.sea.coefficients.get_pos())
				computer.attack(player, player.sea.coefficients.get_pos())
			else:
				print(colored('Incorrect!'))
			clear_console()
		else:
			if player.lose():
				from time import sleep
				message = ''
				for letter in 'ПОРАЖЕНИЕ!!!! Как так вышло? Награды не будет =(':
					sleep(0.1)
					message += letter
					print(message)
					clear_console()
			else:
				from time import sleep
				message = ''
				for letter in 'ПОБЕДА!!!!!\nЭто твоя награда за старания, отдохни и расслабься =)     ':
					sleep(0.1)
					message += letter
					print(message)
					clear_console()
				end_game()


start_seabattle(test_mode=True)
