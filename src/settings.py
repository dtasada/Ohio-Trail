from contextlib import suppress
from math import floor, ceil, sin
from pygame._sdl2.video import Window, Texture, Renderer, Image
from threading import Thread
from typing import Tuple, Callable, Optional
import os
import pygame
import random
import sys
import time


pygame.init()
R = 10
WIDTH, HEIGHT = 1100, 650
WIN = Window(size=(WIDTH, HEIGHT), title="Ohio Trail")
WIN.set_icon(pygame.image.load(os.path.join("assets", "logo.png")))
REN = Renderer(WIN)
clock = pygame.time.Clock()
ticks = pygame.time.get_ticks
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
fonts = [pygame.font.Font(os.path.join("assets", "fonts", "oregon-bound.ttf"), x) for x in range(0, 100)]
font = pygame.font.Font(os.path.join("assets", "fonts", "oregon-bound.ttf"), 18)
beep_sound = pygame.mixer.Sound(os.path.join("assets", "sfx", "beep.wav"))
typewriter_sound = pygame.mixer.Sound(os.path.join("assets", "sfx", "typewriter.wav"))
typewriter_sound.set_volume(0.1)
pickup_sound = pygame.mixer.Sound(os.path.join("assets", "sfx", "pickup.wav"))
ZWS = "​"  # niet empty maar zero width space
day = 1


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
    img = fonts[size].render(text, True, WHITE)
    tex = Texture.from_surface(REN, img)
    rect = img.get_rect(topleft=pos)
    return tex, rect


class Animation:
    def __init__(self, path, pos, frame_count=1, framerate=0, R=5, should_stay=False):
        self.R = R
        self.should_stay = should_stay
        self.path = os.path.join("assets", f"{path}.png")
        self.pos = pos
        self.framerate = framerate
        self.index = 0
        self.frame_count = frame_count
        if self.frame_count > 1:
            self.img = pygame.transform.scale_by(pygame.image.load(self.path), self.R)
            self.frame_width = self.img.get_width() / self.frame_count
            self.frame_height = self.img.get_height()
            self.texs =[Texture.from_surface(REN, self.img.subsurface(x * self.frame_width, 0, self.frame_width, self.frame_height)) for x in range(self.frame_count)]
            self.rects = [tex.get_rect(topleft=self.pos) for tex in self.texs]
        else:
            self.img = pygame.transform.scale_by(pygame.image.load(self.path), self.R)
            self.tex = Texture.from_surface(REN, self.img)
            self.rect = self.tex.get_rect()
        self.kill = False

    def update(self):
        if self.frame_count > 1:
            self.index += (1 / 30) * self.framerate
            if int(self.index) >= len(self.texs):
                if self.should_stay is False:
                    self.kill = True
                else:
                    REN.blit(self.texs[-1], self.rects[-1])
            else:
                REN.blit(self.texs[int(self.index)], self.rects[int(self.index)])
        else:
            print('else')

    def process_event(self, _):
        pass
