from constants import *
from game_state import check_bullet_map_collision, check_bullet_tank_collision
import game_state
from explosion import Explosion


class Bullet:
    def __init__(self, x, y, dir, is_player):
        self.x = x
        self.y = y
        self.dir = dir
        self.is_player = is_player
        self.speed = 4
        self.width = BULLET_SIZE
        self.height = BULLET_SIZE
        self.alive = True
        self.owner = None

    def update(self):
        if not self.alive:
            return
        if self.dir == DIR_UP:
            self.y -= self.speed
        elif self.dir == DIR_RIGHT:
            self.x += self.speed
        elif self.dir == DIR_DOWN:
            self.y += self.speed
        elif self.dir == DIR_LEFT:
            self.x -= self.speed

        if self.x < 0 or self.y < 0 or self.x + self.width > SCREEN_W or self.y + self.height > SCREEN_H:
            self.alive = False
            ex = self.x + BULLET_SIZE // 2 - TILE // 2
            ey = self.y + BULLET_SIZE // 2 - TILE // 2
            game_state.explosions.append(Explosion(ex, ey, 'small'))
            return

        if check_bullet_map_collision(self):
            return

        check_bullet_tank_collision(self)

    def get_image(self):
        dir_str = ['up', 'right', 'down', 'left'][self.dir]
        return f'bullet_{dir_str}'

    def draw(self, screen):
        if not self.alive:
            return
        img = self.get_image()
        screen.blit(img, (int(self.x), int(self.y)))
