from types import coroutine
from .character import *


# storyline functions
def ask_background(name):
    bg_entry = RetroEntry(f"And {name}, what may your background be?", (0, 60), ask_bg_selection, accepts_input=False)
    all_widgets.append(bg_entry)


def ask_bg_selection(*args):
    global bg_select
    bg_list = [data["desc"] for data in possible_backgrounds.values()]
    bg_select = RetroSelection(bg_list, (0, 80), set_character_bg, bg_imgs, bg_rects)
    all_widgets.append(bg_select)


def set_character_bg(bg):
    bg_name = [k for k, v in possible_backgrounds.items() if v["desc"] == bg][0]
    player.background = bg_name
    speed = 0.7 if bg_name == "man" else 0.4
    voiceline_entry = RetroEntry(possible_backgrounds[bg_name]["catchphrase"], (150, 420), ask_food, accepts_input=False, wrap=WIDTH - 300, speed=speed, typewriter=False)
    all_widgets.append(voiceline_entry)
    possible_backgrounds[bg_name]["sound"].play()


@pause1
def ask_food():
    food_entry = RetroEntry("Which product would you like to buy?", (0, 0), show_foods_list, accepts_input=False)
    all_widgets.clear()
    all_widgets.append(food_entry)


def show_foods_list():
    player.show_money = True
    food_list = [f"{k} [${v['price']}]" for k, v in possible_foods.items()]
    food_select = RetroSelection(food_list, (0, 0), deduct_food_money, food_imgs, food_rects)
    all_widgets.append(food_select)


def deduct_food_money(food):
    food_name = food.split(" [")[0]
    player.money -= possible_foods[food_name]["price"]


class TicTacToe:
    def __init__(self):
        self.score = (0, 0)
        self.size = 300
        self.xo = WIDTH/2 - self.size/2
        self.yo = HEIGHT/2 - self.size/2
        self.pos = [1, 1]
        self.cross_x = self.size/3 + self.xo
        self.cross_y = self.size/3 + self.yo
        self.crossed_positions = []
        self.circled_positions = []
        self.lines = [
            [(0, self.size/3),     (self.size, self.size/3)],
            [(0, 2/3 * self.size), (self.size, 2/3 * self.size)],

            [(self.size/3, 0),     (self.size/3, self.size)],
            [(2/3 * self.size, 0), (2/3 * self.size, self.size)],
        ]

    def process_event(self, event):
        if event.key in (pygame.K_DOWN, pygame.K_s) and self.pos[1] != 2:
            self.pos[1] += 1
        if event.key in (pygame.K_UP, pygame.K_w) and self.pos[1] != 0:
            self.pos[1] -= 1
        if event.key in (pygame.K_RIGHT, pygame.K_d) and self.pos[0] != 2:
            self.pos[0] += 1
        if event.key in (pygame.K_LEFT, pygame.K_a) and self.pos[0] != 0:
            self.pos[0] -= 1
        if event.key in (pygame.K_RETURN, pygame.K_SPACE) and not self.pos in ([crossed_position[0] for crossed_position in self.crossed_positions], [circled_position[0] for circled_position in self.circled_positions]):
            self.crossed_positions.append((self.pos, self.cross_x, self.cross_y))

    def update(self):
        self.cross_x = self.pos[0] * self.size/3 + 1.07 * self.xo
        self.cross_y = self.pos[1] * self.size/3 + 1.14 * self.yo
        self.cross, self.cross_rect = writ('x', (self.cross_x, self.cross_y), 40)
        for cross in self.crossed_positions:
            writ('x', (cross[1], cross[2]), 40)
        REN.blit(self.cross, self.cross_rect)
        for line in self.lines:
            draw_line(REN, WHITE, (line[0][0] + self.xo, line[0][1] + self.yo), (line[1][0] + self.xo, line[1][1] + self.yo))


class RetroEntry:
    def __init__(self, final, pos, command, accepts_input=True, wrap=WIDTH, speed=0.6, typewriter=True):
        self.final = final + " "
        self.text = ""
        self.answer = ""
        self.index = 0
        self.last_index = self.index
        self.x, self.y = pos
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
                # type sound
                if int(self.index) > self.last_index and self.text[-1] != " " and self.typewriter:
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
    def __init__(self, texts, pos, command, images=None, image_rects=None):
        self.texts = texts
        self.x, self.y = pos
        self.xo = 40
        self.yo = 40
        self.images = images
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
        self.gt, self.gt_rect = writ(">", (self.rects[0].x - 30, self.rects[0].y))
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


bg_select = None
player = Character()
ttt = TicTacToe()

all_widgets = []
name_entry = RetroEntry("Hello traveler, what is your name?", (0, 0), command=ask_background)
all_widgets.append(name_entry)

# update_objects = [ttt]
update_objects = []


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

        player.update()

        REN.present()

    pygame.quit()
    sys.exit()
