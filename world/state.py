import pygame.font
import pygame.sprite
import pygame.display
from pygame.locals import *
import sys
import player.sam
import random
import colour


class WorldState(object):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 128)

    def __init__(self):
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
    def __init__(self):
        super(StartMenu, self).__init__()
        self._build_assets()

    def _build_assets(self):
        sr = pygame.display.get_surface().get_rect().size
        large_text_font = pygame.font.Font('freesansbold.ttf', 40)
        text_font = pygame.font.Font('freesansbold.ttf', 20)

        # Title text
        text = large_text_font.render('ProCom Curriculum 2022', True, WorldState.GREEN, WorldState.BLUE)
        text_rect = text.get_rect()
        text_rect.center = (sr[0] // 2, sr[1] // 3)
        self._assets["title"] = (text, text_rect)

        # Instruction text
        text = text_font.render('Press spacebar to start', True, WorldState.GREEN, WorldState.WHITE)
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
    def __init__(self):
        super(Game, self).__init__()
        player_1 = player.sam.Player()
        self._sprite_group.add(player_1)

    def update(self, dt, frame_num, events):
        for sprite in self._sprite_group.sprites():
            sprite.move(dt, frame_num)
        pass

    def draw(self, screen):
        screen.fill(WorldState.BLUE)
        self._sprite_group.draw(screen)


class StateHandler(object):
    START_MENU="START_MENU"
    GAME="GAME"

    def __init__(self):
        self._states = {
            StateHandler.START_MENU: StartMenu(),
            StateHandler.GAME: Game()
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
