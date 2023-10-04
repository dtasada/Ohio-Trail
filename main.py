import pygame
import random
import sys


pygame.init()
WIN = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Ohio Trail")
clock = pygame.time.Clock()

running = __name__ == "__main__"

while running:
    clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    WIN.fill([random.randint(0, 255) for _ in range(3)])
    pygame.display.update()

pygame.quit()
sys.exit()
