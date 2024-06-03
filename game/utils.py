from enum import Enum
import pygame


class Utils:

    SCREEN_WIDTH = 720
    SCREEN_HEIGHT = 480
    FRAME_RATE = 8
    COOLDOWN = 4
    ICON = pygame.image.load('assets/icon.png')

    MAP_SIZE = 16
    TILE_SIZE = 16

    GRASS = pygame.image.load('assets/grass.png')
    ITEM = pygame.image.load('assets/mushroom.png')
    WALL = pygame.image.load('assets/wall.png')
    EXIT = pygame.image.load('assets/bonfire.png')
    PLAYER = pygame.image.load('assets/necromancer.png')
    ENEMY = pygame.image.load('assets/slime.png')

    LevelObject = Enum('LevelObject', ['GRASS', 'WALL', 'ITEM_HEAL', 'ITEM_POWER', 'ENEMY', 'ENTER', 'EXIT'])
    EntityState = Enum('EntityState', ['IDLE', 'MOVE', 'HURT', 'ATTACK', 'DEAD'])
    Direction = Enum('Direction', ['UP', 'DOWN', 'LEFT', 'RIGHT'])
    ItemType = Enum('ItemType', ['HEALTH', 'POWER'])

    @staticmethod
    def get_tile_set(image, tile_size):
        tiles = []
        x0 = y0 = 0

        for y in range(x0, image.get_height(), tile_size):
            for x in range(y0, image.get_width(), tile_size):
                tile = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                tile.blit(image, (0, 0), (x, y, * (tile_size, tile_size)))
                tiles.append(tile.convert_alpha())
        return tiles
