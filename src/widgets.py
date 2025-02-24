from .character import *

from contextlib import suppress
from math import ceil, sin
from pygame._sdl2.video import Texture
from typing import Callable, Optional, Tuple

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
        final: str,
        pos: Tuple[int, int] = (0, 0),
        choice_pos: Tuple[int, int] = (0, 30),
        command: Optional[Callable] = None,
        selection=None,
        accepts_input=False,
        wrap: int | str = game.window.size[0] - 50,
        speed=0.6,
        typewriter=True,
        reverse_data=(None, None),
        next_should_be_immediate=False,
        delay=0,
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
        if selection is not None:
            self.selection = RetroSelection(
                selection, pos=choice_pos or len(final.splite("\n")) * 30
            )
        else:
            self.selection = None

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
        self.last_quit = None
        self.delay = delay

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
                self.index = len(self.final) - 1

            if self.accepts_input:
                if self.flickering:

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

                        cond = False
                        if self.should_reverse and self.finished_reversing:
                            cond = True
                        if cond:
                            self.finish(self.answer)
                else:
                    if not self.accepts_input:
                        cond = True
                        if self.delay > 0:
                            if self.last_quit is None:
                                self.last_quit = pygame.time.get_ticks()
                            cond = (
                                pygame.time.get_ticks() - self.last_quit >= self.delay
                            )
                        if cond:
                            self.finish()
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


class RetroSelection(_Retro):
    def __init__(
        self,
        actions,
        pos,
        command: Optional[Callable] = None,
        images=None,
        image_rects=None,
        exit_sel=None,
        autokill=False,
    ):
        self.texts = actions
        self.x, self.y = pos
        self.xo = 40
        self.yo = 40
        self.images = images
        self.exit_sel = exit_sel
        self.images = images or []
        self.image_rects = image_rects or []
        self.command = command
        # selection images, textures and rectangles
        imgs = [
            FONT.render(
                enum_to_str(text.name) if self.command is None else text,
                True,
                Color.WHITE,
            )
            for text in actions
        ]
        self.texs = [Texture.from_surface(game.renderer, img) for img in imgs]
        colored_imgs = [
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
        self.colored_texs = [
            Texture.from_surface(game.renderer, img) for img in colored_imgs
        ]
        # rects
        self.rects = [
            img.get_rect(topleft=(self.x + self.xo, 50 + self.y + y * self.yo))
            for y, img in enumerate(imgs)
        ]
        self.colored_rects = [
            img.get_rect(topleft=(self.x + self.xo, 50 + self.y + y * self.yo))
            for y, img in enumerate(colored_imgs)
        ]
        # other
        self.selected = 0
        self.gt, self.gt_rect = write(">", (self.rects[0].x - 30, self.rects[0].y))
        self.active = True
        self.index = 0
        self.autokill = autokill

    def finish(self, text, quicktime):
        if chance(1 / 8) and False:
            quicktime()()

        else:
            if self.command is not None:
                self.command(text)
            else:
                text.value()
            self.active = False
            if self.autokill:
                active_widgets.remove(self)

    def draw(self):
        for tex, rect, ctex, crect in zip(
            self.texs, self.rects, self.colored_texs, self.colored_rects
        ):
            game.renderer.blit(tex, rect)
            game.renderer.blit(ctex, crect)
        if self.images:
            with suppress(IndexError):
                if self.images[self.index] is not None:
                    game.renderer.blit(
                        self.images[self.index], self.image_rects[self.index]
                    )
        game.renderer.blit(self.gt, self.gt_rect)

    def process_event(self, event, quicktime):
        if self.active:
            if event.key == pygame.K_COMMA:
                self.finish(self.texts[0], quicktime)

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
                self.finish(text, quicktime)

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


class Animation:
    def __init__(
        self,
        path: str,
        pos: Tuple[int, int],
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
            self.texs = [
                Texture.from_surface(
                    game.renderer,
                    self.img.subsurface(
                        x * self.frame_width, 0, self.frame_width, self.frame_height
                    ),
                )
                for x in range(self.frame_count)
            ]
            self.rects = [tex.get_rect(topleft=self.pos) for tex in self.texs]
        else:
            self.img = pygame.transform.scale_by(
                pygame.image.load(self.path), self.scaling
            )
            self.tex = Texture.from_surface(game.renderer, self.img)
            self.rect = self.tex.get_rect()
        self.kill = False

    def update(self):
        if self.frame_count > 1:
            self.index += (1 / 30) * self.framerate
            if int(self.index) >= len(self.texs):
                if self.should_stay is False:
                    self.kill = True
                else:
                    game.renderer.blit(self.texs[-1], self.rects[-1])
            else:
                game.renderer.blit(
                    self.texs[int(self.index)], self.rects[int(self.index)]
                )
        else:
            print("else")

    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_COMMA:
                self.index = len(self.texs) - 1


active_widgets: List[_Retro | TitleCard | Animation] = []
