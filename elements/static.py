import pygame.sprite
import pygame.transform
import pygame.image
import pygame.math
import pygame.display
import os
from pygame.locals import *
from itertools import cycle

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
WORLD_ASSETS_DIR = os.path.join(DIR_PATH, '..', 'assets', 'world')


class PlatformTile(pygame.sprite.Sprite):
    def __init__(self, pos=None, size=None):
        super().__init__()
        self._vec = pygame.math.Vector2

        # self.surf = pygame.Surface((600, 20))
        # self.surf.fill((255,0,0))
        # self.rect = self.surf.get_rect(center = (800/2, 600 - 10))

        size = size or (30, 30)

        image = pygame.image.load(os.path.join(WORLD_ASSETS_DIR, "ground.png")).convert_alpha()
        image = pygame.transform.scale(image, size)
        self.image = image
        self.rect = self.image.get_rect()

        sr = pygame.display.get_surface().get_rect().size
        pos = pos or (sr[0] // 2, sr[1] // 3)

        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def update(self, dt, frame_num, sprites):
        pass


class Ladder(pygame.sprite.Sprite):
    def __init__(self, pos=None, size=None):
        super().__init__()
        self._vec = pygame.math.Vector2

        # self.surf = pygame.Surface((600, 20))
        # self.surf.fill((255,0,0))
        # self.rect = self.surf.get_rect(center = (800/2, 600 - 10))

        size = size or (30, 60)

        image = pygame.image.load(os.path.join(WORLD_ASSETS_DIR, "ladder.png")).convert_alpha()
        image = pygame.transform.scale(image, size)
        self.image = image
        self.rect = self.image.get_rect()

        sr = pygame.display.get_surface().get_rect().size
        pos = pos or (sr[0] // 2, sr[1] // 3)

        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def update(self, dt, frame_num, sprites):
        pass
