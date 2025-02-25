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
    STONE_BAKED_GARLIC_FLATBREAD = _Food("Stone baked garlic flatbread", 4)
    SOUR_PATCH_KIDS = _Food("Sour Patch Kids", 2)
    MRBEAST_FEASTABLES = _Food("MrBeast Feastables", 5)
    PINK_SAUCE = _Food("Pink Sauce", 1)


class Location(Enum):
    CAMP = auto()
    CAMPFIRE = auto()
    CAMPSITE = auto()
    FOREST = auto()
    LAKE = auto()
    MOUNTAIN = auto()
    MY_TENT = auto()
    PLANEWRECK = auto()


class Completed(IntFlag):
    NONE = auto()
    EXPLORED_FOREST = auto()
    EXPLORED_PLANEWRECK = auto()
    EXPLORED_TENT = auto()
    FOUND_PEOPLE = auto()
    LOOTED_CORPSES = auto()
    SET_UP_CAMP = auto()
    MET_MERCHANT = auto()


class Bar:
    def __init__(self, max_, x, y):
        self.max_ = max_
        self.current = self.max_
        self.x = x
        self.y = y
        self.img =  pygame.transform.scale_by(pygame.image.load(Path("assets", "bar.png")), SCALING)
        self.tex = Texture.from_surface(game.renderer, self.img)
        self.rect = self.img.get_rect(topleft=(self.x, self.y))

    def update(self):
        ratio = self.current / self.max_
        color = pygame.Color(Color.RED)
        color = color.lerp(Color.GREEN, ratio)
        fill_rect(game.renderer, color, (self.x, self.y - 270 * ratio + 280, 40 , 270 * ratio))
        game.renderer.blit(self.tex, self.rect)


class Character:
    def __init__(self):
        self.name = None
        self.hp = 100
        self.energy = 100
        self.temp = 100
        self.money = 25
        self.show_money = False
        self.location = Location.PLANEWRECK
        self.completed: Completed = Completed.NONE
        self.food: Dict[Food, int] = {
            Food.FRIKANDELBROODJE: gauss(0.5, 0.5),
            Food.EGGPLANT: gauss(1.5, 1.5),
            Food.PICKLE: gauss(1, 1),
            Food.STONE_BAKED_GARLIC_FLATBREAD: gauss(0.5, 0.5),
        }
        self.healthbar = Bar(self.hp, 880, 300)
        self.energy_bar = Bar(self.energy, 940, 300)
        self.temp_bar = Bar(self.temp, 1000, 300)

    def update(self):
        if self.show_money:
            tex, rect = write(f"${self.money}", (40, 370), 30)
            game.renderer.blit(tex, rect)

        self.healthbar.current = self.hp
        self.healthbar.update()
        tex, rect = write("HP", (885, 600))
        game.renderer.blit(tex, rect)

        self.energy_bar.current = self.energy
        self.energy_bar.update()
        tex, rect = write("EN", (945, 600))
        game.renderer.blit(tex, rect)

        self.temp_bar.current = self.temp
        self.temp_bar.update()
        tex, rect = write("TM", (1005, 600))
        game.renderer.blit(tex, rect)

    def setup(self, name, background):
        self.name = name
        self.background = background

    def complete(self, action: Completed):
        self.completed |= action


player = Character()
