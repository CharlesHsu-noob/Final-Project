import pygame as pg
import XddObjects as xo
import os
import start_menu

main=xo.VAR

def bg_size_correction(w:int,h:int) -> tuple[int,int]:
    rw=w/16
    rh=h/9
    if rw>rh:#h is the benchmark
        return int(rh*16),int(rh*9)
    else:
        return int(rw*16),int(rw*9)

def main_initiate():
    pg.init()
    pg.mixer.init()
    main.fps=60
    main.clock = pg.time.Clock()
    screeninfo=pg.display.Info()
    main.w,main.h=screeninfo.current_w,screeninfo.current_h
    main.menu_w,main.menu_h=bg_size_correction(main.w,main.h)
    main.screen = pg.display.set_mode((main.w,main.h))
    pg.display.set_caption("XDD's adventure")

    #Variable initiation
    main.zoom_ratio=main.w/1920
    main.running=True
    main.is_pause=False
    main.game_status="start_menu"
    main.last_game_status="start_menu"
    main.last_pause_status="start_menu"
    main.MoveKeyQueue=[]
    main.InteractKeyQueue=[]



if __name__ == "__main__":
    main_initiate()