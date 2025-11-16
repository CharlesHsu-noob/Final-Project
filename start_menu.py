import pygame as pg
import XddObjects as xo
import path_dictionary as pd
import os
import main

def setup(game) -> tuple[xo.VAR,xo.VAR] :
    start = xo.VAR
    start.button_list=[]
    start.bg=pg.transform.scale(pg.image.load(pd.start_menu_bg_path).convert_alpha(),
                                (game.menu_w,game.menu_h))
    start.lamp=xo.buttonObject(pd.lamp_path,
                               (100,100),
                               (318*game.zoom_ratio,438*game.zoom_ratio))
    start.notebook=xo.buttonObject(pd.notebook_path,
                                   (200,200),
                                   (255*game.zoom_ratio,438*game.zoom_ratio))
    start.button_list.append(start.lamp)
    start.button_list.append(start.notebook)

def update(pressKeyQueue:list,game:xo.VAR,start:xo.VAR) -> None:
