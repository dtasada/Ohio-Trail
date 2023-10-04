import pygame
from pygame._sdl2.video import Window, Texture, Renderer, Image
import random
import sys
import os

def fill_rect(renderer, color, rect):
    renderer.draw_color = color
    renderer.fill_rect(rect)
    
def draw_line(renderer, color, p1, p2):
    renderer.draw_color = color
    renderer.draw_line(p1, p2)
