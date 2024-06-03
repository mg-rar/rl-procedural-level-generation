from random import randint
import numpy as np
from copy import copy

from game.item import Item
from game.utils import Utils
from game.enemy import Enemy
from game.position import CartesianPosition as Pos


class Level:
    BONFIRE_FRAME = 0
    BONFIRE_FRAMES = 4

    def __init__(self, walls=None, healing_items=None, power_items=None, enemies=None, exit_point=None,
                 entry_point=None, map_size=Utils.MAP_SIZE):
        walls: list[Pos] = [] if walls is None else walls
        enemies: list[Pos] = [] if enemies is None else enemies
        power_items: list[Pos] = [] if power_items is None else power_items
        healing_items: list[Pos] = [] if healing_items is None else healing_items
        if exit_point is None:
            exit_point = Pos(*np.random.default_rng(seed=randint(0, 1000)).integers(0, map_size, size=2, dtype=int))
        if entry_point is None:
            entry_point = Pos(*np.random.default_rng(seed=randint(0, 1000)).integers(0, map_size, size=2, dtype=int))
            while sum(entry_point - exit_point) > map_size / 3:
                entry_point = Pos(*np.random.default_rng(seed=randint(0, 1000)).integers(0, map_size, size=2, dtype=int))

        self.wall_map = np.zeros(shape=(map_size, map_size), dtype=bool)
        self.enemy_map = np.zeros(shape=(map_size, map_size), dtype=bool)
        self.heal_map = np.zeros(shape=(map_size, map_size), dtype=bool)
        self.power_map = np.zeros(shape=(map_size, map_size), dtype=bool)
        self.route = np.zeros(shape=(map_size, map_size), dtype=bool)

        self.__grass = Utils.get_tile_set(Utils.GRASS, Utils.TILE_SIZE)
        self.__exit = Utils.get_tile_set(Utils.EXIT, Utils.TILE_SIZE)

        self.items: list[Item] = []
        self.enemies: list[Enemy] = []
        self.end_location: Pos = exit_point
        self.start_location: Pos = entry_point
        self.map_size: int = map_size

        self.__ground: np.ndarray = np.ndarray(shape=(self.map_size, self.map_size), dtype=int)
        for i in np.ndindex((self.map_size, self.map_size)):
            self.__ground[i] = randint(0, len(self.__grass) - 1)

        for pos in walls:
            self.add_wall_at(pos)
        for pos in enemies:
            self.add_enemy_at(pos)
        for pos in healing_items:
            self.add_healing_item_at(pos)
        for pos in power_items:
            self.add_power_item_at(pos)

    def get_walls(self) -> list[Pos]:
        walls = []
        for (x, y) in np.argwhere(self.wall_map):
            walls.append(Pos(x=x, y=y))
        return walls

    def get_enemies(self) -> list[Enemy]:
        return self.enemies

    def get_items(self) -> list[Item]:
        return self.items

    def add_wall_at(self, pos: Pos):
        self.wall_map[*pos] = True

    def add_enemy_at(self, pos: Pos):
        self.enemy_map[*pos] = True
        self.enemies.append(Enemy(pos=copy(pos)))

    def add_healing_item_at(self, pos: Pos):
        self.heal_map[*pos] = True
        self.items.append(Item(pos=copy(pos), item_type=Utils.ItemType.HEALTH))

    def add_power_item_at(self, pos: Pos):
        self.power_map[*pos] = True
        self.items.append(Item(pos=copy(pos), item_type=Utils.ItemType.POWER))

    def remove_item(self, item: Item):
        match item.get_type():
            case Utils.ItemType.HEALTH:
                self.heal_map[*item.get_pos()] = False
            case Utils.ItemType.POWER:
                self.power_map[*item.get_pos()] = False
        try:
            self.items.remove(item)
        except ValueError:
            return

    def remove_enemy(self, enemy: Enemy):
        self.enemy_map[*enemy.get_pos()] = False
        try:
            self.enemies.remove(enemy)
        except ValueError:
            return

    def get_start_pos(self) -> Pos:
        return self.start_location

    def get_exit_pos(self) -> Pos:
        return self.end_location

    def render(self, screen):
        self.BONFIRE_FRAME %= (self.BONFIRE_FRAMES - 1)
        self.BONFIRE_FRAME += 1

        # render ground
        for (x, y) in np.ndindex((self.map_size, self.map_size)):
            pos = Pos(x=x, y=y)
            coord = pos * Utils.TILE_SIZE
            screen.blit(self.__grass[self.__ground[*pos]], (coord.x, coord.y))

        # render walls
        for wall_pos in self.get_walls():
            coord = wall_pos * Utils.TILE_SIZE
            screen.blit(Utils.WALL, (coord.x, coord.y))

        # render items
        for item in self.get_items():
            item.render(screen)

        # render bonfire
        end_coord = self.end_location * Utils.TILE_SIZE
        screen.blit(self.__exit[self.BONFIRE_FRAME], (end_coord.x, end_coord.y))
