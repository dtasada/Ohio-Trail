from .game import game
from .story_loop import *
from .widgets import *

import sys


def main():
    running = True
    Music.set_music(Music.MAIN_MENU)
    active_widgets.append(
        TitleCard(
            f"{title_card_string}{' ' * 8}{random_ahh}",
            (96, 76),
            24,
            RetroEntry("This is our presentation.", command=slide_2),
            sine=(15, 0.002),
        )
    )

    while running:
        game.clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                for widget in active_widgets[:]:
                    widget.process_event(event)

                for sfx in sfx_queue:
                    sfx.process_event(event)

        pygame.draw.rect(game.display, (0, 0, 0, 255), (0, 0, *game.display.size))

        for widget in active_widgets[:]:
            widget.update()
            if getattr(widget, "kill", False):
                active_widgets.remove(widget)

        for sfx in sfx_queue:
            sfx.update()

        game.update_shake()
        game.window.blit(game.display, game.shake)
        pygame.display.flip()

    pygame.quit()
    sys.exit()
