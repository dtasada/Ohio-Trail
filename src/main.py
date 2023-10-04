from settings import *
from character import *


WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)

pygame.init()
WIDTH, HEIGHT = 1200, 600
WIN = Window(size=(WIDTH, HEIGHT), title="Ohio Trail")
REN = Renderer(WIN)
clock = pygame.time.Clock()
font = pygame.font.Font(os.path.join("assets", "oregon-bound", "oregon-bound.ttf"), 18)
player = Character()
ticks = pygame.time.get_ticks


class TicTacToe:
    # def __init__(self):

    def update(self):
        draw_line(REN, (255, 255, 255, 255), (100, 100), (400, 400))

ttt = TicTacToe()

class RetroEntry:
    def __init__(self, final):
        self.final = final + " "
        self.text = ""
        self.answer = ""
        self.index = 0
        self.x, self.y = (0, 0)
        self.flickering = False
        self.has_underscore = False
        self.last_flicker = ticks()

    def draw(self):
        if int(self.index) >= 1:
            REN.blit(self.image, self.rect)

    def process_event(self, event):
        if self.flickering:
            #
            name = pygame.key.name(event.key)
            self.text = self.text.removesuffix("_")
            if name == "return":
                player.setup(self.answer)
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
        # update the text
        if not self.flickering:
            self.index += 0.6
            if int(self.index) >= 1:
                self.update_tex(self.final[:int(self.index)])
            # if finished, start flickering the underscore (_)
            if self.index >= len(self.final):
                self.flickering = True
                self.last_flicker = ticks()
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


rentry = RetroEntry("Hello traveler, what is your name?")

def main():
    running = __name__ == "__main__"
    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                rentry.process_event(event)

        fill_rect(REN, (0, 0, 0, 255), (0, 0, WIDTH, HEIGHT))

        rentry.update()

        ttt.update()
        REN.present()

    pygame.quit()
    sys.exit()


main()
