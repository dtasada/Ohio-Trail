from .settings import *
from .game import game

from enum import Enum, IntFlag, auto
from pygame._sdl2.video import Texture
from typing import List, Dict
from pathlib import Path

import pygame


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
        self.img = pygame.transform.scale_by(
            pygame.image.load(Path("assets", "bar.png")), SCALING
        )
        self.tex = Texture.from_surface(game.renderer, self.img)
        self.rect = self.img.get_rect(topleft=(self.x, self.y))

    def update(self):
        ratio = self.current / self.max_
        color = pygame.Color(Color.RED)
        color = color.lerp(Color.GREEN, ratio)
        fill_rect(
            game.renderer, 
            color, 
            (self.x, 
             self.y - self.rect.height * ratio + self.rect.height, 
             self.rect.width, 
             self.rect.height * ratio)
        )
        game.renderer.blit(self.tex, self.rect)


class Character:
    def __init__(self):
        self.name = None
        self.money = 3
        self.show_money = False
        self.location = Location.PLANEWRECK
        self.completed: Completed = Completed.NONE
        self.max_hp = 100
        self.max_energy = 10
        self.max_temp = 100

        self.hp = self.max_hp
        self.energy = self.max_energy
        self.temp = self.max_temp

        self.healthbar = Bar(self.max_hp, 910, 380)
        self.energy_bar = Bar(self.max_energy, 950, 380)
        self.temp_bar = Bar(self.max_temp, 990, 380)

    def update_bars(self):
        self.healthbar.current = self.hp
        self.healthbar.update()
        tex, rect = write("HP", (905, 590), 13)
        game.renderer.blit(tex, rect)

        self.energy_bar.current = self.energy
        self.energy_bar.update()
        tex, rect = write("EN", (944, 590), 13)
        game.renderer.blit(tex, rect)

        self.temp_bar.current = self.temp
        self.temp_bar.update()
        tex, rect = write("TM", (982, 590), 13)
        game.renderer.blit(tex, rect)

    def update(self):
        if self.show_money:
            tex, rect = write(f"${self.money}", (40, 370), 30)
            game.renderer.blit(tex, rect)

        self.update_bars()

    def setup(self, name, background):
        self.name = name
        self.background = background

    def complete(self, action: Completed):
        self.completed |= action


player = Character()
