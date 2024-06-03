import pygame
from pygame import Surface

from game.utils import Utils
from game.position import CartesianPosition as Pos


class Entity:

    def __init__(self, pos: Pos, speed: int, health: int, power: int):
        self._speed: int = speed
        self._health: int = health
        self._power: int = power
        self._pos: Pos = pos
        self._state: Utils.EntityState = Utils.EntityState.IDLE
        self._direction: Utils.Direction = Utils.Direction.RIGHT

    def get_pos(self) -> Pos:
        return self._pos

    def set_pos(self, pos: Pos):
        self._pos = pos

    def get_near_pos(self) -> list[Pos]:
        return [
            self.get_pos(),
            self.get_pos() + Pos(x=1, y=0),
            self.get_pos() + Pos(x=-1, y=0),
            self.get_pos() + Pos(x=0, y=1),
            self.get_pos() + Pos(x=0, y=-1),
        ]

    def get_power(self) -> int:
        return self._power

    def set_power(self, power: int):
        self._power = power

    def set_state(self, state: Utils.EntityState):
        self._state = state

    def get_state(self) -> Utils.EntityState:
        return self._state

    def get_health(self) -> int:
        return self._health

    def render_damage(self, damage: int) -> tuple[Pos, Surface]:
        font = pygame.font.Font('assets/Gamepixies.ttf', 12)
        damage_text = font.render(f'-{damage}', False, (255, 255, 255))
        damage_display = Surface(damage_text.get_size(), pygame.SRCALPHA)
        damage_display.blit(damage_text, (0, 0))
        return self.get_pos(), damage_display

    def hurt(self, damage: int):
        if self._state != Utils.EntityState.HURT:
            self.FRAME = -1
            self._state = Utils.EntityState.HURT
            self._health -= damage
