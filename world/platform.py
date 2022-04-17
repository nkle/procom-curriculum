import pygame.sprite


class Platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((600, 20))
        self.surf.fill((255,0,0))
        self.rect = self.surf.get_rect(center = (800/2, 600 - 10))