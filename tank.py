import math
import os
import pygame
from constants import *
from game_state import check_map_collision, check_tank_collision
import game_state
from bullet import Bullet

_run_sound = None

def _get_run_sound():
    global _run_sound
    if _run_sound is None:
        _run_sound = pygame.mixer.Sound(os.path.join('sounds', 'player_move_sound.wav'))
    return _run_sound


class Tank:
    def __init__(self, x, y, dir, is_player=False):
        self.x = x
        self.y = y
        self.dir = dir
        self.is_player = is_player
        self.width = TANK_SIZE
        self.height = TANK_SIZE
        self.speed = 2
        self.moving = False
        self.alive = True
        self.shoot_cooldown = 0
        self.invincible = 180 if is_player else 0
        self.blink_timer = 0
        self._lastX = x
        self._lastY = y
        self.turn_cooldown = 0
        self.prev_dir = dir
        self.run_channel = None

    def get_image(self):
        prefix = 'tank_player' if self.is_player else 'tank_basic'
        dir_str = ['up', 'right', 'down', 'left'][self.dir]
        return f'{prefix}_{dir_str}'

    def update(self):
        if not self.alive:
            self.stop_run_sound()
            return
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.turn_cooldown > 0:
            self.turn_cooldown -= 1
        if self.invincible > 0:
            self.invincible -= 1
            self.blink_timer += 1
        if self.is_player:
            if self.moving:
                self.start_run_sound()
            else:
                self.stop_run_sound()

    def start_run_sound(self):
        if self.run_channel is None or not self.run_channel.get_busy():
            self.run_channel = _get_run_sound().play(-1)

    def stop_run_sound(self):
        if self.run_channel is not None:
            self.run_channel.stop()
            self.run_channel = None

    def snap_to_grid(self):
        if self.dir in (DIR_UP, DIR_DOWN):
            if self.prev_dir == DIR_RIGHT:
                sx = math.ceil(self.x / HALF_TILE) * HALF_TILE
            elif self.prev_dir == DIR_LEFT:
                sx = (self.x // HALF_TILE) * HALF_TILE
            else:
                sx = round(self.x / HALF_TILE) * HALF_TILE
            if sx != self.x and check_map_collision(sx, self.y, self.width, self.height) and \
               check_tank_collision(self, sx, self.y):
                self.x = sx
        else:
            if self.prev_dir == DIR_DOWN:
                sy = math.ceil(self.y / HALF_TILE) * HALF_TILE
            elif self.prev_dir == DIR_UP:
                sy = (self.y // HALF_TILE) * HALF_TILE
            else:
                sy = round(self.y / HALF_TILE) * HALF_TILE
            if sy != self.y and check_map_collision(self.x, sy, self.width, self.height) and \
               check_tank_collision(self, self.x, sy):
                self.y = sy

    def slide_to_grid(self):
        if self.dir == DIR_UP:
            ty = (self.y // HALF_TILE) * HALF_TILE
            if self.y != ty:
                fy = max(self.y - self.speed, ty)
                if check_map_collision(self.x, fy, self.width, self.height) and \
                   check_tank_collision(self, self.x, fy):
                    self.y = fy
        elif self.dir == DIR_DOWN:
            ty = math.ceil(self.y / HALF_TILE) * HALF_TILE
            if self.y != ty:
                fy = min(self.y + self.speed, ty)
                if check_map_collision(self.x, fy, self.width, self.height) and \
                   check_tank_collision(self, self.x, fy):
                    self.y = fy
        elif self.dir == DIR_LEFT:
            tx = (self.x // HALF_TILE) * HALF_TILE
            if self.x != tx:
                fx = max(self.x - self.speed, tx)
                if check_map_collision(fx, self.y, self.width, self.height) and \
                   check_tank_collision(self, fx, self.y):
                    self.x = fx
        elif self.dir == DIR_RIGHT:
            tx = math.ceil(self.x / HALF_TILE) * HALF_TILE
            if self.x != tx:
                fx = min(self.x + self.speed, tx)
                if check_map_collision(fx, self.y, self.width, self.height) and \
                   check_tank_collision(self, fx, self.y):
                    self.x = fx

    def move(self):
        if not self.alive or not self.moving:
            return
        nx, ny = self.x, self.y
        step = self.speed
        if self.dir == DIR_UP:
            ny -= step
        elif self.dir == DIR_RIGHT:
            nx += step
        elif self.dir == DIR_DOWN:
            ny += step
        elif self.dir == DIR_LEFT:
            nx -= step

        if nx < 0 or ny < 0 or nx + self.width > SCREEN_W or ny + self.height > SCREEN_H:
            return

        if not check_map_collision(nx, ny, self.width, self.height):
            return

        if not check_tank_collision(self, nx, ny):
            return

        self.x = nx
        self.y = ny

    def shoot(self):
        if not self.alive or self.shoot_cooldown > 0:
            return
        active = sum(1 for b in game_state.bullets if b.alive and b.owner == self)
        if active >= 2:
            return
        self.shoot_cooldown = 15 if self.is_player else 45
        bx, by = 0, 0
        half_bullet = BULLET_SIZE // 2
        half_tank = TANK_SIZE // 2
        if self.dir == DIR_UP:
            bx = self.x + half_tank - half_bullet
            by = self.y - BULLET_SIZE
        elif self.dir == DIR_RIGHT:
            bx = self.x + self.width
            by = self.y + half_tank - half_bullet
        elif self.dir == DIR_DOWN:
            bx = self.x + half_tank - half_bullet
            by = self.y + self.height
        elif self.dir == DIR_LEFT:
            bx = self.x - BULLET_SIZE
            by = self.y + half_tank - half_bullet
        bullet = Bullet(bx, by, self.dir, self.is_player)
        bullet.owner = self
        game_state.bullets.append(bullet)

    def draw(self, screen):
        if not self.alive:
            return
        if self.invincible > 0 and self.blink_timer % 8 < 4:
            return
        img = self.get_image()
        screen.blit(img, (int(self.x), int(self.y)))
