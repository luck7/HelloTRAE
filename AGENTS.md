# AGENTS.md

## 项目概述

本项目使用 Python 和 Pygame Zero 开发一款 FC 风格的坦克大战游戏，参考经典游戏《Battle City》。

核心玩法：

* 玩家控制坦克移动和射击。
* 敌方坦克会自动移动并攻击。
* 地图由砖墙、钢墙、森林、冰面、水域和基地组成。
* 子弹可以摧毁砖墙和坦克。
* 钢墙需要特殊条件或强化火力才能摧毁。
* 玩家基地被摧毁或玩家生命耗尽时游戏结束。
* 消灭所有敌方坦克后进入下一关。

## 技术要求

* Python 3.10+
* Pygame Zero
* 不使用 Pygame Zero 以外的第三方依赖，除非任务明确要求。
* 游戏必须通过以下命令启动：

```bash
pgzrun main.py

```

## 项目结构
```text
.
├── main.py                 # Pygame Zero 主入口
├── settings.py             # 游戏配置
├── constants.py            # 常量定义
├── game.py                 # 游戏状态和主流程
├── tank.py                 # 玩家坦克和敌方坦克
├── bullet.py               # 子弹逻辑
├── tilemap.py              # 地图加载和地图块处理
├── collision.py            # 碰撞检测
├── level.py                # 关卡数据和关卡管理
├── ui.py                   # 界面、分数和状态提示
├── effects.py              # 爆炸、出生保护等效果
├── levels/
│   ├── level01.py          # 第一关地图
│   └── level02.py          # 第二关地图
├── images/                 # 图片资源
├── sounds/                 # 音效资源
├── fonts/                  # 字体资源
├── tests/                  # 测试文件
├── requirements.txt
└── README.md
```

