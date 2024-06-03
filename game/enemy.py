from game.entity import Entity
from game.utils import Utils


class Enemy(Entity):
    FRAME = 0
    COOLDOWN = 1

    __IDLE_FRAMES = 4
    __ATTACK_FRAMES = 4
    __HURT_FRAMES = 4

    __SPEED = 1
    __HEALTH = 9
    __POWER = 2
    __XP = 3

    def __init__(self, pos):
        super().__init__(pos=pos, speed=self.__SPEED, health=self.__HEALTH, power=self.__POWER)
        self.__enemy = Utils.get_tile_set(Utils.ENEMY, Utils.TILE_SIZE)
        self.__idle = self.__enemy[:4]
        self.__attack = self.__enemy[4:8]
        self.__hurt = self.__enemy[8:]

    def get_current_xp(self) -> int:
        return self.__XP

    def get_state_frames(self) -> int:
        match self._state:
            case Utils.EntityState.IDLE:
                return Enemy.__IDLE_FRAMES
            case Utils.EntityState.ATTACK:
                return Enemy.__ATTACK_FRAMES
            case Utils.EntityState.HURT:
                return Enemy.__HURT_FRAMES

    def tick(self):
        self.FRAME += 1
        match self._state:
            case Utils.EntityState.ATTACK | Utils.EntityState.HURT:
                if self.FRAME == self.get_state_frames():
                    self._state = Utils.EntityState.IDLE
                    self.FRAME = 0
        if self.FRAME >= self.get_state_frames():
            self.FRAME = -self.get_state_frames() + 1

    def render(self, screen):
        coord = self._pos * Utils.TILE_SIZE
        coord = (coord.x, coord.y)
        match self._state:
            case Utils.EntityState.IDLE:
                screen.blit(self.__idle[abs(self.FRAME)], coord)
            case Utils.EntityState.ATTACK:
                screen.blit(self.__attack[abs(self.FRAME)], coord)
            case Utils.EntityState.HURT:
                screen.blit(self.__hurt[abs(self.FRAME)], coord)
