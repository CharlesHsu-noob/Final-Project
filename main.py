import pygame as pg
import XddObjects as xo
import setup
# 引入所有場景
import start_menu, home, forest_a, forest_b, forest_c, forest_d, forest_f, forest_g, forest_h, pause_menu

# 【新增】引入讀檔模組
from gamedata import load_game_from_file

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

    # Variable initiation
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
    start_menu_var = start_menu.setup(main)
    
    global scene
    scene["pause_menu_var"] = pause_menu.setup(main)

    # -------------------------------------------------------------
    # 【初始化所有場景】
    # 為了確保讀檔時不管跳到哪張地圖都有初始化，建議這裡全部執行一次
    # (順便解決 main.char_u 可能還沒產生的問題)
    # -------------------------------------------------------------
    scene["home_var"] = home.setup(main)
    scene["forest_a_var"] = forest_a.setup(main)
    scene["forest_b_var"] = forest_b.setup(main)
    scene["forest_c_var"] = forest_c.setup(main)
    scene["forest_d_var"] = forest_d.setup(main)
    scene["forest_f_var"] = forest_f.setup(main)
    scene["forest_g_var"] = forest_g.setup(main)
    scene["forest_h_var"] = forest_h.setup(main)

    # -------------------------------------------------------------
    # 【整合存檔系統】
    # -------------------------------------------------------------
    # 1. 讀取存檔
    game_data, inventory, loaded_pos, loaded_scene = load_game_from_file()

    # 2. 將資料綁定到 main 物件，讓全域(暫停選單、商店)都能共用
    main.game_data = game_data
    main.inventory = inventory

    # 3. 判斷要進入哪個場景
    if loaded_scene and loaded_pos:
        # A. 如果有存檔，使用存檔的場景和座標
        main.game_state = loaded_scene
        initial_pos = loaded_pos
        print(f"[System] 讀檔成功：進入 {loaded_scene}")
    else:
        # B. 如果沒有存檔 (新遊戲)，使用預設值
        # 這裡設定新遊戲的起始點，例如 "home" 或你測試用的 "forest_g"
        main.game_state = "home" 
        initial_pos = main.state_pos[main.game_state]
        print("[System] 新遊戲開始")

    # 4. 應用座標 (此時 main.char_u 已經在上面的 setup 中建立了)
    main.char_u.map_x, main.char_u.map_y = initial_pos

    # -------------------------------------------------------------

    main.last_game_state = main.game_state
    main.last_pause_state = main.game_state
    
    main.captured_screen = None
    main.refreshing_pause_bg = False 

def bgm_manager():
    if main.game_state == "pause_menu":
        pg.mixer.music.set_volume(0.2)
        return
    
    elif main.last_game_state.find("forest") !=-1 and \
         main.game_state.find("forest") !=-1:
        return
    
    target_music = main.music_playlist.get(main.game_state)
    pg.mixer.music.set_volume(0.5)
    
    if target_music and (target_music != main.current_music):
        pg.mixer.music.fadeout(1000)
        pg.mixer.music.load(target_music)
        pg.mixer.music.play(loops=-1, fade_ms=1500)
        main.current_music = target_music
    elif not target_music and main.current_music:
        pg.mixer.music.fadeout(1000)
        main.current_music = None

if __name__ == "__main__":
    main = xo.VAR()
    font = xo.VAR()
    start_menu_var = xo.VAR()
    
    # 這裡先定義空的場景變數容器
    scene={
        "home_var":xo.VAR(),
        "forest_a_var":xo.VAR(),
        "forest_b_var":xo.VAR(),
        "forest_c_var":xo.VAR(),
        "forest_d_var":xo.VAR(),
        "forest_f_var":xo.VAR(),
        "forest_g_var":xo.VAR(),
        "forest_h_var":xo.VAR(),
        "pause_menu_var":xo.VAR()
    }
    
    main_initiate()
    print("zoom ratio=",main.zoom_ratio)
    
    while main.running:
        main.clock.tick(main.fps)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                main.running=False

            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                if main.game_state == "pause_menu":
                    pass
                elif main.game_state != "start_menu": 
                    # 紀錄進入暫停前的狀態，方便存檔時知道是哪張地圖
                    main.last_pause_state = main.game_state
                    
                    main.game_state = "pause_menu"
                    main.captured_screen = main.screen.copy()
                    continue 

            if main.game_state != "pause_menu":
                if event.type == pg.KEYDOWN:
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
            
            if main.game_state == "pause_menu":
                # 把 main 傳進去，這樣 pause_menu 就能存取 main.game_data 和 main.inventory
                pause_menu.handle_input(main, scene["pause_menu_var"], event)

        bgm_manager()

        main.play_animation = False
        if main.last_game_state != main.game_state and \
                main.last_game_state != "pause_menu" and \
                main.game_state != "pause_menu": 
            main.play_animation = True
        
        if main.game_state != "pause_menu":
             main.last_game_state = main.game_state

        match main.game_state:
            case "start_menu":
                start_menu.update(main,start_menu_var)
            case "home":
                scene=home.update(main,scene,font,scene["home_var"])
            case "forest_a":
                scene=forest_a.update(main,scene,font,scene["forest_a_var"])
            case "forest_b":
                scene=forest_b.update(main, scene, font, scene["forest_b_var"])
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
            case "pause_menu":
                # 暫停選單更新時，也可以存取 main.game_data
                pause_menu.update(main, scene["pause_menu_var"])
                
            case _:
                if main.game_state != "pause_menu":
                    print("no game state:", main.game_state)
                    main.running=False
        
        if main.refreshing_pause_bg:
            # 刷新暫停背景的功能
            main.captured_screen = main.screen.copy()
            main.game_state = "pause_menu"
            pause_menu.update(main, scene["pause_menu_var"])
            main.refreshing_pause_bg = False

        pg.display.update()
    pg.quit()