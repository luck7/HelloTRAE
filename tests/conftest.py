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
# Mock pgzero Actor class (used by entities.py)
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


# Inject Actor into builtins so entities.py can find it
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
# Import game modules and inject pgzero globals
# ---------------------------------------------------------------------------
import constants
import map as game_map
import entities
import game as game_module
import main as entry

_inject_pgzero_globals(entities)
_inject_pgzero_globals(game_module)
_inject_pgzero_globals(entry)


# ---------------------------------------------------------------------------
# Helper utilities for tests
# ---------------------------------------------------------------------------
from constants import (
    TILE_SIZE, GRID_W, GRID_H, GAME_W, GAME_H,
    T_EMPTY, T_BRICK, T_STEEL, T_WATER, T_GRASS,
)


def make_empty_map():
    """Create a GRID_H x GRID_W empty map."""
    return [[T_EMPTY for _ in range(GRID_W)] for _ in range(GRID_H)]
