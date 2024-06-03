from dataclasses import dataclass


@dataclass
class CartesianPosition:
    x: int
    y: int

    def __add__(self, other: 'CartesianPosition'):
        return CartesianPosition(x=self.x + other.x, y=self.y + other.y)

    def __sub__(self, other: 'CartesianPosition'):
        return CartesianPosition(x=self.x - other.x, y=self.y - other.y)

    def __mul__(self, other: int):
        return CartesianPosition(x=self.x * other, y=self.y * other)

    def __iter__(self):
        return iter((self.x, self.y))

    def __copy__(self):
        return CartesianPosition(x=self.x, y=self.y)
