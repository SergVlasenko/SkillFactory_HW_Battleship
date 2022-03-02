from random import randint

from exception import *


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'({self.x}, {self.y})'


class Ship:
    def __init__(self, first_dot, ship_size, ship_orientation):
        self.first_dot = first_dot
        self.ship_size = ship_size
        self.ship_orientation = ship_orientation
        self.ship_lives = ship_size

    # метод генерации списка всех точек корабля
    @property
    def dots(self):
        ship_dots = []
        for i in range(self.ship_size):
            current_x = self.first_dot.x
            current_y = self.first_dot.y

            if self.ship_orientation == 0:
                current_x += i

            elif self.ship_orientation == 1:
                current_y += i

            ship_dots.append(Dot(current_x, current_y))

        return ship_dots


class Board:
    def __init__(self, hid=False, size=6):
        self.hid = hid  # скрываем корабли или нет (False/True)
        self.size = size

        self.count = 0

        self.field = [['O'] * size for _ in range(size)]

        self.busy = []  # список занятых точек на доске
        self.ships = []  # список объектов (установленных кораблей)

    # вывод доски в консоль
    def __str__(self):
        res = ''
        res += '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        for i, row in enumerate(self.field):
            res += f'\n{i + 1} | ' + ' | '.join(row) + ' |'

        if self.hid:
            res = res.replace('■', 'O')
        return res

    # расстановка корабля
    def add_ship(self, ship):
        # проверяем все точки на доступность
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise ShipLayoutException()

        # в случае успешной проверки устанавливаем точку
        for d in ship.dots:
            self.field[d.x][d.y] = '■'
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    # обводка корабля по контуру
    def contour(self, ship, verb=False):
        near = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

        for d in ship.dots:
            for dx, dy in near:
                current = Dot(d.x + dx, d.y + dy)
                if not (self.out(current)) and current not in self.busy:
                    if verb:
                        self.field[current.x][current.y] = '.'
                    self.busy.append(current)

    # метод проверки точки при размещении корабля (True если Dot за пределы поля)
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    # выстрел
    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise RepeatedShotException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.ship_lives -= 1
                self.field[d.x][d.y] = 'X'
                if ship.ship_lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print('Убит!')
                    return True
                else:
                    print('Попал!')
                    return True
        self.field[d.x][d.y] = '.'
        print('Мимо!')
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    # метод определяет точку выстрела (метод перегружается)
    def ask(self):
        raise NotImplementedError()

    # метод делает ход в игре
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except CustomError as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход копьютера: {d.x + 1} {d.y + 1}')
        return d


class User(Player):
    def ask(self):
        while True:
            shoot_coordinate = input('Ваш выстрел: ').split()

            if len(shoot_coordinate) != 2:
                print('Введите 2 координаты! ')
                continue
            x, y = shoot_coordinate

            if not (x.isdigit()) or not (y.isdigit()):
                print('Введите координаты в виде чисел! ')
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        player = self.random_board()
        computer = self.random_board()
        computer.hid = True

        self.ai = AI(computer, player)
        self.us = User(player, computer)

    # метод запускает генерацию случайной доски
    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    # метод расставляет корабли на доске
    def random_place(self):
        length = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0  # попытки размещения корабля на доске
        for l in length:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except ShipLayoutException:
                    pass
        board.begin()
        return board

    # приветствие
    def greet(self):
        print('---------------------------')
        print('----М--О--Р--С--К--О--Й----')
        print('---------Б--О--й-----------')
        print('---------------------------')
        print('--------Инструкция:--------')
        print('-Для выстрела введите: X Y-')
        print('-----X - номер строки------')
        print('-----Y - номер столбца-----')
        print('---------------------------')

    # метод с игровым циклом
    def loop(self):
        num = 0
        while True:
            print('-' * 27)
            print('Доска игрока:')
            print(self.us.board)
            print('-' * 27)
            print('Доска компьютера:')
            print(self.ai.board)
            if num % 2 == 0:
                print('-' * 27)
                print('Ходит игрок!')
                repeat = self.us.move()
            else:
                print('-' * 27)
                print('Ходит компьютер!')
                repeat = self.ai.move()

            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print('-' * 27)
                print('Доска игрока:')
                print(self.us.board)
                print('-' * 27)
                print('Доска компьютера:')
                print(self.ai.board)
                print('-' * 27)
                print('Игрок выиграл!')
                break

            if self.us.board.count == 7:
                print('-' * 27)
                print('Доска игрока:')
                print(self.us.board)
                print('-' * 27)
                print('Доска компьютера:')
                print(self.ai.board)
                print('-' * 27)
                print('Компьютер выиграл!')
                break
            num += 1

    # запуск приветствия и игрового цикла
    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
