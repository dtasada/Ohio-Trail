from settings import *
from character import *

pygame.init()
WIDTH, HEIGHT = 1200, 600
WIN = Window(size=(WIDTH, HEIGHT), title="Ohio Trail")
REN = Renderer(WIN)
clock = pygame.time.Clock()
font = pygame.font.Font(os.path.join("assets", "oregon-bound", "oregon-bound.ttf"), 18)
player = Character()
ticks = pygame.time.get_ticks


class TicTacToe:
    def __init__(self):
        self.score = (0, 0)
        self.size = 300
        self.xo = WIDTH/2 - self.size/2
        self.yo = HEIGHT/2 - self.size/2
        self.cross_x = self.size/3 + self.xo
        self.cross_y = self.size/3 + self.yo
        self.lines = [
            [(0, self.size/3),     (self.size, self.size/3)],
            [(0, 2/3 * self.size), (self.size, 2/3 * self.size)],

            [(self.size/3, 0),     (self.size/3, self.size)],
            [(2/3 * self.size, 0), (2/3 * self.size, self.size)],
        ]

        self.cross_img = font.render('x', True, WHITE)
        self.cross_image = Texture.from_surface(REN, self.cross_img)
        self.cross_rect = self.cross_img.get_rect(topleft=(self.cross_x, self.cross_y))

    def update(self):
        for line in self.lines:
            draw_line(REN, WHITE, (line[0][0] + self.xo, line[0][1] + self.yo), (line[1][0] + self.xo, line[1][1] + self.yo))
        writ('x', (self.cross_x, self.cross_y))

ttt = TicTacToe()

class RetroEntry:
    def __init__(self, final, pos, command, accepts_input=True):
        self.final = final + " "
        self.text = ""
        self.answer = ""
        self.index = 0
        self.x, self.y = pos
        self.flickering = False
        self.has_underscore = False
        self.last_flicker = ticks()
        self.command = command
        self.active = True
        self.accepts_input = accepts_input

    def draw(self):
        if int(self.index) >= 1:
            REN.blit(self.image, self.rect)

    def process_event(self, event):
        if self.accepts_input and self.active:
            if self.flickering:
                #
                name = pygame.key.name(event.key)
                self.text = self.text.removesuffix("_")
                if name == "return":
                    self.command(self.answer)
                    self.active = False
                elif name == "backspace":
                    self.text = self.text[:-1]
                    self.answer = self.answer[:-1]
                #
                elif name == "space":
                    self.text += " "
                    self.answer += " "
                elif len(name) > 1:
                    pass
                else:
                    self.text += name
                    self.answer += name
                self.update_tex(self.text)

    def update(self):
        if self.active:
            # update the text
            if not self.flickering:
                self.index += 0.6
                if int(self.index) >= 1:
                    self.update_tex(self.final[:int(self.index)])
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
        img = font.render(text, True, WHITE)
        self.image = Texture.from_surface(REN, img)
        self.rect = img.get_rect(topleft=(self.x, self.y))


class RetroSelection:
    def __init__(self, texts, pos, command):
        self.texts = texts
        self.x, self.y = pos
        self.xo = 40
        self.yo = 40
        imgs = [font.render(text, True, WHITE) for text in texts]
        self.rects = [img.get_rect(topleft=(self.x + self.xo, 50 + self.y + y * self.yo)) for y, img in enumerate(imgs)]
        self.texs = [Texture.from_surface(REN, img) for img in imgs]
        self.selected = 0
        self.gt, self.gt_rect = writ(">", (self.rects[0].x - 30, self.rects[1].y))
        self.active = True
        self.command = command

    def draw(self):
        for tex, rect in zip(self.texs, self.rects):
            REN.blit(tex, rect)
        REN.blit(self.gt, self.gt_rect)

    def process_event(self, event):
        if self.active:
            if event.key in (pygame.K_s, pygame.K_DOWN):
                if self.gt_rect.y == self.rects[-1].y:
                    self.gt_rect.y = self.rects[0].y
                else:
                    self.gt_rect.y += self.yo
            elif event.key in (pygame.K_w, pygame.K_UP):
                if self.gt_rect.y == self.rects[0].y:
                    self.gt_rect.y = self.rects[-1].y
                else:
                    self.gt_rect.y -= self.yo
            elif event.key == pygame.K_RETURN:
                for i, rect in enumerate(self.rects):
                    if self.gt_rect.y == rect.y:
                        text = self.texts[i]
                        self.command(text)
                        self.active = False
                        break

    def update(self):
        self.draw()


all_entries = []
name_entry = RetroEntry("Hello traveler, what is your name?", (0, 0), command=ask_background)
all_entries.append(name_entry)

def main():
    running = __name__ == "__main__"
    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                for entry in all_entries:
                    entry.process_event(event)

        fill_rect(REN, (0, 0, 0, 255), (0, 0, WIDTH, HEIGHT))

        for entry in all_entries:
            entry.update()

        ttt.update()
        REN.present()

    pygame.quit()
    sys.exit()


main()
