from itertools import cycle

import pygame.display
import pygame.image
import pygame.math
import pygame.sprite
from pygame.locals import *

import elements.static
from utils.common import *

SAM_ASSETS_PATH = get_path(os.path.join('assets', 'sam'))


class Player(pygame.sprite.Sprite):
    ACC = 0.5
    FRIC = -0.12

    def __init__(self, pos):
        super().__init__()
        self._vec = pygame.math.Vector2
        # self.surf = pygame.Surface((30, 30))
        # self.surf.fill((128,255,40))
        # self.rect = self.surf.get_rect(center = (10, 420))
        sam_dir = SAM_ASSETS_PATH

        self._right = cycle([os.path.join(sam_dir, "Right{}.png".format(i)) for i in range(1,5)])
        self._left = cycle([os.path.join(sam_dir, "Left{}.png".format(i)) for i in range(1,5)])
        self._front = cycle([os.path.join(sam_dir, "Front{}.png".format(i)) for i in range(1,5)])
        self._back = cycle([os.path.join(sam_dir, "Back{}.png".format(i)) for i in range(1,5)])

        self.image = pygame.image.load(next(self._front)).convert_alpha()
        # self.rect = self.image.get_rect(center=(800 / 2 , 600 - 30))
        self.rect = self.image.get_rect()

        sr = pygame.display.get_surface().get_rect().size

        pos = pos or (sr[0] / 2, sr[1] * 5 / 7)

        self.pos = self._vec(pos)
        self.vel = self._vec(0, 0)
        self.acc = self._vec(0, 0)

    def update(self, dt, frame_num, events, sprites, player, levels, courses_taken, removed_grid):
        self.acc = self._vec(0, 0)

        pressed_keys = pygame.key.get_pressed()

        on_ladder = False
        on_platform = False
        for sprite in sprites:
            if isinstance(sprite, elements.static.Ladder) and pygame.sprite.collide_rect(self, sprite):
                offset = self.rect.centerx - sprite.rect.centerx
                if -10 < offset < 10:
                    on_ladder = True

            elif isinstance(sprite, elements.static.PlatformTile) and pygame.sprite.collide_rect(self, sprite):
                if self.rect.bottom > sprite.rect.top:
                    overlap = self.rect.bottom - sprite.rect.top
                    if overlap < 10:
                        self.rect.bottom -= overlap
                        on_platform = True
                # if self.rect.top < sprite.rect.bottom:
                #     overlap = sprite.rect.bottom - self.rect.top
                #     self.rect.top += overlap
                #     on_platform = True

        using_ladder = False

        if pressed_keys[K_LEFT]:
            self.acc.x = -Player.ACC
            if frame_num % 10 == 0:
                self.image = pygame.image.load(next(self._left)).convert_alpha()
        elif pressed_keys[K_RIGHT]:
            self.acc.x = Player.ACC
            if frame_num % 10 == 0:
                self.image = pygame.image.load(next(self._right)).convert_alpha()
        elif pressed_keys[K_UP]:
            # if frame_num % 10 == 0:
            #     self.image = pygame.image.load(next(self._back)).convert_alpha()

            if on_ladder:
                self.acc.y = -Player.ACC
                using_ladder = True

        elif pressed_keys[K_DOWN]:
            # if frame_num % 10 == 0:
            #     self.image = pygame.image.load(next(self._back)).convert_alpha()

            if on_ladder:
                self.acc.y = Player.ACC
                using_ladder = True

        else:
            if frame_num % 10 == 0:
                self.image = pygame.image.load(next(self._front)).convert_alpha()

        if not on_ladder:
            if on_platform:
                self.acc.y = 0
                self.vel.y = 0
            else:
                self.acc.y = Player.ACC

        if (on_ladder and not on_platform) or using_ladder:
            if frame_num % 10 == 0:
                self.image = pygame.image.load(next(self._back)).convert_alpha()

        if using_ladder:
            self.vel.x = 0
            self.acc.x = 0

        self.acc.x += self.vel.x * Player.FRIC
        self.acc.y += self.vel.y * Player.FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        sr = pygame.display.get_surface().get_rect().size

        if self.pos.x > sr[0]:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = sr[0]
        if self.pos.y > levels[0] + 5:
            self.pos.y = levels[0] + 5

        self.rect.midbottom = self.pos

