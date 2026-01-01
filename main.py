import pygame as pg
import XddObjects as xo
import setup
# 引入所有場景
import start_menu, home, forest_a, forest_b, forest_c, forest_d, forest_f, forest_g, forest_h, pause_menu

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
    start_menu_var=start_menu.setup(main)
    
    global scene
    # 【重要修正】必須在這裡將所有場景都 setup 初始化
    # 否則讀檔跳到其他沒初始化的場景時，程式會因為變數缺失而閃退
    scene["pause_menu_var"] = pause_menu.setup(main)
    scene["home_var"]       = home.setup(main)
    scene["forest_a_var"]   = forest_a.setup(main)
    scene["forest_b_var"]   = forest_b.setup(main)
    scene["forest_c_var"]   = forest_c.setup(main)
    scene["forest_d_var"]   = forest_d.setup(main)
    scene["forest_f_var"]   = forest_f.setup(main)
    scene["forest_g_var"]   = forest_g.setup(main)
    scene["forest_h_var"]   = forest_h.setup(main)

    # 設定初始遊戲狀態
    # for debug------v----
    initial_state = "forest_g" 
    main.game_state = initial_state
    # for debug------^----

    main.char_u.map_x,main.char_u.map_y=main.state_pos[initial_state]

    main.last_game_state = initial_state
    main.last_pause_state = initial_state
    
    main.captured_screen = None
    
    # 【新增】用來標記是否需要刷新暫停背景
    main.refreshing_pause_bg = False 

def bgm_manager():
    if main.game_state == "pause_menu":
        # 暫停時音樂變小聲
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

            # 【暫停觸發邏輯】
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                if main.game_state == "pause_menu":
                    # 如果已經在暫停，交給下方的 handle_input 處理
                    pass
                elif main.game_state != "start_menu": 
                    # --- 進入暫停 ---
                    main.last_pause_state = main.game_state
                    main.game_state = "pause_menu"
                    # 截圖當前畫面做背景
                    main.captured_screen = main.screen.copy()
                    
                    # 使用 continue 跳過迴圈，防止事件穿透到 handle_input
                    continue 

            # 只有不在暫停時才處理移動
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
            
            # 【暫停選單輸入處理】
            if main.game_state == "pause_menu":
                pause_menu.handle_input(main, scene["pause_menu_var"], event)

        bgm_manager()

        main.play_animation = False
        if main.last_game_state != main.game_state and \
                main.last_game_state != "pause_menu" and \
                main.game_state != "pause_menu": # 進出暫停不算切換場景動畫
            main.play_animation = True
        
        # 更新 main.last_game_state (除了暫停之外的記錄)
        if main.game_state != "pause_menu":
             main.last_game_state = main.game_state

        # 【場景更新與繪製】
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
                pause_menu.update(main, scene["pause_menu_var"])
                
            case _:
                # 容錯處理
                if main.game_state != "pause_menu":
                    print("no game state:", main.game_state)
                    main.running=False

        # ==========================================
        # 【背景刷新邏輯】
        # 當 pause_menu 讀檔後把 main.refreshing_pause_bg 設為 True 時執行
        # ==========================================
        if main.refreshing_pause_bg:
            # 1. 剛剛上面的 match 已經把新場景畫好了，現在截圖
            main.captured_screen = main.screen.copy()
            
            # 2. 馬上把狀態切回 pause_menu (保持暫停狀態)
            main.game_state = "pause_menu"
            
            # 3. 為了避免畫面閃爍，立刻蓋上暫停選單
            pause_menu.update(main, scene["pause_menu_var"])
            
            # 4. 關閉旗標
            main.refreshing_pause_bg = False
        # ==========================================

        pg.display.update()
    pg.quit()