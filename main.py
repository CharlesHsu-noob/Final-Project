import pygame as pg
import sys
import XddObjects as xo
import setup
import start_menu, home, forest_a, forest_b, forest_c, forest_d, forest_f, forest_g, forest_h, pause_menu
import labg_a, labg_c, labg_d
from gamedata import GameData
import fight 
from dialog_box import DialogueSystem, DIALOGUES
import dialog_box 

def bg_size_correction(w: int, h: int) -> tuple[int, int]:
    rw = w / 16
    rh = h / 9
    if rw > rh:
        return int(rh * 16), int(rh * 9)
    else:
        return int(rw * 16), int(rw * 9)

class FontContainer:
    def __init__(self, raw_font):
        self.pos = raw_font   
        self.ui = raw_font    
        self.main = raw_font  

def safe_save(main_obj):
    if hasattr(main_obj.game_data, "save"):
        try:
            current_pos = (0, 0)
            if hasattr(main_obj, 'char_u') and hasattr(main_obj.char_u, 'map_x'):
                current_pos = (main_obj.char_u.map_x, main_obj.char_u.map_y)
            
            main_obj.game_data.save(
                inventory_list=main_obj.inventory, 
                player_pos=current_pos, 
                scene_name=main_obj.game_state
            )
            print(f"[System] 進度已儲存至 save_{main_obj.save_slot}.json")
        except Exception as e:
            print(f"[System] 存檔失敗: {e}")
    else:
        print("[System] 警告: GameData 物件沒有 save() 方法，無法存檔。")

# ========================================================
# 讀取存檔的核心函式
# ========================================================
def start_game_from_slot(main_obj, slot_index):
    print(f"\n[System] === 正在載入存檔槽: {slot_index} ===")
    main_obj.save_slot = slot_index
    
    # 1. 重新建立 GameData
    main_obj.game_data = GameData(slot_index)
    
    # 2. 載入資料
    inv, pos, scene_name = main_obj.game_data.load_from_file()
    main_obj.inventory = inv

    # 3. 判斷是否為新遊戲 (Wake Up)
    if not main_obj.game_data.intro_played:
        print(f"[System] 存檔 {slot_index} 為新遊戲，啟動 Wake Up。")
        main_obj.run_wake_up_sequence = True
        
        # 設定 Wake Up 座標 (避開牆壁)
        safe_wake_up_pos = [2540, 500]
        
        main_obj.state_pos["home"] = safe_wake_up_pos
        if hasattr(main_obj, 'char_u'):
            main_obj.char_u.map_x, main_obj.char_u.map_y = safe_wake_up_pos
        
        main_obj.game_state = "home"
    else:
        print(f"[System] 存檔 {slot_index} 為舊進度，不播放開場。")
        main_obj.run_wake_up_sequence = False
        
        if scene_name:
            main_obj.game_state = scene_name
            print(f"[System] 切換場景至: {scene_name}")

        if pos != (0, 0):
            main_obj.state_pos[scene_name] = list(pos)
            if hasattr(main_obj, 'char_u'):
                main_obj.char_u.map_x, main_obj.char_u.map_y = pos
    
    # 4. 同步解鎖狀態
    main_obj.home_door_unlocked = main_obj.game_data.home_unlocked
    main_obj.cliff_is_locked = not main_obj.game_data.cliff_unlocked
    main_obj.boat_unlocked = main_obj.game_data.boat_unlocked
    main_obj.investigated_items = set()

    # ★★★ 關鍵修正：重新偵測當前按下的按鍵，填回移動佇列 ★★★
    main.MoveKeyQueue = []
    keys = pg.key.get_pressed()
    if keys[pg.K_w] or keys[pg.K_UP]: main.MoveKeyQueue.append(pg.K_w)
    if keys[pg.K_a] or keys[pg.K_LEFT]: main.MoveKeyQueue.append(pg.K_a)
    if keys[pg.K_s] or keys[pg.K_DOWN]: main.MoveKeyQueue.append(pg.K_s)
    if keys[pg.K_d] or keys[pg.K_RIGHT]: main.MoveKeyQueue.append(pg.K_d)

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
    try:
        raw_font_obj = pg.font.Font("C:\\Windows\\Fonts\\msjh.ttc", 24)
    except:
        try:
            raw_font_obj = pg.font.SysFont("microsoftjhenghei", 24)
        except:
            raw_font_obj = pg.font.Font(None, 24)
    
    font = FontContainer(raw_font_obj)

    main.zoom_ratio = main.w / 1920
    main.running = True
    main.is_pause = False
    main.play_animation = False
    
    main.is_glitching = False         
    main.glitch_start_time = 0        
    main.scaled_glitch_current = None 
    try:
        main.u_glitch_img_raw = pg.image.load("image/battle/u_glitch.png").convert_alpha()
    except:
        main.u_glitch_img_raw = None 
    
    main.forest_battle_done = False 
    main.pre_fight_map = None
    main.pre_fight_pos = (0, 0)
    main.MoveKeyQueue = []
    main.InteractKeyQueue = []

    main.state_pos = {}
    main.state_pos["home"] = [2300, 592]
    main.state_pos["forest_a"] = [1619, 550]
    main.state_pos["forest_b"] = [2280, 718]
    main.state_pos["forest_c"] = [3840, 750]
    main.state_pos["forest_d"] = [1380, 570]
    main.state_pos["forest_f"] = [1900, 690]
    main.state_pos["forest_g"] = [3750, 750]
    main.state_pos["forest_h"] = [2180, 672]
    main.state_pos["labg_a"] = [2480, 508]
    main.state_pos["labg_c"] = [1500, 508]
    main.state_pos["labg_d"] = [760, 2220]

    main.sound_assets = {} 
    main.current_music = None 
    setup.music_setup(main)
    
    global start_menu_var
    start_menu_var = start_menu.setup(main)
    global scene
    scene = {} 
    scene["pause_menu_var"] = pause_menu.setup(main)

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
    scene["labg_d_var"] = labg_d.setup(main)

    # 預設載入 Slot 0
    main.save_slot = 0
    main.game_data = GameData(0)
    # ★ 強制設為 -1，觸發初始化
    main.game_data.slot_index = -1 
    
    main.inventory = [] 
    main.game_state = "start_menu"

    main.home_door_unlocked = getattr(main.game_data, 'home_unlocked', False)
    main.cliff_is_locked = not getattr(main.game_data, 'cliff_unlocked', False)
    main.boat_unlocked = getattr(main.game_data, 'boat_unlocked', False)
    
    main.investigated_items = set() 
    main.run_wake_up_sequence = False 

    dialog_box.setup(main, font.pos)
    
    main.last_game_state = main.game_state
    main.last_pause_state = main.game_state
    main.captured_screen = None
    main.refreshing_pause_bg = False

def bgm_manager():
    if not hasattr(main, 'music_playlist'): return

    if main.game_state == "pause_menu":
        pg.mixer.music.set_volume(main.game_data.volume * 0.4)
        return
    if main.last_game_state.find("forest") != -1 and main.game_state.find("forest") != -1: return
    if main.last_game_state.find("lab") != -1 and main.game_state.find("lab") != -1: return
    if main.game_state in ["fight", "home"]:
        pg.mixer.music.pause()
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
        "labg_d_var": xo.VAR(),
    }
    
    main_initiate()
    print("zoom ratio=", main.zoom_ratio)
    
    while main.running:
        main.clock.tick(main.fps)

        # ------------------ 0. Wake Up 開場劇情處理 ------------------
        if getattr(main, 'run_wake_up_sequence', False) and main.game_state == "home":
            main.screen.fill((0, 0, 0))
            pg.display.flip()
            main.dialogue_ui.show("wake_up")
            main.run_wake_up_sequence = False
            main.game_data.intro_played = True
            safe_save(main)
            main.MoveKeyQueue = [] # 清空按鍵
            print("[System] Wake Up 劇情結束，已更新存檔。")

        # ------------------ 1. 事件處理 ------------------
        for event in pg.event.get():
            if event.type == pg.QUIT: main.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_t: pass
                elif event.key == pg.K_ESCAPE:
                    if main.game_state == "pause_menu": pass 
                    elif main.game_state != "start_menu": 
                        main.last_pause_state = main.game_state
                        main.game_state = "pause_menu"
                        main.captured_screen = main.screen.copy()
                        continue 
                elif event.key == pg.K_z:
                    if event.key not in main.InteractKeyQueue: main.InteractKeyQueue.append(event.key)
                    
                    if hasattr(main, 'char_u') and hasattr(main.char_u, 'map_x'):
                        p_w = main.char_u.rect.width if hasattr(main.char_u, 'rect') else 50
                        p_h = main.char_u.rect.height if hasattr(main.char_u, 'rect') else 50
                        player_world_rect = pg.Rect(main.char_u.map_x, main.char_u.map_y, p_w, p_h)

                        if main.game_state == "home":
                            triggers = {
                                "wire": pg.Rect(1950, 432, 50, 50), "coat": pg.Rect(1300, 528, 151, 72),
                                "crayon": pg.Rect(811, 600, 50, 50), "document": pg.Rect(2300, 592, 50, 50),
                                "door": pg.Rect(820, 880, 300, 40)
                            }
                            hit_obj = None
                            for key, rect in triggers.items():
                                if player_world_rect.colliderect(rect):
                                    hit_obj = key
                                    break
                            if hit_obj:
                                if hit_obj == "door":
                                    if len(main.investigated_items) >= 4:
                                        main.dialogue_ui.show("go_out")
                                        if not main.home_door_unlocked:
                                            main.home_door_unlocked = True 
                                            main.game_data.home_unlocked = True
                                            safe_save(main)
                                    else:
                                        main.dialogue_ui.show("locked_door")
                                elif hit_obj in ["document", "wire", "coat", "crayon"]:
                                    main.investigated_items.add(hit_obj)
                                    main.dialogue_ui.show(hit_obj)
                                    if len(main.investigated_items) == 4:
                                        main.dialogue_ui.show(f"{hit_obj}_last") 
                                        main.dialogue_ui.show("cat")

                        elif main.game_state == "forest_a":
                            sign_rect = pg.Rect(2050, 678, 50, 50)
                            if player_world_rect.colliderect(sign_rect): main.dialogue_ui.show("signpost")

                        elif main.game_state == "forest_g":
                            store_rect = pg.Rect(2100, 478, 400, 72)
                            dock_rect = pg.Rect(2200, 900, 80, 100)
                            if player_world_rect.colliderect(store_rect):
                                curr_dlg = "store"
                                in_shop = True
                                main.MoveKeyQueue.clear()
                                while in_shop:
                                    res = main.dialogue_ui.show(curr_dlg, current_money=main.game_data.money)
                                    if res is None or res == "end": in_shop = False
                                    elif res.startswith("buy_") and res != "buy_menu":
                                        key = res.split("_")[1]
                                        cost = 3 if key in ["nut", "drink"] else 5
                                        if main.game_data.money >= cost:
                                            main.game_data.money -= cost
                                            curr_dlg = "buy_success"
                                        else: curr_dlg = "buy_fail"
                                    else: curr_dlg = res
                            elif player_world_rect.colliderect(dock_rect):
                                if main.boat_unlocked:
                                    res = main.dialogue_ui.show("dock_travel")
                                    if res == "go_lake":
                                        main.game_state = "forest_d"
                                        main.char_u.map_x, main.char_u.map_y = 850, 500
                                        main.MoveKeyQueue.clear()
                                else:
                                    res = main.dialogue_ui.show("dock")
                                    if res == "boat_yes":
                                        main.boat_unlocked = True
                                        main.game_data.boat_unlocked = True
                                        safe_save(main)
                                        main.dialogue_ui.show("poem")
                                        main.game_state = "forest_d"
                                        main.char_u.map_x, main.char_u.map_y = 850, 500
                                        main.MoveKeyQueue.clear()

                        elif main.game_state == "forest_c":
                            cliff_rect = pg.Rect(1456, 270, 80, 80)
                            if player_world_rect.colliderect(cliff_rect):
                                main.dialogue_ui.show("cliff")
                                if main.cliff_is_locked:
                                    main.cliff_is_locked = False
                                    main.game_data.cliff_unlocked = True
                                    safe_save(main)

                        elif main.game_state == "forest_d":
                            lake_trigger = pg.Rect(788, 394, 112, 160)
                            if player_world_rect.colliderect(lake_trigger):
                                if main.boat_unlocked:
                                    # ★ 修改：呼叫 lake_intro_unlock -> 跳轉 menu -> 選擇 "boat"
                                    res = main.dialogue_ui.show("lake_menu_unlock")
                                    if res == "boat":
                                        main.game_state = "forest_g"
                                        main.char_u.map_x, main.char_u.map_y = 2240, 850 
                                        main.MoveKeyQueue.clear()
                                        print("[System] 搭船傳送回 forest_g")
                                else: 
                                    main.dialogue_ui.show("lake_intro")

                # ★★★ 移動判定 (補回) ★★★
                elif main.game_state != "pause_menu" and not main.is_glitching:
                    if event.key in [pg.K_w, pg.K_a, pg.K_s, pg.K_d, pg.K_UP, pg.K_LEFT, pg.K_DOWN, pg.K_RIGHT]:
                        if event.key not in main.MoveKeyQueue:
                            main.MoveKeyQueue.append(event.key)
                    elif event.key == pg.K_k:
                        main.pre_fight_map = main.game_state
                        main.pre_fight_pos = (main.char_u.map_x, main.char_u.map_y)
                        main.game_state = "fight"

            elif event.type == pg.KEYUP:
                if main.game_state != "pause_menu":
                    if event.key in main.MoveKeyQueue: main.MoveKeyQueue.remove(event.key)
                    elif event.key in main.InteractKeyQueue: main.InteractKeyQueue.remove(event.key)
            if main.game_state == "pause_menu": pause_menu.handle_input(main, scene["pause_menu_var"], event)

        bgm_manager()
        
        # [已移除隨機遇敵功能]

        main.play_animation = False
        if main.last_game_state != main.game_state and main.last_game_state != "pause_menu" and main.game_state != "pause_menu": 
            main.play_animation = True
        
        # ------------------ 2. 場景更新 ------------------
        match main.game_state:
            case "start_menu":
                start_menu.update(main, start_menu_var)
            case "home":
                if main.game_data.slot_index != main.save_slot:
                    print(f"[System] 偵測到存檔不符，強制重載 Slot {main.save_slot}！")
                    start_game_from_slot(main, main.save_slot)
                    scene["home_var"] = None 
                    continue 

                if scene.get("home_var") is None: scene["home_var"] = home.setup(main)
                scene = home.update(main, scene, font, scene["home_var"])
                
                if not main.home_door_unlocked:
                    if main.char_u.map_y > 880: main.char_u.map_y = 880
                else:
                    if main.char_u.map_y > 900:
                        main.game_state = "forest_a"
                        main.char_u.map_x, main.char_u.map_y = main.state_pos["forest_a"]
                        main.MoveKeyQueue.clear()

            case "forest_a":
                if scene.get("forest_a_var") is None: scene["forest_a_var"] = forest_a.setup(main)
                scene = forest_a.update(main, scene, font, scene["forest_a_var"])
            case "forest_b": scene = forest_b.update(main, scene, font, scene["forest_b_var"])
            case "forest_c":
                scene = forest_c.update(main, scene, font, scene["forest_c_var"])
                if main.cliff_is_locked:
                    if main.char_u.map_y < 270: main.char_u.map_y = 270
            case "forest_d":
                if scene.get("forest_d_var") is None: scene["forest_d_var"] = forest_d.setup(main)
                scene = forest_d.update(main, scene, font, scene["forest_d_var"])
            case "forest_e":
                import climb
                climb.update(main.w,main.h)
                main.game_state="forest_f"
                main.char_u.map_x,main.char_u.map_y=main.state_pos["forest_f"]
                main.MoveKeyQueue=[]
            case "forest_f": scene = forest_f.update(main, scene, font, scene["forest_f_var"])
            case "forest_g": scene = forest_g.update(main, scene, font, scene["forest_g_var"])
            case "forest_h": scene = forest_h.update(main, scene, font, scene["forest_h_var"])
            case "labg_a": scene=labg_a.update(main,scene,font,scene["labg_a_var"])
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
            case "labg_c": scene=labg_c.update(main,scene,font,scene["labg_c_var"])
            case "labg_d": scene=labg_d.update(main,scene,font,scene["labg_d_var"])
            case "labg_e":
                import labg_e
                main=labg_e.update(main.w,main.h,main)
                main.last_game_state="labg_e"
                main.MoveKeyQueue=[]
                continue
            case "fight":
                pg.mixer.music.stop() 
                
                # 1. 準備目前主角的位置資料
                current_pos = (0, 0)
                if hasattr(main, 'char_u') and hasattr(main.char_u, 'map_x'):
                    current_pos = (main.char_u.map_x, main.char_u.map_y)

                # 2. 呼叫戰鬥，並傳入 main.game_data (這包含了目前的 HP/MP)
                # 同時接收回傳值，以便更新戰鬥後的狀態 (例如扣血、升級、或戰敗)
                updated_data, updated_inv, _, _, battle_result = fight.run_battle(
                    main.screen, 
                    main.game_data, 
                    main.inventory, 
                    current_pos, 
                    main.pre_fight_map
                )

                # 3. 將戰鬥後的資料同步回 main 物件
                main.game_data = updated_data
                main.inventory = updated_inv

                # 4. 根據戰鬥結果處理流程
                if battle_result == "GAME_OVER":
                    # 如果戰敗，fight.py 已經將資料回溯到戰鬥前存檔的狀態
                    # 這裡重新載入場景以重置遊戲狀態
                    start_game_from_slot(main, main.save_slot)
                else:
                    # 戰勝或逃跑 (VICTORY / ESCAPE)
                    # 回到原本的地圖
                    if main.pre_fight_map:
                        main.game_state = main.pre_fight_map
                        main.char_u.map_x = main.pre_fight_pos[0]
                        main.char_u.map_y = main.pre_fight_pos[1]
                        main.char_u.map_x -= 50 # 稍微往左移一點，避免剛出來又撞到觸發點
                    else: 
                        main.game_state = "forest_g"
                    
                    main.forest_battle_done = True
                    main.MoveKeyQueue.clear()
            case "pause_menu": pause_menu.update(main, scene["pause_menu_var"])
            case _:
                if main.game_state != "pause_menu":
                    print("no game state:", main.game_state)
                    main.running = False

        # ======== forest_b 定點 Glitch 戰鬥觸發 (保留) ========
        if main.game_state == "forest_b":
            in_x = abs(main.char_u.map_y - 20) <= 1038
            in_y = 1080 <= main.char_u.map_x <= 1512
            if in_x and in_y and (not main.forest_battle_done):
                if not main.is_glitching:
                    print("Battle Triggered! Starting Glitch...")
                    main.is_glitching = True
                    main.glitch_start_time = pg.time.get_ticks() 
                    main.MoveKeyQueue.clear() 
                    if main.u_glitch_img_raw and hasattr(main.char_u, 'rect'):
                        target_size = (main.char_u.rect.width, main.char_u.rect.height)
                        main.scaled_glitch_current = pg.transform.scale(main.u_glitch_img_raw, target_size)
                    else: main.scaled_glitch_current = main.u_glitch_img_raw
                else:
                    if pg.time.get_ticks() - main.glitch_start_time >= 200: 
                        print("Glitch finished. Entering Fight Mode.")
                        main.is_glitching = False
                        main.scaled_glitch_current = None 
                        main.pre_fight_map = main.game_state
                        main.pre_fight_pos = (main.char_u.map_x, main.char_u.map_y)
                        main.game_state = "fight"
        # ====================================================

        if main.is_glitching and main.scaled_glitch_current:
            if hasattr(main.char_u, 'rect'):
                glitch_rect = main.scaled_glitch_current.get_rect(center=main.char_u.rect.center)
                main.screen.blit(main.scaled_glitch_current, glitch_rect)
            else: main.screen.blit(main.scaled_glitch_current, (main.w//2 - 50, main.h//2 - 50))

        if main.refreshing_pause_bg:
            main.captured_screen = main.screen.copy()
            main.game_state = "pause_menu"
            pause_menu.update(main, scene["pause_menu_var"])
            main.refreshing_pause_bg = False

        if main.game_state not in ["fight", "start_menu", "pause_menu"] and \
           hasattr(main, 'char_u') and hasattr(main.char_u, 'map_x'):
            p_w = main.char_u.rect.width if hasattr(main.char_u, 'rect') else 50
            p_h = main.char_u.rect.height if hasattr(main.char_u, 'rect') else 50
            player_world_rect = pg.Rect(main.char_u.map_x, main.char_u.map_y, p_w, p_h)
            current_triggers = []
            if main.game_state == "home":
                current_triggers = [pg.Rect(1950, 432, 50, 50), pg.Rect(1300, 528, 151, 72), pg.Rect(811, 600, 50, 50), pg.Rect(2300, 592, 50, 50), pg.Rect(820, 880, 300, 40)]
            elif main.game_state == "forest_a": current_triggers = [pg.Rect(2050, 678, 50, 50)] 
            elif main.game_state == "forest_c": current_triggers = [pg.Rect(1456, 270, 80, 80)]
            elif main.game_state == "forest_d": current_triggers = [pg.Rect(788, 394, 112, 160)] 
            elif main.game_state == "forest_g": current_triggers = [pg.Rect(2100, 478, 400, 72), pg.Rect(2200, 900, 80, 100)]
            for trig in current_triggers:
                if player_world_rect.colliderect(trig):
                    text_surf = font.ui.render("按 Z 互動", True, (255, 255, 0))
                    screen_x = main.char_u.rect.centerx - (text_surf.get_width() // 2)
                    screen_y = main.char_u.rect.top - 40 
                    bg_rect = text_surf.get_rect(topleft=(screen_x - 5, screen_y - 5))
                    bg_rect.width += 10; bg_rect.height += 10
                    s = pg.Surface((bg_rect.width, bg_rect.height)); s.set_alpha(150); s.fill((0, 0, 0))
                    main.screen.blit(s, (screen_x - 5, screen_y - 5))
                    main.screen.blit(text_surf, (screen_x, screen_y))
                    break 

        if main.game_state != "pause_menu": main.last_game_state = main.game_state
        pg.display.flip() 
    
    pg.quit()