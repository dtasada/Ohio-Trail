from pygame.transform import rotate
from threading import Thread
from pathlib import Path
import pygame
import time
import random
from pygame.time import get_ticks as ticks

from pygame.typing import Point

from .game import game


# Globals
ZWS = "​"  # niet empty maar zero width space
SCALING = 10
FONTS = [
    pygame.font.Font(Path("assets", "fonts", "oregon-bound.ttf"), x)
    for x in range(0, 100)
]
FONT = FONTS[18]

shop_list = []

with open(Path("assets", "text_data", "ohio.txt")) as f:
    ohio_cities = f.read().splitlines()


def imgload(
    *path_,
    after_func=None,
    colorkey=None,
    frames=None,
    whitespace=0,
    frame_pause=0,
    end_frame=None,
    scale=1,
    rotation=0,
    tex=False
):
    """Handy function that loads and returns a texture / a list of textures (spritesheet)"""
    if frames is None:
        ret = pygame.image.load(Path(*path_))
    else:
        ret = []
        img = pygame.image.load(Path(*path_))
        frames = (frames, img.get_width() / frames)
        for i in range(frames[0]):
            ret.append(
                img.subsurface(
                    i * frames[1], 0, frames[1] - whitespace, img.get_height()
                )
            )
        for i in range(frame_pause):
            ret.append(ret[0])
        if end_frame is not None:
            ret.append(ret[end_frame])
    if isinstance(ret, list):
        for i, r in enumerate(ret):
            ret[i] = rotate(
                pygame.transform.scale_by(
                    getattr(r, after_func)() if after_func is not None else r, scale
                ),
                rotation,
            )
    elif isinstance(ret, pygame.Surface):
        ret = rotate(
            pygame.transform.scale_by(
                getattr(ret, after_func)() if after_func is not None else ret, scale
            ),
            rotation,
        )
    return ret


def chance(p: float) -> bool:
    """Returns True with a probability of p"""
    return random.random() < p


def action_to_color(action: str) -> pygame.Color:
    """Returns the rendering color of action"""
    return getattr(Color, action.split(" ")[0].upper(), Color.WHITE)


def pause1(func):
    """
    Decorator used in procedures that require a 1 second pause after completion
    before continuing to its associated command
    """

    def threaded(*args, **kwargs):
        time.sleep(1)
        func(*args, **kwargs)

    def inner(*args, **kwargs):
        Thread(target=threaded, args=args, kwargs=kwargs, daemon=True).start()

    return inner


def pause4(func):
    """
    Decorator used in procedures that require a 4 second pause after completion
    before continuing to its associated command
    """

    def threaded():
        time.sleep(4)
        func()

    def inner():
        Thread(target=threaded, daemon=True).start()

    return inner


def write(text: str, pos: Point, size: int = 18, anchor: str = "topleft", color=None):
    """Rendering function to draw text"""
    img = FONTS[size].render(text, True, Color.WHITE if color is None else color)
    rect = img.get_rect()
    setattr(rect, anchor, pos)
    return img, rect


def str_to_enum(string: str) -> str:
    """Helper function that converts a string to an idiomatic enum member name"""
    return string.replace(" ", "_").upper()


def enum_to_str(string: str) -> str:
    """Helper function that converts an idiomatic enum member name to a string"""
    return string.replace("_", " ").title().replace("Npcs", "NPCs")


def gauss(mean, std, min_=float("-inf"), max_=float("inf")) -> int:
    """Helper function that returns a random integer from a gaussian distribution"""
    return int(max(min(random.gauss(mean, std), max_), min_))


class Color:
    """Color class that contains all the colors used in the game. All colors are static"""

    # Primitive colors
    WHITE = pygame.Color(255, 255, 255, 255)
    BLACK = pygame.Color(0, 0, 0, 255)
    RED = pygame.Color(255, 0, 0, 255)
    GREEN = pygame.Color(0, 255, 0, 255)
    BROWN = pygame.Color(222, 184, 135)

    # Color values
    WALK = pygame.Color(169, 211, 158)
    GO = WALK
    TALK = pygame.Color("deepskyblue")
    EXPLORE = pygame.Color(254, 190, 140)


class Sound:
    """Simple sound wrapper class. Contains enum-like static members."""

    @staticmethod
    def load(path: Path, volume: float = 1) -> pygame.mixer.Sound:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        return sound

    PICKUP = load(Path("assets", "sfx", "pickup.wav"))
    BEEP = load(Path("assets", "sfx", "beep.wav"), 0.4)
    TYPEWRITER = load(Path("assets", "sfx", "typewriter.wav"), 0.1)
    BUY = load(Path("assets", "sfx", "buy.wav"))
    ALERT = load(Path("assets", "sfx", "alert.mp3"))
    EXPLOSION = load(Path("assets", "sfx", "explosion.mp3"), 0.3)
    BUILD_UP = load(Path("assets", "sfx", "scary.mp3"))
    CHOP = load(Path("assets", "sfx", "chop.wav"))


class Music:
    """Simple sound wrapper class. Contains enum-like static members."""

    current = None

    @classmethod
    def set_music(cls, music, volume=1):
        cls.current = music
        pygame.mixer.music.fadeout(1000)
        pygame.mixer.music.unload()
        pygame.mixer.music.load(music)
        pygame.mixer.music.set_volume(0)
        pygame.mixer.music.play(-1)

    @staticmethod
    def stop(time):
        pygame.mixer.music.fadeout(time)

    MAIN_MENU = Path("assets", "sfx", "Main-Menu.mp3")
    INTRO = Path("assets", "sfx", "Intro.mp3")
    FOREST = Path("assets", "sfx", "Forest.mp3")
    HAPPY_FOREST = Path("assets", "sfx", "Happy-Forest.mp3")
    PLANEWRECK = Path("assets", "sfx", "planewreck.mp3")
    CAMP = Path("assets", "sfx", "camp.mp3")
    CREDITS = Path("assets", "sfx", "Credits.mp3")


class Sfx:
    """Sound effect class"""

    def __init__(self, sound, time=0):
        self.time = time
        self.sound = sound
        self.start_time = ticks()

    def update(self):
        """Update sound effect"""
        if ticks() - self.start_time > self.time:
            self.sound.play()
            sfx_queue.remove(self)

    def process_event(self, event):
        """Stop sound effect if procedure is skipped"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_COMMA:
                sfx_queue.remove(self)


sfx_queue = []


class Visuals:
    """Visual elements that don't fit into any other image category such as a fishing bobber"""

    BOBBER = imgload(Path("assets", "items", "bobber.png"), scale=2)
    RADAR = imgload(Path("assets", "items", "radar.png"), scale=2, frames=9)
