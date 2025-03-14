from pathlib import Path
import pygame
from pygame.time import get_ticks as ticks
import random
from typing import Tuple


class Game:
    """Simple game wrapper class"""

    def __init__(self) -> None:
        pygame.init()
        # self.renderer = Renderer(self.window)
        pygame.display.set_caption("Ohio Trail")
        # window initialization
        self.width, self.height = 1100, 650
        self.window = pygame.display.set_mode((self.width, self.height))
        self.display = pygame.display.get_surface()
        self.center = (self.width / 2, self.height / 2)
        # screenshake variables
        self.shake = [0, 0]
        self.shake_offset = 0
        self.last_shake = ticks()
        self.shaking = False
        self.shake_duration = 0
        pygame.display.set_icon(pygame.image.load(Path("assets", "logo.png")))

        self.clock = pygame.time.Clock()
        self.quicktime_active = False

    def update_shake(self):
        """Offsets the offset of the window display"""
        if self.shaking:
            self.shake = [random.randint(-p, p) for p in self.shake_offset]
            if ticks() - self.last_shake >= self.shake_duration:
                self.shake = [0, 0]
                self.shaking = False

    def start_shake(self, offset: Tuple[int, int], duration: int):
        """Initiates screen shake variables"""
        self.shake_offset = offset
        self.shake_duration = duration
        self.last_shake = ticks()
        self.shaking = True


game = Game()
