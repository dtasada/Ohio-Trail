from pygame._sdl2.video import Window, Renderer
from pathlib import Path
import pygame


class Game:
    """Simple game wrapper class"""

    def __init__(self) -> None:
        pygame.init()
        self.window = Window(size=(1100, 650), title="Ohio Trail")
        self.window.set_icon(pygame.image.load(Path("assets", "logo.png")))
        self.renderer = Renderer(self.window)
        self.clock = pygame.time.Clock()
        self.quicktime_active = False


game = Game()
