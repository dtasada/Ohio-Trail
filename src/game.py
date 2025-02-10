from os import access
from .character import *


# storyline functions
def enter_background(name):
    player.name = name
    ent_bg = RetroEntry(f"And {name}, what may your background be?", (0, 60), enter_bg_selection)
    all_widgets.append(ent_bg)


def enter_bg_selection():
    bg_list = [data["desc"] for data in possible_backgrounds.values()]
    sel_bg = RetroSelection(bg_list, (0, 80), set_character_bg, bg_imgs, bg_rects)
    all_widgets.append(sel_bg)


def set_character_bg(bg):
    bg_name = [k for k, v in possible_backgrounds.items() if v["desc"] == bg][0]
    player.background = bg_name
    speed = 0.7 if bg_name == "man" else 0.4
    #
    voiceline_entry = RetroEntry(possible_backgrounds[bg_name]["catchphrase"], (150, 420), intro, accepts_input=False, wrap=WIDTH - 300, speed=speed, typewriter=False)
    all_widgets.append(voiceline_entry)
    possible_backgrounds[bg_name]["sound"].play()


@pause1
def intro():
    #
    all_widgets.clear()
    #
    trip_type = {"banker": "business", "chef": "culinary"}.get(player.background, "pleasure")
    text_intro = \
    f"""Your name is {player.name}. You have boarded a plane headed

towards Cleveland, Ohio.{ZWS * 20}

You are on a {trip_type} trip.{ZWS * 20}

With you on the plane are another 200 people."""

    # plane crashing animation and
    anim_plane = Animation("intro-hook", (0, 100), 5, 0.35, should_stay=True)
    all_widgets.append(anim_plane)
    #
    info_intro = RetroEntry(text_intro, (0, 0), intro_crash, reverse_data=(12, "4 people."))
    all_widgets.append(info_intro)  # important that this is the last thing appended


@pause1
def intro_crash():
    all_widgets.pop()
    text_intro_crash = \
    f"""Oh no!{ZWS * 20} The plane has crashed!{ZWS * 20}

You are one of only 5 survivors.{ZWS * 20}

You and 4 NPCs are now stranded on an island.{ZWS *20}

Objective: survive for as long as possible.
"""
    info_intro_crash = RetroEntry(text_intro_crash, (0, 0), crash_choice)
    all_widgets.append(info_intro_crash)


def crash_choice():
    print("asd")


class _Retro:
    def finish(self, *args, **kwargs):
        self.command(*args, **kwargs)
        self.active = False
        if self.autokill:
            all_widgets.remove(self)


class RetroEntry(_Retro):
    def __init__(self, final, pos, command, accepts_input=False, wrap=WIDTH, speed=0.6, typewriter=True, reverse_data=(None, None), next_should_be_immediate=False, autokill=False):
        self.final = final + " "
        self.text = ""
        self.answer = ""
        self.index = 0
        self.last_index = self.index
        self.x, self.y = [i + 12 for i in pos]
        self.speed = speed
        self.flickering = False
        self.has_underscore = False
        #
        self.reversing = False
        self.reverse_length, self.reverse_string = reverse_data
        self.has_to_reverse = self.reverse_length is not None
        self.finished_reversing = False
        #
        self.last_flicker = ticks()
        self.last_finished_writing = ticks()
        self.deleted = 0
        self.command = command
        self.active = True
        self.accepts_input = accepts_input
        self.wrap = wrap
        self.typewriter = typewriter
        self.kwargs = {"typewriter": typewriter, "speed": speed, "accepts_input": accepts_input}
        self.next_should_be_immediate = next_should_be_immediate
        self.autokill = autokill

    def draw(self):
        if int(self.index) >= 1:
            REN.blit(self.image, self.rect)

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
                        self.update_tex(self.final[:int(self.index)])
                    # type sound
                    if int(self.index) > self.last_index and (self.text[-1] not in (" ", ZWS)) and self.typewriter:
                        typewriter_sound.play()
                        self.last_index = self.index
                    # if finished, start flickering the underscore (_)
                    if self.index >= len(self.final):
                        self.flickering = True
                        self.last_flicker = ticks()
                        self.last_finished_writing = ticks()
                        cond = True
                        if self.has_to_reverse:
                            cond = self.finished_reversing
                        if not self.accepts_input and cond:
                            self.finish(**({"speed": 1000} if self.next_should_be_immediate else {}))
            else:
                self.index -= self.speed
                if ceil(self.index) < self.last_index:
                    self.update_tex(self.text[:-1])
                    self.last_index = self.index
                    self.deleted += 1
                    if self.deleted >= self.reverse_length:
                        if self.reverse_string is None:
                            self.finish(**({"speed": 1000} if self.next_should_be_immediate else {}))
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
            img = font.render(text, True, WHITE)
        except pygame.error:
            img = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.image = Texture.from_surface(REN, img)
        self.rect = img.get_rect(topleft=(self.x, self.y))
        if isinstance(self.wrap, int):
            cond = self.rect.right >= self.wrap
        elif isinstance(self.wrap, str):
            cond = self.text.endswith(self.wrap + " ")
        if cond:
            remaining_text = self.final.removeprefix(self.text)
            new_text = RetroEntry(remaining_text, (self.rect.x, self.rect.y + 30), self.command, **self.kwargs)
            all_widgets.append(new_text)
            self.active = False


class RetroSelection(_Retro):
    def __init__(self, texts, pos, command, images=None, image_rects=None, exit_sel=None, autokill=False):
        self.texts = texts
        self.x, self.y = pos
        self.xo = 40
        self.yo = 40
        self.images = images
        self.exit_sel = exit_sel
        if images is None:
            self.images = []
            self.image_rects = []
        else:
            self.images = images
            self.image_rects = image_rects
        imgs = [font.render(text, True, WHITE) for text in texts]
        self.rects = [img.get_rect(topleft=(self.x + self.xo, 50 + self.y + y * self.yo)) for y, img in enumerate(imgs)]
        self.texs = [Texture.from_surface(REN, img) for img in imgs]
        self.selected = 0
        self.gt, self.gt_rect = write(">", (self.rects[0].x - 30, self.rects[0].y))
        self.active = True
        self.command = command
        self.index = 0
        self.autokill = autokill

    def draw(self):
        for tex, rect in zip(self.texs, self.rects):
            REN.blit(tex, rect)
        if self.images:
            with suppress(IndexError):
                if self.images[self.index] is not None:
                    REN.blit(self.images[self.index], self.image_rects[self.index])
        REN.blit(self.gt, self.gt_rect)

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
                beep_sound.play()
            elif event.key in (pygame.K_w, pygame.K_UP):
                if self.gt_rect.y == self.rects[0].y:
                    self.gt_rect.y = self.rects[-1].y
                    self.index = -1
                else:
                    self.gt_rect.y -= self.yo
                    self.index -= 1
                beep_sound.play()
            elif event.key == pygame.K_RETURN:
                text = self.texts[self.index]
                self.finish(text)

    def update(self):
        self.draw()


class TitleCard:
    def __init__(self, text, pos, size, sine=(None, None)):
        self.tex, self.rect = write(text, pos, size)
        self.amp, self.freq = sine
        self.og_y = self.rect.y

    def process_event(self, event):
        if event.key == pygame.K_SPACE:
            all_widgets.clear()
            all_widgets.append(enter_name)

    def update(self):
        self.rect.y = self.og_y + self.amp * sin(pygame.time.get_ticks() * self.freq)
        REN.blit(self.tex, self.rect)


player = Character()

random_ahh = ' '.join(random.sample(['press', 'space', 'to', 'continue'], 4)).capitalize().replace('space', 'SPACE').replace('Space', 'SPACE')
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
title_card = TitleCard(f"{title_card_string}{' ' * 8}{random_ahh}", (96, 76), 24, sine=(15, 0.002))
enter_name = RetroEntry("Hello traveler, what is your name?", (0, 0), accepts_input=True, command=enter_background)
all_widgets = [title_card]


def main(debug=False):
    running = True
    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                for widget in all_widgets[:]:
                    widget.process_event(event)

        fill_rect(REN, (0, 0, 0, 255), (0, 0, WIDTH, HEIGHT))

        for widget in all_widgets[:]:
            widget.update()
            if getattr(widget, "kill", False):
                all_widgets.remove(widget)

        if player.show_money:
            i = 0
            for k in possible_foods.keys():
                if k in player.food.keys() and player.food[k] != 0:
                    img, rect = write(f"{k}: {player.food[k]}", (38, 460 + i * 28))
                    REN.blit(img, rect)
                    i += 1

        player.update()

        REN.present()

    pygame.quit()
    sys.exit()
