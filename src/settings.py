import pygame
from pygame._sdl2.video import Window, Texture, Renderer, Image
import random
import sys
import os


pygame.init()
WIDTH, HEIGHT = 1200, 600
WIN = Window(size=(WIDTH, HEIGHT), title="Ohio Trail")
REN = Renderer(WIN)
clock = pygame.time.Clock()
ticks = pygame.time.get_ticks
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
fonts = [pygame.font.Font(os.path.join("assets", "oregon-bound", "oregon-bound.ttf"), x) for x in range(1, 100)]
font = pygame.font.Font(os.path.join("assets", "oregon-bound", "oregon-bound.ttf"), 18)


def fill_rect(renderer, color, rect):
    renderer.draw_color = color
    renderer.fill_rect(rect)


def draw_line(renderer, color, p1, p2):
    renderer.draw_color = color
    renderer.draw_line(p1, p2)


def writ(text, pos, size=18):
    img = fonts[size].render(text, True, WHITE)
    tex = Texture.from_surface(REN, img)
    rect = img.get_rect(topleft=pos)
    return tex, rect
