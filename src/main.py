import pygame
import sys

from .character import *
from .game import game
from .inventory import *
from .story_loop import *
from .widgets import *


def main(debug=False):
    running = True
    Music.set_music(Music.MAIN_MENU)
    active_widgets.append(
        TitleCard(
            f"{title_card_string}{' ' * 8}{random_ahh}",
            (96, 76),
            24,
            RetroEntry(
                "Hello traveler, what is your name?",
                accepts_input=True,
                command=ask_name,
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
                    if isinstance(widget, RetroSelection):
                        # selection
                        widget.process_event(
                            event, random_quicktime_event, game.quicktime_active
                        )
                    else:
                        widget.process_event(event)

                for sfx in sfx_queue:
                    sfx.process_event(event)
            
            # elif event.type == pygame.MOUSEBUTTONDOWN:
            #     for widget in active_widgets[:]:
            #         if isinstance(widget, Minigame):
            #             widget.process_event(event)

        fill_rect(game.renderer, (0, 0, 0, 255), (0, 0, *game.window.size))

        for widget in active_widgets[:]:
            widget.update()
            if getattr(widget, "kill", False):
                active_widgets.remove(widget)
        
        for sfx in sfx_queue:
            sfx.update()

        player.update()
        inventory.update()

        game.renderer.present()

    pygame.quit()
    sys.exit()
