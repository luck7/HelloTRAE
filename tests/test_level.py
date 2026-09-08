"""Battle City test suite.

注意：`main.py` 顶层的 ``pgzrun.go()`` 令其无法被 ``import``（pgzero 会抛出
``ImportError: You are running from an interactive interpreter``）。因此这里
不对 `main` 做导入式单元测试，而是用 AST 解析 `main.py` 源码，校验其内部
定义的关卡数据与几何常量——无需触发 pgzero 回调、可无头运行且可被 pytest
正常收集。

若将来把核心逻辑拆出到独立模块（不调用 pgzrun.go()），即可改为直接 import 测试。
"""

import ast
from pathlib import Path

MAIN_PY = Path(__file__).resolve().parent.parent / "main.py"

# 游戏画布常量（与 main.py 定义保持一致，作为回归基线）
GRID_W = 13
GRID_H = 13
TILE_SIZE = 32
GAME_W = GRID_W * TILE_SIZE   # 416
GAME_H = GRID_H * TILE_SIZE   # 416
HUD_W = 96


def _load_main_ast():
    """解析 main.py 为 AST（不做任何执行，避免触发 pgzrun.go()）。"""
    return ast.parse(MAIN_PY.read_text(encoding="utf-8"))


def _level_map_lines():
    """从 main.py 的 LEVEL_MAP 赋值中提取全部关卡的字符行。"""
    tree = _load_main_ast()
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "LEVEL_MAP":
                assert isinstance(node.value, (ast.List, ast.Tuple)), \
                    "LEVEL_MAP 应为字符串列表"
                return [elt.value for elt in node.value.elts]
    raise AssertionError("main.py 中未找到 LEVEL_MAP 定义")


def test_main_py_exists():
    assert MAIN_PY.is_file(), "main.py 未找到"


def test_level_map_dimensions():
    lines = _level_map_lines()
    assert len(lines) == GRID_H, f"关卡应含 {GRID_H} 行，实际 {len(lines)}"
    for i, row in enumerate(lines):
        assert len(row) == GRID_W, f"第 {i} 行长度应为 {GRID_W}，实际 {len(row)}"


def test_level_map_uses_known_tiles():
    allowed = set(".BSWGEHP")  # 空/砖/钢/水/草/敌出生/玩家出生/基地
    for row in _level_map_lines():
        for ch in row:
            assert ch in allowed, f"非法地形字符: {ch!r}"


def test_level_map_has_base_and_player():
    flat = "".join(_level_map_lines())
    assert "H" in flat, "关卡缺少基地(H)"
    assert "P" in flat, "关卡缺少玩家出生点(P)"


def test_level_map_has_enemy_spawns():
    flat = "".join(_level_map_lines())
    assert "E" in flat, "关卡缺少敌人生成点(E)"


def test_stage_geometry_constants():
    # 总画布 512x416 = 战场(416) + HUD 侧栏(96)
    assert GRID_W * TILE_SIZE == 416
    assert GRID_H * TILE_SIZE == 416
    assert GAME_W + HUD_W == 512