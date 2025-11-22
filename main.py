import pygame as pg
import XddObjects as xo
import setup
import os
import start_menu,home

main=xo.VAR()
start_menu_var=xo.VAR()
home_var=xo.VAR()
font=xo.VAR()

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
    main.rainbow_text_color = xo.ColorCycler(speed=0.08)
    global font
    font=setup.font_setup()

    #Variable initiation
    main.zoom_ratio=main.w/1920
    main.running=True
    main.is_pause=False
    main.play_animation=False
    main.game_state= "start_menu"
    main.last_game_state= "start_menu"
    main.last_pause_state= "start_menu"
    main.MoveKeyQueue=[]
    main.InteractKeyQueue=[]

    main.state_pos={}
    main.state_pos["home"]=[5000,1500]

    setup.music_setup(main)
    global start_menu_var
    start_menu_var=start_menu.setup(main)
    global home_var
    home_var=home.setup(main)

def bgm_manager():                         ##not finished
    if main.game_state == "pause_menu":
        return
    target_music = main.music_playlist.get(main.game_state)
    #pg.mixer.music.set_volume(main.volume_twist.current_val)
    #add later
    pg.mixer.music.set_volume(0.5)
    if target_music and target_music != main.current_music:
        pg.mixer.music.fadeout(1000)  # 淡出舊音樂
        pg.mixer.music.load(target_music)
        pg.mixer.music.play(loops=-1, fade_ms=1500) # 播放新音樂
        main.current_music = target_music # 更新當前音樂
    # 如果狀態沒有對應音樂，且有音樂在播放，則停止
    elif not target_music and main.current_music:
        pg.mixer.music.fadeout(1000)
        main.current_music = None

if __name__ == "__main__":
    main_initiate()
    print("zoom ratio=",main.zoom_ratio)
    while main.running:
        main.clock.tick(main.fps)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                main.running=False

            #for pause
            # : )

            #detect keyboard input
            if event.type == pg.KEYDOWN:
                # 確保同一個鍵不會被重複加入
                if event.key in [pg.K_w, pg.K_a, pg.K_s, pg.K_d]:
                    if event.key not in main.MoveKeyQueue:
                        main.MoveKeyQueue.append(event.key)
                elif event.key in [pg.K_f]:
                    if event.key not in main.InteractKeyQueue:
                        main.InteractKeyQueue.append(event.key)

            if event.type == pg.KEYUP:
                if event.key in main.MoveKeyQueue:
                    main.MoveKeyQueue.remove(event.key)
                elif event.key in main.InteractKeyQueue:
                    main.InteractKeyQueue.remove(event.key)

        bgm_manager()

        match main.game_state:
            case "start_menu":
                start_menu.update(main,start_menu_var)
            case "home":
                home.update(main,font,home_var)
            case _:
                print("no game state")
                main.running=False
        #if main.pause_exit.ispress:
        #    main.running = False
        pg.display.update()
    pg.quit()