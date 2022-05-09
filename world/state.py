import pygame.font
import pygame.sprite
import pygame.display
from pygame.locals import *
import sys
import elements.sam
import elements.static
import random
from collections import defaultdict
import colour
from functools import reduce


class WorldState(object):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 128)

    def __init__(self, *args, **kwargs):
        self._sprite_group = pygame.sprite.Group()
        self._assets = dict()

    def draw(self, screen):
        pass

    def update(self, dt, frame_num, events):
        pass

    @staticmethod
    def _quit(event_type):
        if event_type == QUIT:
            pygame.quit()
            sys.exit()


class StartMenu(WorldState):
    def __init__(self, *args, **kwargs):
        super(StartMenu, self).__init__(*args, **kwargs)
        self._build_assets()

    def _build_assets(self):
        sr = pygame.display.get_surface().get_rect().size
        large_text_font = pygame.font.Font('freesansbold.ttf', 40)
        text_font = pygame.font.Font('freesansbold.ttf', 20)

        # Title text
        text = large_text_font.render('ProCom Curriculum 2022', True, WorldState.BLUE, WorldState.BLACK)
        text_rect = text.get_rect()
        text_rect.center = (sr[0] // 2, sr[1] // 3)
        self._assets["title"] = (text, text_rect)

        # Instruction text
        text = text_font.render('Press spacebar to start', True, WorldState.BLUE, WorldState.BLACK)
        text_rect = text.get_rect()
        text_rect.center = (sr[0] // 2, sr[1] // 2)
        self._assets["instructions"] = (text, text_rect)

    def draw(self, screen):
        screen.fill(WorldState.BLACK)

        for asset_name, asset in self._assets.items():
            screen.blit(asset[0], asset[1])

    def update(self, dt, frame_num, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return StateHandler.GAME


class Game(WorldState):
    def __init__(self, *args, **kwargs):
        super(Game, self).__init__(*args, **kwargs)
        self._build_world(kwargs["config"])

    @staticmethod
    def _repackage_config(config):
        repack_config = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

        for element in config:
            repack_config[element["class"]][element["year"]][element["type"]].append(element)

        return repack_config

    def _build_world(self, config):
        repack_config = self._repackage_config(config)

        sr = pygame.display.get_surface().get_rect().size

        # Create player
        sam_pos = (sr[0] / 2, sr[1] * 5 / 7)
        player_1 = elements.sam.Player(pos=sam_pos)
        self._sprite_group.add(player_1)

        # Create platforms
        pt_size = (30, 30)
        lad_size = (30, 60)
        sr = pygame.display.get_surface().get_rect().size

        max_years = 5

        # Make ground floor
        for j in range(0, sr[0],  pt_size[0]):
            pt = elements.static.PlatformTile(pos=(j, (sr[1] * 5) // 7), size=pt_size)
            self._sprite_group.add(pt)

        all_types = set(
            course_type for course_types in repack_config["course"].values() for course_type in course_types
        )

        sizes_by_type = {
            element_type: max(
                (
                    len([course for course in (courses_by_type.get(element_type) or []) if course.get("number") is None])
                     + reduce(lambda a, b: a + b, [course.get("number") or 0 for course in courses_by_type.get(element_type) or []], 0)
                )
                for courses_by_type in repack_config["course"].values()
            ) * 2
            for element_type in all_types
        }

        block_pos = list(range(30, sr[0] - 30,  pt_size[0]))
        blocks_needed = reduce(lambda a, b: a + b, [size for size in sizes_by_type.values()])
        free_blocks = len(block_pos) - blocks_needed

        screen_sections_by_type = dict()
        cur_start = 0
        for course_type in all_types:
            num_blocks = sizes_by_type[course_type]

            screen_sections_by_type[course_type] = block_pos[cur_start:
                                                             cur_start + num_blocks + free_blocks // len(all_types)]

        levels_by_type = defaultdict(list)

        for i in range(1, max_years):
            courses_by_types = repack_config["courses"].get(i) or {}
            prev_courses_by_types = repack_config["courses"].get(i - 1) or {}

            # block_pos = list(range(30, sr[0] - 30,  pt_size[0]))
            #
            # for type, courses in courses_by_types.items():
            #     if prev_keys_by_type.get(type) is None:

            for j in list(range(30, sr[0] - 30,  pt_size[0])):
                pt = elements.static.PlatformTile(pos=(j, (sr[1] * (5 - i)) // 7), size=pt_size)
                self._sprite_group.add(pt)

            # if i % 4 == 0:
            #     lad = elements.static.Ladder(pos=(i, (sr[1] * 5) // 7 - lad_size[1]), size=lad_size)
            #     self._sprite_group.add(lad)

        # Create ladders

        pass

    def update(self, dt, frame_num, events):
        self._sprite_group.update(dt, frame_num, self._sprite_group.sprites())

    def draw(self, screen):
        screen.fill(WorldState.BLUE)
        self._sprite_group.draw(screen)


class StateHandler(object):
    START_MENU="START_MENU"
    GAME="GAME"

    def __init__(self, *args, **kwargs):
        self._states = {
            StateHandler.START_MENU: StartMenu(*args, **kwargs),
            StateHandler.GAME: Game(*args, **kwargs)
        }
        self._current_state = self._states[StateHandler.START_MENU]
        self._next_state = None
        self._fading = None
        self._alpha = 0
        sr = pygame.display.get_surface().get_rect()
        self.veil = pygame.Surface(sr.size)
        self.veil.fill((0, 0, 0))

    def next(self):
        if not self._fading:
            self._fading = 'OUT'
            self._alpha = 0

    def draw(self, screen):
        self._current_state.draw(screen)
        if self._fading:
            self.veil.set_alpha(self._alpha)
            screen.blit(self.veil, (0, 0))

        pygame.display.flip()

    def fade_in(self):
        if self._fading is None:
            self._fading = 'IN'
            self._alpha = 255

    def update(self, dt, frame_num, events):
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        next_state = self._current_state.update(dt, frame_num, events)

        if next_state is not None:
            self._next_state = self._states.get(next_state) or self._current_state
            self._fading = 'OUT'

        if self._fading == 'OUT':
            self._alpha += 8
            if self._alpha >= 255:
                self._fading = 'IN'
                self._current_state = self._next_state
        else:
            self._alpha -= 2
            if self._alpha <= 0:
                self._fading = None
