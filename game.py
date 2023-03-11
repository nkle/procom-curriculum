import json

import pygame

from utils.common import *
from world.state import *


def run_game():
    # Load the configuration file
    config_path = get_path("config.json")
    with open(config_path, "r") as f:
        config = json.load(f)

    # Start PyGame and set name of app
    pygame.init()
    pygame.display.set_caption("ProCom Curriculum 2023")

    # Set FPS and game clock
    fps = 60.0
    fps_clock = pygame.time.Clock()

    # Set up the window
    resolution = (1200, 800)
    screen = pygame.display.set_mode(resolution)

    # Set icon
    icon = pygame.image.load(get_path(os.path.join('assets', 'procom22.icns')))
    pygame.display.set_icon(icon)

    # Initialize state handler that manages the fade in between menu and game screen
    state_handler = StateHandler(config=config)
    state_handler.fade_in()

    dt = 1 / fps
    frame_num = 0

    while True:
        frame_num += 1
        if frame_num > fps:
            frame_num = 1

        # Update state and draw on screen
        state_handler.update(dt, frame_num, pygame.event.get())
        state_handler.draw(screen)
        dt = fps_clock.tick(fps)


if __name__ == "__main__":
    run_game()

