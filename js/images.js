// ==================== 图片资源 ====================
const IMAGES = {};
const IMAGE_SRC = {
    playerUp: 'images/tank_player_up.png',
    playerDown: 'images/tank_player_down.png',
    playerLeft: 'images/tank_player_left.png',
    playerRight: 'images/tank_player_right.png',
    enemyUp: 'images/tank_basic_up.png',
    enemyDown: 'images/tank_basic_down.png',
    enemyLeft: 'images/tank_basic_left.png',
    enemyRight: 'images/tank_basic_right.png',
    bulletUp: 'images/bullet_up.png',
    bulletDown: 'images/bullet_down.png',
    bulletLeft: 'images/bullet_left.png',
    bulletRight: 'images/bullet_right.png',
    brick: 'images/tile_brick.png',
    steel: 'images/tile_steel.png',
    grass: 'images/tile_grass.png',
    water: 'images/tile_water.png',
    base: 'images/base.png',
    baseDestroyed: 'images/base_destroyed.png',
    explosion: 'images/explosion.png'
};

function loadImages() {
    const promises = [];
    for (const [key, src] of Object.entries(IMAGE_SRC)) {
        promises.push(new Promise((resolve) => {
            const img = new Image();
            img.onload = () => { IMAGES[key] = img; resolve(); };
            img.onerror = () => { resolve(); };
            img.src = src;
        }));
    }
    return Promise.all(promises);
}
