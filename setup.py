#font and bgm
import os
import pygame as pg
import XddObjects as xo


def music_setup(game):
    game.music_playlist={
        "start_menu":os.path.join("voice","bgm","start_menu.wav"),
        "forest":os.path.join("voice","bgm","forest_1.wav"),
    }
    game.current_music=None

def font_setup() -> xo.VAR:
    font=xo.VAR()

    font.pos=pg.font.SysFont("times new roman",20)

    return font