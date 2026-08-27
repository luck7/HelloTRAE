"""
Battle City - Game entities.

Contains Bullet, Explosion, Tank (base), PlayerTank, and EnemyTank classes.
All entity classes receive the Game instance as a parameter for accessing
shared state (grid, bullets, tanks) -- they never import the game module.
"""

import random

from constants import (
    TILE_SIZE, GRID_W, GRID_H, GAME_W, GAME_H,
    T_BRICK, T_STEEL, T_WATER,
    UP, DOWN, LEFT, RIGHT,
    DIR_VEC, DIR_BULLET_IMG, DIR_TANK_IMG,
    TANK_SPEED, BULLET_SPEED,
    PLAYER_LIVES, PLAYER_SHOOT_COOLDOWN,
    ENEMY_SHOOT_COOLDOWN_MIN, ENEMY_SHOOT_COOLDOWN_MAX,
    ENEMY_DIR_CHANGE_MIN, ENEMY_DIR_CHANGE_MAX,
)
from map import rect_for_center, snap_axis


# ----------------------------------------------------------------------
# Bullet
# ----------------------------------------------------------------------
class Bullet(Actor):
    def __init__(self, x, y, direction, owner):
        super().__init__(DIR_BULLET_IMG[direction], (x, y))
        self.direction = direction
        self.owner = owner  # 'player' or 'enemy'
        self.alive = True
        dx, dy = DIR_VEC[direction]
        self.vx = dx * BULLET_SPEED
        self.vy = dy * BULLET_SPEED

    def update(self):
        self.x += self.vx
        self.y += self.vy
        # Out of bounds
        if (self.x < 0 or self.x > GAME_W or
                self.y < 0 or self.y > GAME_H):
            self.alive = False


# ----------------------------------------------------------------------
# Explosion
# ----------------------------------------------------------------------
class Explosion(Actor):
    def __init__(self, x, y):
        super().__init__('explosion', (x, y))
        self.timer = 18  # frames

    def update(self):
        self.timer -= 1


# ----------------------------------------------------------------------
# Tank base class
# ----------------------------------------------------------------------
class Tank(Actor):
    tank_type = 'player'

    def __init__(self, kind, x, y, direction=UP):
        super().__init__(DIR_TANK_IMG[kind][direction], (x, y))
        self.kind = kind
        self.direction = direction
        self.alive = True
        self.shoot_cooldown = 0
        self.protection = 0  # frames of invulnerability
        self.moving = False

    def set_direction(self, new_dir):
        if new_dir == self.direction:
            return
        # Snap perpendicular axis to grid for clean corridor navigation
        if new_dir in (UP, DOWN):
            self.x = snap_axis(self.x)
        else:
            self.y = snap_axis(self.y)
        self.direction = new_dir
        self.image = DIR_TANK_IMG[self.kind][new_dir]

    def try_move(self, dx, dy, game):
        new_x = self.x + dx
        new_y = self.y + dy
        new_rect = rect_for_center(new_x, new_y, TILE_SIZE - 2)
        # Bounds check (stay inside playfield)
        if (new_rect.left < 0 or new_rect.right > GAME_W or
                new_rect.top < 0 or new_rect.bottom > GAME_H):
            return False
        # Wall collisions
        for c, r in self._cells_under(new_rect):
            if 0 <= c < GRID_W and 0 <= r < GRID_H:
                t = game.grid[r][c]
                if t in (T_BRICK, T_STEEL, T_WATER):
                    return False
        # Base collision (cannot drive over base)
        if new_rect.colliderect(game.base_rect):
            return False
        # Tank-tank collisions
        for tank in game.tanks:
            if tank is self or not tank.alive:
                continue
            if new_rect.colliderect(rect_for_center(tank.x, tank.y, TILE_SIZE - 2)):
                return False
        self.x = new_x
        self.y = new_y
        return True

    def _cells_under(self, rect):
        """Return list of cells overlapping the given rect."""
        cells = set()
        c0 = max(0, rect.left // TILE_SIZE)
        c1 = min(GRID_W - 1, (rect.right - 1) // TILE_SIZE)
        r0 = max(0, rect.top // TILE_SIZE)
        r1 = min(GRID_H - 1, (rect.bottom - 1) // TILE_SIZE)
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                cells.add((c, r))
        return cells

    def shoot(self, game):
        if self.shoot_cooldown > 0:
            return
        # Player can only have one bullet on screen at a time
        if self.kind == 'player':
            for b in game.bullets:
                if b.owner == 'player' and b.alive:
                    return
        else:
            for b in game.bullets:
                if b.owner == 'enemy' and b.alive and b._shooter is self:
                    return
        dx, dy = DIR_VEC[self.direction]
        bx = self.x + dx * (TILE_SIZE // 2)
        by = self.y + dy * (TILE_SIZE // 2)
        b = Bullet(bx, by, self.direction, 'player' if self.kind == 'player' else 'enemy')
        b._shooter = self
        game.bullets.append(b)
        self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN if self.kind == 'player' \
            else random.randint(ENEMY_SHOOT_COOLDOWN_MIN, ENEMY_SHOOT_COOLDOWN_MAX)
        if self.kind == 'player':
            try:
                sounds.fire.play()
            except Exception:
                pass


# ----------------------------------------------------------------------
# Player tank
# ----------------------------------------------------------------------
class PlayerTank(Tank):
    def __init__(self, x, y):
        super().__init__('player', x, y, UP)
        self.lives = PLAYER_LIVES

    def update(self, game):
        if not self.alive:
            return
        self.shoot_cooldown = max(0, self.shoot_cooldown - 1)
        self.protection = max(0, self.protection - 1)
        self.moving = False
        # Movement input (priority: last pressed wins)
        if keyboard.left or keyboard.a:
            self.set_direction(LEFT)
            self.moving = self.try_move(-TANK_SPEED, 0, game)
        elif keyboard.right or keyboard.d:
            self.set_direction(RIGHT)
            self.moving = self.try_move(TANK_SPEED, 0, game)
        elif keyboard.up or keyboard.w:
            self.set_direction(UP)
            self.moving = self.try_move(0, -TANK_SPEED, game)
        elif keyboard.down or keyboard.s:
            self.set_direction(DOWN)
            self.moving = self.try_move(0, TANK_SPEED, game)
        if keyboard.space:
            self.shoot(game)
        # Animation flicker while moving handled by draw()


# ----------------------------------------------------------------------
# Enemy tank
# ----------------------------------------------------------------------
class EnemyTank(Tank):
    def __init__(self, x, y):
        super().__init__('enemy', x, y, DOWN)
        self.dir_timer = random.randint(ENEMY_DIR_CHANGE_MIN, ENEMY_DIR_CHANGE_MAX)
        self.shoot_cooldown = random.randint(ENEMY_SHOOT_COOLDOWN_MIN, ENEMY_SHOOT_COOLDOWN_MAX)
        self.protection = 30
        self.move_sound_timer = 0

    def update(self, game):
        if not self.alive:
            return
        self.shoot_cooldown = max(0, self.shoot_cooldown - 1)
        self.protection = max(0, self.protection - 1)
        self.dir_timer -= 1

        if self.dir_timer <= 0:
            self._pick_direction(game)
            self.dir_timer = random.randint(ENEMY_DIR_CHANGE_MIN, ENEMY_DIR_CHANGE_MAX)

        dx, dy = DIR_VEC[self.direction]
        moved = self.try_move(dx * TANK_SPEED, dy * TANK_SPEED, game)
        if not moved:
            # Try to find another direction
            self._pick_direction(game)
        if self.shoot_cooldown == 0:
            self.shoot(game)

    def _pick_direction(self, game):
        # Bias toward the base / player for some aggression
        choices = [UP, DOWN, LEFT, RIGHT]
        random.shuffle(choices)
        # Prefer direction that doesn't immediately collide
        for d in choices:
            dx, dy = DIR_VEC[d]
            test_rect = rect_for_center(self.x + dx * TANK_SPEED, self.y + dy * TANK_SPEED, TILE_SIZE - 2)
            if (0 <= test_rect.left and test_rect.right <= GAME_W and
                    0 <= test_rect.top and test_rect.bottom <= GAME_H):
                blocked = False
                for c, r in self._cells_under(test_rect):
                    if 0 <= c < GRID_W and 0 <= r < GRID_H:
                        t = game.grid[r][c]
                        if t in (T_BRICK, T_STEEL, T_WATER):
                            blocked = True
                            break
                if not blocked:
                    self.set_direction(d)
                    return
        self.set_direction(random.choice([UP, DOWN, LEFT, RIGHT]))
