import pygame.sprite
import pygame.image
import pygame.math
import pygame.display
import os
from pygame.locals import *
from itertools import cycle


DIR_PATH = os.path.dirname(os.path.realpath(__file__))


class Player(pygame.sprite.Sprite):
    ACC = 0.5
    FRIC = -0.12

    def __init__(self):
        super().__init__()
        self._vec = pygame.math.Vector2
        # self.surf = pygame.Surface((30, 30))
        # self.surf.fill((128,255,40))
        # self.rect = self.surf.get_rect(center = (10, 420))
        sam_dir = os.path.join(DIR_PATH, '..', 'assets', 'sam')

        self._right = cycle([os.path.join(sam_dir, "Right{}.png".format(i)) for i in range(1,5)])
        self._left = cycle([os.path.join(sam_dir, "Left{}.png".format(i)) for i in range(1,5)])
        self._front = cycle([os.path.join(sam_dir, "Front{}.png".format(i)) for i in range(1,5)])
        self._back = cycle([os.path.join(sam_dir, "Back{}.png".format(i)) for i in range(1,5)])

        self.image = pygame.image.load(next(self._front)).convert_alpha()
        # self.rect = self.image.get_rect(center=(800 / 2 , 600 - 30))
        self.rect = self.image.get_rect()

        sr = pygame.display.get_surface().get_rect().size

        self.pos = self._vec((sr[0] / 2, sr[1] - 30))
        self.vel = self._vec(0, 0)
        self.acc = self._vec(0, 0)

    def move(self, dt, frame_num):
        self.acc = self._vec(0, 0)

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_LEFT]:
            self.acc.x = -Player.ACC
            if frame_num % 10 == 0:
                self.image = pygame.image.load(next(self._left)).convert_alpha()
        elif pressed_keys[K_RIGHT]:
            self.acc.x = Player.ACC
            if frame_num % 10 == 0:
                self.image = pygame.image.load(next(self._right)).convert_alpha()
        elif pressed_keys[K_UP]:
            if frame_num % 10 == 0:
                self.image = pygame.image.load(next(self._back)).convert_alpha()
        else:
            if frame_num % 10 == 0:
                self.image = pygame.image.load(next(self._front)).convert_alpha()

        self.acc.x += self.vel.x * Player.FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        sr = pygame.display.get_surface().get_rect().size

        if self.pos.x > sr[0]:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = sr[0]

        self.rect.midbottom = self.pos

