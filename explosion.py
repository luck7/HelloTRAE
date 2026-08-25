from constants import *
from pgzero.builtins import sounds, images
import pygame


class Explosion:
    def __init__(self, x, y, size='normal', obj_size=TILE):
        self.x = x
        self.y = y
        self.size = size
        self.obj_size = obj_size
        self.frame = 0
        self.max_frame = 8
        self.alive = True
        self.timer = 0
        if size == 'big':
            sounds.enemy_explode.play()
        elif size == 'small':
            sounds.bullet_hit_wall.play()
        elif size == 'destroy':
            sounds.player_explode.play()
        elif size == 'brick':
            sounds.destory_wall.play()

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
        scale = 1 if self.size == 'destroy' else (1 if self.size == 'big' else (0.6 if self.size in ('small', 'brick') else 1))
        progress = self.frame / self.max_frame
        img = images.explosion
        draw_size = int(TANK_SIZE * scale * (0.5 + progress * 0.5))
        if draw_size < 4:
            return
        scaled = pygame.transform.scale(img, (draw_size, draw_size))
        scaled.set_alpha(int(255 * (1 - progress * 0.7)))
        cx = self.x + self.obj_size / 2
        cy = self.y + self.obj_size / 2
        ox = int(cx - draw_size / 2)
        oy = int(cy - draw_size / 2)
        screen.blit(scaled, (ox, oy))
