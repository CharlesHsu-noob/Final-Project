import pygame as pg
import XddObjects as xo
import setup
import start_menu, home, forest_a, forest_b, forest_c, forest_d, forest_f, forest_g, forest_h, pause_menu
import labg_a
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
    
    # ★★★ 2. 新增一個變數來記錄戰鬥是否完成 ★★★
    main.forest_battle_done = False 
    
    # ★★★ 新增：用來記錄戰鬥前的位置變數 ★★★
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

    # 音效資產載入 (for pause_menu volume control)
    main.sound_assets = {} 

    setup.music_setup(main)
    
    global start_menu_var
    start_menu_var = start_menu.setup(main)
    global scene
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
    scene["labg_a_var"]=labg_a.setup(main)

    # -------------------------------------------------------------
    # 【修改：不自動讀檔，而是初始化空資料】
    # -------------------------------------------------------------
    
    # 建立全新的遊戲資料與空背包
    main.game_data = GameData()
    main.inventory = [] # 這裡先給空列表，pause_menu 會負責填入預設物品
    main.game_state = "start_menu"
    print("[System] 遊戲啟動，進入標題畫面")

    main.last_game_state = main.game_state
    main.last_pause_state = main.game_state
    
    main.captured_screen = None
    main.refreshing_pause_bg = False 

def bgm_manager():
    if main.game_state == "pause_menu":
        # 暫停時音量變小，但不切歌
        pg.mixer.music.set_volume(main.game_data.volume * 0.4)
        return
    
    # 如果是在同一區的場景切換 (例如 forest_a -> forest_b)，不切歌
    if main.last_game_state.find("forest") != -1 and \
       main.game_state.find("forest") != -1:
        return
    
    if main.game_state in ["fight", "home"]:
        # 這些場景可能有自己的 BGM 邏輯，這裡先略過
        return

    # 根據場景播放音樂
    target_music = main.music_playlist.get(main.game_state)
    
    # 套用當前設定的音量
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
        "labg_a_var": xo.VAR()
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
                    pass # 暫停選單內的 ESC 由 pause_menu 處理
                elif main.game_state != "start_menu": 
                    main.last_pause_state = main.game_state
                    main.game_state = "pause_menu"
                    main.captured_screen = main.screen.copy()
                    continue 

            if main.game_state != "pause_menu":
                if event.type == pg.KEYDOWN:
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
        
        if main.game_state != "pause_menu":
             main.last_game_state = main.game_state

        # ------------------ 2. 場景更新 (Match Case) ------------------
        match main.game_state:
            case "start_menu":
                start_menu.update(main, start_menu_var)
            
            case "home":
                # 【修改】崩潰修復：若 home_var 為空 (例如讀檔後)，重新執行 setup
                if scene.get("home_var") is None:
                    scene["home_var"] = home.setup(main)
                scene = home.update(main, scene, font, scene["home_var"])
            
            case "forest_a":
                # 建議加上相同保護
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
                main=labg_b.update(main)
                main.MoveKeyQueue=[]
                if main.game_state=="labg_a":
                    main.last_map_x,main.last_map_y=(200,502)
            case "fight":
                pg.mixer.music.stop() 
                fight.run_battle(main.screen)
                
                # ★★★ 戰鬥結束後的處理：回到戰鬥前的地圖與位置 ★★★
                if main.pre_fight_map:
                    main.game_state = main.pre_fight_map
                    # 恢復座標
                    main.char_u.map_x = main.pre_fight_pos[0]
                    main.char_u.map_y = main.pre_fight_pos[1]
                    
                    # 稍微後退一點點，避免視覺上還黏在觸發點
                    main.char_u.map_x -= 50
                else:
                    # 如果沒有紀錄（防呆），預設回 forest_g
                    main.game_state = "forest_g"

                main.forest_battle_done = True 
                main.MoveKeyQueue.clear()
            case "pause_menu":
                pause_menu.update(main, scene["pause_menu_var"])
                
            case _:
                if main.game_state != "pause_menu":
                    print("no game state:", main.game_state)
                    main.running = False
        
        # ------------------ 3. 戰鬥觸發判定 ------------------
        
        target_x = 2453
        target_y_top = 600
        target_y_bottom = 1200
        tolerance_x = 20

        # 請注意：這段邏輯是針對 forest_a，若你換地圖要改這裡
        if main.game_state == "forest_a":
            in_x = abs(main.char_u.map_x - target_x) <= tolerance_x
            in_y = target_y_top <= main.char_u.map_y <= target_y_bottom

            if in_x and in_y and (not main.forest_battle_done):
                # ★ 觸發時紀錄當前位置
                main.pre_fight_map = main.game_state
                main.pre_fight_pos = (main.char_u.map_x, main.char_u.map_y)
                
                main.game_state = "fight"

        # ------------------ 4. 畫面更新 ------------------
        if main.refreshing_pause_bg:
            main.captured_screen = main.screen.copy()
            main.game_state = "pause_menu"
            pause_menu.update(main, scene["pause_menu_var"])
            main.refreshing_pause_bg = False

        pg.display.update()
    
    pg.quit()