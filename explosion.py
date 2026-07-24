from constants import *
from pgzero.builtins import sounds


class Explosion:
    def __init__(self, x, y, size='normal'):
        self.x = x
        self.y = y
        self.size = size
        self.frame = 0
        self.max_frame = 8
        self.alive = True
        self.timer = 0
        if size == 'big':
            sounds.boom.play()
        elif size == 'small':
            sounds.hit.play()
        elif size == 'destroy':
            sounds.destroy.play()

    def update(self):
        self.timer += 1
        if self.timer > 4:
            self.timer = 0
            self.frame += 1
            if self.frame >= self.max_frame:
                self.alive = False

    def draw(self, screen):
        if not self.alive:
            return
        scale = 3 if self.size == 'destroy' else (2 if self.size == 'big' else (0.6 if self.size == 'small' else 1))
        progress = self.frame / self.max_frame
        alpha = 1 - progress
        draw_size = TILE * scale
        if self.frame < 3:
            screen.draw.filled_circle(
                (self.x + TILE/2, self.y + TILE/2),
                (8 + self.frame * 4) * scale,
                (255, int(120 + self.frame * 15), 0)
            )
            screen.draw.circle(
                (self.x + TILE/2, self.y + TILE/2),
                (8 + self.frame * 4) * scale + 4,
                (255, 200, 0)
            )
        else:
            screen.draw.filled_circle(
                (self.x + TILE/2, self.y + TILE/2),
                (8 + self.frame * 4) * scale,
                (255, int(120 + self.frame * 15), 0)
            )
