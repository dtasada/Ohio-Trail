from .settings import *

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
        self.cross, self.cross_rect = write('x', (self.cross_x, self.cross_y), 40)
        for cross in self.crossed_positions:
            write('x', (cross[1], cross[2]), 40)
        REN.blit(self.cross, self.cross_rect)
        for line in self.lines:
            draw_line(REN, WHITE, (line[0][0] + self.xo, line[0][1] + self.yo), (line[1][0] + self.xo, line[1][1] + self.yo))
