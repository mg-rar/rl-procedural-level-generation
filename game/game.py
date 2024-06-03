import numpy as np
import pygame
from pygame import Surface

from game.level import Level
from game.level_gen import LevelGenerator
from game.player import Player
from game.utils import Utils
from game.position import CartesianPosition as Pos


class Game:

    def __init__(self, window=None):
        pygame.init()
        pygame.display.set_caption("Buenos Dias, Fuckboy")
        pygame.display.set_icon(Utils.ICON)

        self.font = pygame.font.Font('assets/Gamepixies.ttf', 24)
        if window is None:
            self.window = pygame.display.set_mode((Utils.SCREEN_WIDTH, Utils.SCREEN_HEIGHT), pygame.RESIZABLE)
        else:
            self.window = window
        self.screen = Surface((Utils.TILE_SIZE * Utils.MAP_SIZE, Utils.TILE_SIZE * Utils.MAP_SIZE))

        self.render_queue: list[tuple[Pos, Surface]] = []
        self.render_delay: int = 120
        self.game_over: bool = False
        self.level: Level = LevelGenerator().make_level()
        self.player: Player = Player(pos=self.level.get_start_pos())

    def reset(self, level: Level = None, health: int = 10):
        if level is None:
            level = LevelGenerator().make_level()
        self.game_over: bool = False
        self.level: Level = level
        self.player: Player = Player(pos=self.level.get_start_pos())
        self.player._health = health

    def move_player(self, direction: Utils.Direction) -> bool:
        next_pos = self.player.get_next_pos(direction)
        if (next_pos.x not in range(self.level.map_size)
                or next_pos.y not in range(self.level.map_size)
                or next_pos in self.level.get_walls()):
            return False
        self.player.set_pos(self.player.get_next_pos(direction))
        return True

    def grab_item(self) -> int:
        grabbed = 0
        for item in self.level.get_items():
            if self.player.get_pos() == item.get_pos():
                self.player.receive_bonus(item)
                item.render_bonus(self.screen)
                self.level.remove_item(item)
                grabbed += 1
        return grabbed

    def attack_enemy(self) -> tuple[int, int]:
        if self.player.get_state() != Utils.EntityState.ATTACK:
            self.player.FRAME = 0
            self.player.set_state(Utils.EntityState.ATTACK)

        killed = 0
        damaged = 0
        for enemy in self.level.get_enemies():
            if enemy.get_pos() not in self.player.get_near_pos():
                continue
            enemy.hurt(self.player.get_power())
            self.render_queue.append(enemy.render_damage(self.player.get_power()))
            if enemy.get_health() <= 0:
                self.player.receive_xp(enemy.get_current_xp())
                self.level.remove_enemy(enemy)
                killed += 1
            else:
                damaged += 1
        return killed, damaged

    def attack_player(self) -> int:
        hurt = 0
        if self.player.get_state() == Utils.EntityState.ATTACK:
            return 0
        for enemy in self.level.get_enemies():
            if self.player.get_pos() not in enemy.get_near_pos():
                continue
            if enemy.get_state() != Utils.EntityState.ATTACK:
                enemy.COOLDOWN += 1
                enemy.COOLDOWN %= Utils.COOLDOWN
            if enemy.COOLDOWN == 0:
                enemy.FRAME = -1
                enemy.set_state(Utils.EntityState.ATTACK)
                self.player.hurt(enemy.get_power())
                self.render_queue.append(self.player.render_damage(enemy.get_power()))
                hurt += 1
        return hurt

    def tick(self, player_action) -> int:
        self.render_queue = []
        self.player.tick()
        for enemy in self.level.get_enemies():
            enemy.tick()

        if self.game_over:
            return 0

        reward = 0
        move_direction = None
        match player_action:
            case 0:
                move_direction = Utils.Direction.UP
            case 1:
                move_direction = Utils.Direction.DOWN
            case 2:
                move_direction = Utils.Direction.LEFT
            case 3:
                move_direction = Utils.Direction.RIGHT
        if move_direction is not None:
            exit_distance = sum(self.player.get_pos() - self.level.get_exit_pos())
            reward += -1 if self.move_player(move_direction) else -3
            new_distance = sum(self.player.get_pos() - self.level.get_exit_pos())
            if self.player.get_pos() == self.level.get_exit_pos():
                self.game_over = True
                return 100
            if new_distance < exit_distance:
                reward += 1
        if player_action == 4:
            k, d = self.attack_enemy()
            reward += -1 + k * 5 + d * 1
        reward += self.grab_item() * 3

        reward -= self.attack_player()
        if self.player.get_health() > 0:
            return reward

        # death
        self.player.FRAME = 0
        self.player.set_state(Utils.EntityState.DEAD)
        self.game_over = True
        return -100

    def render(self, side, center):
        pygame.time.delay(self.render_delay)
        self.screen.fill((0, 0, 0))

        self.level.render(self.screen)
        self.player.render(self.screen)
        for enemy in self.level.get_enemies():
            enemy.render(self.screen)
        for ((x, y), render_item) in self.render_queue:
            self.screen.blit(render_item, (x * Utils.TILE_SIZE, y * Utils.TILE_SIZE - 8))
        scaled_screen = pygame.transform.scale(self.screen, (side, side))
        self.window.blit(scaled_screen, (center, 0))
        # self._render_stats(center)
        pygame.display.update()

    def _render_stats(self, center):
        hp_stat = self.font.render('health : ' + str(self.player.get_health()), False, (255, 255, 255))
        hp_display = Surface(hp_stat.get_size(), pygame.SRCALPHA)
        hp_display.blit(hp_stat, (0, 0))

        xp_stat = self.font.render('score : ' + str(self.player.get_current_xp()), False, (255, 255, 255))
        xp_display = Surface(xp_stat.get_size(), pygame.SRCALPHA)
        xp_display.blit(xp_stat, (0, 0))

        self.window.blit(hp_display, (center + 2, 2))
        self.window.blit(xp_display, (center + 2, hp_stat.get_size()[1] + 2))


if __name__ == '__main__':
    game = Game()
    game.reset()
    game.run_playtest()
