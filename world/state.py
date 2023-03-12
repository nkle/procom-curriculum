from __future__ import division

import webbrowser
from collections import defaultdict
from functools import reduce
from math import floor
from random import randrange

import pygame.display
import pygame.font
import pygame.sprite
from pygame.locals import *

import elements.sam
import elements.static
from utils.common import *

WORLD_ASSETS_DIR = get_path(os.path.join('assets', 'world'))


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
    """WorldState that has the start menu information."""
    def __init__(self, *args, **kwargs):
        super(StartMenu, self).__init__(*args, **kwargs)
        self._build_assets()

    def _build_assets(self):
        # Get screen size
        sr = pygame.display.get_surface().get_rect().size

        # Create large font for main title and subtitle
        large_text_font = pygame.font.Font(os.path.join(WORLD_ASSETS_DIR, 'freesansbold.ttf'), 40)
        text_font = pygame.font.Font(os.path.join(WORLD_ASSETS_DIR, 'freesansbold.ttf'), 20)

        # Title text render and add
        text = large_text_font.render('ProCom Curriculum 2023', True, WorldState.BLUE, WorldState.BLACK)
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

        # Iterate over dict items and draw them on screen
        for asset_name, asset in self._assets.items():
            screen.blit(asset[0], asset[1])

    def update(self, dt, frame_num, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                # When spacebar is pressed, send request to change states
                if event.key == pygame.K_SPACE:
                    return StateHandler.GAME


class Game(WorldState):
    def __init__(self, *args, **kwargs):
        super(Game, self).__init__(*args, **kwargs)
        self._levels = dict()

        self._bottom_grid = defaultdict(lambda: None)
        self._rows = 5
        self._columns = 8

        self._course_list = dict()

        self._build_world(kwargs["config"])
        self._courses_taken = list()

        self._active_course_info = None

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

        repack_config = self._repackage_config(config["courses"])

        sr = pygame.display.get_surface().get_rect().size

        # Create platforms
        pt_size = (20, 20)
        lad_size = (20, 120)
        chest_size = (30, 30)
        sr = pygame.display.get_surface().get_rect().size

        max_years = 5

        course_space_multiplier = 3

        # Make ground floor
        floor_block_pos = list(range(0, sr[0],  pt_size[0]))
        for tile_num, j in enumerate(floor_block_pos):
            # if j == floor_block_pos[0]:
            #     tile_type = elements.static.PlatformTile.TYPE_LEFT
            # elif j == floor_block_pos[-1]:
            #     tile_type = elements.static.PlatformTile.TYPE_RIGHT
            if tile_num % 3 == 0:
                tile_type = elements.static.PlatformTile.TYPE_LEFT
            elif tile_num % 3 == 2:
                tile_type = elements.static.PlatformTile.TYPE_RIGHT
            else:
                tile_type = elements.static.PlatformTile.TYPE_MIDDLE

            pt = elements.static.PlatformTile(pos=(j, self._levels[0]), size=pt_size, tile_type=tile_type)
            self._sprite_group.add(pt)

        # all_types = list(set(
        #     course_type for course_types in repack_config["course"].values() for course_type in course_types
        # ))
        all_types = [type_info["type"] for type_info in config["types"]]
        self._colors_by_type = {
            type_info["type"]: type_info["color"] for type_info in config["types"]
        }

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
                try:
                    used_extra_blocks = randrange(0, extra_blocks)
                except ValueError:
                    used_extra_blocks = 0

            extra_blocks -= used_extra_blocks

            cur_end = cur_start + num_blocks + used_extra_blocks + free_blocks_per_type
            self._screen_sections_by_type[course_type] = block_pos[cur_start: cur_end]

            cur_start = cur_end + 1

        self._platform_locations_per_year = defaultdict(lambda: defaultdict(list))
        self._connections_by_year = defaultdict(lambda: defaultdict(dict))
        course_type_title = dict()
        chests = list()

        for i in self._levels.keys():
            for course_type in all_types:
                # Unpack courses
                courses = reduce(lambda a, b: a + b, [
                    [course for _ in range(0, course.get("number", 1))]
                    for course in repack_config["course"][i].get(course_type, list())
                ], list())

                if not courses:
                    continue

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
                cur_end = cur_start + cur_blocks_needed

                # Add extra blocks
                # try:
                #     cur_end += randrange(0, len(self._screen_sections_by_type[course_type]) - cur_end)
                # except ValueError:
                #     pass

                if block_pos_needed is not None:
                    while block_pos_needed not in self._screen_sections_by_type[course_type][cur_start: cur_end]:
                        cur_start = randrange(0, len(self._screen_sections_by_type[course_type]) - cur_blocks_needed)
                        cur_end = cur_start + cur_blocks_needed

                        # Add extra blocks
                        # try:
                        #     cur_end += randrange(0, len(self._screen_sections_by_type[course_type]) - cur_end)
                        # except ValueError:
                        #     pass

                for tile_num, j in enumerate(self._screen_sections_by_type[course_type][cur_start: cur_end]):
                    # if j == self._screen_sections_by_type[course_type][cur_start: cur_end][0]:
                    #     tile_type = "left"
                    # elif j == self._screen_sections_by_type[course_type][cur_start: cur_end][-1]:
                    #     tile_type = "right"
                    if tile_num % 3 == 0:
                        tile_type = elements.static.PlatformTile.TYPE_LEFT
                    elif tile_num % 3 == 2:
                        tile_type = elements.static.PlatformTile.TYPE_RIGHT
                    else:
                        tile_type = elements.static.PlatformTile.TYPE_MIDDLE

                        # Create course chest
                        course_info = courses.pop()
                        chests.append(
                            elements.static.CourseChest(pos=(j, ((sr[1] * 5) // 8) + 10 - 105 * i), size=chest_size,
                                                        course_id=course_info.get("id"),
                                                        course_color=self._colors_by_type[course_info.get("type")],
                                                        chest_name=course_info.get("chest_name"),
                                                        prereq_type=course_info.get("prereq_type"),
                                                        requirements=course_info.get("prereq"))
                        )
                        title_center = chests[-1].rect.center
                        chests.append(
                            elements.static.CourseTitle(pos=title_center,
                                                        course_id=course_info.get("id"),
                                                        chest_name=course_info.get("chest_name"))
                        )

                        self._course_list[course_info["id"]] = course_info

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
                    text_font = pygame.font.Font(os.path.join(WORLD_ASSETS_DIR, 'freesansbold.ttf'), 20)
                    text_pos = self._platform_locations_per_year[i][course_type][0]

                    # Instruction text
                    text = text_font.render(course_type, True, WorldState.WHITE)
                    text_rect = text.get_rect()
                    text_rect.center = (text_pos, self._levels[i])

                    even_num_tiles = len(self._platform_locations_per_year[i][course_type]) % 2 == 0
                    text_pos = (self._platform_locations_per_year[i][course_type][
                        len(self._platform_locations_per_year[i][course_type]) // 2
                                ], self._levels[i])

                    course_title = elements.static.CourseTypeTitle(course_type=course_type,
                                                                   pos=(
                                                                       text_pos[0] if even_num_tiles
                                                                       else text_pos[0] + pt_size[0] // 2,
                                                                       text_pos[1])
                                                                   )
                    # self._sprite_group.add(course_title)

                    course_type_title[course_type] = course_title

            courses_by_types = repack_config["courses"].get(i) or {}
            prev_courses_by_types = repack_config["courses"].get(i - 1) or {}

        for course_title in course_type_title.values():
            self._sprite_group.add(course_title)

        self._total_courses = len(chests) // 2

        for chest in chests:
            self._sprite_group.add(chest)

        # Create bottom grid coordinates
        self._grid_coordinates = [(floor(sr[0] * x / (self._columns + 2)),
                                   floor((sr[1] * 5 / 8 + 30) + (sr[1] * 3 / 8 + 30) * y / (self._rows + 2)))
                                  for x in range(1, self._columns + 1)
                                  for y in range(1, self._rows + 1)]

        # Create player
        sam_pos = (sr[0] / 2, ((sr[1] * 5) // 8) + 30)
        self._player = elements.sam.Player(pos=sam_pos)
        self._sprite_group.add(self._player)

    def update(self, dt, frame_num, events):

        sr = pygame.display.get_surface().get_rect().size

        # Add tracking of courses taken
        courses_taken = [
            sprite for sprite in self._sprite_group
            if isinstance(sprite, elements.static.CourseChest)
               and sprite.chest_state == elements.static.CourseChest.OPEN
        ]

        missing_courses = [course for course in courses_taken if course not in self._courses_taken]

        if missing_courses:
            for coor in self._grid_coordinates:
                if self._bottom_grid[coor] is None:
                    try:
                        course = missing_courses.pop(0)
                    except IndexError:
                        break
                    course_tracked = elements.static.CourseTracked(course_id=course.course_id,
                                                                   course_color=course.course_color,
                                                                   size=(120, 50),
                                                                   pos=coor)
                    self._bottom_grid[coor] = course
                    self._sprite_group.add(course_tracked)

        removed_grid = list()
        completed_requirements = 0

        for coor, course in self._bottom_grid.items():
            if course is not None and course not in courses_taken:
                self._bottom_grid[coor] = None
                removed_grid.append(coor)

            if self._bottom_grid[coor] is not None:
                completed_requirements += 1

        self._courses_taken = courses_taken

        # # Create extra info screens
        # buttons = pygame.mouse.get_pressed()
        # if buttons[0]:

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for sprite in self._sprite_group:
                    if isinstance(sprite, elements.static.CourseChest) and sprite.rect.collidepoint(pygame.mouse.get_pos()):
                        course_info = self._course_list[sprite.course_id]

                        side = elements.static.CourseInfoScreen.SIDE_RIGHT
                        if self._player.pos.x > sr[0] / 2:
                            side = elements.static.CourseInfoScreen.SIDE_LEFT

                        course_info_scr = elements.static.CourseInfoScreen(
                            course_id=course_info.get("id"),
                            course_name=course_info.get("name"),
                            course_desc=course_info.get("description"),
                            course_link=course_info.get("link"),
                            course_info=course_info,
                            side=side
                        )

                        if self._active_course_info is not None:
                            self._active_course_info.kill()

                        self._active_course_info = course_info_scr

                        self._sprite_group.add(course_info_scr)
                    elif isinstance(sprite, elements.static.CourseInfoScreen) and sprite.link_rect.collidepoint(pygame.mouse.get_pos()):
                        print(frame_num)
                        webbrowser.open_new(sprite.course_link)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._active_course_info = None

        # Add degree
        degree_size = (30, 30)
        degree_present = any([isinstance(sprite, elements.static.Degree) for sprite in self._sprite_group])
        if completed_requirements >= self._total_courses and not any(
                [isinstance(sprite, elements.static.Degree) for sprite in self._sprite_group]):
            self._sprite_group.add(elements.static.Degree(pos=(sr[0] // 2, self._levels[0]), size=degree_size))

        self._sprite_group.update(dt, frame_num, events, self._sprite_group.sprites(), self._player, self.levels,
                                  [course.course_id for course in self._courses_taken], removed_grid)

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

        # Black veil for fade in and fade out
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
