import pygame as pg
import XddObjects as xo
import path_dictionary as pd
import os
import main

def setup(game:xo.VAR) -> xo.VAR :
    start = xo.VAR
    start.button_list=[]
    start.bg=pg.transform.scale(pg.image.load(pd.start_menu_bg_path).convert_alpha(),
                                (game.menu_w,game.menu_h))
    start.lamp=xo.buttonObject(pd.lamp_path,
                               (1150,250),
                               (318*game.zoom_ratio,438*game.zoom_ratio))
    start.notebook=xo.buttonObject(pd.notebook_path,
                                   (850,550),
                                   (255*game.zoom_ratio,290*game.zoom_ratio))
    start.button_list.append(start.lamp)
    start.button_list.append(start.notebook)
    return start

def update(game:xo.VAR,start:xo.VAR) -> None:
    game.screen.blit(start.bg,(0,0))
    for button in start.button_list:
        button.update()
        game.screen.blit(button.image,button.rect)