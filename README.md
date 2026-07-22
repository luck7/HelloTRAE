# Battle City - FC坦克大战复刻版

经典FC坦克大战游戏的Pygame Zero复刻版。

## 游戏特性

- ✅ 玩家坦克操控（WASD移动，空格射击）
- ✅ 敌方坦克AI（追踪玩家、自动射击）
- ✅ 砖墙、钢墙、草地、水地形
- ✅ 基地保护机制
- ✅ 子弹与坦克碰撞检测
- ✅ 子弹碰撞抵消（玩家子弹与敌方子弹互相抵消）
- ✅ 爆炸效果
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
| 空格 | 射击 / 开始游戏 |
| P | 暂停/继续 |

## 游戏规则

1. 保护基地不被敌人摧毁
2. 消灭所有敌方坦克过关
3. 玩家有3条生命
4. 第二关及以后地图随机生成

## 运行方式

### 开发与运行

```bash
# 创建虚拟环境
python -m virtualenv .venv --no-download --no-seed

# 激活虚拟环境（Windows）
.venv\Scripts\activate

# 安装依赖
pip install pgzero

# 运行游戏
pgzrun main.py
```

### 使用pytest运行测试

```bash
# 安装测试依赖
pip install pytest

# 运行测试
pytest
```

## 技术栈

- Python 3.10+
- Pygame Zero 1.2+
- Pygame 2.0+
- NumPy

## 文件结构

```
BattleCity/
├── main.py              # 游戏主文件（包含所有逻辑）
├── .gitignore          # Git忽略文件
├── README.md           # 项目说明
├── .venv/              # 虚拟环境（自动生成）
└── images/             # 游戏资源图片
    ├── tank_player_*.png    # 玩家坦克（四个方向）
    ├── tank_basic_*.png     # 敌方坦克（四个方向）
    ├── bullet_*.png         # 子弹（四个方向）
    ├── tile_brick.png       # 砖墙
    ├── tile_steel.png       # 钢墙
    ├── tile_grass.png       # 草地
    ├── tile_water.png       # 水
    ├── base.png             # 基地
    └── base_destroyed.png   # 被摧毁的基地
```

## 游戏截图

游戏界面包含：
- 416x416像素的游戏画布
- 侧边栏显示玩家生命、分数、敌军数量和关卡

## 开发说明

游戏所有逻辑都在 `main.py` 文件中，使用Pygame Zero框架开发。

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

- 初始版本：HTML5 Canvas实现
- v2.0：迁移到Pygame Zero框架

## 许可证

MIT License