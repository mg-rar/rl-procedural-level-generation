import pygame

from game.entity import Entity
from game.item import Item
from game.utils import Utils
from game.position import CartesianPosition as Pos


class Player(Entity):
    FRAME: int = 0

    __IDLE_FRAMES = 4
    __ATTACK_FRAMES = 4
    __HURT_FRAMES = 4
    __DEAD_FRAMES = 4

    __SPEED = 1
    __HEALTH = 10
    __POWER = 3
    __XP = 0

    def __init__(self, pos):
        super().__init__(pos=pos, speed=self.__SPEED, health=self.__HEALTH, power=self.__POWER)
        self.__player = Utils.get_tile_set(Utils.PLAYER, Utils.TILE_SIZE)
        self.__idle = self.__player[:4]
        self.__move = self.__player[4:8]
        self.__attack = self.__player[8:12]
        self.__hurt = self.__player[12:16]
        self.__die = self.__player[16:]

    def get_next_pos(self, direction: Utils.Direction) -> Pos:
        diff = Pos(0, 0)
        match direction:
            case Utils.Direction.UP:
                diff = Pos(0, 1)
            case Utils.Direction.DOWN:
                diff = Pos(0, -1)
            case Utils.Direction.LEFT:
                diff = Pos(-1, 0)
            case Utils.Direction.RIGHT:
                diff = Pos(1, 0)
        return self._pos + diff

    def receive_bonus(self, item: Item):
        match item.get_type():
            case Utils.ItemType.HEALTH:
                self._health += item.get_bonus()
            case Utils.ItemType.POWER:
                self._power += item.get_bonus()

    def receive_xp(self, xp: int):
        self.__XP += xp

    def get_current_xp(self) -> int:
        return self.__XP

    def get_state_frames(self) -> int:
        match self._state:
            case Utils.EntityState.IDLE:
                return Player.__IDLE_FRAMES
            case Utils.EntityState.ATTACK:
                return Player.__ATTACK_FRAMES
            case Utils.EntityState.HURT:
                return Player.__HURT_FRAMES
            case Utils.EntityState.DEAD:
                return Player.__DEAD_FRAMES

    def tick(self):
        self.FRAME += 1
        match self._state:
            case Utils.EntityState.DEAD:
                if self.FRAME == self.get_state_frames():
                    self.FRAME = self.get_state_frames() - 1
            case Utils.EntityState.HURT:
                if self.FRAME == self.get_state_frames():
                    self._state = Utils.EntityState.IDLE
                    self.FRAME = 0
            case Utils.EntityState.ATTACK:
                if self.FRAME == self.get_state_frames():
                    self.set_state(Utils.EntityState.IDLE)
                    self.set_power(self.__POWER)
                    self.FRAME = 0
        self.FRAME %= self.get_state_frames()

    def render(self, screen):
        coord = self._pos * Utils.TILE_SIZE
        coord = (coord.x, coord.y)
        flip = self._direction == Utils.Direction.LEFT
        match self._state:
            case Utils.EntityState.IDLE:
                surface = self.__idle[self.FRAME]
            case Utils.EntityState.MOVE:
                surface = self.__move[self.FRAME]
            case Utils.EntityState.HURT:
                surface = self.__hurt[self.FRAME]
            case Utils.EntityState.ATTACK:
                surface = self.__attack[self.FRAME]
            case Utils.EntityState.DEAD:
                surface = self.__die[self.FRAME]
            case _:
                return
        surface = pygame.transform.flip(surface, flip, False)
        screen.blit(surface, coord)
