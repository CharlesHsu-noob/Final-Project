import pygame as pg
import XddObjects as xo
import setup
import start_menu, home, forest_a, forest_b, forest_c, forest_d, forest_f, forest_g, forest_h, pause_menu
import labg_a, labg_c
from gamedata import GameData
import fight 

def bg_size_correction(w: int, h: int) -> tuple[int, int]:
    rw = w / 16
    rh = h / 9
    if rw > rh:
        return int(rh * 16), int(rh * 9)
    else:
        return int(rw * 16), int(rw * 9)

def main_initiate():
    pg.init()
    pg.mixer.init()
    main.fps = 60
    main.clock = pg.time.Clock()
    screeninfo = pg.display.Info()
    main.w, main.h = screeninfo.current_w, screeninfo.current_h
    main.menu_w, main.menu_h = bg_size_correction(main.w, main.h)
    main.screen = pg.display.set_mode((main.w, main.h)) 
    pg.display.set_caption("XDD's adventure")
    main.rainbow_text_color = xo.ColorCycler(speed=0.08)
    global font
    font = setup.font_setup()

    # Variable initiation
    main.zoom_ratio = main.w / 1920
    main.running = True
    main.is_pause = False
    main.play_animation = False
    
    # ★★★ 1. Glitch (變身) 相關變數 ★★★
    main.is_glitching = False         # 是否正在播放進戰鬥前的特效
    main.glitch_start_time = 0        # 特效開始時間
    main.scaled_glitch_current = None # ★★★ 新增：用來存放縮放後符合主角大小的暫存圖片
    try:
        # 載入 Glitch 原始圖片
        main.u_glitch_img_raw = pg.image.load("image/battle/u_glitch.png").convert_alpha()
        print("[System] Glitch image loaded successfully.")
    except Exception as e:
        print(f"[Warning] Glitch image loading failed: {e}")
        main.u_glitch_img_raw = None 
    
    # ★★★ 2. 戰鬥狀態變數 ★★★
    main.forest_battle_done = False 
    
    # ★★★ 3. 戰鬥前位置紀錄 ★★★
    main.pre_fight_map = None
    main.pre_fight_pos = (0, 0)

    main.MoveKeyQueue = []
    main.InteractKeyQueue = []

    main.state_pos = {}
    main.state_pos["home"] = [2539, 544]
    main.state_pos["forest_a"] = [1619, 550]
    main.state_pos["forest_b"] = [2280, 718]
    main.state_pos["forest_c"] = [3840, 750]
    main.state_pos["forest_d"] = [1380, 570]
    main.state_pos["forest_f"] = [1900, 690]
    main.state_pos["forest_g"] = [3750, 750]
    main.state_pos["forest_h"] = [2180, 672]
    main.state_pos["labg_a"] = [2480, 508]
    main.state_pos["labg_c"] = [1500, 508]

    # 音效資產載入
    main.sound_assets = {} 
    main.current_music = None 
    setup.music_setup(main)
    
    global start_menu_var
    start_menu_var = start_menu.setup(main)
    global scene
    scene = {} 
    scene["pause_menu_var"] = pause_menu.setup(main)

    # -------------------------------------------------------------
    # 【初始化所有場景】
    # -------------------------------------------------------------
    scene["home_var"] = home.setup(main)
    scene["forest_a_var"] = forest_a.setup(main)
    scene["forest_b_var"] = forest_b.setup(main)
    scene["forest_c_var"] = forest_c.setup(main)
    scene["forest_d_var"] = forest_d.setup(main)
    scene["forest_f_var"] = forest_f.setup(main)
    scene["forest_g_var"] = forest_g.setup(main)
    scene["forest_h_var"] = forest_h.setup(main)
    scene["labg_a_var"] = labg_a.setup(main)
    scene["labg_c_var"] = labg_c.setup(main)

    # -------------------------------------------------------------
    # 【初始化遊戲資料】
    # -------------------------------------------------------------
    main.game_data = GameData()
    main.inventory = [] 
    main.game_state = "start_menu"
    print("[System] 遊戲啟動，進入標題畫面")

    main.last_game_state = main.game_state
    main.last_pause_state = main.game_state
    
    main.captured_screen = None
    main.refreshing_pause_bg = False 

def bgm_manager():
    if not hasattr(main, 'music_playlist'): return

    if main.game_state == "pause_menu":
        pg.mixer.music.set_volume(main.game_data.volume * 0.4)
        return
    
    if main.last_game_state.find("forest") != -1 and \
       main.game_state.find("forest") != -1:
        return
    
    if main.game_state in ["fight", "home"]:
        return

    target_music = main.music_playlist.get(main.game_state)
    pg.mixer.music.set_volume(main.game_data.volume)
    
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
    
    scene = {
        "home_var": xo.VAR(),
        "forest_a_var": xo.VAR(),
        "forest_b_var": xo.VAR(),
        "forest_c_var": xo.VAR(),
        "forest_d_var": xo.VAR(),
        "forest_f_var": xo.VAR(),
        "forest_g_var": xo.VAR(),
        "forest_h_var": xo.VAR(),
        "pause_menu_var": xo.VAR(),
        "labg_a_var": xo.VAR(),
        "labg_c_var": xo.VAR(),
    }
    
    main_initiate()
    print("zoom ratio=", main.zoom_ratio)
    
    while main.running:
        main.clock.tick(main.fps)

        # ------------------ 1. 事件處理 ------------------
        for event in pg.event.get():
            if event.type == pg.QUIT:
                main.running = False

            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                if main.game_state == "pause_menu":
                    pass 
                elif main.game_state != "start_menu": 
                    main.last_pause_state = main.game_state
                    main.game_state = "pause_menu"
                    main.captured_screen = main.screen.copy()
                    continue 

            if main.game_state != "pause_menu":
                if event.type == pg.KEYDOWN:
                    # 如果正在 Glitch 變身中，鎖住按鍵輸入
                    if not main.is_glitching:
                        if event.key in [pg.K_w, pg.K_a, pg.K_s, pg.K_d,pg.K_UP, pg.K_LEFT, pg.K_DOWN, pg.K_RIGHT]:
                            if event.key not in main.MoveKeyQueue:
                                main.MoveKeyQueue.append(event.key)
                        elif event.key in [pg.K_f]:
                            if event.key not in main.InteractKeyQueue:
                                main.InteractKeyQueue.append(event.key)
                    
                    # 測試鍵：按 K 強制進戰鬥
                    if event.key == pg.K_k:
                        main.pre_fight_map = main.game_state
                        main.pre_fight_pos = (main.char_u.map_x, main.char_u.map_y)
                        main.game_state = "fight"

                if event.type == pg.KEYUP:
                    if event.key in main.MoveKeyQueue:
                        main.MoveKeyQueue.remove(event.key)
                    elif event.key in main.InteractKeyQueue:
                        main.InteractKeyQueue.remove(event.key)
            
            if main.game_state == "pause_menu":
                pause_menu.handle_input(main, scene["pause_menu_var"], event)

        bgm_manager()

        main.play_animation = False
        if main.last_game_state != main.game_state and \
                main.last_game_state != "pause_menu" and \
                main.game_state != "pause_menu": 
            main.play_animation = True
        
        # ------------------ 2. 場景更新 (Match Case) ------------------
        match main.game_state:
            case "start_menu":
                start_menu.update(main, start_menu_var)
            
            case "home":
                if scene.get("home_var") is None:
                    scene["home_var"] = home.setup(main)
                scene = home.update(main, scene, font, scene["home_var"])
            
            case "forest_a":
                if scene.get("forest_a_var") is None: 
                    scene["forest_a_var"] = forest_a.setup(main)
                scene = forest_a.update(main, scene, font, scene["forest_a_var"])
            
            case "forest_b":
                scene = forest_b.update(main, scene, font, scene["forest_b_var"])
            case "forest_c":
                scene = forest_c.update(main, scene, font, scene["forest_c_var"])
            case "forest_d":
                scene = forest_d.update(main, scene, font, scene["forest_d_var"])
            case "forest_e":
                import climb
                climb.update(main.w,main.h)
                main.game_state="forest_f"
                main.char_u.map_x,main.char_u.map_y=main.state_pos["forest_f"]
                main.MoveKeyQueue=[]
            case "forest_f":
                scene = forest_f.update(main, scene, font, scene["forest_f_var"])
            case "forest_g":
                scene = forest_g.update(main, scene, font, scene["forest_g_var"])
            case "forest_h":
                scene = forest_h.update(main, scene, font, scene["forest_h_var"])
            case "labg_a":
                scene=labg_a.update(main,scene,font,scene["labg_a_var"])
            case "labg_b":
                import labg_b
                if main.last_game_state=="labg_c":
                    main=labg_b.update(main,True)
                    main.state_pos["labg_c"]=[1500,508]
                else:
                    main=labg_b.update(main)
                    main.state_pos["labg_a"] = [2480, 508]
                main.MoveKeyQueue=[]
                main.last_game_state="labg_b"

                continue
            case "labg_c":
                scene=labg_c.update(main,scene,font,scene["labg_c_var"])
            case "fight":
                pg.mixer.music.stop() 
                fight.run_battle(main.screen)
                
                # 戰鬥結束後的處理
                if main.pre_fight_map:
                    main.game_state = main.pre_fight_map
                    main.char_u.map_x = main.pre_fight_pos[0]
                    main.char_u.map_y = main.pre_fight_pos[1]
                    main.char_u.map_x -= 50
                else:
                    main.game_state = "forest_g"

                main.forest_battle_done = True 
                main.MoveKeyQueue.clear()
            case "pause_menu":
                pause_menu.update(main, scene["pause_menu_var"])
            
            case _:
                if main.game_state != "pause_menu":
                    print("no game state:", main.game_state)
                    main.running = False

        if main.game_state != "pause_menu":
             main.last_game_state = main.game_state
        
        # ------------------ 3. 戰鬥觸發判定 ------------------

        if main.game_state == "forest_b":
            in_x = abs(main.char_u.map_y - 20) <= 1038
            in_y = 1080 <= main.char_u.map_x <= 1512

            # ★★★ 修改：戰鬥觸發 + 0.2 秒 Glitch 變身等待 ★★★
            if in_x and in_y and (not main.forest_battle_done):
                
                # A. 開始變身：第一次偵測到觸發
                if not main.is_glitching:
                    print("Battle Triggered! Starting Glitch...")
                    main.is_glitching = True
                    main.glitch_start_time = pg.time.get_ticks() # 記錄時間
                    main.MoveKeyQueue.clear() # 讓主角停下來
                    
                    # ★★★ 新增：在這裡進行圖片縮放 ★★★
                    # 確保原始圖和主角的 rect 都存在
                    if main.u_glitch_img_raw and hasattr(main.char_u, 'rect'):
                        # 抓取主角當下的寬高
                        target_size = (main.char_u.rect.width, main.char_u.rect.height)
                        # 將原始 Glitch 圖縮放到主角的大小，存入 scaled_glitch_current
                        main.scaled_glitch_current = pg.transform.scale(main.u_glitch_img_raw, target_size)
                    else:
                        # 如果抓不到主角大小，就用原圖（防呆）
                        main.scaled_glitch_current = main.u_glitch_img_raw
                
                # B. 變身中：檢查時間
                else:
                    current_time = pg.time.get_ticks()
                    if current_time - main.glitch_start_time >= 200: # 0.2 秒
                        # 時間到 -> 進戰鬥
                        print("Glitch finished. Entering Fight Mode.")
                        main.is_glitching = False
                        main.scaled_glitch_current = None # 清空暫存圖
                        
                        main.pre_fight_map = main.game_state
                        main.pre_fight_pos = (main.char_u.map_x, main.char_u.map_y)
                        
                        main.game_state = "fight"

        # ------------------ 4. 畫面更新 (含 Glitch 繪製) ------------------
        
        # ★★★ 關鍵修正：繪製縮放後的 Glitch 圖片 ★★★
        if main.is_glitching and main.scaled_glitch_current:
            if hasattr(main.char_u, 'rect'):
                # 將縮放後的圖片中心對齊主角的中心
                glitch_rect = main.scaled_glitch_current.get_rect(center=main.char_u.rect.center)
                main.screen.blit(main.scaled_glitch_current, glitch_rect)
            else:
                # 防呆備用方案
                main.screen.blit(main.scaled_glitch_current, (main.w//2 - 50, main.h//2 - 50))

        if main.refreshing_pause_bg:
            main.captured_screen = main.screen.copy()
            main.game_state = "pause_menu"
            pause_menu.update(main, scene["pause_menu_var"])
            main.refreshing_pause_bg = False

        pg.display.update()
    
    pg.quit()