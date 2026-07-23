import random
import math
from pgzero.clock import schedule

TILE = 32
MAP_W = 13
MAP_H = 13
SCREEN_W = MAP_W * TILE
SCREEN_H = MAP_H * TILE
TANK_SIZE = 32
BULLET_SIZE = 16
GRID = 16

DIR_UP = 0
DIR_RIGHT = 1
DIR_DOWN = 2
DIR_LEFT = 3

TERRAIN_EMPTY = 0
TERRAIN_BRICK = 1
TERRAIN_STEEL = 2
TERRAIN_GRASS = 3
TERRAIN_WATER = 4

BASE_COL = 6
BASE_ROW = 12

STAGE_MAP = [
    [0,0,0,2,0,0,0,0,0,2,0,0,0],
    [0,1,0,2,0,1,1,1,0,2,0,1,0],
    [0,1,0,0,3,1,1,1,3,0,0,1,0],
    [0,1,0,0,3,0,0,0,3,0,0,1,0],
    [0,1,0,1,0,1,0,1,0,1,0,1,0],
    [0,3,0,1,0,1,0,1,0,1,0,3,0],
    [2,3,0,0,0,0,0,0,0,0,0,3,2],
    [0,3,0,1,0,1,0,1,0,1,0,3,0],
    [0,3,0,1,0,1,0,1,0,1,0,3,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,1,0,0,0,1,1,1,0,0,0,1,0],
    [0,0,0,0,0,1,1,1,0,0,0,0,0],
    [0,0,0,0,0,1,0,1,0,0,0,0,0]
]

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

class Tank:
    def __init__(self, x, y, dir, is_player=False):
        self.x = x
        self.y = y
        self.dir = dir
        self.is_player = is_player
        self.width = TANK_SIZE
        self.height = TANK_SIZE
        self.speed = 1
        self.moving = False
        self.alive = True
        self.shoot_cooldown = 0
        self.invincible = 180 if is_player else 0
        self.blink_timer = 0
        self._lastX = x
        self._lastY = y
        self.turn_cooldown = 0

    def get_image(self):
        prefix = 'tank_player' if self.is_player else 'tank_basic'
        dir_str = ['up', 'right', 'down', 'left'][self.dir]
        return f'{prefix}_{dir_str}'

    def update(self):
        if not self.alive:
            return
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.turn_cooldown > 0:
            self.turn_cooldown -= 1
        if self.invincible > 0:
            self.invincible -= 1
            self.blink_timer += 1

    def snap_to_grid(self):
        # 转向时只对齐垂直于移动方向的轴，避免斜向跳动
        if self.dir in (DIR_UP, DIR_DOWN):
            sx = round(self.x / GRID) * GRID
            if check_map_collision(sx, self.y, self.width, self.height) and \
               check_tank_collision(self, sx, self.y):
                self.x = sx
        else:
            sy = round(self.y / GRID) * GRID
            if check_map_collision(self.x, sy, self.width, self.height) and \
               check_tank_collision(self, self.x, sy):
                self.y = sy

    def slide_to_grid(self):
        # 只沿移动方向单轴滑动，始终向前（不后退），避免反向跳动
        if self.dir == DIR_UP:
            ty = (self.y // GRID) * GRID
            if self.y != ty:
                fy = max(self.y - self.speed, ty)
                if check_map_collision(self.x, fy, self.width, self.height) and \
                   check_tank_collision(self, self.x, fy):
                    self.y = fy
        elif self.dir == DIR_DOWN:
            ty = math.ceil(self.y / GRID) * GRID
            if self.y != ty:
                fy = min(self.y + self.speed, ty)
                if check_map_collision(self.x, fy, self.width, self.height) and \
                   check_tank_collision(self, self.x, fy):
                    self.y = fy
        elif self.dir == DIR_LEFT:
            tx = (self.x // GRID) * GRID
            if self.x != tx:
                fx = max(self.x - self.speed, tx)
                if check_map_collision(fx, self.y, self.width, self.height) and \
                   check_tank_collision(self, fx, self.y):
                    self.x = fx
        elif self.dir == DIR_RIGHT:
            tx = math.ceil(self.x / GRID) * GRID
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
        active = sum(1 for b in bullets if b.alive and b.owner == self)
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
        bullets.append(bullet)

    def draw(self):
        if not self.alive:
            return
        if self.invincible > 0 and self.blink_timer % 8 < 4:
            return
        img = self.get_image()
        screen.blit(img, (int(self.x), int(self.y)))

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
            explosions.append(Explosion(ex, ey, 'small'))
            return

        if check_bullet_map_collision(self):
            return

        check_bullet_tank_collision(self)

    def get_image(self):
        dir_str = ['up', 'right', 'down', 'left'][self.dir]
        return f'bullet_{dir_str}'

    def draw(self):
        if not self.alive:
            return
        img = self.get_image()
        screen.blit(img, (int(self.x), int(self.y)))

class Explosion:
    def __init__(self, x, y, size='normal'):
        self.x = x
        self.y = y
        self.size = size
        self.frame = 0
        self.max_frame = 8
        self.alive = True
        self.timer = 0

    def update(self):
        self.timer += 1
        if self.timer > 4:
            self.timer = 0
            self.frame += 1
            if self.frame >= self.max_frame:
                self.alive = False

    def draw(self):
        if not self.alive:
            return
        scale = 2 if self.size == 'big' else (0.6 if self.size == 'small' else 1)
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

def rect_overlap(x1, y1, w1, h1, x2, y2, w2, h2):
    return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2

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
                explosions.append(Explosion(cx * TILE, cy * TILE, 'small'))
                return True
            elif tile == TERRAIN_STEEL:
                bullet.alive = False
                explosions.append(Explosion(cx * TILE, cy * TILE, 'small'))
                return True

    if right >= BASE_COL and left <= BASE_COL and bottom >= BASE_ROW and top <= BASE_ROW:
        bullet.alive = False
        global base_alive, gameover_delay
        if base_alive:
            base_alive = False
            gameover_delay = 180
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
                explosions.append(Explosion(e.x, e.y, 'normal'))
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
                game_over('You were defeated!')
            else:
                schedule(respawn_player, 1.5)

def check_bullet_bullet_collision():
    player_bullets = [b for b in bullets if b.alive and b.is_player]
    enemy_bullets = [b for b in bullets if b.alive and not b.is_player]
    for pb in player_bullets:
        for eb in enemy_bullets:
            if rect_overlap(pb.x, pb.y, pb.width, pb.height, eb.x, eb.y, eb.width, eb.height):
                pb.alive = False
                eb.alive = False
                explosions.append(Explosion(
                    (pb.x + eb.x) / 2,
                    (pb.y + eb.y) / 2,
                    'small'
                ))

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
    if lives > 0:
        player = Tank(4 * TILE, 12 * TILE, DIR_UP, True)

def spawn_enemy():
    global spawned_enemies
    if spawned_enemies >= total_enemies:
        return
    spawn_points = [0, 6, 12]
    sx = spawn_points[random.randint(0, 2)] * TILE
    sy = 0
    occupied = False
    for e in enemies:
        if e.alive and abs(e.x - sx) < TILE and abs(e.y - sy) < TILE:
            occupied = True
            break
    if not occupied:
        enemies.append(Tank(sx, sy, DIR_DOWN, False))
        spawned_enemies += 1

def update_enemies():
    for e in enemies:
        if not e.alive:
            continue
        e.moving = True
        old_dir = e.dir

        if e.turn_cooldown <= 0:
            if random.random() < 0.008:
                opposite = (e.dir + 2) % 4
                choices = [d for d in [0, 1, 2, 3] if d != opposite]
                e.dir = choices[random.randint(0, len(choices) - 1)]

            if player and player.alive and random.random() < 0.06:
                dx = player.x - e.x
                dy = player.y - e.y
                opposite = (e.dir + 2) % 4
                new_dir = e.dir
                if abs(dx) > abs(dy):
                    new_dir = DIR_RIGHT if dx > 0 else DIR_LEFT
                else:
                    new_dir = DIR_DOWN if dy > 0 else DIR_UP
                if new_dir != opposite:
                    e.dir = new_dir

        # 转向时对齐垂直轴
        if e.dir != old_dir:
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
    global spawn_timer, game_state, stage_transition_timer, bullets, explosions, enemies, gameover_delay

    if gameover_delay > 0:
        gameover_delay -= 1
        if player:
            player.moving = False
        if gameover_delay <= 0:
            game_over('Base destroyed!')
        return

    if game_state == 'stageTransition':
        stage_transition_timer -= 1
        if stage_transition_timer <= 0:
            reset_stage()
            game_state = 'playing'
        return

    if game_state != 'playing' or paused:
        return

    spawn_timer += 1
    if spawn_timer > 200:
        spawn_timer = 0
        if sum(1 for e in enemies if e.alive) < 3:
            spawn_enemy()

    if player and player.alive:
        player.moving = False
        if keyboard.w or keyboard.up:
            player.dir = DIR_UP
            player.moving = True
        elif keyboard.s or keyboard.down:
            player.dir = DIR_DOWN
            player.moving = True
        elif keyboard.a or keyboard.left:
            player.dir = DIR_LEFT
            player.moving = True
        elif keyboard.d or keyboard.right:
            player.dir = DIR_RIGHT
            player.moving = True

        if player.moving:
            player.move()
        else:
            player.slide_to_grid()
        player.update()

    if keyboard.space and player and player.alive:
        player.shoot()

    update_enemies()
    for e in enemies:
        e.update()

    for b in bullets:
        b.update()
    check_bullet_bullet_collision()
    bullets = [b for b in bullets if b.alive]

    for ex in explosions:
        ex.update()
    explosions = [ex for ex in explosions if ex.alive]

    enemies = [e for e in enemies if e.alive]

    if spawned_enemies >= total_enemies and len(enemies) == 0:
        stage_complete()

def draw():
    screen.fill((0, 0, 0))
    # 右侧状态栏底色
    screen.draw.filled_rect(Rect(SCREEN_W, 0, 120, SCREEN_H), (99, 99, 98))

    if game_state == 'menu':
        screen.draw.filled_rect(Rect(0, 0, SCREEN_W, SCREEN_H), (0, 0, 0, 224))
        screen.draw.text('BATTLE CITY', center=(SCREEN_W/2, SCREEN_H/2 - 60), fontsize=36, color=(255, 204, 102))
        screen.draw.text('Classic FC Tank Battle Remake', center=(SCREEN_W/2, SCREEN_H/2 - 20), fontsize=12, color=(204, 204, 204))
        screen.draw.text('WASD Move | SPACE Shoot', center=(SCREEN_W/2, SCREEN_H/2 + 10), fontsize=12, color=(204, 204, 204))
        screen.draw.text('Protect your base, destroy all enemies', center=(SCREEN_W/2, SCREEN_H/2 + 35), fontsize=12, color=(204, 204, 204))
        screen.draw.text('Press SPACE to Start', center=(SCREEN_W/2, SCREEN_H/2 + 70), fontsize=14, color=(255, 204, 102))
        return

    for y in range(MAP_H):
        for x in range(MAP_W):
            tile = map_data[y][x]
            tx, ty = x * TILE, y * TILE
            if tile == TERRAIN_BRICK:
                screen.blit('tile_brick', (tx, ty))
            elif tile == TERRAIN_STEEL:
                screen.blit('tile_steel', (tx, ty))
            elif tile == TERRAIN_WATER:
                screen.blit('tile_water', (tx, ty))

    if base_alive:
        screen.blit('base', (BASE_COL * TILE, BASE_ROW * TILE))
    else:
        screen.blit('base_destroyed', (BASE_COL * TILE, BASE_ROW * TILE))

    for e in enemies:
        e.draw()
    if player:
        player.draw()

    for b in bullets:
        b.draw()

    for ex in explosions:
        ex.draw()

    for y in range(MAP_H):
        for x in range(MAP_W):
            if map_data[y][x] == TERRAIN_GRASS:
                screen.blit('tile_grass', (x * TILE, y * TILE))

    if paused:
        screen.draw.filled_rect(Rect(0, 0, SCREEN_W, SCREEN_H), (0, 0, 0, 192))
        screen.draw.text('PAUSED', center=(SCREEN_W/2, SCREEN_H/2), fontsize=24, color='white')
        screen.draw.text('Press P to Continue', center=(SCREEN_W/2, SCREEN_H/2 + 24), fontsize=12, color='white')

    if game_state == 'menu':
        screen.draw.filled_rect(Rect(0, 0, SCREEN_W, SCREEN_H), (0, 0, 0, 224))
        screen.draw.text('BATTLE CITY', center=(SCREEN_W/2, SCREEN_H/2 - 60), fontsize=36, color=(255, 204, 102))
        screen.draw.text('Classic FC Tank Battle Remake', center=(SCREEN_W/2, SCREEN_H/2 - 20), fontsize=12, color=(204, 204, 204))
        screen.draw.text('WASD Move | SPACE Shoot', center=(SCREEN_W/2, SCREEN_H/2 + 10), fontsize=12, color=(204, 204, 204))
        screen.draw.text('Protect your base, destroy all enemies', center=(SCREEN_W/2, SCREEN_H/2 + 35), fontsize=12, color=(204, 204, 204))
        screen.draw.text('Press SPACE to Start', center=(SCREEN_W/2, SCREEN_H/2 + 70), fontsize=14, color=(255, 204, 102))

    if game_state == 'gameover':
        screen.draw.filled_rect(Rect(0, 0, SCREEN_W, SCREEN_H), (0, 0, 0, 224))
        screen.draw.text('GAME OVER', center=(SCREEN_W/2, SCREEN_H/2 - 40), fontsize=36, color=(204, 68, 68))
        screen.draw.text(f'Final Score: {score}', center=(SCREEN_W/2, SCREEN_H/2 + 10), fontsize=16, color=(204, 204, 204))
        screen.draw.text('Press SPACE to Restart', center=(SCREEN_W/2, SCREEN_H/2 + 50), fontsize=14, color=(255, 204, 102))

    if game_state == 'stageTransition':
        screen.draw.filled_rect(Rect(0, 0, SCREEN_W, SCREEN_H), (0, 0, 0, 224))
        screen.draw.text(f'STAGE {stage}', center=(SCREEN_W/2, SCREEN_H/2), fontsize=36, color='white')
        screen.draw.text('Ready?', center=(SCREEN_W/2, SCREEN_H/2 + 30), fontsize=14, color='#ccc')

    draw_hud()

def draw_hud():
    screen.draw.text(f'Score: {score}', (SCREEN_W + 10, 10), fontsize=12, color=(204, 204, 204))
    screen.draw.text(f'Stage: {stage}', (SCREEN_W + 10, 30), fontsize=12, color=(204, 204, 204))
    screen.draw.text(f'Lives: {lives}', (SCREEN_W + 10, 50), fontsize=12, color=(204, 204, 204))
    remaining = total_enemies - spawned_enemies + sum(1 for e in enemies if e.alive)
    screen.draw.text(f'Enemies: {remaining}', (SCREEN_W + 10, 70), fontsize=12, color=(204, 204, 204))

def on_key_down(key):
    global paused, game_state
    if key == keys.P and game_state == 'playing':
        paused = not paused
    if key == keys.SPACE:
        if game_state == 'menu':
            game_state = 'playing'
            reset_game()
        elif game_state == 'gameover':
            game_state = 'playing'
            reset_game()

def game_over(reason):
    global game_state
    game_state = 'gameover'

def reset_game():
    global score, lives, stage, gameover_delay
    score = 0
    lives = 3
    stage = 1
    gameover_delay = 0
    reset_stage()

def reset_stage():
    global player, enemies, bullets, explosions, spawned_enemies, spawn_timer, base_alive, total_enemies
    init_map()
    player = Tank(4 * TILE, 12 * TILE, DIR_UP, True)
    enemies = []
    bullets = []
    explosions = []
    spawned_enemies = 0
    spawn_timer = 0
    base_alive = True
    total_enemies = 8 + stage * 2

def stage_complete():
    global game_state, stage, stage_transition_timer
    game_state = 'stageTransition'
    stage += 1
    stage_transition_timer = 120

WIDTH = SCREEN_W + 120
HEIGHT = SCREEN_H