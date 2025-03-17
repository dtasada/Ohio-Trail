from .settings import *
from contextlib import suppress
from math import ceil, sin
from operator import setitem
from pygame.time import get_ticks as ticks
from pygame.typing import Point
from typing import Callable, Optional, Tuple, List

import pygame.gfxdraw


class _Retro:
    autokill: bool
    command: Optional[Callable]

    def finish(self, *args, **kwargs):
        """Called when the widget is finished. By default, it will call the associated command."""
        if self.command:
            self.command(*args, **kwargs)
        self.active = False
        if self.autokill:
            active_widgets.remove(self)

    def update(self): ...
    def process_event(self, event: pygame.Event): ...


class RetroSelection(_Retro):
    def __init__(
        self,
        actions,
        pos: Point,
        command: Optional[Callable] = None,
        images: List[pygame.Surface] = [],
        image_rects: List[pygame.Rect] = [],
        autokill: bool = False,
    ):
        """Initialize the selection widget. 'actions' is a List of 'Action', a RetroSelection, or a List of strings."""
        self.texts = list(actions)
        self.x, self.y = pos
        self.xo: int = 40
        self.yo: int = 40
        self.portrait_images: List[pygame.Surface] = images
        self.image_rects: List[pygame.Rect] = image_rects
        self.command: Optional[Callable] = command

        # selection images, textures and rectangles

        self.images: List[pygame.Surface] = [
            FONT.render(
                enum_to_str(text.name) if self.command is None else text,
                True,
                Color.WHITE,
            )
            for text in actions
        ]
        # text color coded (walk, talk to, etc.)
        self.colored_images: List[pygame.Surface] = [
            FONT.render(
                enum_to_str(text.name if self.command is None else text).split(" ")[0],
                True,
                action_to_color(
                    enum_to_str(text.name if self.command is None else text).split(" ")[
                        0
                    ]
                ),
            )
            for text in actions
        ]

        # rectangle hitboxes
        self.rects: List[pygame.Rect] = [
            img.get_rect(topleft=(self.x + self.xo, 50 + self.y + y * self.yo))
            for y, img in enumerate(self.images)
        ]
        self.colored_rects: List[pygame.Rect] = [
            img.get_rect(topleft=(self.x + self.xo, 50 + self.y + y * self.yo))
            for y, img in enumerate(self.colored_images)
        ]
        # other state variables
        self.gt, self.gt_rect = write(">", (self.rects[0].x - 30, self.rects[0].y))
        self.active: bool = True
        self.index: int = 0
        self.autokill: bool = autokill

    def finish(self, text: "Action", quicktime: Callable, quicktime_active: bool):
        """Called when the selection is finished. By default, it will call the associated command."""
        if self.command is not None:
            self.command(text)
        else:
            text.value()
        self.active = False
        if self.autokill:
            active_widgets.remove(self)

    def draw(self):
        """Draw the selection widget"""
        for tex, rect, ctex, crect in zip(
            self.images, self.rects, self.colored_images, self.colored_rects
        ):
            # render all text
            game.display.blit(tex, rect)
            game.display.blit(ctex, crect)
        if self.portrait_images:
            # check if there is a big portrait image and render it
            with suppress(IndexError):
                if self.portrait_images[self.index] is not None:
                    game.display.blit(
                        self.portrait_images[self.index], self.image_rects[self.index]
                    )
        game.display.blit(self.gt, self.gt_rect)

    def process_event(
        self, event: pygame.Event, quicktime: Callable, quicktime_active: bool,
    ):
        if self.active:
            if event.key == pygame.K_COMMA:
                # skip cutscene
                self.finish(self.texts[0], quicktime, quicktime_active)

            # keys W and S move the arrow on the selection
            if event.key in (pygame.K_s, pygame.K_DOWN):
                if self.gt_rect.y == self.rects[-1].y:
                    self.gt_rect.y = self.rects[0].y
                    self.index = 0
                else:
                    self.gt_rect.y += self.yo
                    self.index += 1
                Sound.BEEP.play()
            elif event.key in (pygame.K_w, pygame.K_UP):
                if self.gt_rect.y == self.rects[0].y:
                    self.gt_rect.y = self.rects[-1].y
                    self.index = -1
                else:
                    self.gt_rect.y -= self.yo
                    self.index -= 1
                Sound.BEEP.play()
            elif event.key == pygame.K_RETURN:
                text = list(self.texts)[self.index]
                self.finish(text, quicktime, quicktime_active)

    def update(self):
        self.draw()


class RetroEntry(_Retro):
    """Represents a text entry widget. It prints out text and accepts input from the user."""

    def __init__(
        self,
        final: str,
        pos: Point = (0, 0),
        choice_pos: Point = (0, 30),
        command: Optional[Callable] = None,
        selection: Optional[RetroSelection | List["Action"]] = None,
        accepts_input: bool = False,
        wrap: int | str = game.width - 50,
        speed: float = 0.6,
        typewriter: bool = True,
        reverse_data: Tuple[Optional[int], Optional[str]] = (None, None),
        next_should_be_immediate: bool = False,
        delay: int = 0,
        autokill: bool = False,
    ):
        self.final: str = final + " "
        self.text: str = ""
        self.answer: str = ""
        self.index: float = 0
        self.last_index: float = self.index
        self.x, self.y = [i + 12 for i in pos]
        self.speed: float = speed
        self.flickering: bool = False
        self.has_underscore: bool = False

        self.reversing: bool = False
        self.reverse_length, self.reverse_string = reverse_data
        self.should_reverse = self.reverse_length is not None
        self.finished_reversing: bool = False

        self.last_flicker: int = ticks()
        self.last_finished_writing: int = ticks()
        self.deleted: int = 0
        self.command: Optional[Callable] = command

        self.selection: RetroSelection = (
            RetroSelection(selection, pos=choice_pos) if selection else None
        )

        self.active: bool = True
        self.accepts_input: bool = accepts_input
        self.wrap: int | str = wrap
        self.typewriter: bool = typewriter
        self.kwargs = {
            "typewriter": typewriter,
            "speed": speed,
            "accepts_input": accepts_input,
        }
        self.next_should_be_immediate: bool = next_should_be_immediate
        self.autokill: bool = autokill
        self.last_quit: Optional[int] = None
        self.delay: int = delay

    def finish(self, *args, **kwargs):
        """Called when the entry is finished scrolling or got an input. By default, it will call the associated command."""
        if self.command is not None:
            self.command(*args, **kwargs)
        elif self.selection is not None:
            active_widgets.append(self.selection)

        self.active = False
        if self.autokill:
            active_widgets.remove(self)

    def draw(self):
        if int(self.index) >= 1:
            game.display.blit(self.image, self.rect)

    def process_event(self, event: pygame.Event):
        if self.active:
            if event.key == pygame.K_SPACE:
                if self.index == len(self.final) - 1:
                    self.finish()
                else:
                    self.index = len(self.final) - 1


            if self.accepts_input:
                if self.flickering:
                    # flickering is the cursor at the end of the text
                    mods = pygame.key.get_mods()
                    name = pygame.key.name(event.key)
                    self.text = self.text.removesuffix("_")
                    if name == "return":
                        if self.answer:
                            self.finish(self.answer)
                    elif name == "backspace":
                        if self.text != self.final:
                            self.text = self.text[:-1]
                            self.answer = self.answer[:-1]
                    elif name == "space":
                        self.text += " "
                        self.answer += " "
                    elif len(name) > 1:
                        # do nothing
                        ...
                    else:
                        if len(self.answer) < 20:
                            if mods in (1, 2):
                                name = name.capitalize()
                            self.text += name
                            self.answer += name
                    self.update_tex(self.text)

    def update(self):
        if self.active:
            # update the text if not reversing (for effect)
            if not self.reversing:
                # check if not flickering
                if not self.flickering:
                    # scroll the text (nothing special happening, so go)
                    self.index += self.speed
                    if int(self.index) >= 1:
                        self.update_tex(self.final[: int(self.index)])
                    # typing sound
                    if (
                        int(self.index) > self.last_index
                        and (self.text[-1] not in (" ", ZWS))
                        and self.typewriter
                    ):
                        Sound.TYPEWRITER.play()
                        self.last_index = self.index
                    # if finished, start flickering the underscore (_)
                    if self.index >= len(self.final):
                        self.flickering = True
                        self.last_flicker = ticks()
                        self.last_finished_writing = ticks()

                        if self.should_reverse and self.finished_reversing:
                            self.finish(self.answer)
                # else:
                #     # check if delay has to happen, if so, if finished, then finish()
                #     if not self.accepts_input:
                #         cond = True
                #         if self.delay > 0:
                #             if self.last_quit is None:
                #                 self.last_quit = ticks()
                #             cond = ticks() - self.last_quit >= self.delay
                #         if cond:
                #             self.finish()
            else:
                self.index -= self.speed
                if ceil(self.index) < self.last_index:
                    self.update_tex(self.text[:-1])
                    self.last_index = self.index
                    self.deleted += 1
                    if self.deleted >= self.reverse_length:
                        if self.reverse_string is None:
                            self.finish()
                        else:
                            self.reversing = False
                            self.finished_reversing = True
                            self.final = self.text + self.reverse_string
            if self.accepts_input:
                # execute when flickering
                if self.flickering:
                    if ticks() - self.last_flicker >= 500:
                        if self.has_underscore:
                            self.update_tex(self.text.removesuffix("_"))
                        else:
                            self.update_tex(self.text + "_")
                        self.has_underscore = not self.has_underscore
                        self.last_flicker = ticks()

        if not self.reversing:
            if self.index >= len(self.final):
                if self.reverse_length is not None:
                    if ticks() - self.last_finished_writing >= 1_000:
                        self.last_index = self.index
                        self.reversing = True
                        self.flickering = False
        # draw the player
        self.draw()

    def update_tex(self, text):
        self.text = text
        try:
            img = FONT.render(text, True, Color.WHITE)
        except pygame.error:
            img = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.image = img
        self.rect = img.get_rect(topleft=(self.x, self.y))


random_ahh: str = (
    " ".join(random.sample(["press", "space", "to", "continue"], 4))
    .capitalize()
    .replace("space", "SPACE")
    .replace("Space", "SPACE")
)

title_card_string = r'''
   ___   _        _
  / _ \ | |_     (_)    ___     o O O
 | (_) || ' \    | |   / _ \   o
  \___/ |_||_|  _|_|_  \___/  TS__[O]
_|"""""_|"""""_|"""""_|"""""|{======_
"`-0-0-"`-0-0-"`-0-0-"`-0-0-./o--000"
   _____                  _      _
  |_   _|   _ _  __ _    (_)    | |
    | |    | '_|/ _` |   | |    | |
   _|_|_  _|_|_ \__,_|  _|_|_  _|_|_
  |"""""_|"""""_|"""""_|"""""_|"""""|
  `-0-0-"`-0-0-"`-0-0-"`-0-0-"`-0-0-


'''


class TitleCard(_Retro):
    def __init__(self, text, pos, size, next: RetroEntry, sine=(None, None)):
        self.autokill = True
        self.command = lambda: setitem(active_widgets, 0, next)
        self.tex, self.rect = write(text, pos, size)
        self.amp, self.freq = sine
        self.og_y = self.rect.y

    def process_event(self, event: pygame.Event):
        if event.key == pygame.K_SPACE:
            if self.command:
                self.command()

    def update(self):
        self.rect.y = self.og_y + self.amp * sin(ticks() * self.freq)
        game.display.blit(self.tex, self.rect)


class Animation:
    def __init__(
        self,
        path: str,
        pos: Point,
        frame_count: int = 1,
        framerate: float = 0,
        scaling: int = 5,
        should_stay: bool = False,
    ):
        self.scaling = scaling
        self.should_stay = should_stay
        self.path = Path("assets", f"{path}.png")
        self.pos = pos
        self.framerate = framerate
        self.index = 0
        self.frame_count = frame_count
        if self.frame_count > 1:
            self.img = pygame.transform.scale_by(
                pygame.image.load(self.path), self.scaling
            )
            self.frame_width = self.img.get_width() / self.frame_count
            self.frame_height = self.img.get_height()
            self.images = [
                self.img.subsurface(
                    x * self.frame_width, 0, self.frame_width, self.frame_height
                )
                for x in range(self.frame_count)
            ]
            self.rects = [tex.get_rect(topleft=self.pos) for tex in self.images]
        else:
            self.images = [
                pygame.transform.scale_by(pygame.image.load(self.path), self.scaling)
            ]
            self.rects = [self.images[0].get_rect(topleft=self.pos)]
        self.kill = False

    def update(self):
        if self.frame_count >= 1:
            self.index += (1 / 30) * self.framerate
            if int(self.index) >= len(self.images):
                if not self.should_stay:
                    self.kill = True
                else:
                    game.display.blit(self.images[-1], self.rects[-1])
            else:
                game.display.blit(
                    self.images[int(self.index)], self.rects[int(self.index)]
                )

    def process_event(self, event: pygame.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_COMMA:
                self.index = len(self.images) - 1



active_widgets: List[_Retro | TitleCard | Animation] = []
