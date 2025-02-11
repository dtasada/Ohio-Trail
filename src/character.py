from enum import Enum, IntFlag, auto
from typing import List, Dict
import random
from .settings import *

has_camp = False


class Background:
    def __init__(self, index, name, desc, catchphrase) -> None:
        self.name: str = name
        self.desc: str = desc
        self.catchphrase: str = catchphrase
        self.img = pygame.transform.scale_by(
            pygame.image.load(os.path.join("assets", "characters", f"{self.name}.png")),
            scaling,
        )
        self.tex = Texture.from_surface(renderer, self.img)
        self.rect = self.img.get_rect(center=(window.size[0] - 220, window.size[1] / 2))
        self.desc = f"{index}. {self.desc}"
        self.sound = pygame.mixer.Sound(
            os.path.join("assets", "sfx", f"{self.name}.wav")
        )


class _Food:
    def __init__(self, name, price) -> None:
        self.name = name
        self.price = price
        self.img = pygame.transform.scale_by(
            pygame.image.load(
                os.path.join("assets", "food", f"{name.lower().replace(' ', '-')}.png")
            ),
            scaling,
        )
        self.tex = Texture.from_surface(renderer, self.img)
        self.rect = self.img.get_rect(center=(window.size[0] - 300, window.size[1] / 2))


possible_backgrounds: List[Background] = [
    Background(
        1, "banker", "Be a banker from New York", f"Impressive,{ZWS * 10} very nice."
    ),
    Background(2, "chef", "Be a chef from France", "Anyone can cook!"),
    Background(
        3,
        "man",
        "Be a man from Florida",
        f"{ZWS * 5}W{'o' * 29}!{ZWS * 7}\nYeah{ZWS * 10} baby!",
    ),
]

possible_daily_choice = {
    "camp": "Set up camp",
    "firewood": "Collect firewood",
    "food": "Search for food",
    "water": "Go get water",
    "skip": "Skip day",
}


class Food(Enum):
    EGGPLANT = _Food("Eggplant", 1)
    FRIKANDELBROODJE = _Food("Frikandelbroodje", 1)
    PICKLE = _Food("Pickle", 1)
    STONE_BAKED_GARLIC_FLAT_BREAD = _Food("Stone baked garlic flat bread", 4)
    SOUR_PATCH_KIDS = _Food("Sour Patch Kids", 2)
    MRBEAST_FEASTABLES = _Food("MrBeast Feastables", 5)
    PINK_SAUCE = _Food("Pink-Sauce", 1)
    # "Pineapple Pizza": { "price": 2 },
    # "Beef Jerky": { "price": 2 }
    # "CocoNutz": { "price": 1 },


clothing = {
    "Kilt": 10,
    "Skinny jeans": 10,
    "Among Us hoodie": 69,
    "Minecraft t-shirt": 20,
    "$19 Fortnite card": 20,
}


class Locations(Enum):
    PLANEWRECK = auto()
    CAMPSITE = auto()
    CAMPFIRE = auto()
    TENT = auto()
    FOREST = auto()


class Character:
    class Completed(IntFlag):
        EXPLORED_PLANEWRECK = auto()
        EXPLORED_TENT = auto()
        LOOTED_CORPSES = auto()
        FOUND_PEOPLE = auto()
        SET_UP_CAMP = auto()

    def __init__(self):
        self.name = None
        self.hp = 5
        self.money = 25
        self.show_money = False
        self.location = "planewreck"
        self.completed: List[Character.Completed] = []
        self.food: Dict[Food, int] = {
            Food.EGGPLANT: int(random.gauss(1.5, 1.5)),
            Food.FRIKANDELBROODJE: int(random.gauss(0.5, 0.5)),
            Food.PICKLE: int(random.gauss(1, 1)),
            Food.STONE_BAKED_GARLIC_FLAT_BREAD: int(random.gauss(0.5, 0.5)),
        }

    def update(self):
        if self.show_money:
            tex, rect = write(f"${self.money}", (40, 370), 30)
            renderer.blit(tex, rect)

    def setup(self, name, background):
        self.name = name
        self.background = background
