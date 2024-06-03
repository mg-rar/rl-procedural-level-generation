import math
import random
from copy import copy
from enum import Enum

import numpy as np
import pygame
from gymnasium import Env
from game.game import Game
from game.utils import Utils
from game.level import Level
from game.position import CartesianPosition as Pos
import matplotlib.pyplot as plt


class Stage(Enum):
    WALLS = 0
    WALL_SOLVER = 1
    ENEMY = 2
    ITEM = 3
    SOLVER = 4


class GenEnv(Env):
    def __init__(self,
                 map_size: int = None,
                 wall_density: float = None,
                 item: int = None,
                 health: int = None,
                 damage: int = None,
                 safe_zone: int = None):

        self.window = pygame.display.set_mode((Utils.SCREEN_WIDTH, Utils.SCREEN_HEIGHT), pygame.RESIZABLE)
        self.render = False
        self.clock = None
        self.side: int = min(Utils.SCREEN_WIDTH, Utils.SCREEN_HEIGHT)
        self.center: int = (Utils.SCREEN_WIDTH - self.side) // 2
        self.agent_spaces: dict[Stage, tuple[int, int]] = {
            Stage.WALLS: (26, 2),
            Stage.ENEMY: (14, 2),
            Stage.ITEM: (21, 3),
            Stage.SOLVER: (33, 8),
        }

        self.SIZE: int = map_size
        self.DENSITY: float = wall_density
        self.DAMAGE: int = damage
        self.HEALTH: int = health
        self.ITEM: int = item
        self.SAFE_ZONE: int = safe_zone

        self.current_density = 0
        self.current_damage = 0
        self.current_item = 0
        self.current_safe_zone = 0

        self.game: Game = Game(window=self.window)
        self.stage: Stage = Stage.WALLS
        self.steps: int = 0
        self.agent_location: Pos = Pos(0, 0)
        self.reset()

    def reset(self, seed=None, options=None) -> tuple[np.array, dict]:
        super().reset(seed=random.randint(0, 10000))
        map_size = random.randint(5, 10) if self.SIZE is None else self.SIZE
        health = random.randint(2, 10) if self.HEALTH is None else self.HEALTH
        self.current_density = random.randint(10, 500) / 1000 if self.DENSITY is None else self.DENSITY
        self.current_damage = random.randint(10, 600) / 1000 * health if self.DAMAGE is None else self.DAMAGE
        self.current_item = random.randint(1, map_size**2 // 8) if self.ITEM is None else self.ITEM
        self.current_safe_zone = random.randint(0, map_size // 3) if self.SAFE_ZONE is None else self.SAFE_ZONE
        self.game = Game(window=self.window)
        self.game.render_delay = 20
        self.game.reset(level=Level(map_size=map_size), health=health)
        self.stage = Stage.WALLS
        self.steps = 0
        self.agent_location: Pos = Pos(0, 0)
        return np.array(self._get_complete_obs_walls()), {}

    def step(self, action: int) -> tuple[np.array, int, bool, bool, dict]:
        reward = 0
        obs = None
        stage_done = False
        truncated = False

        match self.stage:
            case Stage.WALLS:
                reward = self._apply_action_walls(action)
                stage_done = self._move_agent_sweep()
                obs = self._get_complete_obs_walls()
            case Stage.WALL_SOLVER:
                reward = self._apply_action_solver(action)
                self.steps += 1 - 3 * (reward > 0)
                obs = self._get_complete_obs_solver()
                truncated = self.steps > self._l().map_size ** 2 * 4
                stage_done = self.agent_location == self._l().end_location
            case Stage.ENEMY:
                reward = self._apply_action_enemy(action)
                stage_done = self._move_agent_sweep()
                obs = self._get_complete_obs_enemy()
            case Stage.ITEM:
                reward = self._apply_action_item(action)
                stage_done = self._move_agent_sweep()
                obs = self._get_complete_obs_items()
            case Stage.SOLVER:
                reward = self._apply_action_solver(action)
                self.steps += 1 - 3 * (reward > 0)
                obs = self._get_complete_obs_solver()
                truncated = self.game.player.get_health() <= 0
                stage_done = (self.agent_location == self._l().end_location
                              or self.steps > self._l().map_size ** 2 * 8)

        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                self.side = min(event.size[0], event.size[1])
                self.center = (event.size[0] - self.side) // 2
        if self.render:
            self.game.render(self.side, self.center)

        return (
            np.array(obs),
            reward,
            stage_done,
            truncated,
            {
                "stage": self.stage
            }
        )

    def advance(self) -> tuple[np.array, dict]:
        obs = None
        match self.stage:
            case Stage.WALLS:
                self.stage = Stage.WALL_SOLVER
                self.agent_location = copy(self._l().start_location)
                self.steps = 0
                obs = self._get_complete_obs_solver()
            case Stage.WALL_SOLVER:
                self.agent_location = Pos(0, 0)
                self.stage = Stage.ENEMY
                obs = self._get_complete_obs_enemy()
            case Stage.ENEMY:
                self.stage = Stage.ITEM
                self.agent_location = Pos(0, 0)
                obs = self._get_complete_obs_items()
            case Stage.ITEM:
                self.stage = Stage.SOLVER
                self.agent_location = copy(self._l().start_location)
                self.game.player.set_pos(copy(self._l().start_location))
                self.steps = 0
                obs = self._get_complete_obs_solver()

        return np.array(obs), {"stage": self.stage}

    def _l(self) -> Level:
        return self.game.level

    def _get_obs_entry_distance(self) -> list[int]:  # 1
        start_delta = self._l().start_location - self.agent_location
        start_distance = abs(start_delta.x) + abs(start_delta.y)
        return [start_distance]

    def _get_obs_exit_distance(self) -> list[int]:  # 1
        end_delta = self._l().end_location - self.agent_location
        end_distance = abs(end_delta.x) + abs(end_delta.y)
        return [end_distance]

    def _get_obs_exit_direction(self) -> list[int]:  # 2
        diff: Pos = self._l().end_location - self.agent_location
        horizontal = diff.x / (abs(diff.x) + .01)
        vertical = diff.y / (abs(diff.y) + .01)
        return [round(horizontal), round(vertical)]

    def _get_obs_closest_delta_to(self, _map: np.ndarray) -> list[int]:  # 2
        idx = np.argwhere(_map)
        closest_direction = None
        for (x, y) in idx:
            diff = Pos(x=x, y=y) - self.agent_location
            if closest_direction is None or sum(diff) < sum(closest_direction):
                closest_direction = diff
        if closest_direction is None:
            return [0, 0]
        return [closest_direction.x, closest_direction.y]

    def _get_obs_near_amount(self, _map: np.ndarray) -> list[int]:  # 1
        _map = np.pad(_map.astype(int), ((1, 1), (1, 1)), "constant", constant_values=0)
        pos = self.agent_location + Pos(x=1, y=1)
        objects = [
            _map[*pos],
            _map[*(pos + Pos(x=1, y=0))],
            _map[*(pos + Pos(x=0, y=1))],
            _map[*(pos + Pos(x=-1, y=0))],
            _map[*(pos + Pos(x=0, y=-1))],
        ]
        return [sum(objects)]

    def _get_obs_of(self, _map: np.ndarray, r: int = 1) -> np.ndarray:
        (x, y) = self.agent_location
        world = np.pad(_map.astype(int), ((r, r+1), (r, r+1)), "constant", constant_values=0)
        return world[x:x+2*r+1, y:y+2*r+1]

    def _get_obs_health(self) -> list:  # 1
        return [self.game.player.get_health()]

    def _get_obs_enemy_density(self) -> list:  # 1
        return [math.floor(self.game.player.get_health() / self.current_damage - 1) / self._l().map_size**2]

    def _get_obs_item_density(self) -> list:  # 1
        return [self.current_item / self._l().map_size**2]

    def _get_complete_obs_walls(self) -> list:  # 26
        world = self._l().wall_map.astype(int)
        world[*self._l().get_exit_pos()] = -1
        world[*self._l().get_exit_pos()] = -1
        view = self._get_obs_of(world, r=2)  # 25
        return view.flatten().tolist() + [self.current_density]  # 1

    def _get_complete_obs_enemy(self) -> list:  # 14
        obs = self._get_obs_of(self._l().wall_map).flatten().tolist()  # 9
        obs += [sum(self._get_obs_closest_delta_to(self._l().route))]  # 1
        obs += self._get_obs_entry_distance()  # 1
        obs += self._get_obs_exit_distance()  # 1
        obs += self._get_obs_enemy_density()  # 1
        obs += self._get_obs_health()  # 1
        return obs

    def _get_complete_obs_items(self) -> list[int]:  # 21
        obs = self._get_obs_of(self._l().wall_map).flatten().tolist()  # 9
        obs += self._get_obs_of(self._l().enemy_map).flatten().tolist()  # 9
        obs += [sum(self._get_obs_closest_delta_to(self._l().route))]  # 1
        obs += self._get_obs_health()  # 1
        obs += self._get_obs_item_density()  # 1
        return obs

    def _get_complete_obs_solver(self) -> list[int]:  # 33
        world = self._l().wall_map.astype(int)
        world = -world
        idx = (np.argwhere(self._l().enemy_map).tolist()
               + np.argwhere(self._l().heal_map).tolist()
               + np.argwhere(self._l().power_map).tolist())
        for (x, y) in idx:
            if Pos(x, y) not in self._l().get_walls():
                world[x, y] += 1
        world[*self._l().end_location] = 3
        world = np.pad(world, ((2, 3), (2, 3)), "constant", constant_values=-1)
        (x, y) = self.agent_location
        view = world[x:x+5, y:y+5]
        obs = view.flatten().tolist()  # 25
        obs += self._get_obs_near_amount(self._l().enemy_map)  # 1
        obs += self._get_obs_closest_delta_to(self._l().heal_map)  # 2
        obs += self._get_obs_closest_delta_to(self._l().power_map)  # 2
        obs += self._get_obs_exit_direction()  # 2
        obs += self._get_obs_health()  # 1
        return obs

    def _apply_action_walls(self, action) -> int:
        reward = 0
        if action == 1:
            reward += 1
            self._l().add_wall_at(self.agent_location)
            if self.agent_location in (self._l().start_location, self._l().end_location):
                reward -= 20
            relative_density = self._l().wall_map.sum() / self._l().map_size ** 2 / self.current_density
            reward -= round(relative_density * 4. - 3.)
        return reward

    def _apply_action_enemy(self, action):
        left = math.floor(self.game.player.get_health() / self.current_damage - 1)
        reward = 0
        if action == 1:
            reward += 1
            self._l().add_enemy_at(self.agent_location)
            start_distance = self._get_obs_entry_distance()[0]
            end_distance = self._get_obs_exit_distance()[0]
            if start_distance < self.current_safe_zone or end_distance < self.current_safe_zone:
                reward -= 10
            if self.agent_location in self._l().get_walls():
                reward -= 5
            if self._l().enemy_map.sum() > left:
                reward -= 1
        return reward

    def _apply_action_item(self, action):
        enemies = len(self._l().enemies)
        relative_density = len(self._l().items) / self.current_item
        reward = 0
        if action >= 1:
            reward += 1
            reward -= round(relative_density * 4. - 3.)
            if action == 1:
                self._l().add_healing_item_at(self.agent_location)
                if self.game.player.get_health() - self.current_damage * enemies < self.current_damage:
                    reward += 1
            else:
                self._l().add_power_item_at(self.agent_location)
                if self.game.player.get_health() - self.current_damage * enemies >= self.current_damage:
                    reward += 1
            if (self.agent_location in (self._l().start_location, self._l().end_location)
                    or self.agent_location in self._l().get_walls()
                    or self.agent_location in self._l().get_enemies()):
                reward -= 10
        return reward

    def _apply_action_solver(self, action):
        self._l().route[*self.game.player.get_pos()] = True
        reward = self.game.tick(action)
        self.agent_location = self.game.player.get_pos()
        return reward

    def _move_agent_sweep(self) -> bool:
        if self.agent_location.x == self._l().map_size - 1:
            self.agent_location.y += 1
        self.agent_location.x += 1
        self.agent_location.x %= self._l().map_size
        return self.agent_location.y >= self._l().map_size
