"""
Battle City - Game controller.

Contains the Game class that manages game state, entity updates,
collision detection, spawning, and rendering.
"""

import random
import pygame

from constants import (
    TILE_SIZE, GRID_W, GRID_H, GAME_W, GAME_H, HUD_W, WIDTH, HEIGHT,
    T_EMPTY, T_BRICK, T_STEEL, T_WATER, T_GRASS,
    UP, DOWN, LEFT, RIGHT, DIR_TANK_IMG,
    STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER, STATE_WIN,
    BLACK, WHITE, GRAY, LIGHT_GRAY,
    HUD_BG, HUD_BORDER, YELLOW, ORANGE, GREEN,
    TANK_SPEED, BULLET_SPEED,
    PLAYER_LIVES, PLAYER_SHOOT_COOLDOWN,
    MAX_ENEMIES_ON_SCREEN, TOTAL_ENEMIES,
    SPAWN_INTERVAL, SPAWN_PROTECTION,
)
from map import parse_level, cell_to_pixel, rect_for_center, bullet_rect
from entities import Bullet, Explosion, PlayerTank, EnemyTank


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.grid, self.enemy_spawn_points, self.player_spawn, self.base_cell = parse_level()
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
        self.base_rect = rect_for_center(*cell_to_pixel(*self.base_cell))
        self.menu_timer = 0
        self.state_timer = 0
        self.intro_delay = 0  # delay for "stage start" message
        self.shake_timer = 0
        # Pre-place a destroyed-base marker
        self._base_destroyed_pos = cell_to_pixel(*self.base_cell)

    @property
    def tanks(self):
        t = list(self.enemies)
        if self.player and self.player.alive:
            t.append(self.player)
        return t

    def start_game(self):
        self.grid, self.enemy_spawn_points, self.player_spawn, self.base_cell = parse_level()
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
        px, py = cell_to_pixel(*self.player_spawn)
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
        candidates = list(self.enemy_spawn_points)
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
        px, py = cell_to_pixel(*self.player_spawn)
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
        bx, by = cell_to_pixel(*self.base_cell)
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
