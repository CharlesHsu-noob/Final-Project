import pygame as pg
import XddObjects as xo
import path_dictionary as pd
import os
import json
from gamedata import GameData

# ================= 設定區 =================

SAVE_DIR = "saves"

# 介面配色 (與 pause_menu 統一)
C = {
    'DARK': (90, 74, 66), 'MID': (141, 114, 89), 'LIGHT': (166, 138, 118),
    'BG_MAIN': (191, 164, 139), 'BG_SLOT': (214, 132, 115), 'WHITE': (250, 248, 245)
}

def check_slots():
    """讀取 3 個存檔的簡要資訊"""
    slots_data = [None] * 3
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    
    for i in range(3):
        path = os.path.join(SAVE_DIR, f"save_{i}.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                slots_data[i] = json.load(f)
        except:
            slots_data[i] = None
    return slots_data

def enter_game(game, slot_idx):
    """進入遊戲：有檔讀檔，沒檔新建"""
    path = os.path.join(SAVE_DIR, f"save_{slot_idx}.json")
    
    # 初始化資料
    game.game_data = GameData()
    game.inventory = [] 
    
    if os.path.exists(path):
        # --- 讀檔 ---
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            inv, pos, scene = game.game_data.load_from_dict(data)
            game.inventory = inv
            
            # 修正圖片載入狀態
            for item in game.inventory: item["icon"] = None 

            if scene: game.game_state = scene.lower()
            else: game.game_state = "home"
            
            if pos: game.char_u.map_x, game.char_u.map_y = pos
            
        except:
            # 讀檔發生嚴重錯誤時，強制視為新遊戲
            _create_new_game(game, path)
    else:
        # --- 新建 ---
        _create_new_game(game, path)

def _create_new_game(game, path):
    """建立新遊戲初始狀態並佔用存檔格"""
    game.game_data.reset()
    game.inventory = [] 
    
    game.game_state = "home"
    game.char_u.map_x, game.char_u.map_y = game.state_pos["home"]
    
    try:
        base_data = game.game_data.to_dict([], (game.char_u.map_x, game.char_u.map_y), "home")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(base_data, f, indent=4)
    except:
        pass

# ================= Setup =================

def setup(game:xo.VAR) -> xo.VAR :
    start = xo.VAR()
    start.button_list=[]
    
    # 背景
    start.bg = pg.transform.scale(pg.image.load(pd.start_menu_bg_path).convert_alpha(), (game.menu_w,game.menu_h))
    
    # 按鈕
    start.lamp = xo.buttonObject(pd.lamp_path, (0.838*game.menu_w, 0.338*game.menu_h), (318*game.zoom_ratio, 438*game.zoom_ratio))
    start.notebook = xo.buttonObject(pd.notebook_path, (0.642*game.menu_w, 0.731*game.menu_h), (255*game.zoom_ratio, 290*game.zoom_ratio))
    start.button_list.append(start.lamp)
    start.button_list.append(start.notebook)
    
    # 介面控制變數
    start.show_save_ui = False
    start.slots_data = [None] * 3
    
    # 尺寸縮放 helper
    s_x = lambda val: int(val * game.zoom_ratio)
    s_y = lambda val: int(val * game.zoom_ratio)
    
    # 定義存檔格區域
    slot_w, slot_h = s_x(240), s_y(80) 
    gap = s_y(20)
    start_x = (game.menu_w - slot_w) // 2
    start_y = (game.menu_h - (slot_h * 3 + gap * 2)) // 2 + s_y(50)
    
    start.slot_rects = []
    for i in range(3):
        r = pg.Rect(start_x, start_y + i * (slot_h + gap), slot_w, slot_h)
        start.slot_rects.append(r)
        
    start.close_rect = pg.Rect(0, 0, s_x(40), s_y(40))
    start.close_rect.centerx = game.menu_w // 2
    start.close_rect.top = start.slot_rects[-1].bottom + s_y(30)

    # 字體設定
    font_path = "font/NotoSansTC-VariableFont_wght.ttf"
    try:
        start.font_mid = pg.font.Font(font_path, int(25 * game.zoom_ratio))
        start.font_small = pg.font.Font(font_path, int(15 * game.zoom_ratio))
    except:
        start.font_mid = pg.font.SysFont("arial", int(25 * game.zoom_ratio))
        start.font_small = pg.font.SysFont("arial", int(15 * game.zoom_ratio))

    return start

def update(game:xo.VAR, start:xo.VAR) -> None:
    # 1. 繪製背景
    game.screen.blit(start.bg, (0,0))
    
    # 2. 繪製按鈕 (筆記本、燈)
    for button in start.button_list:
        button.update()
        game.screen.blit(button.image, button.rect)
        
    if start.show_save_ui:
        # 半透明黑底
        overlay = pg.Surface((game.menu_w, game.menu_h))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        game.screen.blit(overlay, (0,0))
        
        # 標題
        title = start.font_mid.render("選擇存檔進入", True, C['WHITE'])
        game.screen.blit(title, (game.menu_w//2 - title.get_width()//2, start.slot_rects[0].top - 50))

        mouse_pos = pg.mouse.get_pos()
        mouse_click = pg.mouse.get_pressed()[0]
        
        # 繪製三個存檔格
        for i, r in enumerate(start.slot_rects):
            is_hover = r.collidepoint(mouse_pos)
            
            # 格子繪製
            pg.draw.rect(game.screen, C['WHITE'], r, border_radius=6)
            border_c = C['MID'] if is_hover else C['LIGHT']
            border_w = 3 if is_hover else 1
            pg.draw.rect(game.screen, border_c, r, border_w, 6)
            
            # 存檔資訊顯示
            d = start.slots_data[i]
            
            # 序號
            game.screen.blit(start.font_mid.render(f"No.{i+1}", True, C['DARK']), (r.x + 10, r.y + 10))
            
            if d:
                # 顯示時間與遊玩時數
                time_str = d.get("timestamp", "")
                ts = int(d.get('playtime',0)); m, sc = divmod(ts, 60); h, m = divmod(m, 60)
                dur_str = f"Time: {h:02d}:{m:02d}:{sc:02d}"
                
                t_surf = start.font_small.render(time_str, True, C['DARK'])
                game.screen.blit(t_surf, (r.right - t_surf.get_width() - 10, r.y + 10))
                
                d_surf = start.font_small.render(dur_str, True, C['LIGHT'])
                game.screen.blit(d_surf, (r.x + 10, r.bottom - 25))
            else:
                # 空存檔
                empty_surf = start.font_mid.render("---- Empty ----", True, C['LIGHT'])
                game.screen.blit(empty_surf, empty_surf.get_rect(center=r.center))

            # 點擊處理
            if is_hover and mouse_click:
                enter_game(game, i)
                start.show_save_ui = False
                pg.time.wait(200)
                return

        # 關閉按鈕 (X)
        is_close_hover = start.close_rect.collidepoint(mouse_pos)
        pg.draw.circle(game.screen, C['BG_SLOT'] if is_close_hover else C['BG_MAIN'], start.close_rect.center, start.close_rect.width//2)
        x_surf = start.font_mid.render("X", True, C['WHITE'])
        game.screen.blit(x_surf, x_surf.get_rect(center=start.close_rect.center))
        
        if is_close_hover and mouse_click:
            start.show_save_ui = False
            pg.time.wait(200)

        return

    # ================= 主畫面邏輯 =================
    
    if start.notebook.ispress:
        start.slots_data = check_slots()
        
        # 判斷是否全空
        all_empty = all(d is None for d in start.slots_data)
        
        if all_empty:
            # 全空直接進 Slot 0
            enter_game(game, 0)
        else:
            # 開啟選擇視窗
            start.show_save_ui = True
            start.notebook.ispress = False 
            pg.time.wait(200)

    elif start.lamp.ispress:
        game.running = False