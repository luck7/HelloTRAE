"""
Battle City - Tank Battle Game
Built with Pygame Zero.

Controls:
  Arrow Keys / WASD : Move tank
  Space             : Fire
  P                 : Pause / Resume
  Enter             : Start / Restart
  Esc               : Back to menu
"""

import pgzrun
import random
import pygame
from pygame import Rect

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
TILE_SIZE = 32
GRID_W = 13
GRID_H = 13
GAME_W = GRID_W * TILE_SIZE   # 416
GAME_H = GRID_H * TILE_SIZE   # 416
HUD_W = 96
WIDTH = GAME_W + HUD_W   # 512
HEIGHT = GAME_H          # 416
FPS = 60

# Tile types
T_EMPTY = 0
T_BRICK = 1
T_STEEL = 2
T_WATER = 3
T_GRASS = 4

# Directions
UP, DOWN, LEFT, RIGHT = 'up', 'down', 'left', 'right'
DIR_VEC = {
    UP: (0, -1),
    DOWN: (0, 1),
    LEFT: (-1, 0),
    RIGHT: (1, 0),
}
DIR_BULLET_IMG = {
    UP: 'bullet_up',
    DOWN: 'bullet_down',
    LEFT: 'bullet_left',
    RIGHT: 'bullet_right',
}
DIR_TANK_IMG = {
    'player': {
        UP: 'tank_player_up',
        DOWN: 'tank_player_down',
        LEFT: 'tank_player_left',
        RIGHT: 'tank_player_right',
    },
    'enemy': {
        UP: 'tank_basic_up',
        DOWN: 'tank_basic_down',
        LEFT: 'tank_basic_left',
        RIGHT: 'tank_basic_right',
    },
}

# Game states
STATE_MENU = 'menu'
STATE_PLAYING = 'playing'
STATE_PAUSED = 'paused'
STATE_GAME_OVER = 'game_over'
STATE_WIN = 'win'

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (60, 60, 60)
GRAY = (110, 110, 110)
LIGHT_GRAY = (180, 180, 180)
HUD_BG = (24, 24, 24)
HUD_BORDER = (90, 90, 90)
RED = (210, 60, 60)
YELLOW = (230, 200, 60)
GREEN = (70, 200, 70)
ORANGE = (220, 130, 40)
BROWN = (140, 90, 50)

# Tuning
TANK_SPEED = 2
BULLET_SPEED = 4
PLAYER_LIVES = 3
MAX_ENEMIES_ON_SCREEN = 4
TOTAL_ENEMIES = 20
PLAYER_SHOOT_COOLDOWN = 18      # frames
ENEMY_SHOOT_COOLDOWN_MIN = 50
ENEMY_SHOOT_COOLDOWN_MAX = 150
ENEMY_DIR_CHANGE_MIN = 40
ENEMY_DIR_CHANGE_MAX = 180
SPAWN_INTERVAL = 180             # frames between enemy spawns
SPAWN_PROTECTION = 120           # frames of invulnerability after spawn
ENEMY_SPAWN_POINTS = []          # filled from map
PLAYER_SPAWN = (0, 0)            # filled from map
BASE_CELL = (0, 0)               # filled from map

# ----------------------------------------------------------------------
# Level Map
#   .  empty       B  brick        S  steel
#   W  water       G  grass        H  base (eagle)
#   E  enemy spawn P  player spawn
# ----------------------------------------------------------------------
LEVEL_MAP = [
    "E.....E.....E",
    ".............",
    "..BBBBBBBBB..",
    "..B.......B..",
    "..B.SSSSS.B..",
    "..B...G...B..",
    "..BBBBBBBBB..",
    ".............",
    ".WW...G...WW.",
    ".WW.......WW.",
    ".....BBB.....",
    ".....BHB.....",
    "......P......",
]


def parse_level():
    """Parse LEVEL_MAP into a tile grid and locate spawn / base cells."""
    global ENEMY_SPAWN_POINTS, PLAYER_SPAWN, BASE_CELL
    grid = [[T_EMPTY for _ in range(GRID_W)] for _ in range(GRID_H)]
    enemy_spawns = []
    player_spawn = (GRID_W // 2, GRID_H - 1)
    base_cell = (GRID_W // 2, GRID_H - 2)
    for r, row in enumerate(LEVEL_MAP):
        for c, ch in enumerate(row):
            if ch == 'B':
                grid[r][c] = T_BRICK
            elif ch == 'S':
                grid[r][c] = T_STEEL
            elif ch == 'W':
                grid[r][c] = T_WATER
            elif ch == 'G':
                grid[r][c] = T_GRASS
            elif ch == 'E':
                enemy_spawns.append((c, r))
            elif ch == 'P':
                player_spawn = (c, r)
            elif ch == 'H':
                base_cell = (c, r)
    ENEMY_SPAWN_POINTS = enemy_spawns
    PLAYER_SPAWN = player_spawn
    BASE_CELL = base_cell
    return grid


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def cell_to_pixel(col, row):
    """Convert grid cell to pixel center for a 32x32 actor."""
    return col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2


def pixel_to_cell(x, y):
    """Convert pixel center to grid cell."""
    return int((x - TILE_SIZE // 2) // TILE_SIZE), int((y - TILE_SIZE // 2) // TILE_SIZE)


def snap_axis(value):
    """Snap a pixel center to the nearest tile center on its axis."""
    return round((value - TILE_SIZE // 2) / TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2


def rect_for_center(x, y, size=TILE_SIZE):
    """Build a Rect for an actor of given size centered at (x, y)."""
    half = size // 2
    return Rect(x - half, y - half, size, size)


BULLET_SIZE = 16  # bullet sprites are 16x16


def bullet_rect(b):
    """Build a pygame.Rect for a 16x16 bullet centered at (b.x, b.y).

    pgzero's Actor does not expose ``.rect`` directly, so we construct one
    from the position. Used for collision tests against pygame.Rects.
    """
    half = BULLET_SIZE // 2
    return Rect(int(b.x) - half, int(b.y) - half, BULLET_SIZE, BULLET_SIZE)


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


# ----------------------------------------------------------------------
# Game controller
# ----------------------------------------------------------------------
class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.grid = parse_level()
        self.state = STATE_MENU
        self.player = None
        self.enemies = []
        self.bullets = []
        self.explosions = []
        self.score = 0
        self.high_score = getattr(self, 'high_score', 0)
        self.enemies_remaining = TOTAL_ENEMIES
        self.spawn_timer = 0
        self.base_alive = True
        self.base_rect = rect_for_center(*cell_to_pixel(*BASE_CELL))
        self.menu_timer = 0
        self.state_timer = 0
        self.intro_delay = 0  # delay for "stage start" message
        self.shake_timer = 0
        # Pre-place a destroyed-base marker
        self._base_destroyed_pos = cell_to_pixel(*BASE_CELL)

    @property
    def tanks(self):
        t = list(self.enemies)
        if self.player and self.player.alive:
            t.append(self.player)
        return t

    def start_game(self):
        self.grid = parse_level()
        self.bullets = []
        self.explosions = []
        self.enemies = []
        self.score = 0
        self.enemies_remaining = TOTAL_ENEMIES
        self.spawn_timer = 60
        self.base_alive = True
        self.state = STATE_PLAYING
        self.state_timer = 0
        self.intro_delay = 90  # show "STAGE START" briefly
        px, py = cell_to_pixel(*PLAYER_SPAWN)
        self.player = PlayerTank(px, py)
        self.player.protection = SPAWN_PROTECTION
        # Initial enemy spawn
        self._spawn_enemy()
        self._spawn_enemy()
        # Start music
        try:
            pygame.mixer.music.load('music/game_start.mp3')
            pygame.mixer.music.play()
        except Exception:
            pass

    # ---- spawning ----
    def _spawn_enemy(self):
        if self.enemies_remaining <= 0:
            return
        if len(self.enemies) >= MAX_ENEMIES_ON_SCREEN:
            return
        # Choose a spawn point that isn't blocked by another tank
        candidates = list(ENEMY_SPAWN_POINTS)
        random.shuffle(candidates)
        for (c, r) in candidates:
            x, y = cell_to_pixel(c, r)
            spawn_rect = rect_for_center(x, y, TILE_SIZE)
            blocked = False
            for t in self.tanks:
                if spawn_rect.colliderect(rect_for_center(t.x, t.y, TILE_SIZE)):
                    blocked = True
                    break
            if not blocked:
                self.enemies.append(EnemyTank(x, y))
                self.enemies_remaining -= 1
                try:
                    sounds.power_up_spawn.play()
                except Exception:
                    pass
                return

    # ---- main update ----
    def update(self):
        if self.state == STATE_PLAYING:
            self._update_playing()
        elif self.state == STATE_MENU:
            self.menu_timer += 1
        else:
            self.state_timer += 1

    def _update_playing(self):
        self.state_timer += 1
        if self.intro_delay > 0:
            self.intro_delay -= 1
            # Allow minimal updates during intro
            return

        # Update player
        if self.player:
            self.player.update(self)
            if not self.player.alive:
                if self.player.lives > 0:
                    self._respawn_player()
                else:
                    self._end_game(STATE_GAME_OVER)

        # Update enemies
        for e in self.enemies:
            e.update(self)

        # Spawn enemies periodically
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            self._spawn_enemy()
            self.spawn_timer = SPAWN_INTERVAL

        # Update bullets
        for b in self.bullets:
            self._update_bullet(b)
        self.bullets = [b for b in self.bullets if b.alive]

        # Update explosions
        for ex in self.explosions:
            ex.update()
        self.explosions = [e for e in self.explosions if e.timer > 0]

        # Remove dead enemies
        self.enemies = [e for e in self.enemies if e.alive]

        # Win condition
        if self.enemies_remaining == 0 and not self.enemies:
            self._end_game(STATE_WIN)

        if self.shake_timer > 0:
            self.shake_timer -= 1

    def _update_bullet(self, b):
        # Move step-by-step to catch thin walls
        steps = BULLET_SPEED
        step_x = b.vx / steps if steps else 0
        step_y = b.vy / steps if steps else 0
        for _ in range(int(steps)):
            if not b.alive:
                return
            b.x += step_x
            b.y += step_y
            if b.x < 0 or b.x > GAME_W or b.y < 0 or b.y > GAME_H:
                self._spawn_explosion(b.x, b.y, small=True)
                b.alive = False
                return
            # Wall collision
            col = int(b.x // TILE_SIZE)
            row = int(b.y // TILE_SIZE)
            if 0 <= col < GRID_W and 0 <= row < GRID_H:
                t = self.grid[row][col]
                if t == T_BRICK:
                    self.grid[row][col] = T_EMPTY
                    self._spawn_explosion(b.x, b.y, small=True)
                    try:
                        sounds.destroy_wall.play()
                    except Exception:
                        pass
                    b.alive = False
                    return
                elif t == T_STEEL:
                    self._spawn_explosion(b.x, b.y, small=True)
                    try:
                        sounds.bullet_hit_wall.play()
                    except Exception:
                        pass
                    b.alive = False
                    return
            # Base collision
            if self.base_alive and bullet_rect(b).colliderect(self.base_rect):
                self.base_alive = False
                self._spawn_explosion(*self._base_destroyed_pos, big=True)
                self._spawn_explosion(*self._base_destroyed_pos, big=True)
                try:
                    sounds.player_explode.play()
                except Exception:
                    pass
                b.alive = False
                self.shake_timer = 40
                self._end_game(STATE_GAME_OVER)
                return
            # Tank collisions
            for tank in self.tanks:
                if not tank.alive:
                    continue
                if bullet_rect(b).colliderect(rect_for_center(tank.x, tank.y, TILE_SIZE - 4)):
                    # Friendly fire skip
                    if b.owner == 'player' and tank.kind == 'player':
                        continue
                    if b.owner == 'enemy' and tank.kind == 'enemy':
                        continue
                    if tank.protection > 0:
                        # Bounced off a protected tank
                        b.alive = False
                        return
                    tank.alive = False
                    self._spawn_explosion(tank.x, tank.y, big=True)
                    try:
                        if tank.kind == 'player':
                            sounds.player_explode.play()
                        else:
                            sounds.enemy_explode.play()
                    except Exception:
                        pass
                    if tank.kind == 'enemy' and b.owner == 'player':
                        self.score += 100
                        if self.score > self.high_score:
                            self.high_score = self.score
                    b.alive = False
                    return
            # Bullet vs bullet
            for other in self.bullets:
                if other is b or not other.alive:
                    continue
                if bullet_rect(b).colliderect(bullet_rect(other)):
                    b.alive = False
                    other.alive = False
                    return

    # ---- helpers ----
    def _spawn_explosion(self, x, y, small=False, big=False):
        self.explosions.append(Explosion(x, y))

    def _respawn_player(self):
        self.player.lives -= 1
        if self.player.lives <= 0:
            self.player = None
            self._end_game(STATE_GAME_OVER)
            return
        px, py = cell_to_pixel(*PLAYER_SPAWN)
        self.player.x, self.player.y = px, py
        self.player.direction = UP
        self.player.image = DIR_TANK_IMG['player'][UP]
        self.player.alive = True
        self.player.protection = SPAWN_PROTECTION
        self.player.shoot_cooldown = PLAYER_SHOOT_COOLDOWN
        try:
            sounds.consume_extra_life.play()
        except Exception:
            pass

    def _end_game(self, state):
        if self.state == state:
            return
        self.state = state
        self.state_timer = 0
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    # ---- drawing ----
    def draw(self):
        screen.fill(BLACK)
        if self.state == STATE_MENU:
            self._draw_menu()
        elif self.state in (STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER, STATE_WIN):
            self._draw_world()
            self._draw_hud()
            if self.state == STATE_PAUSED:
                self._draw_overlay('PAUSED', 'Press P to resume')
            elif self.state == STATE_GAME_OVER:
                self._draw_overlay('GAME OVER', 'Press ENTER to restart')
            elif self.state == STATE_WIN:
                self._draw_overlay('VICTORY!', 'Press ENTER to play again')
            elif self.state == STATE_PLAYING and self.intro_delay > 0:
                self._draw_overlay('STAGE 1', 'Get Ready!')

    def _draw_world(self):
        # Subtle battlefield background
        screen.surface.fill((10, 10, 10), (0, 0, GAME_W, GAME_H))
        # Draw tiles (grass drawn last so tanks appear under it)
        grass_cells = []
        for r in range(GRID_H):
            for c in range(GRID_W):
                t = self.grid[r][c]
                x, y = cell_to_pixel(c, r)
                if t == T_BRICK:
                    screen.blit('tile_brick', (x - TILE_SIZE // 2, y - TILE_SIZE // 2))
                elif t == T_STEEL:
                    screen.blit('tile_steel', (x - TILE_SIZE // 2, y - TILE_SIZE // 2))
                elif t == T_WATER:
                    screen.blit('tile_water', (x - TILE_SIZE // 2, y - TILE_SIZE // 2))
                elif t == T_GRASS:
                    grass_cells.append((x, y))
        # Base
        bx, by = cell_to_pixel(*BASE_CELL)
        if self.base_alive:
            screen.blit('base', (bx - TILE_SIZE // 2, by - TILE_SIZE // 2))
        else:
            screen.blit('base_destroyed', (bx - TILE_SIZE // 2, by - TILE_SIZE // 2))
        # Tanks
        for tank in self.tanks:
            if not tank.alive:
                continue
            if tank.protection > 0 and (tank.protection // 4) % 2 == 0:
                # Flicker during protection
                continue
            tank.draw()
        # Bullets
        for b in self.bullets:
            if b.alive:
                b.draw()
        # Explosions
        for ex in self.explosions:
            ex.draw()
        # Grass last (covers tanks)
        for (x, y) in grass_cells:
            screen.blit('tile_grass', (x - TILE_SIZE // 2, y - TILE_SIZE // 2))

    def _draw_hud(self):
        hud_x = GAME_W
        screen.surface.fill(HUD_BG, (hud_x, 0, HUD_W, HEIGHT))
        pygame.draw.rect(screen.surface, HUD_BORDER,
                         (hud_x, 0, HUD_W, HEIGHT), 2)
        cx = hud_x + HUD_W // 2

        # Score
        self._hud_label('SCORE', cx, 18)
        self._hud_value(str(self.score).zfill(4), cx, 36, YELLOW)
        # High score
        self._hud_label('HI-SCORE', cx, 70)
        self._hud_value(str(self.high_score).zfill(4), cx, 88, ORANGE)

        # Enemies remaining
        self._hud_label('ENEMIES', cx, 130)
        remaining = self.enemies_remaining + len(self.enemies)
        # Draw small tank icons (max 20, in a 2-col grid)
        col_x_left = hud_x + 12
        col_x_right = hud_x + HUD_W - 12 - 12
        for i in range(min(remaining, 20)):
            col = i % 2
            row = i // 2
            ix = col_x_left if col == 0 else col_x_right
            iy = 150 + row * 14
            screen.blit('tank_basic_down', (ix, iy))

        # Lives (player tank icon + count)
        lives_y = HEIGHT - 70
        self._hud_label('LIVES', cx, lives_y)
        if self.player:
            screen.blit('tank_player_up', (col_x_left, lives_y + 18))
            self._hud_value('x{}'.format(self.player.lives),
                            col_x_right + 12, lives_y + 34, GREEN)

        # State hint at bottom
        if self.state == STATE_PLAYING:
            self._hud_label('P : PAUSE', cx, HEIGHT - 18)

    def _hud_label(self, text, cx, y, color=LIGHT_GRAY):
        screen.draw.text(text, centerx=cx, top=y,
                         fontsize=12, color=color)
        pygame.draw.line(screen.surface, HUD_BORDER,
                         (cx - 28, y + 16), (cx + 28, y + 16), 1)

    def _hud_value(self, text, cx, y, color=YELLOW):
        screen.draw.text(text, centerx=cx, top=y,
                         fontsize=18, color=color)

    def _draw_menu(self):
        # Title art (scaled and cached)
        if not hasattr(self, '_title_surf'):
            try:
                src = pygame.image.load('images/title_screen.png').convert_alpha()
                w, h = src.get_size()
                new_w = 320
                new_h = int(h * new_w / w)
                self._title_surf = pygame.transform.smoothscale(src, (new_w, new_h))
            except Exception:
                self._title_surf = None
        if getattr(self, '_title_surf', None) is not None:
            rect = self._title_surf.get_rect(midtop=(WIDTH // 2, 12))
            screen.surface.blit(self._title_surf, rect)
        screen.draw.text('TANK BATTLE', centerx=WIDTH // 2, top=190,
                         fontsize=42, color=YELLOW, owidth=2, ocolor=BLACK)
        screen.draw.text('A Pygame Zero Battle City Clone',
                         centerx=WIDTH // 2, top=240, fontsize=14, color=LIGHT_GRAY)
        # Blinking start prompt
        if (self.menu_timer // 30) % 2 == 0:
            screen.draw.text('PRESS ENTER TO START',
                             centerx=WIDTH // 2, top=295,
                             fontsize=22, color=WHITE)
        # Controls
        screen.draw.text('ARROWS / WASD  -  MOVE',
                         centerx=WIDTH // 2, top=335, fontsize=13, color=GRAY)
        screen.draw.text('SPACE  -  FIRE',
                         centerx=WIDTH // 2, top=355, fontsize=13, color=GRAY)
        screen.draw.text('P  -  PAUSE     ESC  -  MENU',
                         centerx=WIDTH // 2, top=375, fontsize=13, color=GRAY)

    def _draw_overlay(self, title, subtitle):
        # Dim background
        overlay = pygame.Surface((GAME_W, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.surface.blit(overlay, (0, 0))
        screen.draw.text(title, centerx=GAME_W // 2,
                         centery=HEIGHT // 2 - 20,
                         fontsize=44, color=YELLOW,
                         owidth=2, ocolor=BLACK)
        if subtitle:
            screen.draw.text(subtitle, centerx=GAME_W // 2,
                             top=HEIGHT // 2 + 20,
                             fontsize=18, color=WHITE)


# ----------------------------------------------------------------------
# Global game instance
# ----------------------------------------------------------------------
game = Game()


# ----------------------------------------------------------------------
# Pygame Zero hooks
# ----------------------------------------------------------------------
def update():
    game.update()


def draw():
    game.draw()


def on_key_down(key):
    if game.state == STATE_MENU:
        if key == keys.RETURN:
            game.start_game()
        return
    if game.state == STATE_PLAYING:
        if key == keys.P:
            game.state = STATE_PAUSED
            game.state_timer = 0
        elif key == keys.ESCAPE:
            game.state = STATE_MENU
            game.menu_timer = 0
        return
    if game.state == STATE_PAUSED:
        if key == keys.P:
            game.state = STATE_PLAYING
        elif key == keys.ESCAPE:
            game.state = STATE_MENU
            game.menu_timer = 0
        return
    if game.state in (STATE_GAME_OVER, STATE_WIN):
        if key == keys.RETURN:
            game.start_game()
        elif key == keys.ESCAPE:
            game.reset()
            game.menu_timer = 0
        return


pgzrun.go()
