import random
from constants import *
from explosion import Explosion

map_data = []
player = None
enemies = []
bullets = []
explosions = []
score = 0
lives = 3
stage = 1
total_enemies = 20
spawned_enemies = 0
spawn_timer = 0
base_alive = True
game_state = 'menu'
paused = False
stage_transition_timer = 0
gameover_delay = 0


def rect_overlap(x1, y1, w1, h1, x2, y2, w2, h2):
    return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2


def check_map_collision(x, y, w, h):
    left = int(x // TILE)
    right = int((x + w - 1) // TILE)
    top = int(y // TILE)
    bottom = int((y + h - 1) // TILE)

    for ty in range(top, bottom + 1):
        for tx in range(left, right + 1):
            if ty < 0 or ty >= MAP_H or tx < 0 or tx >= MAP_W:
                return False
            tile = map_data[ty][tx]
            if tile == TERRAIN_BRICK or tile == TERRAIN_STEEL or tile == TERRAIN_WATER:
                return False

    base_x = BASE_COL * TILE
    base_y = BASE_ROW * TILE
    if x < base_x + TILE and x + w > base_x and y < base_y + TILE and y + h > base_y:
        return False
    return True


def check_tank_collision(self, nx, ny):
    sw, sh = self.width, self.height
    if player and player.alive and player != self:
        if rect_overlap(nx, ny, sw, sh, player.x, player.y, player.width, player.height):
            return False
    for e in enemies:
        if e.alive and e != self:
            if rect_overlap(nx, ny, sw, sh, e.x, e.y, e.width, e.height):
                return False
    return True


def check_bullet_map_collision(bullet):
    left = int(bullet.x // TILE)
    right = int((bullet.x + bullet.width - 1) // TILE)
    top = int(bullet.y // TILE)
    bottom = int((bullet.y + bullet.height - 1) // TILE)

    for cy in range(top, bottom + 1):
        for cx in range(left, right + 1):
            if cy < 0 or cy >= MAP_H or cx < 0 or cx >= MAP_W:
                bullet.alive = False
                ex = bullet.x + BULLET_SIZE // 2 - TILE // 2
                ey = bullet.y + BULLET_SIZE // 2 - TILE // 2
                explosions.append(Explosion(ex, ey, 'small'))
                return True
            tile = map_data[cy][cx]
            if tile == TERRAIN_BRICK:
                map_data[cy][cx] = TERRAIN_EMPTY
                bullet.alive = False
                explosions.append(Explosion(cx * TILE, cy * TILE, 'brick'))
                return True
            elif tile == TERRAIN_STEEL:
                bullet.alive = False
                if bullet.dir == DIR_UP:
                    explosions.append(Explosion(cx * TILE, cy * TILE + TILE // 2, 'small'))
                elif bullet.dir == DIR_DOWN:
                    explosions.append(Explosion(cx * TILE, cy * TILE - TILE // 2, 'small'))
                elif bullet.dir == DIR_LEFT:
                    explosions.append(Explosion(cx * TILE + TILE // 2, cy * TILE, 'small'))
                else:  # DIR_RIGHT
                    explosions.append(Explosion(cx * TILE - TILE // 2, cy * TILE, 'small'))
                return True

    if right >= BASE_COL and left <= BASE_COL and bottom >= BASE_ROW and top <= BASE_ROW:
        bullet.alive = False
        global base_alive, gameover_delay
        if base_alive:
            base_alive = False
            gameover_delay = 180
            explosions.append(Explosion(BASE_COL * TILE, BASE_ROW * TILE, 'destroy'))
        return True

    return False


def check_bullet_tank_collision(bullet):
    global score, lives
    if bullet.is_player:
        for e in enemies:
            if e.alive and rect_overlap(bullet.x, bullet.y, bullet.width, bullet.height,
                                        e.x, e.y, e.width, e.height):
                bullet.alive = False
                e.alive = False
                explosions.append(Explosion(e.x, e.y, 'big'))
                score += 100
                return
    else:
        if player and player.alive and player.invincible <= 0 and \
           rect_overlap(bullet.x, bullet.y, bullet.width, bullet.height,
                        player.x, player.y, player.width, player.height):
            bullet.alive = False
            player.alive = False
            explosions.append(Explosion(player.x, player.y, 'big'))
            lives -= 1
            if lives <= 0:
                import main
                main.game_over('You were defeated!')
            else:
                from pgzero.clock import schedule
                schedule(respawn_player, 1.5)


def check_bullet_bullet_collision():
    player_bullets = [b for b in bullets if b.alive and b.is_player]
    enemy_bullets = [b for b in bullets if b.alive and not b.is_player]
    for pb in player_bullets:
        for eb in enemy_bullets:
            if rect_overlap(pb.x, pb.y, pb.width, pb.height, eb.x, eb.y, eb.width, eb.height):
                pb.alive = False
                eb.alive = False
                explosions.append(Explosion(pb.x, pb.y, 'small', BULLET_SIZE))
                explosions.append(Explosion(eb.x, eb.y, 'small', BULLET_SIZE))


def init_map():
    global map_data
    map_data = []
    if stage <= 1:
        for y in range(MAP_H):
            map_data.append(STAGE_MAP[y].copy())
    else:
        generate_random_map()


def generate_random_map():
    global map_data
    map_data = []
    for y in range(MAP_H):
        map_data.append([TERRAIN_EMPTY] * MAP_W)

    for y in range(1, MAP_H - 2):
        for x in range(MAP_W):
            r = random.random()
            if r < 0.18:
                map_data[y][x] = TERRAIN_BRICK
            elif r < 0.24:
                map_data[y][x] = TERRAIN_STEEL
            elif r < 0.32:
                map_data[y][x] = TERRAIN_GRASS
            elif r < 0.38:
                map_data[y][x] = TERRAIN_WATER

    map_data[11][5] = TERRAIN_BRICK
    map_data[11][6] = TERRAIN_BRICK
    map_data[11][7] = TERRAIN_BRICK
    map_data[12][5] = TERRAIN_BRICK
    map_data[12][7] = TERRAIN_BRICK
    map_data[10][5] = TERRAIN_BRICK
    map_data[10][6] = TERRAIN_BRICK
    map_data[10][7] = TERRAIN_BRICK

    for x in range(MAP_W):
        map_data[0][x] = TERRAIN_EMPTY
    map_data[12][4] = TERRAIN_EMPTY
    map_data[12][6] = TERRAIN_EMPTY

    map_data[1][0] = TERRAIN_EMPTY
    map_data[1][6] = TERRAIN_EMPTY
    map_data[1][12] = TERRAIN_EMPTY
    map_data[11][4] = TERRAIN_EMPTY
    map_data[12][3] = TERRAIN_EMPTY


def respawn_player():
    global player
    from tank import Tank
    if lives > 0:
        player = Tank(4 * TILE, 12 * TILE, DIR_UP, True)
