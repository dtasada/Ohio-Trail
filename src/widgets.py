from .character import *
from .settings import *
from contextlib import suppress
from math import floor, ceil, sin, cos, pi
import pygame.gfxdraw
from pygame.typing import Point
from pygame.time import get_ticks as ticks
from typing import Callable, Optional, Tuple, List

from operator import setitem


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
        self.texts = actions
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
        self.rects: List[pygame.Rect] = [
            img.get_rect(topleft=(self.x + self.xo, 50 + self.y + y * self.yo))
            for y, img in enumerate(self.images)
        ]
        self.colored_rects: List[pygame.Rect] = [
            img.get_rect(topleft=(self.x + self.xo, 50 + self.y + y * self.yo))
            for y, img in enumerate(self.colored_images)
        ]
        # other
        self.gt, self.gt_rect = write(">", (self.rects[0].x - 30, self.rects[0].y))
        self.active: bool = True
        self.index: int = 0
        self.autokill: bool = autokill

    def finish(self, text: "Action", quicktime: Callable, quicktime_active: bool):
        """Called when the selection is finished. By default, it will call the associated command."""
        if False and not quicktime_active and chance(1 / 2):
            Sound.ALERT.play()
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
        """Draw the selection widget"""
        for tex, rect, ctex, crect in zip(
            self.images, self.rects, self.colored_images, self.colored_rects
        ):
            game.display.blit(tex, rect)
            game.display.blit(ctex, crect)
        if self.portrait_images:
            with suppress(IndexError):
                if self.portrait_images[self.index] is not None:
                    game.display.blit(
                        self.portrait_images[self.index], self.image_rects[self.index]
                    )
        game.display.blit(self.gt, self.gt_rect)

    def process_event(
        self, event: pygame.Event, quicktime: Callable, quicktime_active: bool
    ):
        if self.active:
            if event.key == pygame.K_COMMA:
                self.finish(self.texts[0], quicktime, quicktime_active)

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
                        self.last_flicker = ticks()
                        self.last_finished_writing = ticks()

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
                                self.last_quit = ticks()
                            cond = ticks() - self.last_quit >= self.delay
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
    def __init__(self, text, pos, size, ask_name: RetroEntry, sine=(None, None)):
        self.autokill = True
        self.command = lambda: setitem(active_widgets, 0, ask_name)
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
            self.img = pygame.transform.scale_by(
                pygame.image.load(self.path), self.scaling
            )
            self.tex = pygame.Surface.from_surface(game.display, self.img)
            self.rect = self.tex.get_rect()
        self.kill = False

    def update(self):
        if self.frame_count > 1:
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


class Minigame:
    def check_finished(self):
        pass


class WoodChopping(Minigame):
    def __init__(self, action):
        # gameplay variables
        self.w, self.h = 300, 34
        self.x, self.y = (
            game.width / 2 - self.w / 2,
            game.height / 2 - self.h / 2,
        )
        self.action = action
        self.chop_x = self.x
        self.chop_y = self.y + self.h / 2
        self.chop_w, self.chop_h = 10, 60
        self.def_speed = self.speed = 0.003
        self.num_chopped = 0
        self.set_correct()

        # timer and particles for UI/UX
        self.last_start = ticks()
        # TODO: particles
        self.particles = []

    def finish(self):
        active_widgets.remove(self)
        self.action(self.num_chopped)

    def chop(self):
        if self.correct_x <= self.chop_x <= self.correct_x + self.correct_w:
            Sound.CHOP.play()
            self.num_chopped += 1
        self.set_correct()

    def set_correct(self):
        self.correct_w = random.randint(12, 30)
        self.correct_x = random.randint(
            int(self.x), int(self.x + self.w - self.correct_w)
        )

    def process_event(self, event):
        if event.key == pygame.K_SPACE:
            # timing for chopping the wood
            # self.action.value()
            self.chop()

    def draw(self):
        # render the UI
        remaining_seconds = floor(10 - (ticks() - self.last_start) / 1000)
        if remaining_seconds <= -1:
            self.finish()
        else:
            game.display.blit(
                *write(
                    str(remaining_seconds),
                    (self.x + self.w / 2, self.y - 100),
                    size=30,
                    anchor="center",
                )
            )

        # render the game
        pygame.draw.rect(game.display, Color.WHITE, (self.x, self.y, self.w, self.h), 1)
        self.chop_x = self.x + self.w / 2 + sin(ticks() * self.speed) * self.w / 2
        pygame.draw.rect(
            game.display,
            Color.WHITE,
            (
                self.chop_x - self.chop_w / 2,
                self.chop_y - self.chop_h / 2,
                self.chop_w,
                self.chop_h,
            ),
        )
        pygame.draw.rect(
            game.display, Color.BROWN, (self.correct_x, self.y, self.correct_w, self.h)
        )

    def update(self):
        self.draw()
        self.check_finished()


class Wave:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.alpha = 0
        self.direc = 1

    def update(self, scroll):
        self.image = pygame.Surface((self.w, self.h))
        self.image.fill((255, 255, 255))
        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.alpha += self.direc * 6
        if self.alpha >= 255:
            self.direc = -1
        # self.y -= 1
        game.display.blit(self.image, self.rect.move(-scroll[0], -scroll[1]))


class Fishing(Minigame):
    def __init__(self, action):
        self.action = action
        self.water_size = 400
        self.num_fishes = 0
        self.bobbered = False
        self.radar_index = 0
        self.radar_rect = Visuals.RADAR[0].get_rect(center=(game.center))
        self.bobber_rect = Visuals.BOBBER.get_rect(center=(game.center))
        self.waves = []
        self.last_wave = ticks()
        self.scroll = [0, 0]

        self.blink_size = self.max_blink_size = 8
        self.last_blink = ticks()
        self.change_blink_pos()
        self.detected = False
        self.last_bite = ticks()
        self.started_reeling = False
        self.reel_level = 0
        self.tension = False

        self.tension_arrow_offset = 0
        self.last_released_tension = ticks()

    def finish(self, num=1):
        active_widgets.remove(self)
        self.action(num)

    def process_event(self, event):
        if event.key == pygame.K_SPACE:
            # if not bobblerd yet, just bobble the boblard
            if not self.bobbered:
                self.bobbered = True

    def detect_fish(self):
        self.detected = True
        game.start_shake([7, 0], 2000)
        self.last_bite = ticks()

    def move(self):
        # move the bobber
        keys = pygame.key.get_pressed()
        self.moving = False
        # apply the scroll
        vel = 2
        # move bobber to find fish
        if not self.detected:
            if keys[pygame.K_LEFT]:
                self.bobber_rect.x -= vel
                self.moving = True
            if keys[pygame.K_RIGHT]:
                self.bobber_rect.x += vel
                self.moving = True
            if keys[pygame.K_UP]:
                self.bobber_rect.y -= vel
                self.moving = True
            if keys[pygame.K_DOWN]:
                self.bobber_rect.y += vel
                self.moving = True
        else:
            # already caught fish, have to reel it in
            if self.started_reeling:
                # cause tension shenanigans
                if not self.tension:
                    if chance(1 / 60):
                        self.tension = True
                        self.last_released_tension = ticks()
                        self.tension_direction = random.choice((-1, 1))
                else:
                    # update frantic arrow position
                    self.tension_arrow_offset += 5
                    if self.tension_arrow_offset >= 40:
                        self.tension_arrow_offset = 0
                    # already tensioning, break apart
                    if keys[
                        (
                            pygame.K_RIGHT
                            if self.tension_direction == 1
                            else pygame.K_LEFT
                        )
                    ]:
                        if ticks() - self.last_released_tension >= random.randint(
                            2000, 3000
                        ):
                            self.tension = False
                # fix the tension
                if keys[pygame.K_SPACE]:
                    if not self.tension:
                        self.reel_level += 0.4
                        if self.reel_level >= 100:
                            self.finish()
                    else:
                        # foei foei you are reeling while under tension
                        if chance(1 / 70):
                            self.finish(-1)
        # perhaps catch fish?
        if not self.detected and not self.started_reeling:
            if self.moving and chance(1 / 700):
                self.detect_fish()
        # scroll
        m = 0.1
        self.scroll[0] += (
            self.bobber_rect.x
            - self.scroll[0]
            - game.width / 2
            + self.bobber_rect.width / 2
        ) * m
        self.scroll[1] += (
            self.bobber_rect.y
            - self.scroll[1]
            - game.height / 2
            + self.bobber_rect.height / 2
        ) * m

    def change_blink_pos(self):
        m = self.water_size / 2 - 10
        angle = random.uniform(0, 2 * pi)
        self.blink_pos = (
            int(game.center[0] + m * cos(angle)),
            int(game.center[1] + m * sin(angle)),
        )
        self.last_blink = ticks()

    def update_blink(self):
        # change size of the blink
        self.blink_size -= 0.9
        if self.blink_size <= 0:
            self.blink_size = self.max_blink_size
        # check if blink needs to teleport to a different place
        if ticks() - self.last_blink >= 2700:
            self.change_blink_pos()

    def draw(self):
        water_rect = (
            game.width / 2 - self.water_size / 2,
            game.height / 2 - self.water_size / 2,
            self.water_size,
            self.water_size,
        )
        pygame.draw.rect(game.display, pygame.Color("deepskyblue2"), water_rect)
        pygame.draw.rect(game.display, Color.WHITE, water_rect, 1)
        if not self.bobbered:
            # just loaded in, have to throw bobber first
            self.radar_index += 0.4
            try:
                Visuals.RADAR[int(self.radar_index)]
            except IndexError:
                self.radar_index = 0
            finally:
                game.display.blit(Visuals.RADAR[int(self.radar_index)], self.radar_rect)
            game.display.blit(
                *write(
                    "Press <space> to throw bobber", (game.width / 2, 50), 14, "midtop"
                )
            )
        else:
            # update and draw the waters
            if ticks() - self.last_wave >= 370:
                w, h = random.randint(30, 50), 4
                self.waves.append(
                    Wave(
                        random.randint(
                            self.bobber_rect.centerx - self.water_size // 2,
                            self.bobber_rect.centerx + self.water_size // 2 - w,
                        ),
                        random.randint(
                            self.bobber_rect.centery - self.water_size // 2,
                            self.bobber_rect.centery + self.water_size // 2 - w,
                        ),
                        w,
                        h,
                    )
                )
                self.last_wave = ticks()
            for wave in self.waves[:]:
                wave.update(self.scroll)
                if wave.alpha <= 0:
                    self.waves.remove(wave)
            scrolled_rect = self.bobber_rect.move(-self.scroll[0], -self.scroll[1])
            # black border
            pygame.draw.rect(
                game.display,
                Color.BLACK,
                (0, 0, game.width, game.height / 2 - self.water_size / 2),
            )  # top
            pygame.draw.rect(
                game.display,
                Color.BLACK,
                (0, 0, game.width / 2 - self.water_size / 2, game.height),
            )  # left
            pygame.draw.rect(
                game.display,
                Color.BLACK,
                (
                    game.width / 2 + self.water_size / 2,
                    0,
                    game.width / 2 - self.water_size / 2,
                    game.height,
                ),
            )  # right
            pygame.draw.rect(
                game.display,
                Color.BLACK,
                (
                    0,
                    game.height / 2 + self.water_size / 2,
                    game.width,
                    game.height / 2 - self.water_size / 2,
                ),
            )  # bottom

            game.display.blit(Visuals.BOBBER, scrolled_rect)
            pygame.draw.line(
                game.display,
                Color.BLACK,
                (
                    game.width / 2 - self.water_size / 2,
                    game.height / 2 + self.water_size / 2,
                ),
                scrolled_rect.midbottom,
            )

            # render the blink
            if not self.detected:
                game.display.blit(
                    *write("Move to detect fish", (game.width / 2, 50), 14, "midtop")
                )
                pygame.gfxdraw.filled_circle(
                    game.display,
                    *self.blink_pos,
                    int(self.blink_size),
                    pygame.Color("orange"),
                )
                pygame.gfxdraw.aacircle(
                    game.display, *self.blink_pos, int(self.blink_size), Color.BLACK
                )
            else:
                if not self.started_reeling:
                    game.display.blit(
                        *write(
                            "Got bite !!",
                            (game.width / 2, game.height / 2 - 60),
                            14,
                            "midtop",
                            pygame.Color("darkslategray1"),
                        )
                    )
                    if ticks() - self.last_bite >= 2000:
                        self.started_reeling = True
                else:
                    game.display.blit(
                        *write(
                            "Hold <space> to reel",
                            (game.width / 2, 40),
                            14,
                            "midtop",
                            Color.WHITE,
                        )
                    )
                    bar_width, bar_height = 180, 22
                    reel_width = self.reel_level / 100 * bar_width
                    pygame.draw.rect(
                        game.display,
                        Color.WHITE,
                        (game.width / 2 - bar_width / 2, 70, bar_width, bar_height),
                        1,
                    )
                    pygame.draw.rect(
                        game.display,
                        Color.WHITE,
                        (game.width / 2 - bar_width / 2, 70, reel_width, bar_height),
                    )
                    # tension !!!
                    if self.tension:
                        game.start_shake([2, 0], 500)
                        game.display.blit(
                            *write(
                                "tension !!!",
                                (game.width / 2, game.height / 2 - 60),
                                14,
                                "midtop",
                                Color.WHITE,
                            )
                        )
                        if self.tension_direction == 1:
                            game.display.blit(
                                *write(
                                    ">",
                                    (
                                        game.width / 2
                                        + 110
                                        + self.tension_arrow_offset,
                                        game.height / 2 - 50,
                                    ),
                                    22,
                                    "midright",
                                    Color.WHITE,
                                )
                            )
                        else:
                            game.display.blit(
                                *write(
                                    "<",
                                    (
                                        game.width / 2
                                        - 110
                                        - self.tension_arrow_offset,
                                        game.height / 2 - 50,
                                    ),
                                    22,
                                    "midright",
                                    Color.WHITE,
                                )
                            )

    def update(self):
        if self.bobbered:
            self.move()
            self.update_blink()
        self.draw()


active_widgets: List[_Retro | TitleCard | Animation | Minigame] = []
