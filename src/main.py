<<<<<<< HEAD:main.py
import pygame
from pygame._sdl2.video import Window, Texture, Renderer, Image
import random
import sys
from pyengine.pgbasics import *
from pyengine.pgwidgets import *

=======
from settings import *
>>>>>>> f5e40b11781ff82e40d7e5fabc1e3ee10fd7c3ee:src/main.py

WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)

pygame.init()
WIN = Window(size=(800, 600), title="Ohio Trail")
REN = Renderer(WIN)
clock = pygame.time.Clock()
font = pygame.font.Font(path("assets", "Oregon-Bound", "oregon-bound.ttf"), 14)


class RetroEntry:
    def __init__(self, final):
        self.final = final
        self.text = ""
        self.index += 1

    def update(self):
        self.index += 0.01
        img = font.render(self.text[:int(self.index)], True, ())
        self.image = Texture.from_surface(font.render(el))


rentry = RetroEntry()


def main():
    running = __name__ == "__main__"
    while running:
        clock.tick(30)
        for event in pygame.event.get():
            process_widget_events(event, pygame.mouse.get_pos())
            if event.type == pygame.QUIT:
                running = False

        fill_rect(REN, (100, 100, 100, 255), (0, 0, 800, 600))
        draw_and_update_widgets()
        REN.present()

    pygame.quit()
    sys.exit()


main()
