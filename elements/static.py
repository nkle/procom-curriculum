import pygame.sprite
import pygame.transform
import pygame.image
import pygame.math
import pygame.display
import os
from pygame.locals import *
from itertools import cycle
from random import randrange
import elements.sam

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
WORLD_ASSETS_DIR = os.path.join(DIR_PATH, '..', 'assets', 'world')


class PlatformTile(pygame.sprite.Sprite):
    TYPE_MIDDLE="middle"
    TYPE_LEFT="left"
    TYPE_RIGHT="right"

    def __init__(self, pos=None, size=None, tile_type=None):
        super().__init__()
        tile_type = tile_type or PlatformTile.TYPE_MIDDLE
        self._vec = pygame.math.Vector2

        # self.surf = pygame.Surface((600, 20))
        # self.surf.fill((255,0,0))
        # self.rect = self.surf.get_rect(center = (800/2, 600 - 10))

        size = size or (30, 30)

        tile_img_path = os.path.join(WORLD_ASSETS_DIR, "tile_%s.jpg" % tile_type)

        image = pygame.image.load(tile_img_path).convert_alpha()
        image = pygame.transform.scale(image, size)
        self.image = image
        self.rect = self.image.get_rect()

        sr = pygame.display.get_surface().get_rect().size
        pos = pos or (sr[0] // 2, sr[1] // 3)

        self.rect.x = pos[0]
        self.rect.y = pos[1]


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


class CourseTypeTitle(pygame.sprite.Sprite):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 128)

    def __init__(self, course_type=None, pos=None):
        super().__init__()
        pygame.sprite.Sprite.__init__(self)

        course_type = course_type or "Placeholder"
        pos = pos or (0, 0)

        self.font = pygame.font.Font('freesansbold.ttf', 15)
        self.textSurf = self.font.render(course_type, True, CourseTypeTitle.WHITE)
        width, height = self.textSurf.get_size()
        # self.image = pygame.Surface((width, height))

        # sr = pygame.display.get_surface().get_rect().size
        # self.image = pygame.Surface(sr)

        # width = 300
        # height = 25
        vertical_offset = 25
        self.image = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        self.image = self.image.convert_alpha()
        W = self.textSurf.get_width()
        H = self.textSurf.get_height()
        self.image.blit(self.textSurf, [width / 2 - W / 2, height / 2 - H / 2])

        # self.image.blit(self.textSurf, pos)

        self.rect = self.textSurf.get_rect()
        self.rect.center = (pos[0], pos[1] + vertical_offset)

        # # Instruction text
        # text = text_font.render(course_title, True, CourseTitle.WHITE)
        # text_rect = text.get_rect()
        # text_rect.center = (text_pos, self._levels[i])


class CourseChest(pygame.sprite.Sprite):
    ACTIVE="active"
    INACTIVE="inactive"
    OPEN="open"

    def __init__(self, pos=None, size=None, course_id=None, chest_state=None, requirements=None):
        super().__init__()
        self._course_id = course_id or "COURSE ID"
        self._chest_state = chest_state or CourseChest.INACTIVE
        self._vec = pygame.math.Vector2
        self._size = size or (30, 30)

        # self.surf = pygame.Surface((600, 20))
        # self.surf.fill((255,0,0))
        # self.rect = self.surf.get_rect(center = (800/2, 600 - 10))

        self._chest_states = {
            CourseChest.ACTIVE: os.path.join(WORLD_ASSETS_DIR, "chest_%s.png" % CourseChest.ACTIVE),
            CourseChest.INACTIVE:  os.path.join(WORLD_ASSETS_DIR, "chest_%s.png" % CourseChest.INACTIVE),
            CourseChest.OPEN:  os.path.join(WORLD_ASSETS_DIR, "chest_%s.png" % CourseChest.OPEN)
        }

        image = pygame.image.load(self._chest_states[self._chest_state]).convert_alpha()
        image = pygame.transform.scale(image, size)
        self.image = image
        self.rect = self.image.get_rect()

        sr = pygame.display.get_surface().get_rect().size
        pos = pos or (sr[0] // 2, sr[1] // 3)

        self.rect.x = pos[0]
        self.rect.y = pos[1]

        self._requirements = requirements or list()

    @property
    def course_id(self):
        return self._course_id

    @property
    def chest_state(self):
        return self._chest_state

    def update(self, dt, frame_num, sprites, player, levels, courses_taken):
        if self._chest_state == CourseChest.INACTIVE \
                and (all(map(lambda x: x in courses_taken, self._requirements)) or not self._requirements):
            self._chest_state = CourseChest.ACTIVE
            image = pygame.image.load(self._chest_states[self._chest_state]).convert_alpha()
            image = pygame.transform.scale(image, self._size)
            self.image = image

        pressed_keys = pygame.key.get_pressed()

        touched = False

        if pygame.sprite.collide_rect(self, player):
            touched = True

        if touched and pressed_keys[K_SPACE] and frame_num % 5 == 0:
            if self._chest_state == CourseChest.ACTIVE:
                self._chest_state = CourseChest.OPEN
                image = pygame.image.load(self._chest_states[self._chest_state]).convert_alpha()
                image = pygame.transform.scale(image, self._size)
                self.image = image
            elif self._chest_state == CourseChest.OPEN:
                self._chest_state = CourseChest.ACTIVE
                image = pygame.image.load(self._chest_states[self._chest_state]).convert_alpha()
                image = pygame.transform.scale(image, self._size)
                self.image = image


class CourseTitle(pygame.sprite.Sprite):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 128)

    def __init__(self, course_id=None, pos=None):
        super().__init__()
        pygame.sprite.Sprite.__init__(self)

        course_id = course_id or "Placeholder"
        pos = pos or (0, 0)

        self.font = pygame.font.Font('freesansbold.ttf', 10)
        self.textSurf = self.font.render(course_id, True, CourseTypeTitle.WHITE)
        width, height = self.textSurf.get_size()
        # self.image = pygame.Surface((width, height))

        # sr = pygame.display.get_surface().get_rect().size
        # self.image = pygame.Surface(sr)

        # width = 300
        # height = 25
        vertical_offset = - 5
        self.image = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        self.image = self.image.convert_alpha()
        W = self.textSurf.get_width()
        H = self.textSurf.get_height()
        self.image.blit(self.textSurf, (width / 2 - W / 2, height / 2 - H / 2))

        # self.image.blit(self.textSurf, pos)

        self.rect = self.textSurf.get_rect()
        self.rect.center = (pos[0], pos[1] + vertical_offset)

        # # Instruction text
        # text = text_font.render(course_title, True, CourseTitle.WHITE)
        # text_rect = text.get_rect()
        # text_rect.center = (text_pos, self._levels[i])


class CourseTracked(pygame.sprite.Sprite):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 128)

    def __init__(self, course_id=None, pos=None):
        super().__init__()
        pygame.sprite.Sprite.__init__(self)

        course_id = course_id or "Placeholder"
        pos = pos or (0, 0)

        self.font = pygame.font.Font('freesansbold.ttf', 15)
        self.textSurf = self.font.render(course_id, True, CourseTypeTitle.WHITE)
        width, height = self.textSurf.get_size()
        # self.image = pygame.Surface((width, height))

        # sr = pygame.display.get_surface().get_rect().size
        # self.image = pygame.Surface(sr)

        # width = 300
        # height = 25
        vertical_offset = 0
        self.image = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        self.image = self.image.convert_alpha()
        W = self.textSurf.get_width()
        H = self.textSurf.get_height()
        self.image.blit(self.textSurf, (width / 2 - W / 2, height / 2 - H / 2))

        # self.image.blit(self.textSurf, pos)

        self.rect = self.textSurf.get_rect()
        self.rect.center = (pos[0], pos[1] + vertical_offset)

        # # Instruction text
        # text = text_font.render(course_title, True, CourseTitle.WHITE)
        # text_rect = text.get_rect()
        # text_rect.center = (text_pos, self._levels[i])


