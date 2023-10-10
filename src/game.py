from .character import *
from .ttt import *


# storyline functions
def ask_background(name):
    player.name = name
    ent_bg = RetroEntry(f"And {name}, what may your background be?", (0, 60), ask_bg_selection, accepts_input=False)
    all_widgets.append(ent_bg)

    
def ask_bg_selection(*args):
    bg_list = [ data["desc"] for data in possible_backgrounds.values() ]
    sel_bg = RetroSelection(bg_list, (0, 80), set_character_bg, bg_imgs, bg_rects)
    all_widgets.append(sel_bg)


def set_character_bg(bg):
    bg_name = [k for k, v in possible_backgrounds.items() if v["desc"] == bg][0]
    player.background = bg_name
    speed = 0.7 if bg_name == "man" else 0.4
    voiceline_entry = RetroEntry(possible_backgrounds[bg_name]["catchphrase"], (150, 420), ask_food, accepts_input=False, wrap=WIDTH - 300, speed=speed, typewriter=False)
    all_widgets.append(voiceline_entry)
    possible_backgrounds[bg_name]["sound"].play()

@pause1
def intro():
    all_widgets.clear()
    intro_hook = f"""Your name is {player.name}. You have boarded a plane headed
towards Cleveland, Ohio.{ZWS * 20}

You are on a {'cooking' if player.background == 'chef' else 'business' if player.background == 'banker' else 'pleasure'} trip.{ZWS * 20}

With you on the plane are another 200 people.
    """
    ent_intro = RetroEntry(intro_hook, (0, 0), lambda: None, accepts_input=False, backspace=(11, '4 people.'))
    plane_anim = Animation('intro-hook', (0, 500), 5, 0.5)
    all_widgets.append(ent_intro)
    all_widgets.append(plane_anim)



@pause1
def ask_daily_choice():
    all_widgets.clear()
    ent_daily_choice = RetroEntry("What do you want to do today?", (0, 0), daily_choice_selection, accepts_input=False)
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
            pass
        case "water":
            pass
        case "skip":
            pass
    all_widgets.clear()


@pause1
def ask_food():
    food_entry = RetroEntry("Which product would you like to buy?", (0, 0), show_foods_list, accepts_input=False)
    all_widgets.clear()
    all_widgets.append(food_entry)


def show_foods_list():
    global food_select

    player.show_money = True
    food_list = [f"{k} [${v['price']}]" for k, v in possible_foods.items()]
    food_select = RetroSelection(food_list, (0, 0), deduct_food_money, food_imgs, food_rects)
    all_widgets.append(food_select)



def deduct_food_money(food):
    food_name = food.split(" [")[0]
    price = possible_foods[food_name]["price"]
    if player.money - price >= 0:
        print(player.money)
        print(price)
        if food_name in player.food:
            player.food[food_name] += 1
        else:
            player.food[food_name] = 1
        player.money -= price
        pickup_sound.play()
    all_widgets.remove(food_select)
    show_foods_list()


class RetroEntry:
    def __init__(self, final, pos, command, accepts_input=True, wrap=WIDTH, speed=0.6, typewriter=True, backspace=(None, None)):
        self.final = final + " "
        self.text = ""
        self.answer = ""
        self.index = 0
        self.last_index = self.index
        self.x, self.y = [i + 12 for i in pos]
        self.speed = speed
        self.flickering = False
        self.has_underscore = False
        self.last_flicker = ticks()
        self.command = command
        self.active = True
        self.accepts_input = accepts_input
        self.wrap = wrap
        self.typewriter = typewriter
        self.kwargs = {"typewriter": typewriter, "speed": speed, "accepts_input": accepts_input}
        self.backspace_index, self.backspace_text = backspace

    def draw(self):
        if int(self.index) >= 1:
            REN.blit(self.image, self.rect)

    def process_event(self, event):
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
            if not self.flickering:
                self.index += self.speed
                if int(self.index) >= 1:
                    self.update_tex(self.final[:int(self.index)])
                    # if self.backspace_index != None:
                    #     for _ in range(1, self.backspace_index):
                    #         list(self.text).pop()
                    #         print(self.text)
                    #         self.index -= self.backspace_index
                # type sound
                if int(self.index) > self.last_index and (not self.text[-1] in (" ", ZWS)) and self.typewriter:
                    typewriter_sound.play()
                    self.last_index = self.index
                # if finished, start flickering the underscore (_)
                if self.index >= len(self.final):
                    self.flickering = True
                    self.last_flicker = ticks()
                    if not self.accepts_input:
                        self.command()
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
    def __init__(self, text, pos, size):
        self.tex, self.rect = write(text, pos, size)

    def process_event(self, event):
        if event.key == pygame.K_SPACE:
            all_widgets.clear()
            all_widgets.append(name_entry)

    def update(self):
        REN.blit(self.tex, self.rect)

food_select = None
money_warning = None
player = Character()
ttt = TicTacToe()

all_widgets = []
name_entry = RetroEntry("Hello traveler, what is your name?", (0, 0), command=ask_background)

title_card = GenText(r'''
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


      Press any SPACE to continue
''', (96, 76), 24)
all_widgets.append(title_card)
# all_widgets.append(name_entry)

# update_objects = [ ttt ]
update_objects = []


if food_select is not None:
    for i, k in enumerate(possible_foods.keys()):
        print(1, k)
        if k in player.food.keys() and k != 0:
            print(2, k)

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
                for obj in update_objects:
                    obj.process_event(event)


        fill_rect(REN, (0, 0, 0, 255), (0, 0, WIDTH, HEIGHT))

        for widget in all_widgets:
            widget.update()

        for obj in update_objects:
            obj.update()

        if food_select is not None:
            i = 0
            for k in possible_foods.keys():
                if k in player.food.keys() and player.food[k] != 0:
                    img, rect = write(f"{k}: {player.food[k]}", (38, 420 + i * 28))
                    REN.blit(img, rect)
                    i += 1

        player.update()

        REN.present()

    pygame.quit()
    sys.exit()
