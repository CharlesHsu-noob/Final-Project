import os, json, time, pygame as pg
from datetime import datetime
import XddObjects as xo 

# 【修改 1】直接從 gamedata.py 引入，不重複定義
from gamedata import GameData

# ================= 核心類別 =================

class Slider:
    def __init__(self, rect, init_val=0.5):
        self.rect = rect
        self.val = max(0.0, min(1.0, init_val))

    def change_value(self, amount):
        self.val = max(0.0, min(1.0, self.val + amount))

    def set_value(self, new_val):
        self.val = max(0.0, min(1.0, new_val))

    def get_value(self):
        return self.val

    def draw(self, surface, c):
        pg.draw.rect(surface, c['LIGHT'], self.rect, border_radius=self.rect.height//2)
        fill_w = int(self.rect.width * self.val)
        if fill_w > 0:
            pg.draw.rect(surface, c['BG_MAIN'], (self.rect.x, self.rect.y, fill_w, self.rect.height), border_radius=self.rect.height//2)
        pg.draw.circle(surface, c['DARK'], (self.rect.x + fill_w, self.rect.centery), self.rect.height//2 + 3)

# ================= Setup 初始化 =================

def setup(main):
    v = xo.VAR()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 路徑
    v.IMG_DIR = os.path.join(base_dir, "image")
    v.IMG_BAG = os.path.join(v.IMG_DIR, "bag")
    v.IMG_MENU = os.path.join(v.IMG_DIR, "pause_menu")
    v.IMG_CHAR = os.path.join(v.IMG_DIR, "char")
    v.SAVE_DIR = os.path.join(base_dir, "saves")
    os.makedirs(v.SAVE_DIR, exist_ok=True)

    # UI 顏色庫
    v.C = {
        'DARK': (90, 74, 66), 'MID': (141, 114, 89), 'LIGHT': (166, 138, 118),
        'BG_MAIN': (191, 164, 139), 'BG_SLOT': (214, 132, 115), 'WHITE': (250, 248, 245)
    }

    # 縮放與 Helper
    v.UI_SCALE = min(main.w / 800, main.h / 600)
    v.s_x = lambda val: int(val * (main.w / 800))
    v.s_y = lambda val: int(val * (main.h / 600))
    v.s_rect = lambda x, y, w, h: pg.Rect(v.s_x(x), v.s_y(y), v.s_x(w), v.s_y(h))

    # 字體與圖片
    font_path = os.path.join(base_dir, "font", "NotoSansTC-VariableFont_wght.ttf")
    try:
        v.font_big = pg.font.Font(font_path, int(50 * v.UI_SCALE))
        v.font_mid = pg.font.Font(font_path, int(25 * v.UI_SCALE))
        v.font_small = pg.font.Font(font_path, int(15 * v.UI_SCALE))
    except:
        v.font_big = pg.font.SysFont("arial", int(50 * v.UI_SCALE))
        v.font_mid = pg.font.SysFont("arial", int(25 * v.UI_SCALE))
        v.font_small = pg.font.SysFont("arial", int(15 * v.UI_SCALE))

    v.load_icon = lambda f: pg.image.load(os.path.join(v.IMG_BAG, f)).convert_alpha() if os.path.exists(os.path.join(v.IMG_BAG, f)) else None
    
    # 符文圖片
    v.rune_assets = {}
    rune_map = {"血量":"berkano","智力":"laguz","暴擊":"dagaz","能量":"sowilo","攻擊":"tiwaz","防禦":"algiz"}
    for n, f in rune_map.items():
        p = os.path.join(v.IMG_BAG, f"rune_{f}.png")
        if os.path.exists(p): v.rune_assets[n] = pg.transform.smoothscale(pg.image.load(p), (60, 60))

    v.RUNES_DATA = [
        {"symbol":"ᛒ","name":"血量","stat":"HP"}, {"symbol":"ᛚ","name":"智力","stat":"INT"},
        {"symbol":"ᛞ","name":"暴擊","stat":"CRT"}, {"symbol":"ᛋ","name":"能量","stat":"ENG"},
        {"symbol":"ᛏ","name":"攻擊","stat":"ATK"}, {"symbol":"ᛉ","name":"防禦","stat":"DEF"}
    ]

    # 背景圖
    bg_p = os.path.join(v.IMG_MENU, "book1.png")
    if not os.path.exists(bg_p): bg_p = os.path.join(v.IMG_DIR, "book1.png")
    if os.path.exists(bg_p):
        raw = pg.image.load(bg_p).convert_alpha()
        ratio = (main.w * 0.85) / raw.get_width()
        v.bg = pg.transform.smoothscale(raw, (int(raw.get_width()*ratio), int(raw.get_height()*ratio)))
    else:
        v.bg = pg.Surface((v.s_x(640), v.s_y(420))); v.bg.fill(v.C['WHITE'])
    v.bg_rect = v.bg.get_rect(center=(main.w//2, main.h//2))

    # 連結 Main 的 GameData
    if hasattr(main, "game_data"):
        v.game_data = main.game_data
    else:
        v.game_data = GameData()

    v.save_slots = [None] * 3
    
    # 物品
    v.inventory_list = []
    v.ITEM_TEMPLATES = [
        {"name":"能量飲料", "desc":"能量+3", "type":"consumable", "effect":"ENG +3", "icon_file":"enrgdrnk.png"},
        {"name":"堅果棒", "desc":"血量回復20%", "type":"consumable", "effect":"HP +20%", "icon_file":"nutbar.png"},
        {"name":"空白符文", "desc":"點擊開啟刻印選單", "type":"rune", "effect":"Rune", "icon_file":"rune_empty.png"}
    ]
    v.item_map = {}
    for t in v.ITEM_TEMPLATES: v.item_map[t["name"]] = t["icon_file"]

    # 預設物品
    for init in [{"name":"能量飲料","count":-1}, {"name":"堅果棒","count":-1}, {"name":"空白符文","count":-1}]:
        tmpl = next((t for t in v.ITEM_TEMPLATES if t["name"] == init["name"]), None)
        if tmpl:
            item = tmpl.copy()
            item.update({"count":init["count"], "icon":v.load_icon(tmpl["icon_file"])})
            v.inventory_list.append(item)

    # UI 元件
    s_x, s_y, s_rect = v.s_x, v.s_y, v.s_rect
    v.btn_cont = s_rect(0,0,140,40); v.btn_cont.center = (s_x(225), s_y(210))
    v.btn_exit = s_rect(0,0,140,40); v.btn_exit.center = (s_x(225), s_y(440))
    
    v.slider_m = Slider(s_rect(130, 290, 200, 5), v.game_data.volume)
    v.slider_s = Slider(s_rect(130, 360, 200, 5), v.game_data.sfx_volume)
    
    v.slots = [s_rect(470, 150+i*90, 200, 75) for i in range(3)]
    v.btn_save = s_rect(0,0,80,35); v.btn_save.center = (s_x(520), s_y(440))
    v.btn_load = s_rect(0,0,80,35); v.btn_load.center = (s_x(620), s_y(440))
    
    # Page 2 UI
    v.P2_CHAR_N, v.P2_ITEM_N = 5, 3
    v.box_char = [pg.Rect(s_x(110+i*53), s_y(140), s_x(48), s_y(150)) for i in range(v.P2_CHAR_N)]
    v.box_item = [pg.Rect(0, s_y(140+i*52), s_x(180), s_y(40)) for i in range(v.P2_ITEM_N)]
    for r in v.box_item: r.centerx = s_x(560)
    v.desc_l = pg.Rect(s_x(110), s_y(360), s_x(250), s_y(130))
    v.desc_r = pg.Rect(0, s_y(360), s_x(250), s_y(130)); v.desc_r.centerx = s_x(560)

    v.overlay = pg.Surface((main.w, main.h)); v.overlay.fill((0,0,0)); v.overlay.set_alpha(150)
    
    # 狀態變數
    v.page = 1; v.cursor = [0,0]; v.alpha = 0
    v.fade_out = False; v.fade_in = True; v.ui_on = True
    v.p2_sect = 0; v.p2_c_idx = 0; v.p2_i_idx = 0
    v.POP_NONE, v.POP_RUNE, v.POP_TARGET, v.POP_MSG = 0, 1, 2, 3
    v.pop_st = v.POP_NONE; v.rune_cur = 0; v.tar_cur = 0; v.sel_rune = None
    v.msg = ""; v.msg_timer = 0; v.save_msg = ""; v.save_timer = 0; v.act_slot = 0
    v.first_init = True

    refresh_slots(v)
    return v

# ================= 邏輯處理 =================

def update_volume(main, v):
    vol_music = v.slider_m.get_value()
    vol_sfx = v.slider_s.get_value()
    v.game_data.volume = vol_music
    v.game_data.sfx_volume = vol_sfx
    pg.mixer.music.set_volume(vol_music)
    if hasattr(main, "sound_assets") and isinstance(main.sound_assets, dict):
        for sound in main.sound_assets.values():
            if hasattr(sound, "set_volume"):
                sound.set_volume(vol_sfx)

def refresh_slots(v):
    for i in range(3):
        try:
            with open(os.path.join(v.SAVE_DIR, f"save_{i}.json"), "r", encoding="utf-8") as f:
                v.save_slots[i] = json.load(f)
        except: v.save_slots[i] = None

def save_slot(main, v, idx):
    v.game_data.volume = v.slider_m.get_value()
    v.game_data.sfx_volume = v.slider_s.get_value()
    
    pos = (main.char_u.map_x, main.char_u.map_y) if hasattr(main, "char_u") else None
    scene = main.last_pause_state if hasattr(main, "last_pause_state") else main.game_state
    
    try:
        with open(os.path.join(v.SAVE_DIR, f"save_{idx}.json"), "w", encoding="utf-8") as f:
            json.dump(v.game_data.to_dict(v.inventory_list, pos, scene), f, indent=4)
        refresh_slots(v)
        return "存檔成功"
    except Exception as e: print(e); return "存檔失敗"

def load_slot(main, v, idx):
    path = os.path.join(v.SAVE_DIR, f"save_{idx}.json")
    if not os.path.exists(path): return "無存檔"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        inv, pos, scene_name = v.game_data.load_from_dict(data)
        
        v.slider_m.set_value(v.game_data.volume)
        v.slider_s.set_value(v.game_data.sfx_volume)
        update_volume(main, v)

        if scene_name:
            s_target = scene_name.lower()
            main.last_pause_state = s_target
            main.last_game_state = s_target
            main.game_state = s_target
            main.refreshing_pause_bg = True
        
        if pos and hasattr(main, "char_u"):
            main.char_u.map_x, main.char_u.map_y = pos[0], pos[1]
            if hasattr(main.char_u, "rect"):
                main.char_u.rect.x, main.char_u.rect.y = int(pos[0]), int(pos[1])

        main.inventory = inv
        v.inventory_list = inv
        for it in v.inventory_list:
            fname = v.item_map.get(it["name"])
            it["icon"] = v.load_icon(fname) if fname else None
        
        refresh_slots(v)
        return "讀檔成功"
    except Exception as e:
        print(f"讀檔錯誤: {e}")
        return "讀檔失敗"

def use_item(v, idx):
    if idx >= len(v.inventory_list): return
    
    if v.inventory_list[idx]["count"] <= -1:
        v.msg = "數量不足！"
        v.pop_st, v.msg_timer = v.POP_MSG, 30
        return

    if v.inventory_list[idx]["type"] == "rune": v.pop_st, v.rune_cur, v.sel_rune = v.POP_RUNE, 0, None
    else: v.pop_st, v.tar_cur, v.sel_rune = v.POP_TARGET, 0, None

def confirm_use(main, v):
    tar = v.game_data.party_data[v.tar_cur]
    item = v.inventory_list[v.p2_i_idx]
    log = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "char": tar["name"]}
    
    if v.sel_rune:
        log["source"], log["effect"] = f"符文:{v.sel_rune['name']}", f"{v.sel_rune['stat']} UP"
        v.msg = f"{tar['name']} 刻印了 [{v.sel_rune['name']}]！"
        if "runes" not in tar: tar["runes"] = []
        tar["runes"].append(v.sel_rune['name'])
    else:
        log["source"], log["effect"] = item["name"], item["effect"]
        v.msg = f"對 {tar['name']} 使用了 {item['name']}!"
        
        eff = item.get("effect", "")
        if "HP" in eff: 
            tar["hp"] = min(tar["hp"]+int(tar["max_hp"]*0.2), tar["max_hp"])
            
        if "ENG" in eff or "MP" in eff:
            cur_mp = tar.get("mp", 0)
            max_mp = tar.get("max_mp", 10)
            tar["mp"] = min(cur_mp + 3, max_mp)
    
    v.game_data.upgrade_log.append(log)
    item["count"] -= 1
    
    save_slot(main, v, 0)
    v.pop_st, v.msg_timer = v.POP_MSG, 50

# ================= 輸入與更新 =================

def update(main, v):
    if hasattr(main, "game_data"):
        v.game_data = main.game_data
    
    if hasattr(main, "inventory"):
        if v.first_init:
            if not main.inventory:
                new_items = []
                for t in v.ITEM_TEMPLATES:
                    item = t.copy()
                    item["count"] = -1
                    item["icon"] = v.load_icon(t["icon_file"])
                    new_items.append(item)
                main.inventory.extend(new_items)
            v.first_init = False

        v.inventory_list = main.inventory
        for item in v.inventory_list:
            if "icon" not in item or item["icon"] is None:
                fname = v.item_map.get(item["name"])
                item["icon"] = v.load_icon(fname) if fname else None

    if hasattr(main, "captured_screen"): main.screen.blit(main.captured_screen, (0,0))
    main.screen.blit(v.overlay, (0, 0))
    main.screen.blit(v.bg, v.bg_rect)
    
    layer = pg.Surface((main.w, main.h), pg.SRCALPHA)
    if v.fade_out:
        layer.set_alpha(v.alpha)
        draw_p1(main,v,layer) if v.page==1 else draw_p2(main,v,layer)
        v.alpha -= 30
        if v.alpha <= 0:
            v.alpha, v.fade_out, v.fade_in = 0, False, True
            v.page = 3 - v.page 
            if v.page==2: v.p2_sect, v.p2_c_idx = 0, 0
            else: v.cursor = [1, 0]
    elif v.fade_in:
        layer.set_alpha(v.alpha)
        draw_p1(main,v,layer) if v.page==1 else draw_p2(main,v,layer)
        v.alpha += 30
        if v.alpha >= 255: v.alpha, v.fade_in, v.ui_on = 255, False, True
    else:
        draw_p1(main,v,layer) if v.page==1 else draw_p2(main,v,layer)
        
    main.screen.blit(layer, (0, 0))
    if v.save_timer > 0: v.save_timer -= 1
    if v.pop_st == v.POP_MSG and v.msg_timer > 0: v.msg_timer -= 1
    
def handle_input(main, v, evt):
    if not v.ui_on or evt.type != pg.KEYDOWN: return
    
    if evt.key == pg.K_ESCAPE and v.pop_st == v.POP_NONE:
        target = getattr(main, "last_pause_state", None)
        if not target: target = getattr(main, "last_game_state", "home")
        main.game_state = target
        return

    if v.page == 1: inp_p1(main, v, evt)
    else: inp_p2(main, v, evt)

def inp_p1(main, v, e):
    c, r = v.cursor
    if e.key == pg.K_UP: 
        v.cursor[1] = 2 if c==1 and r>=3 else max(0, r-1)
    elif e.key == pg.K_DOWN: 
        # 修改處：取消 3->4 導向。c=1 時最大值設為 3 (存檔按鈕)
        v.cursor[1] = min(3, r+1) if c==0 else min(3, r+1)
    
    elif e.key == pg.K_LEFT:
        if c==1: 
            # 保留處：讀檔(r=4) 往左跳回 存檔(c=1, r=3)
            if r == 4: v.cursor = [1, 3] 
            else: v.cursor = [0, min(r,3)]
        elif r==1: 
            v.slider_m.change_value(-0.05); update_volume(main, v) 
        elif r==2: 
            v.slider_s.change_value(-0.05); update_volume(main, v) 
            
    elif e.key == pg.K_RIGHT:
        if c==0: 
            if r==1: v.slider_m.change_value(0.05); update_volume(main, v) 
            elif r==2: v.slider_s.change_value(0.05); update_volume(main, v) 
            else: v.cursor = [1, r]
        else:
            if r==3: v.cursor[1]=4
            else: v.fade_out, v.ui_on, v.alpha = True, False, 255
            
    elif e.key in (pg.K_RETURN, pg.K_SPACE, pg.K_z):
        if c==0:
            if r==0:
                target = getattr(main, "last_pause_state", None)
                if not target: target = getattr(main, "last_game_state", "home")
                main.game_state = target
            elif r==3: main.game_state = "start_menu"
        else:
            if r<=2: v.act_slot = r
            elif r==3: v.save_msg, v.save_timer = save_slot(main, v, v.act_slot), 60
            elif r==4: v.save_msg, v.save_timer = load_slot(main, v, v.act_slot), 60

def inp_p2(main, v, e):
    if v.pop_st == v.POP_RUNE:
        if e.key == pg.K_LEFT and v.rune_cur%2==1: v.rune_cur-=1
        elif e.key == pg.K_RIGHT and v.rune_cur%2==0: v.rune_cur+=1
        elif e.key == pg.K_UP and v.rune_cur>=2: v.rune_cur-=2
        elif e.key == pg.K_DOWN and v.rune_cur<=3: v.rune_cur+=2
        elif e.key in (pg.K_RETURN, pg.K_z): v.sel_rune=v.RUNES_DATA[v.rune_cur]; v.pop_st=v.POP_TARGET; v.tar_cur=0
        elif e.key == pg.K_ESCAPE: v.pop_st=v.POP_NONE
        return
    elif v.pop_st == v.POP_TARGET:
        if e.key == pg.K_UP: v.tar_cur = max(0, v.tar_cur-1)
        elif e.key == pg.K_DOWN: v.tar_cur = min(len(v.game_data.party_data)-1, v.tar_cur+1)
        elif e.key in (pg.K_RETURN, pg.K_z): confirm_use(main, v)
        elif e.key == pg.K_ESCAPE: v.pop_st = v.POP_RUNE if v.sel_rune else v.POP_NONE
        return
    elif v.pop_st == v.POP_MSG:
        v.pop_st = v.POP_NONE; return

    if v.p2_sect == 0:
        if e.key == pg.K_LEFT:
            if v.p2_c_idx > 0: v.p2_c_idx -= 1
            else: v.fade_out, v.ui_on, v.alpha = True, False, 255
        elif e.key == pg.K_RIGHT:
            if v.p2_c_idx < v.P2_CHAR_N-1: v.p2_c_idx += 1
            else: v.p2_sect=1; v.p2_i_idx=min(v.p2_i_idx, len(v.inventory_list)-1); v.p2_sect=0 if not v.inventory_list else 1
    else:
        if not v.inventory_list: v.p2_sect=0; return
        if e.key == pg.K_UP: v.p2_i_idx = max(0, v.p2_i_idx-1)
        elif e.key == pg.K_DOWN: v.p2_i_idx = min(len(v.inventory_list)-1, v.p2_i_idx+1)
        elif e.key == pg.K_LEFT: v.p2_sect, v.p2_c_idx = 0, v.P2_CHAR_N-1
        elif e.key in (pg.K_RETURN, pg.K_z): use_item(v, v.p2_i_idx)

# ================= 繪圖 =================

def draw_txt(surf, lines, x, y, font, c, lh):
    for i, l in enumerate(lines.split('\n')): surf.blit(font.render(l, True, c), (x, y+i*lh))

def draw_p1(main, v, s):
    C = v.C; sx, sy = v.s_x, v.s_y
    s.blit(v.font_big.render("遊戲暫停", True, C['DARK']), (sx(150), sy(100)))
    
    sel = (v.cursor[0]==0)
    for i, (r, txt) in enumerate([(v.btn_cont,"繼續遊戲"),(None,""),(None,""),(v.btn_exit,"退出遊戲")]):
        if not r: continue
        now = (sel and v.cursor[1]==i)
        pg.draw.rect(s, C['BG_MAIN'], r, 2, sx(6))
        if now: pg.draw.rect(s, C['MID'], r, 3, sx(6))
        t = v.font_mid.render(txt, True, C['MID'] if now else C['BG_MAIN'])
        s.blit(t, t.get_rect(center=r.center))
    
    for i, (sl, t) in enumerate([(v.slider_m,"音樂"),(v.slider_s,"音效")]):
        sl.draw(s, C)
        if sel and v.cursor[1]==i+1: pg.draw.rect(s, C['BG_SLOT'], sl.rect.inflate(10,20), 2, 5)
        val = sl.get_value() 
        s.blit(v.font_small.render(f"{t}: {int(val*100)}%", True, C['DARK']), (sx(180), sy(260+i*70)))

    s.blit(v.font_mid.render("冒險紀錄", True, C['DARK']), (sx(530), sy(110)))
    for i, r in enumerate(v.slots):
        me = (v.cursor==[1,i]); act = (i==v.act_slot)
        pg.draw.rect(s, C['WHITE'], r, border_radius=sx(6))
        pg.draw.rect(s, C['MID'] if me else (C['BG_MAIN'] if act else C['LIGHT']), r, 3 if me or act else 1, sx(6))
        s.blit(v.font_mid.render(f"No.{i+1}", True, C['DARK']), (r.x+sx(10), r.y+sy(10)))
        d = v.save_slots[i]
        if d:
            s.blit(v.font_small.render(d.get("timestamp",""), True, C['DARK']), (r.right-sx(90), r.y+sy(10)))
            ts = int(d.get('playtime',0)); m, sc = divmod(ts, 60); h, m = divmod(m, 60)
            s.blit(v.font_small.render(f"Time: {h:02d}:{m:02d}:{sc:02d}", True, C['LIGHT']), (r.x+sx(10), r.bottom-sy(25)))
        else: s.blit(v.font_mid.render("----", True, C['LIGHT']), (r.centerx-sx(10), r.centery-sy(5)))
    
    for i, (r, t) in enumerate([(v.btn_save,"存檔"), (v.btn_load,"讀檔")]):
        idx = i + 3
        f = (v.cursor==[1, idx])
        pg.draw.rect(s, C['BG_MAIN'], r, 2, sx(6))
        if f: pg.draw.rect(s, C['MID'], r, 3, sx(6))
        ts = v.font_mid.render(t, True, (255,255,255) if f else C['BG_MAIN'])
        s.blit(ts, ts.get_rect(center=r.center))
    
    if v.save_timer > 0:
        m = v.font_small.render(v.save_msg, True, C['BG_SLOT'])
        s.blit(m, m.get_rect(center=(sx(570), v.btn_save.bottom+sy(25))))
    pg.draw.polygon(s, C['MID'], [(sx(710), main.h//2+sy(10)), (sx(690), main.h//2), (sx(690), main.h//2+sy(20))])

def draw_p2(main, v, s):
    C = v.C; sx, sy = v.s_x, v.s_y
    s.blit(v.font_mid.render("角色", True, C['DARK']), (sx(210), sy(100)))

    for i, r in enumerate(v.box_char):
        f = (v.p2_sect==0 and v.p2_c_idx==i and v.pop_st==v.POP_NONE)
        pg.draw.rect(s, C['WHITE'], r, border_radius=sx(6))
        pg.draw.rect(s, C['MID'] if f else C['LIGHT'], r, 3 if f else 1, sx(6))
        d = v.game_data.party_data[i]
        n = v.font_mid.render(d['name'], True, C['DARK']); s.blit(n, n.get_rect(center=(r.centerx, r.y+sy(20))))
        
        if d['name'] == "U":
            try:
                img = pg.image.load(os.path.join(v.IMG_CHAR, "U", "u_stand.png")).convert_alpha()
                sc = min((r.w-sx(10))/img.get_width(), sy(65)/img.get_height())
                s.blit(pg.transform.smoothscale(img, (int(img.get_width()*sc), int(img.get_height()*sc))), (r.x+sx(5), r.centery-sy(35)))
            except: pass
        
            hp_rect = pg.Rect(r.x+sx(6), r.bottom-sy(38), r.w-sx(12), sy(8))
            pg.draw.rect(s, (200,200,200), hp_rect, border_radius=3)
            if d['max_hp'] > 0 and d['hp'] > 0:
                w = hp_rect.w * (d['hp'] / d['max_hp'])
                pg.draw.rect(s, (167,191,139), (hp_rect.x, hp_rect.y, w, hp_rect.h), border_radius=3)
            pg.draw.rect(s, (150,150,150), hp_rect, 1, border_radius=3)

            mp_rect = pg.Rect(r.x+sx(6), r.bottom-sy(25), r.w-sx(12), sy(8))
            pg.draw.rect(s, (200,200,200), mp_rect, border_radius=3)
            max_mp = d.get('max_mp', 0)
            cur_mp = d.get('mp', 0)
            if max_mp > 0 and cur_mp > 0:
                w = mp_rect.w * (cur_mp / max_mp)
                pg.draw.rect(s, (100, 180, 255), (mp_rect.x, mp_rect.y, w, mp_rect.h), border_radius=3)
            pg.draw.rect(s, (150,150,150), mp_rect, 1, border_radius=3)

    pg.draw.rect(s, C['BG_MAIN'], v.desc_l, 2, sx(6))
    cd = v.game_data.party_data[v.p2_c_idx]
    
    status_str = f"[ {cd['name']} ]  HP: {cd['hp']}/{cd['max_hp']}"
    if cd['name'] == "U":
        status_str += f"  MP: {cd.get('mp',0)}/{cd.get('max_mp',0)}"
        
    s.blit(v.font_small.render(status_str, True, C['DARK']), (v.desc_l.x+sx(10), v.desc_l.y+sy(10)))
    s.blit(v.font_small.render("Runes: "+(", ".join(cd.get("runes",[])) or "None"), True, C['LIGHT']), (v.desc_l.x+sx(10), v.desc_l.y+sy(35)))
    draw_txt(s, cd['desc'], v.desc_l.x+sx(10), v.desc_l.y+sy(60), v.font_small, C['LIGHT'], sy(20))

    s.blit(v.font_mid.render("背包", True, C['DARK']), (sx(540), sy(100)))
    for i, r in enumerate(v.box_item):
        if i >= len(v.inventory_list): break
        f = (v.p2_sect==1 and v.p2_i_idx==i and v.pop_st==v.POP_NONE)
        pg.draw.rect(s, C['WHITE'], r, border_radius=sx(6))
        pg.draw.rect(s, C['MID'] if f else C['LIGHT'], r, 3 if f else 1, sx(6))
        it = v.inventory_list[i]
        
        if it['count'] <= -1: txt_color = (180, 180, 180)
        else: txt_color = C['DARK'] if f else C['LIGHT']

        if it.get("icon"): s.blit(pg.transform.smoothscale(it["icon"], (32,32)), (r.x+sx(5), r.centery-16))
        s.blit(v.font_mid.render(it["name"], True, txt_color), (r.x+sx(45 if it.get("icon") else 10), r.centery-sy(15)))
        s.blit(v.font_mid.render(f"x{it['count'] + 1}", True, txt_color), (r.right-sx(35), r.centery-sy(15)))

    pg.draw.rect(s, C['BG_MAIN'], v.desc_r, 2, sx(6))
    if v.inventory_list and v.p2_i_idx < len(v.inventory_list):
        it = v.inventory_list[v.p2_i_idx]
        s.blit(v.font_small.render(f"[ {it['name']} ]", True, C['DARK']), (v.desc_r.x+sx(10), v.desc_r.y+sy(10)))
        draw_txt(s, it['desc'], v.desc_r.x+sx(10), v.desc_r.y+sy(35), v.font_small, C['LIGHT'], sy(20))
    
    if v.pop_st == v.POP_NONE:
        pg.draw.polygon(s, C['MID'], [(sx(90), main.h//2+sy(10)), (sx(110), main.h//2), (sx(110), main.h//2+sy(20))])
    else: draw_popup(main, v, s)

def draw_popup(main, v, s):
    C = v.C; sx, sy = v.s_x, v.s_y
    mask = pg.Surface((main.w,main.h), pg.SRCALPHA); mask.fill((0,0,0,140)); s.blit(mask,(0,0))
    cx, cy = main.w//2, main.h//2
    
    if v.pop_st == v.POP_RUNE:
        r = v.s_rect(0,0,420,320); r.center = (cx,cy)
        pg.draw.rect(s, C['WHITE'], r, border_radius=10); pg.draw.rect(s, C['BG_MAIN'], r, 3, 10)
        t = v.font_mid.render("選擇刻印符文", True, C['DARK']); s.blit(t, t.get_rect(center=(cx, r.top+sy(30))))
        for i, rune in enumerate(v.RUNES_DATA):
            rr = pg.Rect(r.centerx-sx(190)+(i%2)*sx(200), r.top+sy(80)+(i//2)*sy(70), sx(180), sy(55))
            me = (i == v.rune_cur)
            pg.draw.rect(s, (255,255,255) if me else (242,235,225), rr, border_radius=5)
            pg.draw.rect(s, C['MID'] if me else C['BG_MAIN'], rr, 2, 5)
            if rune['name'] in v.rune_assets:
                img = v.rune_assets[rune['name']]; s.blit(img, img.get_rect(midleft=(rr.left+sx(10), rr.centery)))
            s.blit(v.font_mid.render(rune['name'], True, C['MID'] if me else C['BG_MAIN']), (rr.left+sx(80), rr.centery-10))
            
    elif v.pop_st == v.POP_TARGET:
        r = v.s_rect(0,0,300,300); r.center = (cx,cy)
        pg.draw.rect(s, C['WHITE'], r, border_radius=10); pg.draw.rect(s, C['BG_MAIN'], r, 3, 10)
        t = v.font_mid.render("選擇對象", True, C['DARK']); s.blit(t, t.get_rect(center=(cx, r.top+sy(30))))
        for i, c in enumerate(v.game_data.party_data):
            tr = pg.Rect(r.left+sx(20), r.top+sy(70)+i*sy(40), r.w-sx(40), sy(35))
            if i==v.tar_cur: pg.draw.rect(s, C['MID'], tr, border_radius=5)
            s.blit(v.font_mid.render(c["name"], True, (255,255,255) if i==v.tar_cur else C['DARK']), (tr.x+sx(10), tr.centery-10))
            
    elif v.pop_st == v.POP_MSG:
        r = v.s_rect(0,0,320,120); r.center = (cx,cy)
        pg.draw.rect(s, C['WHITE'], r, border_radius=10); pg.draw.rect(s, C['BG_SLOT'], r, 2, 10)
        draw_txt(s, v.msg, r.x+sx(20), r.y+sy(25), v.font_mid, C['DARK'], sy(30))