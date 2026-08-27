"""
Pytest configuration and shared fixtures for Battle City tests.

Mock pgzero runtime environment so game modules can be imported
without starting the actual game window.
"""
import sys
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Mock pgzrun BEFORE importing any game module
# ---------------------------------------------------------------------------
mock_pgzrun = MagicMock()
mock_pgzrun.go = MagicMock()
sys.modules.setdefault('pgzrun', mock_pgzrun)

# ---------------------------------------------------------------------------
# Mock pgzero built-in globals (sounds, images, keyboard, keys, screen)
# These are normally injected by pgzero's custom module loader.
# ---------------------------------------------------------------------------
mock_sounds = MagicMock()
mock_images = MagicMock()
mock_keyboard = MagicMock()
mock_keys = MagicMock()
mock_screen = MagicMock()


# ---------------------------------------------------------------------------
# Mock pgzero Actor class (used by battle_city.py)
# ---------------------------------------------------------------------------
class MockActor:
    """Minimal stand-in for pgzero's Actor that stores position and image."""
    def __init__(self, image='', pos=(0, 0), **kwargs):
        self.image = image
        self.x = pos[0] if pos else 0
        self.y = pos[1] if pos else 0
        self.alive = True

    def draw(self):
        pass


# Inject Actor into builtins so battle_city.py can find it
import builtins
builtins.Actor = MockActor


def _inject_pgzero_globals(module):
    """Inject pgzero magic globals into an already-imported module."""
    module.sounds = mock_sounds
    module.images = mock_images
    module.keyboard = mock_keyboard
    module.keys = mock_keys
    module.screen = mock_screen


# ---------------------------------------------------------------------------
# Pytest fixtures
# ---------------------------------------------------------------------------
import pytest
import main
from main import (
    MAP_W, MAP_H, TERRAIN_EMPTY, TILE,
    map_data, player, enemies, bullets, explosions,
    score, lives, base_alive, game_state,
    spawned_enemies, total_enemies, gameover_delay, stage,
)

# Inject pgzero globals into the imported main module
_inject_pgzero_globals(main)

# Import battle_city and inject pgzero globals
import battle_city as bc
_inject_pgzero_globals(bc)


@pytest.fixture(autouse=True)
def reset_main_state():
    """Reset main.py global state before each test and restore after."""
    # Save original state
    saved = {
        'map_data': main.map_data,
        'player': main.player,
        'enemies': main.enemies,
        'bullets': main.bullets,
        'explosions': main.explosions,
        'score': main.score,
        'lives': main.lives,
        'base_alive': main.base_alive,
        'game_state': main.game_state,
        'spawned_enemies': main.spawned_enemies,
        'total_enemies': main.total_enemies,
        'gameover_delay': main.gameover_delay,
        'stage': main.stage,
        'paused': main.paused,
        'stage_transition_timer': main.stage_transition_timer,
        'spawn_timer': getattr(main, 'spawn_timer', 0),
    }

    # Reset to clean defaults
    main.map_data = []
    main.player = None
    main.enemies = []
    main.bullets = []
    main.explosions = []
    main.score = 0
    main.lives = 3
    main.base_alive = True
    main.game_state = 'menu'
    main.spawned_enemies = 0
    main.total_enemies = 20
    main.gameover_delay = 0
    main.paused = False
    main.stage_transition_timer = 0
    main.spawn_timer = 0

    yield

    # Restore original state
    for key, value in saved.items():
        setattr(main, key, value)


def make_empty_map():
    """Create a MAP_H x MAP_W empty map."""
    return [[TERRAIN_EMPTY] * MAP_W for _ in range(MAP_H)]


def make_standard_map():
    """Create a map based on STAGE_MAP."""
    return [row.copy() for row in main.STAGE_MAP]
