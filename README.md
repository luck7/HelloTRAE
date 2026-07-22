# Battle City - FC坦克大战复刻版

经典FC坦克大战游戏的HTML5 Canvas复刻版。

## 游戏特性

- ✅ 玩家坦克操控（WASD移动，空格射击）
- ✅ 敌方坦克AI（追踪玩家、自动射击）
- ✅ 砖墙、钢墙、草地、水地形
- ✅ 基地保护机制
- ✅ 子弹与坦克碰撞检测
- ✅ 子弹碰撞抵消（玩家子弹与敌方子弹互相抵消）
- ✅ 爆炸效果与音效
- ✅ 坦克停止时对齐半格（16px）网格
- ✅ 每坦克最多同时发射两个子弹
- ✅ 多关卡系统（第二关开始随机地图）
- ✅ 计分系统与生命系统

## 操作说明

| 按键 | 功能 |
|------|------|
| W / ↑ | 向上移动 |
| S / ↓ | 向下移动 |
| A / ← | 向左移动 |
| D / → | 向右移动 |
| 空格 | 射击 |
| P | 暂停/继续 |

## 游戏规则

1. 保护基地不被敌人摧毁
2. 消灭所有敌方坦克过关
3. 玩家有3条生命
4. 第二关及以后地图随机生成

## 运行方式

### 本地开发服务器

```bash
# 使用Python启动HTTP服务器
python -m http.server 8080

# 或使用Node.js
npx serve -p 8080
```

然后在浏览器中访问 `http://localhost:8080`

### 直接打开

直接在浏览器中打开 `index.html` 文件即可运行。

## 技术栈

- HTML5 Canvas
- JavaScript (ES6+)
- Web Audio API（音效）
- CSS3

## 文件结构

```
BattleCity/
├── index.html          # 游戏主文件（包含所有逻辑）
├── .gitignore          # Git忽略文件
├── README.md           # 项目说明
└── images/             # 游戏资源图片
    ├── tank_player_*.png    # 玩家坦克（四个方向）
    ├── tank_basic_*.png     # 敌方坦克（四个方向）
    ├── bullet_*.png         # 子弹（四个方向）
    ├── tile_brick.png       # 砖墙
    ├── tile_steel.png       # 钢墙
    ├── tile_grass.png       # 草地
    ├── tile_water.png       # 水
    ├── base.png             # 基地
    ├── base_destroyed.png   # 被摧毁的基地
    └── explosion.png        # 爆炸效果
```

## 游戏截图

游戏界面包含：
- 416x416像素的游戏画布
- 侧边栏显示玩家生命、分数、敌军数量和关卡

## 开发说明

游戏所有逻辑都在 `index.html` 单个文件中，无需构建工具即可运行。

### 关键常量

- `TILE = 32` - 地图格子大小（像素）
- `MAP_W = 13` - 地图宽度（格子数）
- `MAP_H = 13` - 地图高度（格子数）
- `TANK_SIZE = 32` - 坦克大小
- `BULLET_SIZE = 16` - 子弹大小
- `GRID = 16` - 半格对齐单位

### 游戏状态

- `menu` - 菜单界面
- `playing` - 游戏进行中
- `stageTransition` - 关卡切换
- `gameover` - 游戏结束

## 历史版本

- 初始版本：实现基本游戏功能
- v2.0：修复碰撞检测，优化地图布局
- v3.0：添加音效系统、子弹碰撞抵消、坦克对齐

## 许可证

MIT License