// ==================== 地图数据 ====================
// 13x13 地图，每格32x32像素（从26x26合并2x2块得到）
// 0=空地 1=砖墙 2=钢墙 3=草地 4=水
const STAGE_MAP = [
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
];

function initMap() {
    map = [];
    if (stage <= 1) {
        // 第一关使用固定地图
        for (let y = 0; y < MAP_H; y++) {
            map[y] = [];
            for (let x = 0; x < MAP_W; x++) {
                map[y][x] = STAGE_MAP[y][x];
            }
        }
    } else {
        // 第二关及以后使用随机地图
        generateRandomMap();
    }
}

// 随机生成地图（保证基地可达、出生点通畅）
function generateRandomMap() {
    map = [];
    for (let y = 0; y < MAP_H; y++) {
        map[y] = [];
        for (let x = 0; x < MAP_W; x++) {
            map[y][x] = TERRAIN.EMPTY;
        }
    }

    // 随机放置砖墙、钢墙、草地、水
    for (let y = 1; y < MAP_H - 2; y++) {
        for (let x = 0; x < MAP_W; x++) {
            const r = Math.random();
            if (r < 0.18) map[y][x] = TERRAIN.BRICK;
            else if (r < 0.24) map[y][x] = TERRAIN.STEEL;
            else if (r < 0.32) map[y][x] = TERRAIN.GRASS;
            else if (r < 0.38) map[y][x] = TERRAIN.WATER;
        }
    }

    // 确保基地周围有砖墙保护（基地在(6,12)）
    // 第11行：5,6,7列放砖墙
    map[11][5] = TERRAIN.BRICK;
    map[11][6] = TERRAIN.BRICK;
    map[11][7] = TERRAIN.BRICK;
    // 第12行：5和7列放砖墙（6是基地）
    map[12][5] = TERRAIN.BRICK;
    map[12][7] = TERRAIN.BRICK;
    // 第10行：5,6,7列放砖墙（加强保护）
    map[10][5] = TERRAIN.BRICK;
    map[10][6] = TERRAIN.BRICK;
    map[10][7] = TERRAIN.BRICK;

    // 确保敌人出生点（第0行）通畅
    for (let x = 0; x < MAP_W; x++) {
        map[0][x] = TERRAIN.EMPTY;
    }
    // 确保玩家出生点（第12行第4列）通畅
    map[12][4] = TERRAIN.EMPTY;
    // 确保基地位置为空（由baseAlive控制绘制）
    map[12][6] = TERRAIN.EMPTY;

    // 确保出生点周围有通道
    map[1][0] = TERRAIN.EMPTY;
    map[1][6] = TERRAIN.EMPTY;
    map[1][12] = TERRAIN.EMPTY;
    map[11][4] = TERRAIN.EMPTY;
    map[12][3] = TERRAIN.EMPTY;
}
