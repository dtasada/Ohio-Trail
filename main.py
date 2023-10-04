import pygame
from pygame._sdl2.video import Window, Texture, Renderer, Image
import random
import sys
from pyengine.pgbasics import *


pygame.init()
WIN = Window(size=(800, 600), title="Ohio Trail")
REN = Renderer(WIN)
clock = pygame.time.Clock()


def main():
    running = __name__ == "__main__"
    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        fill_rect(REN, [random.randint(0, 255) for _ in range(3)] + [255], (0, 0, 800, 600))
        REN.present()

    pygame.quit()
    sys.exit()


main()
