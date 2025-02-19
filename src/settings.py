from pygame._sdl2.video import Texture
from threading import Thread
from typing import Tuple
from pathlib import Path
import pygame
import time
import random

from .game import game

# Globals
ZWS = "​"  # niet empty maar zero width space
SCALING = 10
FONTS = [
    pygame.font.Font(Path("assets", "fonts", "oregon-bound.ttf"), x)
    for x in range(0, 100)
]
FONT = FONTS[18]

with open(Path("assets", "text_data", "ohio.txt")) as f:
    ohio_cities = f.read().splitlines()


def test(*args):
    print(random.randint(0, 100), *args)


def pause1(func):
    def threaded():
        time.sleep(1)
        func()

    def inner():
        Thread(target=threaded, daemon=True).start()

    return inner


def pause4(func):
    def threaded():
        time.sleep(4)
        func()

    def inner():
        Thread(target=threaded, daemon=True).start()

    return inner


def fill_rect(renderer, color, rect):
    renderer.draw_color = color
    renderer.fill_rect(rect)


def draw_line(renderer, color, p1, p2):
    renderer.draw_color = color
    renderer.draw_line(p1, p2)


def write(text, pos, size=18):
    img = FONTS[size].render(text, True, Color.WHITE)
    tex = Texture.from_surface(game.renderer, img)
    rect = img.get_rect(topleft=pos)
    return tex, rect


def str_to_enum(string: str) -> str:
    return string.replace(" ", "_").upper()


def enum_to_str(string: str) -> str:
    return string.replace("_", " ").title()


class Animation:
    def __init__(
        self,
        path: str,
        pos: Tuple[int, int],
        frame_count: int = 1,
        framerate: float = 0,
        scaling: int = 5,
        should_stay: bool = False,
    ):
        self.scaling = scaling
        self.should_stay = should_stay
        self.path = Path("assets", f"{path}.png")
        self.pos = pos
        self.framerate = framerate
        self.index = 0
        self.frame_count = frame_count
        if self.frame_count > 1:
            self.img = pygame.transform.scale_by(
                pygame.image.load(self.path), self.scaling
            )
            self.frame_width = self.img.get_width() / self.frame_count
            self.frame_height = self.img.get_height()
            self.texs = [
                Texture.from_surface(
                    game.renderer,
                    self.img.subsurface(
                        x * self.frame_width, 0, self.frame_width, self.frame_height
                    ),
                )
                for x in range(self.frame_count)
            ]
            self.rects = [tex.get_rect(topleft=self.pos) for tex in self.texs]
        else:
            self.img = pygame.transform.scale_by(
                pygame.image.load(self.path), self.scaling
            )
            self.tex = Texture.from_surface(game.renderer, self.img)
            self.rect = self.tex.get_rect()
        self.kill = False

    def update(self):
        if self.frame_count > 1:
            self.index += (1 / 30) * self.framerate
            if int(self.index) >= len(self.texs):
                if self.should_stay is False:
                    self.kill = True
                else:
                    game.renderer.blit(self.texs[-1], self.rects[-1])
            else:
                game.renderer.blit(
                    self.texs[int(self.index)], self.rects[int(self.index)]
                )
        else:
            print("else")

    def process_event(self, _):
        pass


class Color:
    WHITE = (255, 255, 255, 255)
    BLACK = (0, 0, 0, 255)


class Sound:
    @staticmethod
    def load(path: Path, volume: float = 1) -> pygame.mixer.Sound:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        return sound

    PICKUP = load(Path("assets", "sfx", "pickup.wav"))
    BEEP = load(Path("assets", "sfx", "beep.wav"))
    TYPEWRITER = load(Path("assets", "sfx", "typewriter.wav"), 0.1)
