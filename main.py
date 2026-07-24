import random
import pygame
from constants import *
from tank import Tank
from bullet import Bullet
from explosion import Explosion
import game_state as gs

WIDTH = SCREEN_W + 120
HEIGHT = SCREEN_H


def game_over(reason):
    gs.game_state = 'gameover'


def reset_game():
    gs.score = 0
    gs.lives = 3
    gs.stage = 1
    gs.gameover_delay = 0
    reset_stage()


def reset_stage():
    gs.init_map()
    gs.player = Tank(4 * TILE, 12 * TILE, DIR_UP, True)
    gs.enemies = []
    gs.bullets = []
    gs.explosions = []
    gs.spawned_enemies = 0
    gs.spawn_timer = 0
    gs.base_alive = True
    gs.total_enemies = 8 + gs.stage * 2


def stage_complete():
    gs.game_state = 'stageTransition'
    gs.stage += 1
    gs.stage_transition_timer = 120
    if gs.player:
        gs.player.stop_run_sound()
    pygame.mixer.stop()


def spawn_enemy():
    if gs.spawned_enemies >= gs.total_enemies:
        return
    spawn_points = [0, 6, 12]
    sx = spawn_points[random.randint(0, 2)] * TILE
    sy = 0
    occupied = False
    for e in gs.enemies:
        if e.alive and abs(e.x - sx) < TILE and abs(e.y - sy) < TILE:
            occupied = True
            break
    if not occupied:
        gs.enemies.append(Tank(sx, sy, DIR_DOWN, False))
        gs.spawned_enemies += 1


def update_enemies():
    for e in gs.enemies:
        if not e.alive:
            continue
        e.moving = True
        old_dir = e.dir

        if e.turn_cooldown <= 0:
            if random.random() < 0.008:
                opposite = (e.dir + 2) % 4
                choices = [d for d in [0, 1, 2, 3] if d != opposite]
                e.dir = choices[random.randint(0, len(choices) - 1)]

            if gs.player and gs.player.alive and random.random() < 0.06:
                dx = gs.player.x - e.x
                dy = gs.player.y - e.y
                opposite = (e.dir + 2) % 4
                new_dir = e.dir
                if abs(dx) > abs(dy):
                    new_dir = DIR_RIGHT if dx > 0 else DIR_LEFT
                else:
                    new_dir = DIR_DOWN if dy > 0 else DIR_UP
                if new_dir != opposite:
                    e.dir = new_dir

        if e.dir != old_dir:
            e.prev_dir = old_dir
            e.turn_cooldown = 60
            e.snap_to_grid()

        e.move()

        if e.x == e._lastX and e.y == e._lastY:
            if e.turn_cooldown <= 0:
                opposite = (e.dir + 2) % 4
                choices = [d for d in [0, 1, 2, 3] if d != e.dir and d != opposite]
                e.dir = choices[random.randint(0, len(choices) - 1)]
                e.turn_cooldown = 60
        e._lastX = e.x
        e._lastY = e.y

        if random.random() < 0.012:
            e.shoot()


def update():
    if gs.gameover_delay > 0:
        gs.gameover_delay -= 1
        if gs.player:
            gs.player.moving = False
        if gs.gameover_delay <= 0:
            game_over('Base destroyed!')
        return

    if gs.game_state == 'stageTransition':
        gs.stage_transition_timer -= 1
        if gs.stage_transition_timer <= 0:
            reset_stage()
            gs.game_state = 'playing'
        return

    if gs.game_state != 'playing' or gs.paused:
        return

    gs.spawn_timer += 1
    if gs.spawn_timer > 200:
        gs.spawn_timer = 0
        if sum(1 for e in gs.enemies if e.alive) < 3:
            spawn_enemy()

    if gs.player and gs.player.alive:
        old_dir = gs.player.dir
        gs.player.moving = False
        if keyboard.w or keyboard.up:
            gs.player.dir = DIR_UP
            gs.player.moving = True
        elif keyboard.s or keyboard.down:
            gs.player.dir = DIR_DOWN
            gs.player.moving = True
        elif keyboard.a or keyboard.left:
            gs.player.dir = DIR_LEFT
            gs.player.moving = True
        elif keyboard.d or keyboard.right:
            gs.player.dir = DIR_RIGHT
            gs.player.moving = True

        if gs.player.dir != old_dir:
            gs.player.prev_dir = old_dir
            gs.player.snap_to_grid()

        if gs.player.moving:
            gs.player.move()
        else:
            gs.player.slide_to_grid()
        gs.player.update()

    if keyboard.space and gs.player and gs.player.alive:
        gs.player.shoot()

    update_enemies()
    for e in gs.enemies:
        e.update()

    for b in gs.bullets:
        b.update()
    gs.check_bullet_bullet_collision()
    gs.bullets = [b for b in gs.bullets if b.alive]

    for ex in gs.explosions:
        ex.update()
    gs.explosions = [ex for ex in gs.explosions if ex.alive]

    gs.enemies = [e for e in gs.enemies if e.alive]

    if gs.spawned_enemies >= gs.total_enemies and len(gs.enemies) == 0:
        stage_complete()


def draw():
    screen.fill((0, 0, 0))
    screen.draw.filled_rect(Rect(SCREEN_W, 0, 120, SCREEN_H), (99, 99, 98))

    if gs.game_state == 'menu':
        screen.draw.filled_rect(Rect(0, 0, SCREEN_W, SCREEN_H), (0, 0, 0, 224))
        screen.draw.text('BATTLE CITY', center=(SCREEN_W/2, SCREEN_H/2 - 60), fontsize=36, color=(255, 204, 102))
        screen.draw.text('Classic FC Tank Battle Remake', center=(SCREEN_W/2, SCREEN_H/2 - 20), fontsize=12, color=(204, 204, 204))
        screen.draw.text('WASD Move | SPACE Shoot', center=(SCREEN_W/2, SCREEN_H/2 + 10), fontsize=12, color=(204, 204, 204))
        screen.draw.text('Protect your base, destroy all enemies', center=(SCREEN_W/2, SCREEN_H/2 + 35), fontsize=12, color=(204, 204, 204))
        screen.draw.text('Press SPACE to Start', center=(SCREEN_W/2, SCREEN_H/2 + 70), fontsize=14, color=(255, 204, 102))
        return

    for y in range(MAP_H):
        for x in range(MAP_W):
            tile = gs.map_data[y][x]
            tx, ty = x * TILE, y * TILE
            if tile == TERRAIN_BRICK:
                screen.blit('tile_brick', (tx, ty))
            elif tile == TERRAIN_STEEL:
                screen.blit('tile_steel', (tx, ty))
            elif tile == TERRAIN_WATER:
                screen.blit('tile_water', (tx, ty))

    if gs.base_alive:
        screen.blit('base', (BASE_COL * TILE, BASE_ROW * TILE))
    else:
        screen.blit('base_destroyed', (BASE_COL * TILE, BASE_ROW * TILE))

    for e in gs.enemies:
        e.draw(screen)
    if gs.player:
        gs.player.draw(screen)

    for b in gs.bullets:
        b.draw(screen)

    for ex in gs.explosions:
        ex.draw(screen)

    for y in range(MAP_H):
        for x in range(MAP_W):
            if gs.map_data[y][x] == TERRAIN_GRASS:
                screen.blit('tile_grass', (x * TILE, y * TILE))

    if gs.paused:
        screen.draw.filled_rect(Rect(0, 0, SCREEN_W, SCREEN_H), (0, 0, 0, 192))
        screen.draw.text('PAUSED', center=(SCREEN_W/2, SCREEN_H/2), fontsize=24, color='white')
        screen.draw.text('Press P to Continue', center=(SCREEN_W/2, SCREEN_H/2 + 24), fontsize=12, color='white')

    if gs.game_state == 'menu':
        screen.draw.filled_rect(Rect(0, 0, SCREEN_W, SCREEN_H), (0, 0, 0, 224))
        screen.draw.text('BATTLE CITY', center=(SCREEN_W/2, SCREEN_H/2 - 60), fontsize=36, color=(255, 204, 102))
        screen.draw.text('Classic FC Tank Battle Remake', center=(SCREEN_W/2, SCREEN_H/2 - 20), fontsize=12, color=(204, 204, 204))
        screen.draw.text('WASD Move | SPACE Shoot', center=(SCREEN_W/2, SCREEN_H/2 + 10), fontsize=12, color=(204, 204, 204))
        screen.draw.text('Protect your base, destroy all enemies', center=(SCREEN_W/2, SCREEN_H/2 + 35), fontsize=12, color=(204, 204, 204))
        screen.draw.text('Press SPACE to Start', center=(SCREEN_W/2, SCREEN_H/2 + 70), fontsize=14, color=(255, 204, 102))

    if gs.game_state == 'gameover':
        screen.draw.filled_rect(Rect(0, 0, SCREEN_W, SCREEN_H), (0, 0, 0, 224))
        screen.draw.text('GAME OVER', center=(SCREEN_W/2, SCREEN_H/2 - 40), fontsize=36, color=(204, 68, 68))
        screen.draw.text(f'Final Score: {gs.score}', center=(SCREEN_W/2, SCREEN_H/2 + 10), fontsize=16, color=(204, 204, 204))
        screen.draw.text('Press SPACE to Restart', center=(SCREEN_W/2, SCREEN_H/2 + 50), fontsize=14, color=(255, 204, 102))

    if gs.game_state == 'stageTransition':
        screen.draw.filled_rect(Rect(0, 0, SCREEN_W, SCREEN_H), (0, 0, 0, 224))
        screen.draw.text(f'STAGE {gs.stage}', center=(SCREEN_W/2, SCREEN_H/2), fontsize=36, color='white')
        screen.draw.text('Ready?', center=(SCREEN_W/2, SCREEN_H/2 + 30), fontsize=14, color=(204, 204, 204))

    draw_hud()


def draw_hud():
    screen.draw.text(f'Score: {gs.score}', (SCREEN_W + 10, 10), fontsize=12, color=(204, 204, 204))
    screen.draw.text(f'Stage: {gs.stage}', (SCREEN_W + 10, 30), fontsize=12, color=(204, 204, 204))
    screen.draw.text(f'Lives: {gs.lives}', (SCREEN_W + 10, 50), fontsize=12, color=(204, 204, 204))
    remaining = gs.total_enemies - gs.spawned_enemies + sum(1 for e in gs.enemies if e.alive)
    screen.draw.text(f'Enemies: {remaining}', (SCREEN_W + 10, 70), fontsize=12, color=(204, 204, 204))


def on_key_down(key):
    if key == keys.P and gs.game_state == 'playing':
        gs.paused = not gs.paused
    if key == keys.SPACE:
        if gs.game_state == 'menu':
            gs.game_state = 'playing'
            reset_game()
        elif gs.game_state == 'gameover':
            gs.game_state = 'playing'
            reset_game()
