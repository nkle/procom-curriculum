import pygame
from elements.sam import Player
from elements.static import PlatformTile
from world.state import *
import sys
import json


def run_game(config):
    with open(config, "r") as f:
        config = json.load(f)

    pygame.init()
    pygame.display.set_caption("ProCom Curriculum")

    fps = 60.0
    fps_clock = pygame.time.Clock()

    # Set up the window.
    resolution = (1200, 900)
    screen = pygame.display.set_mode(resolution)

    state_handler = StateHandler(config=config)
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
    run_game(sys.argv[1])

