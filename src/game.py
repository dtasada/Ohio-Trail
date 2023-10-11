from .character import *
from .ttt import *


# storyline functions
def stop_program():
    pygame.quit()
    sys.exit()


def ask_background(name):
    if name.lower() == "joe":
        ent_balls = RetroEntry("Ligma balls", (0, 60), stop_program)
        all_widgets.append(ent_balls)
    else:
        player.name = name
        ent_bg = RetroEntry(f"And {name}, what may your background be?", (0, 60), ask_bg_selection)
        all_widgets.append(ent_bg)


def ask_bg_selection():
    bg_list = [data["desc"] for data in possible_backgrounds.values()]
    sel_bg = RetroSelection(bg_list, (0, 80), set_character_bg, bg_imgs, bg_rects)
    all_widgets.append(sel_bg)


def set_character_bg(bg):
    bg_name = [k for k, v in possible_backgrounds.items() if v["desc"] == bg][0]
    player.background = bg_name
    speed = 0.7 if bg_name == "man" else 0.4
    voiceline_entry = RetroEntry(possible_backgrounds[bg_name]["catchphrase"], (150, 420), intro, accepts_input=False, wrap=WIDTH - 300, speed=speed, typewriter=False)
    all_widgets.append(voiceline_entry)
    possible_backgrounds[bg_name]["sound"].play()


@pause1
def intro():
    all_widgets.clear()
    trip_type = {"banker": "business", "chef": "culinary"}.get(player.background, "pleasure")
    intro_hook = f"""Your name is {player.name}. You have boarded a plane headed
towards Cleveland, Ohio.{ZWS * 20}

You are on a {trip_type} trip.{ZWS * 20}

With you on the plane are another 200 people."""
    plane_anim = Animation('intro-hook', (0, 100), 5, 0.35)
    ent_intro = RetroEntry(intro_hook, (0, 0), intro_p2, reverse_data=(12, "4 people."))
    all_widgets.append(ent_intro)
    all_widgets.append(plane_anim)


@pause1
def intro_p2():
    all_widgets.clear()
    intro_p2_hook = f"""Oh no!{ZWS * 20} The plane has crashed!{ZWS * 20}

You are one of only 5 survivors.{ZWS * 20}

You and 4 NPCs are now stranded on an island.{ZWS *20}

Objective: survive for as long as possible.
"""
    ent_intro_p2 = RetroEntry(intro_p2_hook, (0, 0), list_opts)
    all_widgets.append(ent_intro_p2)


@pause1
def list_opts():
    all_widgets.clear()
    opts_list = []
    match player.location:
        case "planewreck":
            opts_list = [
                "Loot corpses",
                "Explore planewreck",
                "Walk to campsite",
                "Walk to forest",
            ]
        case "campsite":
            opts_list = [
                "Go to campfire",
                "Go to tent",
            ]
        case "campfire":
            opts_list = [
                "Add firewood",
                "Enjoy warmth",
            ]
        case "tent":
            opts_list = [
                "Open chest",
                "Sleep",
            ]
        case "forest":
            opts_list = [
                "Explore forest",
                "Collect firewood",
            ]
    opts_list.append(f"Leave the {player.location}")
    ent_location = RetroEntry(f"You are at the {player.location}", (0,0), set_player_location)
    sel_opts = RetroSelection(opts_list, (0, 60), lambda: None)
    all_widgets.append(ent_location)
    all_widgets.append(sel_opts)


def set_player_location(location):
    player.location = location
    list_opts()


@pause1
def ask_daily_choice():
    player.show_money = False
    all_widgets.clear()
    ent_daily_choice = RetroEntry("What do you want to do today?", (0, 0), daily_choice_selection)
    all_widgets.append(ent_daily_choice)


def daily_choice_selection():
    daily_choice_list = list(possible_daily_choice.values())
    sel_daily_choice = RetroSelection(daily_choice_list, (0, 0), set_daily_choice)
    all_widgets.append(sel_daily_choice)


def set_daily_choice(choice):
    match {v: k for k, v in possible_daily_choice.items()}[choice]:
        case "camp":
            pass
        case "firewood":
            pass
        case "food":
            ask_food()
        case "water":
            pass
        case "skip":
            skip_day()
    all_widgets.clear()


@pause1
def ask_food():
    food_entry = RetroEntry("Which product would you like to buy?", (0, 0), show_foods_list)
    all_widgets.clear()
    all_widgets.append(food_entry)


def show_foods_list():
    global food_select
    player.show_money = True
    food_list = [f"{k} [${v['price']}]" for k, v in possible_foods.items()] + ["Leave Shop"]
    food_select = RetroSelection(food_list, (0, 0), deduct_food_money, food_imgs + [None], food_rects)
    all_widgets.append(food_select)


def deduct_food_money(food):
    if food == "Leave Shop":
        ask_daily_choice()
    else:
        food_name = food.split(" [")[0]
        price = possible_foods[food_name]["price"]
        if player.money - price >= 0:
            if food_name in player.food:
                player.food[food_name] += 1
            else:
                player.food[food_name] = 1
            player.money -= price
            pickup_sound.play()
        all_widgets.remove(food_select)
        show_foods_list()

@pause1
def skip_day():
    global day
    skip_entry = RetroEntry(f"Day {day}", (0, 0), ask_daily_choice, speed= 0.2, reverse_data=(6, f"Day {day + 1}"))
    all_widgets.clear()
    all_widgets.append(skip_entry)
    day += 1


class RetroEntry:
    def __init__(self, final, pos, command, accepts_input=False, wrap=WIDTH, speed=0.6, typewriter=True, reverse_data=(None, None)):
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

    def draw(self):
        if int(self.index) >= 1:
            REN.blit(self.image, self.rect)

    def process_event(self, event):
        if event.key == pygame.K_SPACE:
            def skip():
                pass
                # Skip function pls
            skip()
        if self.accepts_input and self.active:
            if self.flickering:
                #
                mods = pygame.key.get_mods()
                name = pygame.key.name(event.key)
                self.text = self.text.removesuffix("_")
                if name == "return":
                    self.command(self.answer)
                    self.active = False
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
                            self.command()
                            self.active = False
            else:
                self.index -= self.speed
                if ceil(self.index) < self.last_index:
                    self.update_tex(self.text[:-1])
                    self.last_index = self.index
                    self.deleted += 1
                    if self.deleted >= self.reverse_length:
                        if self.reverse_string is None:
                            self.command()
                            self.active = False
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


class RetroSelection:
    def __init__(self, texts, pos, command, images=None, image_rects=None, exit_sel=None):
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
                self.command(text)
                self.active = False

    def update(self):
        self.draw()


class GenText:
    def __init__(self, text, pos, size, sine=(None, None)):
        self.tex, self.rect = write(text, pos, size)
        self.amp, self.freq = sine
        self.og_y = self.rect.y

    def process_event(self, event):
        if event.key == pygame.K_SPACE:
            all_widgets.clear()
            all_widgets.append(name_entry)

    def update(self):
        self.rect.y = self.og_y + self.amp * sin(pygame.time.get_ticks() * self.freq)
        REN.blit(self.tex, self.rect)

food_select = None
money_warning = None
player = Character()
ttt = TicTacToe()

name_entry = RetroEntry("Hello traveler, what is your name?", (0, 0), accepts_input=True, command=ask_background)

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
title_card = GenText(f"{title_card_string}       {random_ahh}", (96, 76), 24, sine=(15, 0.002))
all_widgets = [title_card]


def main():
    running = True
    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                for widget in all_widgets:
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
