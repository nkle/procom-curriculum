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
import os
from itertools import cycle
from random import randrange


DIR_PATH = os.path.dirname(os.path.realpath(__file__))
WORLD_ASSETS_DIR = os.path.join(DIR_PATH, '..', 'assets', 'world')


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
        self._levels = dict()
        self._build_world(kwargs["config"])

    @property
    def levels(self):
        return self._levels

    @staticmethod
    def _repackage_config(config):
        repack_config = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

        for element in config:
            repack_config[element["class"]][element["year"]][element["type"]].append(element)

        return repack_config

    def _build_world(self, config):
        sr = pygame.display.get_surface().get_rect().size
        level_zero = ((sr[1] * 5) // 8) + 30
        self._levels = {i: level_zero - 105 * i for i in range(1, 5)}
        self._levels[0] = level_zero

        repack_config = self._repackage_config(config)

        sr = pygame.display.get_surface().get_rect().size

        # Create platforms
        pt_size = (20, 20)
        lad_size = (20, 120)
        sr = pygame.display.get_surface().get_rect().size

        max_years = 5

        course_space_multiplier = 4

        # Make ground floor
        floor_block_pos = list(range(0, sr[0],  pt_size[0]))
        for j in floor_block_pos:
            if j == floor_block_pos[0]:
                tile_type = elements.static.PlatformTile.TYPE_LEFT
            elif j == floor_block_pos[-1]:
                tile_type = elements.static.PlatformTile.TYPE_RIGHT
            else:
                tile_type = elements.static.PlatformTile.TYPE_MIDDLE

            pt = elements.static.PlatformTile(pos=(j, self._levels[0]), size=pt_size, tile_type=tile_type)
            self._sprite_group.add(pt)

        all_types = list(set(
            course_type for course_types in repack_config["course"].values() for course_type in course_types
        ))

        sizes_by_type = {
            element_type: max(
                (
                    len([course for course in (courses_by_type.get(element_type) or []) if course.get("number") is None])
                     + reduce(lambda a, b: a + b, [course.get("number") or 0 for course in courses_by_type.get(element_type) or []], 0)
                )
                for courses_by_type in repack_config["course"].values()
            ) * course_space_multiplier
            for element_type in all_types
        }

        block_pos = list(range(30, sr[0] - 30,  pt_size[0]))
        blocks_needed = reduce(lambda a, b: a + b, [size for size in sizes_by_type.values()])
        free_blocks = len(block_pos) - blocks_needed
        free_blocks_per_type = free_blocks // len(all_types)
        extra_blocks = free_blocks % len(all_types)

        self._screen_sections_by_type = dict()
        cur_start = 0
        for course_type in all_types:
            num_blocks = sizes_by_type[course_type]

            if course_type == all_types[-1]:
                used_extra_blocks = extra_blocks
            else:
                used_extra_blocks = randrange(0, extra_blocks)

            extra_blocks -= used_extra_blocks

            cur_end = cur_start + num_blocks + used_extra_blocks + free_blocks_per_type
            self._screen_sections_by_type[course_type] = block_pos[cur_start: cur_end]

            cur_start = cur_end + 1

        self._platform_locations_per_year = defaultdict(lambda: defaultdict(list))
        self._connections_by_year = defaultdict(lambda: defaultdict(dict))
        course_type_title = dict()

        for i in self._levels.keys():
            for course_type in all_types:
                courses = repack_config["course"][i].get(course_type, list())

                if not courses:
                    continue

                if i == 1:
                    # Add label
                    pass

                cur_blocks_needed = len(courses) * course_space_multiplier

                for j in range(1, i + 1):
                    block_pos_needed = self._connections_by_year[i - j].get(course_type)
                    ladder_multiplier = j
                    connecting_level = i - j

                    if block_pos_needed is not None:
                        break

                try:
                    cur_start = randrange(0, len(self._screen_sections_by_type[course_type]) - cur_blocks_needed)
                except ValueError:
                    cur_start = 0
                cur_end = cur_start + cur_blocks_needed + 1

                try:
                    cur_end += randrange(0, len(self._screen_sections_by_type[course_type]) - cur_end)
                except ValueError:
                    pass

                if block_pos_needed is not None:
                    while block_pos_needed not in self._screen_sections_by_type[course_type][cur_start: cur_end]:
                        cur_start = randrange(0, len(self._screen_sections_by_type[course_type]) - cur_blocks_needed)
                        cur_end = cur_start + cur_blocks_needed + 1

                        try:
                            cur_end += randrange(0, len(self._screen_sections_by_type[course_type]) - cur_end)
                        except ValueError:
                            pass

                for j in self._screen_sections_by_type[course_type][cur_start: cur_end]:
                    if j == self._screen_sections_by_type[course_type][cur_start: cur_end][0]:
                        tile_type = "left"
                    elif j == self._screen_sections_by_type[course_type][cur_start: cur_end][-1]:
                        tile_type = "right"
                    else:
                        tile_type = "middle"

                    self._platform_locations_per_year[i][course_type].append(j)
                    pt = elements.static.PlatformTile(pos=(j, ((sr[1] * 5) // 8) + 30 - 105 * i),
                                                      size=pt_size, tile_type=tile_type)
                    self._sprite_group.add(pt)

                self._connections_by_year[i][course_type] = self._screen_sections_by_type[course_type][randrange(cur_start, cur_end)]

                if block_pos_needed is None:
                    block_pos_needed = self._platform_locations_per_year[i][course_type][randrange(
                        0, len(self._platform_locations_per_year[i][course_type])
                    )]

                for j in range(connecting_level, i):
                    lad = elements.static.Ladder(pos=(block_pos_needed, self._levels[j] - lad_size[1]),
                                                 size=(lad_size[0], lad_size[1]))
                    self._sprite_group.add(lad)

                if course_type_title.get(course_type) is None:
                    # Add course title card
                    text_font = pygame.font.Font('freesansbold.ttf', 20)
                    text_pos = self._platform_locations_per_year[i][course_type][0]

                    # Instruction text
                    text = text_font.render(course_type, True, WorldState.WHITE)
                    text_rect = text.get_rect()
                    text_rect.center = (text_pos, self._levels[i])

                    text_pos = (self._platform_locations_per_year[i][course_type][
                        len(self._platform_locations_per_year[i][course_type]) // 2
                                ], self._levels[i])

                    course_title = elements.static.CourseTitle(course_title=course_type, pos=text_pos)
                    # self._sprite_group.add(course_title)

                    course_type_title[course_type] = course_title

            courses_by_types = repack_config["courses"].get(i) or {}
            prev_courses_by_types = repack_config["courses"].get(i - 1) or {}

        for course_title in course_type_title.values():
            self._sprite_group.add(course_title)

        # Create player
        sam_pos = (sr[0] / 2, ((sr[1] * 5) // 8) + 30)
        player_1 = elements.sam.Player(pos=sam_pos)
        self._sprite_group.add(player_1)

            # block_pos = list(range(30, sr[0] - 30,  pt_size[0]))
            #
            # for type, courses in courses_by_types.items():
            #     if prev_keys_by_type.get(type) is None:

            # for j in list(range(30, sr[0] - 30,  pt_size[0])):
            #     pt = elements.static.PlatformTile(pos=(j, ((sr[1] * 5) // 8) + 30 - 105 * i), size=pt_size)
            #     self._sprite_group.add(pt)

            # if i % 4 == 0:
            #     lad = elements.static.Ladder(pos=(i, (sr[1] * 5) // 7 - lad_size[1]), size=lad_size)
            #     self._sprite_group.add(lad)

        # Create ladders

        pass

    def update(self, dt, frame_num, events):
        self._sprite_group.update(dt, frame_num, self._sprite_group.sprites(), self.levels)

    def draw(self, screen):
        sr = pygame.display.get_surface().get_rect().size
        bg = pygame.image.load(os.path.join(WORLD_ASSETS_DIR, "bg.jpg"))
        bg = pygame.transform.scale(bg, sr)
        screen.blit(bg, (0, 0))

        # screen.fill(WorldState.BLUE)
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

    @property
    def states(self):
        return self._states

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
