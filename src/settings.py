from pygame._sdl2.video import Texture
from threading import Thread
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


def chance(p):
    return random.random() < p


def action_to_color(text):
    return getattr(Color, text.split(" ")[0].upper(), Color.WHITE)


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


def write(text, pos, size=18, anchor="topleft"):
    img = FONTS[size].render(text, True, Color.WHITE)
    tex = Texture.from_surface(game.renderer, img)
    rect = img.get_rect()
    setattr(rect, anchor, pos)
    return tex, rect


def str_to_enum(string: str) -> str:
    return string.replace(" ", "_").upper()


def enum_to_str(string: str) -> str:
    return string.replace("_", " ").title().replace("Npcs", "NPCs")


def gauss(mean, std, min_=float("-inf"), max_=float("inf")) -> int:
    return int(max(min(random.gauss(mean, std), max_), min_))


class Color:
    WHITE = (255, 255, 255, 255)
    BLACK = (0, 0, 0, 255)
    RED = (255, 0, 0, 255)
    GREEN = (0, 255, 0, 255)
    WALK = (169, 211, 158)
    GO = WALK
    TALK = pygame.Color("deepskyblue")
    EXPLORE = (254, 190, 140)


class Sound:
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
    

class Music:
    @staticmethod
    def set_music(music, volume=1):
        pygame.mixer.music.fadeout(1000)
        pygame.mixer.music.unload()
        pygame.mixer.music.load(music)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)

    @staticmethod
    def stop():
        pygame.mixer.music.fadeout(1000)
        
    MAIN_MENU = Path("assets", "sfx", "Main-Menu.mp3")
    INTRO = Path("assets", "sfx", "Intro.mp3")
    CREDITS = Path("assets", "sfx", "Credits.mp3")


class Sfx:
    def __init__(self, time, sound):
        self.time = time
        self.sound = sound
        self.start_time = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.start_time > self.time:
            self.sound.play()
            sfx_queue.remove(self)
        
    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_COMMA:
                sfx_queue.remove(self)


sfx_queue = []