from .settings import *
from .game import game
from .inventory import *

from enum import Enum, IntFlag, auto
from pygame._sdl2.video import Texture
from typing import List
from pathlib import Path

import pygame


class Background:
    """Simple background object for the character background type. Effectively a dataclass"""

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


possible_backgrounds = {
    i.desc: i
    for i in [
        Background(
            1,
            "banker",
            "Be a banker from New York",
            f"Impressive,{ZWS * 10} very nice.",
        ),
        Background(2, "chef", "Be a chef from France", "Anyone can cook!"),
        Background(
            3,
            "man",
            "Be a man from Florida",
            f"{ZWS * 5}W{'o' * 29}!{ZWS * 7}\n\nYeah{ZWS * 10} baby!",
        ),
    ]
}


class Location(Enum):
    """Location enum for the player's current location"""

    CAMP = auto()
    CAMPFIRE = auto()
    CAMPSITE = auto()
    FOREST = auto()
    LAKE = auto()
    MOUNTAIN = auto()
    MY_TENT = auto()
    PLANEWRECK = auto()


class Completed(IntFlag):
    """Enum for completed actions and achievements. Used for progression"""

    NONE = auto()
    ENTERED_FOREST = auto()
    EXPLORED_FOREST = auto()
    EXPLORED_PLANEWRECK = auto()
    EXPLORED_TENT = auto()
    FOUND_PEOPLE = auto()
    LOOTED_CORPSES = auto()
    SET_UP_CAMP = auto()
    MET_MERCHANT = auto()


class Bar:
    """Bar component used for health, energy, and temperature bars"""

    def __init__(self, max_: int, x: int, y: int):
        self.max_: int = max_
        self.current: int = self.max_
        self.x: int = x
        self.y: int = y
        self.img: pygame.Surface = pygame.transform.scale_by(
            pygame.image.load(Path("assets", "bar.png")), SCALING
        )
        self.tex = Texture.from_surface(game.renderer, self.img)
        self.rect = self.img.get_rect(topleft=(self.x, self.y))
        self.should_draw = False

    def enable(self):
        self.should_draw = True

    def disable(self):
        self.should_draw = False

    def update(self):
        if not self.should_draw:
            return

        ratio = self.current / self.max_
        # color = color.lerp(Color.GREEN, ratio)  # commented bc ratio was > 1?
        color = Color.RED
        color = color.lerp(Color.GREEN, 1.0)

        fill_rect(
            game.renderer,
            color,
            (
                self.x,
                self.y - self.rect.height * ratio + self.rect.height,
                self.rect.width,
                self.rect.height * ratio,
            ),
        )
        game.renderer.blit(self.tex, self.rect)


class Character:
    """Main character class for the player object"""

    def __init__(self):
        self.name: Optional[str] = None
        self.money: int = 3
        self.show_money: bool = False
        self.location: Location = Location.PLANEWRECK
        self.completed: Completed = Completed.NONE
        self.max_hp: int = 100
        self.max_energy: int = 10
        self.max_temp: int = 100

        self.hp: int = self.max_hp
        self.energy: int = self.max_energy
        self.temp: int = self.max_temp

        self.background: Optional[Background] = None
        self.healthbar: Bar = Bar(self.max_hp, 910, 380)
        self.energy_bar: Bar = Bar(self.max_energy, 950, 380)
        self.temp_bar: Bar = Bar(self.max_temp, 990, 380)

    def update_bars(self):
        """Ran every timestep to update the health, energy, and temperature bars"""
        if self.healthbar.should_draw:
            self.healthbar.current = self.hp
            self.healthbar.update()
            tex, rect = write("HP", (905, 590), 13)
            game.renderer.blit(tex, rect)

        if self.energy_bar.should_draw:
            self.energy_bar.current = self.energy
            self.energy_bar.update()
            tex, rect = write("EN", (944, 590), 13)
            game.renderer.blit(tex, rect)

        if self.temp_bar.should_draw:
            self.temp_bar.current = self.temp
            self.temp_bar.update()
            tex, rect = write("TM", (982, 590), 13)
            game.renderer.blit(tex, rect)

    def update(self):
        """Main update function for the player object"""
        if self.show_money:
            tex, rect = write(f"${self.money}", (40, 370), 30)
            game.renderer.blit(tex, rect)

        self.update_bars()

    def complete(self, action: Completed):
        """Simple method to mark an action as completed"""
        self.completed |= action


player = Character()
