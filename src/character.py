from .settings import *
from .game import game

from enum import Enum, IntFlag, auto
from pygame._sdl2.video import Texture
from typing import List, Dict
from pathlib import Path

import pygame
import random


class Background:
    def __init__(self, index, name, desc, catchphrase) -> None:
        self.name: str = name
        self.desc: str = desc
        self.catchphrase: str = catchphrase
        self.img: pygame.Surface = pygame.transform.scale_by(
            pygame.image.load(Path("assets", "characters", f"{self.name}.png")),
            SCALING,
        )
        self.tex = Texture.from_surface(game.renderer, self.img)
        self.rect = self.img.get_rect(
            center=(game.window.size[0] - 220, game.window.size[1] / 2)
        )
        self.desc = f"{index}. {self.desc}"
        self.sound = pygame.mixer.Sound(Path("assets", "sfx", f"{self.name}.wav"))


class _Food:
    def __init__(self, name, price) -> None:
        self.name = name
        self.price = price
        self.img = pygame.transform.scale_by(
            pygame.image.load(
                Path("assets", "food", f"{name.lower().replace(' ', '-')}.png")
            ),
            SCALING,
        )
        self.tex = Texture.from_surface(game.renderer, self.img)
        self.rect = self.img.get_rect(
            center=(game.window.size[0] - 300, game.window.size[1] / 2)
        )


possible_backgrounds: List[Background] = [
    Background(
        1, "banker", "Be a banker from New York", f"Impressive,{ZWS * 10} very nice."
    ),
    Background(2, "chef", "Be a chef from France", "Anyone can cook!"),
    Background(
        3,
        "man",
        "Be a man from Florida",
        f"{ZWS * 5}W{'o' * 29}!{ZWS * 7}\n\nYeah{ZWS * 10} baby!",
    ),
]


class Food(Enum):
    EGGPLANT = _Food("Eggplant", 1)
    FRIKANDELBROODJE = _Food("Frikandelbroodje", 1)
    PICKLE = _Food("Pickle", 1)
    STONE_BAKED_GARLIC_FLAT_BREAD = _Food("Stone baked garlic flat bread", 4)
    SOUR_PATCH_KIDS = _Food("Sour Patch Kids", 2)
    MRBEAST_FEASTABLES = _Food("MrBeast Feastables", 5)
    PINK_SAUCE = _Food("Pink-Sauce", 1)


class Locations(Enum):
    PLANEWRECK = auto()
    CAMPSITE = auto()
    CAMPFIRE = auto()
    TENT = auto()
    FOREST = auto()


class Completed(IntFlag):
    EXPLORED_PLANEWRECK = auto()
    EXPLORED_TENT = auto()
    LOOTED_CORPSES = auto()
    FOUND_PEOPLE = auto()
    SET_UP_CAMP = auto()


class Character:
    def __init__(self):
        self.name = None
        self.hp = 5
        self.money = 25
        self.show_money = False
        self.location = "planewreck"
        self.completed: List[Completed] = []
        self.food: Dict[Food, int] = {
            Food.EGGPLANT: int(random.gauss(1.5, 1.5)),
            Food.FRIKANDELBROODJE: int(random.gauss(0.5, 0.5)),
            Food.PICKLE: int(random.gauss(1, 1)),
            Food.STONE_BAKED_GARLIC_FLAT_BREAD: int(random.gauss(0.5, 0.5)),
        }

    def update(self):
        if self.show_money:
            tex, rect = write(f"${self.money}", (40, 370), 30)
            game.renderer.blit(tex, rect)

    def setup(self, name, background):
        self.name = name
        self.background = background


player = Character()
