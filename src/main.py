import pygame
import sys

from .game import game
from .character import *
from .story_loop import *
from .widgets import *


def main(debug=False):
    running = True
    active_widgets.append(
        TitleCard(
            f"{title_card_string}{' ' * 8}{random_ahh}",
            (96, 76),
            24,
            RetroEntry(
                "Hello traveler, what is your name?",
                accepts_input=True,
                command=ask_background,
            ),
            sine=(15, 0.002),
        )
    )

    while running:
        game.clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                inventory.process_event(event)
                for widget in active_widgets[:]:
                    try:
                        widget.process_event(event, random_quicktime_event)
                    except TypeError:
                        widget.process_event(event)

        fill_rect(game.renderer, (0, 0, 0, 255), (0, 0, *game.window.size))

        for widget in active_widgets[:]:
            widget.update()
            if getattr(widget, "kill", False):
                active_widgets.remove(widget)

        if player.show_money:
            i = 0
            for food in player.food:
                if player.food[food] != 0:
                    img, rect = write(
                        f"{food}: {player.food[food]}", (38, 460 + i * 28)
                    )
                    game.renderer.blit(img, rect)
                    i += 1
        
        player.update()
        inventory.update()

        game.renderer.present()

    pygame.quit()
    sys.exit()
