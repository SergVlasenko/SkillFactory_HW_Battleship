class CustomError(Exception):
    pass

class BoardOutException(CustomError):
    def __str__(self):
        return 'Вы хотите выстрелить за пределы поля!'

class RepeatedShotException(CustomError):
    def __str__(self):
        return 'В эту клетку вы уже стреляли!'

class ShipLayoutException(CustomError):
    pass
