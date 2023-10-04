import pygame
from pygame._sdl2.video import Window, Texture, Renderer, Image
import random
import sys
import os

WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)

def fill_rect(renderer, color, rect):
    renderer.draw_color = color
    renderer.fill_rect(rect)
    
def draw_line(renderer, color, p1, p2):
    renderer.draw_color = color
    renderer.draw_line(p1, p2)

def writ(text, pos):
    img = font.render(text, True, WHITE)
    tex = Texture.from_surface(REN, img)
    rect = img.get_rect(topleft=pos)
    return tex, rect


def ask_background(name):
    bg_entry = RetroEntry(f"And {name}, what may your background be?", (0, 60), ask_bg_selection, accepts_input=False)
    all_entries.append(bg_entry)


def ask_bg_selection(*args):
    bg_list = [data[0] for data in possible_backgrounds.values()]
    bg_select = RetroSelection(bg_list, (0, 80), set_character_bg)
    all_entries.append(bg_select)


def set_character_bg(bg):
    bg_name = [k for k, v in possible_backgrounds.items() if v[0] == bg][0]
    player.background = bg_name
    print(bg_name)
