import pygame as pg
import XddObjects as xo
import setup
import start_menu,home,forest_a,forest_b,forest_c,forest_d,forest_f,forest_g,forest_h

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

    main.MoveKeyQueue=[]
    main.InteractKeyQueue=[]

    main.state_pos={}
    main.state_pos["home"]=[2539,544]
    main.state_pos["forest_a"]=[1619,550]
    main.state_pos["forest_b"]=[2280,718]
    main.state_pos["forest_c"]=[3840,750]
    main.state_pos["forest_d"]=[1380,570]
    main.state_pos["forest_f"]=[1900,690]
    main.state_pos["forest_g"]=[3750,750]
    main.state_pos["forest_h"]=[2180,672]


    setup.music_setup(main)
    global start_menu_var
    start_menu_var=start_menu.setup(main)
    #global scene
    # for debug------v----

    global scene
    initial_state = "forest_g"
    scene["forest_g_var"] = forest_g.setup(main)
    main.game_state = initial_state

    # for debug------^----
    scene["home_var"]=home.setup(main)
    #initial_state = "home"
    main.char_u.map_x,main.char_u.map_y=main.state_pos[initial_state]

    #main.game_state = "start_menu"
    main.last_game_state = initial_state
    main.last_pause_state = initial_state

def bgm_manager():                         ##not finished i need to add volume change code
    if main.game_state == "pause_menu":
        return
    elif main.last_game_state.find("forest") !=-1 and\
        main.game_state.find("forest") !=-1:
        return
    target_music = main.music_playlist.get(main.game_state)
    ''' add this will cause a huge lag!
    if main.last_game_state.find("forest") ==-1 and\
        main.game_state.find("forest") !=-1:
        target_music=main.music_playlist.get("forest")
    no good solution yet
    '''
    #pg.mixer.music.set_volume(main.volume_twist.current_val)
    #add later
    pg.mixer.music.set_volume(0.5)
    if target_music and (target_music != main.current_music):
        pg.mixer.music.fadeout(1000)  # 淡出舊音樂
        pg.mixer.music.load(target_music)
        pg.mixer.music.play(loops=-1, fade_ms=1500) # 播放新音樂
        main.current_music = target_music # 更新當前音樂
    # 如果狀態沒有對應音樂，且有音樂在播放，則停止
    elif not target_music and main.current_music:
        pg.mixer.music.fadeout(1000)
        main.current_music = None

if __name__ == "__main__":
    main = xo.VAR()
    font = xo.VAR()
    start_menu_var = xo.VAR()
    scene={
        "home_var":xo.VAR(),
        "forest_a_var":xo.VAR(),
        "forest_b_var":xo.VAR(),
        "forest_c_var":xo.VAR(),
        "forest_d_var":xo.VAR(),
        "forest_f_var":xo.VAR(),
        "forest_g_var":xo.VAR(),
        "forest_h_var":xo.VAR(),
    }
    #forest_a_var=xo.VAR()
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

        main.play_animation = False
        if main.last_game_state != main.game_state and \
                main.last_game_state != "pause_menu":
            main.play_animation = True
        main.last_game_state = main.game_state

        match main.game_state:
            case "start_menu":
                start_menu.update(main,start_menu_var)
            case "home":
                scene=home.update(main,scene,font,scene["home_var"])
            case "forest_a":
                scene=forest_a.update(main,scene,font,scene["forest_a_var"])
            case "forest_b":
                scene= forest_b.update(main, scene, font, scene["forest_b_var"])
            case "forest_c":
                scene=forest_c.update(main,scene,font,scene["forest_c_var"])
            case "forest_d":
                scene=forest_d.update(main,scene,font,scene["forest_d_var"])
            case "forest_f":
                scene=forest_f.update(main,scene,font,scene["forest_f_var"])
            case "forest_g":
                scene=forest_g.update(main,scene,font,scene["forest_g_var"])
            case "forest_h":
                scene=forest_h.update(main,scene,font,scene["forest_h_var"])
            case _:
                print("no game state")
                main.running=False
        #if main.pause_exit.ispress:
        #    main.running = False
        pg.display.update()
    pg.quit()