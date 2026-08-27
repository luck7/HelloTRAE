"""
Battle City - Tank Battle Game
Built with Pygame Zero.

Controls:
  Arrow Keys / WASD : Move tank
  Space             : Fire
  P                 : Pause / Resume
  Enter             : Start / Restart
  Esc               : Back to menu
"""

import pgzrun

from constants import STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER, STATE_WIN
from game import Game

# ----------------------------------------------------------------------
# Global game instance
# ----------------------------------------------------------------------
game = Game()


# ----------------------------------------------------------------------
# Pygame Zero hooks
# ----------------------------------------------------------------------
def update():
    game.update()


def draw():
    game.draw()


def on_key_down(key):
    if game.state == STATE_MENU:
        if key == keys.RETURN:
            game.start_game()
        return
    if game.state == STATE_PLAYING:
        if key == keys.P:
            game.state = STATE_PAUSED
            game.state_timer = 0
        elif key == keys.ESCAPE:
            game.state = STATE_MENU
            game.menu_timer = 0
        return
    if game.state == STATE_PAUSED:
        if key == keys.P:
            game.state = STATE_PLAYING
        elif key == keys.ESCAPE:
            game.state = STATE_MENU
            game.menu_timer = 0
        return
    if game.state in (STATE_GAME_OVER, STATE_WIN):
        if key == keys.RETURN:
            game.start_game()
        elif key == keys.ESCAPE:
            game.reset()
            game.menu_timer = 0
        return


pgzrun.go()
