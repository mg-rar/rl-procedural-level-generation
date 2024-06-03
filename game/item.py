import pygame
from pygame import Surface
from game.utils import Utils
from game.position import CartesianPosition as Pos


class Item:
    def __init__(self, pos: Pos, item_type: Utils.ItemType):
        self.__font = pygame.font.Font('assets/Gamepixies.ttf', 12)
        self.__pos: Pos = pos
        self.__item = Utils.get_tile_set(Utils.ITEM, Utils.TILE_SIZE)
        self.__item_type: Utils.ItemType = item_type

    def get_pos(self) -> Pos:
        return self.__pos

    def get_type(self) -> Utils.ItemType:
        return self.__item_type

    def get_bonus(self) -> int:
        match self.__item_type:
            case Utils.ItemType.HEALTH:
                return 2
            case Utils.ItemType.POWER:
                return 3

    def render_bonus(self, screen):
        bonus = self.__font.render(f'+{self.get_bonus()} {self.__item_type.name}',
                                   False,
                                   (255, 255, 255))
        bonus_display = Surface(bonus.get_size(), pygame.SRCALPHA)
        bonus_display.blit(bonus, (0, 0))
        coord = self.__pos * Utils.TILE_SIZE
        screen.blit(bonus_display, (coord.x, coord.y))

    def render(self, screen):
        coord = self.__pos * Utils.TILE_SIZE
        coord = (coord.x, coord.y)
        match self.get_type():
            case Utils.ItemType.HEALTH:
                screen.blit(self.__item[0], coord)
            case Utils.ItemType.POWER:
                screen.blit(self.__item[1], coord)
