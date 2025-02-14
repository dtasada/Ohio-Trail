from .character import *

from contextlib import suppress
from math import ceil, sin
from pygame._sdl2.video import Texture
from typing import Callable, Optional

from operator import setitem


class _Retro:
    autokill: bool
    command: Optional[Callable]

    def finish(self, *args, **kwargs):
        if self.command:
            self.command(*args, **kwargs)
        self.active = False
        if self.autokill:
            active_widgets.remove(self)

    def update(self): ...
    def process_event(self, event): ...


class RetroEntry(_Retro):
    def __init__(
        self,
        final,
        pos,
        command=None,
        selection=None,
        accepts_input=False,
        wrap: int | str = game.window.size[0] - 50,
        speed=0.6,
        typewriter=True,
        reverse_data=(None, None),
        next_should_be_immediate=False,
        autokill=False,
    ):
        self.final = final + " "
        self.text = ""
        self.answer = ""
        self.index = 0
        self.last_index = self.index
        self.x, self.y = [i + 12 for i in pos]
        self.speed = speed
        self.flickering = False
        self.has_underscore = False

        self.reversing = False
        self.reverse_length, self.reverse_string = reverse_data
        self.should_reverse = self.reverse_length is not None
        self.finished_reversing = False

        self.last_flicker = pygame.time.get_ticks()
        self.last_finished_writing = pygame.time.get_ticks()
        self.deleted = 0
        self.command = command
        self.selection = selection
        self.active = True
        self.accepts_input = accepts_input
        self.wrap: int | str = wrap
        self.typewriter = typewriter
        self.kwargs = {
            "typewriter": typewriter,
            "speed": speed,
            "accepts_input": accepts_input,
        }
        self.next_should_be_immediate = next_should_be_immediate
        self.autokill = autokill

    def finish(self, *args, **kwargs):
        if self.command is not None:
            self.command(*args, **kwargs)
        elif self.selection is not None:
            active_widgets.append(self.selection)
        self.active = False
        if self.autokill:
            active_widgets.remove(self)

    def draw(self):
        if int(self.index) >= 1:
            game.renderer.blit(self.image, self.rect)

    def process_event(self, event):
        if self.active:
            if event.key == pygame.K_COMMA:
                try:
                    self.finish("ligma")
                except TypeError:
                    self.finish()

            if self.accepts_input:
                if self.flickering:
                    #
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
                    #
                    elif name == "space":
                        self.text += " "
                        self.answer += " "
                    elif len(name) > 1:
                        pass
                    else:
                        if len(self.answer) < 20:
                            if mods in (1, 2):
                                name = name.capitalize()
                            self.text += name
                            self.answer += name
                    self.update_tex(self.text)

    def update(self):
        if self.active:
            # update the text
            if not self.reversing:
                if not self.flickering:
                    self.index += self.speed
                    if int(self.index) >= 1:
                        self.update_tex(self.final[: int(self.index)])
                    # type sound
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
                        self.last_flicker = pygame.time.get_ticks()
                        self.last_finished_writing = pygame.time.get_ticks()
                        condition = True
                        if self.should_reverse:
                            condition = self.finished_reversing
                        if not self.accepts_input and condition:
                            self.finish(
                                **(
                                    {"speed": 1000}
                                    if self.next_should_be_immediate
                                    else {}
                                )
                            )
            else:
                self.index -= self.speed
                if ceil(self.index) < self.last_index:
                    self.update_tex(self.text[:-1])
                    self.last_index = self.index
                    self.deleted += 1
                    if self.deleted >= self.reverse_length:
                        if self.reverse_string is None:
                            self.finish(
                                **(
                                    {"speed": 1000}
                                    if self.next_should_be_immediate
                                    else {}
                                )
                            )
                        else:
                            self.reversing = False
                            self.finished_reversing = True
                            self.final = self.text + self.reverse_string
            if self.accepts_input:
                # execute when flickering
                if self.flickering:
                    if pygame.time.get_ticks() - self.last_flicker >= 500:
                        if self.has_underscore:
                            self.update_tex(self.text.removesuffix("_"))
                        else:
                            self.update_tex(self.text + "_")
                        self.has_underscore = not self.has_underscore
                        self.last_flicker = pygame.time.get_ticks()

        if not self.reversing:
            if self.index >= len(self.final):
                if self.reverse_length is not None:
                    if pygame.time.get_ticks() - self.last_finished_writing >= 1_000:
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
        self.image = Texture.from_surface(game.renderer, img)
        self.rect = img.get_rect(topleft=(self.x, self.y))

        condition = (
            (self.rect.right >= self.wrap)
            if isinstance(self.wrap, int)
            else self.text.endswith(self.wrap + " ")
        )
        # if condition:
        #     self.text += "\n\n"
        # if condition:
        #     remaining_text = self.final.removeprefix(self.text)
        #     new_text = RetroEntry(
        #         remaining_text,
        #         (self.rect.x, self.rect.y + 30),
        #         self.command,
        #         **self.kwargs,
        #     )
        #     active_widgets.append(new_text)
        #     self.active = False


class RetroSelection(_Retro):
    def __init__(
        self,
        texts,
        pos,
        command: Optional[Callable] = None,
        images=None,
        image_rects=None,
        exit_sel=None,
        autokill=False,
    ):
        self.texts = texts
        self.x, self.y = pos
        self.xo = 40
        self.yo = 40
        self.images = images
        self.exit_sel = exit_sel
        self.images = images or []
        self.image_rects = image_rects or []
        self.command = command
        imgs = [
            FONT.render(
                enum_to_str(text.name) if self.command is None else text,
                True,
                Color.WHITE,
            )
            for text in texts
        ]
        self.rects = [
            img.get_rect(topleft=(self.x + self.xo, 50 + self.y + y * self.yo))
            for y, img in enumerate(imgs)
        ]
        self.texs = [Texture.from_surface(game.renderer, img) for img in imgs]
        self.selected = 0
        self.gt, self.gt_rect = write(">", (self.rects[0].x - 30, self.rects[0].y))
        self.active = True
        self.index = 0
        self.autokill = autokill

    def finish(self, text):
        if self.command is not None:
            self.command(text)
        else:
            text.value()
        self.active = False
        if self.autokill:
            active_widgets.remove(self)

    def draw(self):
        for tex, rect in zip(self.texs, self.rects):
            game.renderer.blit(tex, rect)
        if self.images:
            with suppress(IndexError):
                if self.images[self.index] is not None:
                    game.renderer.blit(
                        self.images[self.index], self.image_rects[self.index]
                    )
        game.renderer.blit(self.gt, self.gt_rect)

    def process_event(self, event):
        if self.active:
            if event.key == pygame.K_COMMA:
                self.finish(self.texts[0])

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
                text = self.texts[self.index]
                self.finish(text)

    def update(self):
        self.draw()


random_ahh = (
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
    def __init__(self, text, pos, size, ask_name: RetroEntry, sine=(None, None)):
        self.autokill = True
        self.command = lambda: setitem(active_widgets, 0, ask_name)
        self.tex, self.rect = write(text, pos, size)
        self.amp, self.freq = sine
        self.og_y = self.rect.y

    def process_event(self, event):
        if event.key == pygame.K_SPACE:
            if self.command:
                self.command()

    def update(self):
        self.rect.y = self.og_y + self.amp * sin(pygame.time.get_ticks() * self.freq)
        game.renderer.blit(self.tex, self.rect)

active_widgets: List[_Retro | TitleCard | Animation] = []
