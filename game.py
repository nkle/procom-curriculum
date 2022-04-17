import sys
import pygame
from pygame.locals import *
from player.sam import Player
from world.platform import Platform
from world.state import *


def run_game():
    pygame.init()
    pygame.display.set_caption("ProCom Curriculum")

    fps = 60.0
    fps_clock = pygame.time.Clock()

    # Set up the window.
    resolution = (800, 600)
    screen = pygame.display.set_mode(resolution)

    # Load starting sprites
    sprites = {
        "player": pygame.sprite.Group(),
        "platform": pygame.sprite.Group()
    }

    P1 = Player()
    PT1 = Platform()

    sprites["player"].add(P1)
    sprites["platform"].add(PT1)

    state_handler = StateHandler()
    state_handler.fade_in()

    dt = 1 / fps
    frame_num = 0
    while True:
        frame_num += 1
        if frame_num > fps:
            frame_num = 1

        state_handler.update(dt, frame_num, pygame.event.get())
        state_handler.draw(screen)
        dt = fps_clock.tick(fps)


if __name__ == "__main__":
    run_game()

