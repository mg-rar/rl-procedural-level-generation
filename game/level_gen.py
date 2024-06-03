from random import randint
import numpy as np

from game.utils import Utils
from game.level import Level
from game.position import CartesianPosition as Pos


class LevelGenerator:
    def __init__(self, map_size=Utils.MAP_SIZE):
        self.map_size = map_size
        self.__level_map = self.__test_map()

    def make_level(self) -> Level:
        walls = []
        health_items = []
        power_items = []
        enemies = []
        start_point = None
        end_point = None
        for (row, col) in np.ndindex((self.map_size, self.map_size)):
            pos = Pos(x=col, y=self.map_size - row - 1)
            match self.__level_map[row][col]:
                case Utils.LevelObject.ITEM_HEAL:
                    health_items.append(pos)
                case Utils.LevelObject.ITEM_POWER:
                    power_items.append(pos)
                case Utils.LevelObject.ENEMY.value:
                    enemies.append(pos)
                case Utils.LevelObject.WALL.value:
                    walls.append(pos)
                case Utils.LevelObject.ENTER.value:
                    start_point = pos
                case Utils.LevelObject.EXIT.value:
                    end_point = pos
        if start_point is None:
            start_point = Pos(x=0, y=0)
        if end_point is None:
            end_point = Pos(x=self.map_size - 1, y=self.map_size - 1)
        return Level(
            walls=walls,
            power_items=power_items,
            healing_items=health_items,
            enemies=enemies,
            entry_point=start_point,
            exit_point=end_point
        )

    def __test_map(self):
        test_map = [[0] * self.map_size for _ in range(self.map_size)]
        for row in range(self.map_size):
            for col in range(self.map_size):
                tile = randint(0, 99)
                if tile < 71:
                    test_map[row][col] = Utils.LevelObject.GRASS
                elif tile < 91:
                    test_map[row][col] = Utils.LevelObject.WALL
                elif tile < 93:
                    test_map[row][col] = Utils.LevelObject.ITEM_HEAL
                elif tile < 96:
                    test_map[row][col] = Utils.LevelObject.ITEM_POWER
                else:
                    test_map[row][col] = Utils.LevelObject.ENEMY
        enter_point = [0, 0]
        exit_point = [0, 0]
        while enter_point == exit_point:
            enter_point[0], enter_point[1] = randint(0, self.map_size - 1), randint(0, self.map_size - 1)
            exit_point[0], exit_point[1] = randint(0, self.map_size - 1), randint(0, self.map_size - 1)

        test_map[enter_point[0]][enter_point[1]] = Utils.LevelObject.ENTER
        test_map[exit_point[0]][exit_point[1]] = Utils.LevelObject.EXIT

        return test_map
