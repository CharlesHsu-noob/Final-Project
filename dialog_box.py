import pygame as pg
import sys
from gamedata import GameData, save_game_to_file, load_game_from_file, update_shop_data

WIDTH, HEIGHT = 800, 600

UI_SETTINGS = {
    "BOX_COLOR": (20, 20, 20), "BORDER_COLOR": (255, 255, 255),
    "BOX_X": 50, "BOX_Y": HEIGHT - 180, "BOX_W": WIDTH - 100, "BOX_H": 160,
    "TEXT_X": 30, "TEXT_Y": 30,
    "OPTION_X": 50, "OPTION_START_Y": 40, "OPTION_SPACING": 35, "TYPING_SPEED": 30, "COL_GAP": 350,
}

ITEM_DB = {
    "nut":   {"name": "堅果棒",   "desc": "恢復 10 HP", "type": "consumable", "icon_file": "icon_food.png"},
    "drink": {"name": "能量飲料", "desc": "恢復 20 HP", "type": "consumable", "icon_file": "icon_potion.png"},
    "rune":  {"name": "空白符文", "desc": "可注入技能", "type": "material",   "icon_file": "icon_rune.png"}
}

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("RPG：對話系統 (不影響大地圖座標版)")

try:
    font_path = "C:\\Windows\\Fonts\\msjh.ttc"
    font = pg.font.Font(font_path, 24)
    small_font = pg.font.Font(font_path, 20)
except:
    font = pg.font.Font(None, 32)
    small_font = pg.font.Font(None, 24)

clock = pg.time.Clock()

DIALOGUES = {
    "cliff": [{"type": "text", "content": "墨星往上爬了"}, {"type": "text", "content": "之後要買個貓爬架給牠"}, {"type": "end"}],
    "lake_intro": [{"type": "text", "content": "一個生機蓬勃的湖泊"}, {"type": "jump", "next": "lake_menu"}],
    "lake_intro_unlock": [{"type": "text", "content": "一個生機蓬勃的湖泊"}, {"type": "jump", "next": "lake_menu_unlock"}],
    "lake_menu": [{"type": "choice", "options": [{"text": "釣魚", "next": "no_rod"}, {"text": "離開", "next": "exit_prompt"}]}],
    "lake_menu_unlock": [{"type": "choice", "options": [{"text": "搭船", "next": "boat"}, {"text": "釣魚", "next": "no_rod_unlock"}, {"text": "離開", "next": "exit_prompt"}]}],
    "boat": [{"type": "end"}],
    "no_rod": [{"type": "text", "content": "你發現你沒有釣竿"}, {"type": "jump", "next": "lake_menu"}],
    "no_rod_unlock": [{"type": "text", "content": "你沒有釣竿 只能看著魚發呆"}, {"type": "jump", "next": "lake_menu_unlock"}],
    "exit_prompt": [{"type": "text", "content": "於是你轉身向山裡走去"}, {"type": "end"}],
    "signpost": [{"type": "text", "content": "   <---森林 小鎮--->   "}, {"type": "text", "content": "墨星怕人 絕對不可能往鎮上走 我應該去森林裡找牠"}, {"type": "end"}],
    "dock": [{"type": "text", "content": "要搭船嗎？"}, {"type": "choice", "options": [{"text": "是", "next": "boat_yes"}, {"text": "否", "next": "end"}]}],
    "boat_yes": [{"type": "end"}],
    "poem": [{"type": "text", "content": "我願順流而下 找尋她的方向"}, {"type": "end"}],
    "store": [{"type": "choice", "options": [{"text": "購物", "next": "buy_menu"}, {"text": "對話", "next": "busnessman_talk"}, {"text": "離開", "next": "end"}]}],
    "buy_menu": [{"type": "choice", "options": [{"text": "堅果棒 3$", "next": "buy_nut"}, {"text": "能量飲料 3$", "next": "buy_drink"}, {"text": "空白符文 5$", "next": "buy_rune"}, {"text": "返回", "next": "store"}]}],
    "buy_nut": [{"type": "end"}], "buy_drink": [{"type": "end"}], "buy_rune": [{"type": "end"}],
    "buy_success": [{"type": "text", "content": "交易成功！"}, {"type": "jump", "next": "buy_menu"}],
    "buy_fail": [{"type": "text", "content": "你的錢不夠..."}, {"type": "jump", "next": "buy_menu"}],
    "busnessman_talk": [{"type": "choice", "options": [{"text": "你是誰", "next": "who_are_you"}, {"text": "為什麼有人會想在這種地方開店阿", "next": "why_here"}, {"text": "返回", "next": "store"}]}],
    "who_are_you": [{"type": "text", "content": "一個提供幫助的人。"}, {"type": "jump", "next": "busnessman_talk"}],
    "why_here": [{"type": "text", "content": "為什麼會有人想要來這種地方玩啊。"}, {"type": "jump", "next": "busnessman_talk"}],
    "wake_up": [{"type": "text", "content": "......"}, {"type": "text", "content": "今天...有點安靜......"}, {"type": "end"}],
    "document": [{"type": "text", "content": "(一疊被打亂的文件)"}, {"type": "end"}],
    "document_last": [{"type": "text", "content": "我真該在放墨星進來之前把資料收好..."}, {"type": "end"}],
    "wire": [{"type": "text", "content": "(一條充滿咬痕的吉他導線)"}, {"type": "end"}],
    "wire_last": [{"type": "text", "content": "這大概是墨星咬壞的第800條導線了..."}, {"type": "end"}],
    "coat": [{"type": "text", "content": "(被丟在地上的大衣)"}, {"type": "end"}],
    "coat_last": [{"type": "text", "content": "明明已經買貓窩給牠了 墨星還是喜歡睡在外套上..."}, {"type": "end"}],
    "crayon": [{"type": "text", "content": "(昨天畫完畫忘記收起來的蠟筆)"}, {"type": "end"}],
    "crayon_last": [{"type": "text", "content": "幸好墨星沒有把這當食物..."}, {"type": "end"}],
    "cat": [{"type": "text", "content": "不對...墨星!"}, {"type": "text", "content": "難怪那麼安靜 牠一定又跑出去了"}, {"type": "text", "content": "我要出去找牠!"}, {"type": "end"}],
    "go_out": [{"type": "text", "content": "手機 錢包 鑰匙..."}, {"type": "text", "content": "都帶了 出門吧"}, {"type": "end"}],
    "locked_door": [{"type": "text", "content": "(現在還不能出門 得先確認家裡的情況...)"}, {"type": "end"}]
}

class DialogueSystem:
    def __init__(self, screen, font, small_font, dialogue_data):
        self.screen = screen; self.font = font; self.small_font = small_font; self.dialogue_data = dialogue_data
        self.clock = pg.time.Clock()

    def _draw_box(self):
        box = pg.Rect(UI_SETTINGS["BOX_X"], UI_SETTINGS["BOX_Y"], UI_SETTINGS["BOX_W"], UI_SETTINGS["BOX_H"])
        pg.draw.rect(self.screen, UI_SETTINGS["BOX_COLOR"], box); pg.draw.rect(self.screen, UI_SETTINGS["BORDER_COLOR"], box, 2)
        return box

    def show(self, key, current_money=None):
        if key not in self.dialogue_data: return None
        bg_snap = self.screen.copy(); current_pages = self.dialogue_data[key]; current_key = key 
        index = 0; option_index = 0; displayed_text = ""; target_text = ""; char_index = 0; last_typing_time = 0; page_init = True; running_dialogue = True

        while running_dialogue:
            current_time = pg.time.get_ticks(); self.clock.tick(60)
            if index >= len(current_pages): break
            cur = current_pages[index]
            if cur["type"] == "jump":
                if cur["next"] in self.dialogue_data: current_key = cur["next"]; current_pages = self.dialogue_data[cur["next"]]; index = 0; option_index = 0; page_init = True; continue
                else: break
            if cur["type"] == "end": break
            if page_init:
                if cur["type"] == "text": target_text = cur["content"]; displayed_text = ""; char_index = 0; last_typing_time = current_time
                page_init = False
            if cur["type"] == "text":
                if char_index < len(target_text):
                    if current_time - last_typing_time > UI_SETTINGS["TYPING_SPEED"]: char_index += 1; displayed_text = target_text[:char_index]; last_typing_time = current_time
                else: displayed_text = target_text

            self.screen.blit(bg_snap, (0, 0)); box = self._draw_box()
            if current_money is not None:
                money_surf = self.small_font.render(f"持有金錢: ${current_money}", True, (255, 223, 0))
                self.screen.blit(money_surf, money_surf.get_rect(topright=(box.right - 30, box.y + 20)))
            hint_str = "[X] 關閉" + ("   [Z] 繼續" if cur["type"]=="text" and char_index>=len(target_text) else "   [↑↓] 選擇   [Z] 確定" if cur["type"]=="choice" else "")
            self.screen.blit(self.small_font.render(hint_str, True, (150, 150, 150)), (box.right - 220, box.bottom - 25))

            if cur["type"] == "text": self.screen.blit(self.font.render(displayed_text, True, (255, 255, 255)), (box.x + UI_SETTINGS["TEXT_X"], box.y + UI_SETTINGS["TEXT_Y"]))
            elif cur["type"] == "choice":
                for i, opt in enumerate(cur["options"]):
                    x_pos = box.x + UI_SETTINGS["OPTION_X"] + ((0 if i < 3 else 1) * UI_SETTINGS["COL_GAP"] if len(cur["options"])>3 else 0)
                    y_pos = box.y + UI_SETTINGS["OPTION_START_Y"] + ((i if i < 3 else i - 3) * UI_SETTINGS["OPTION_SPACING"])
                    self.screen.blit(self.font.render(f"{'> ' if i==option_index else '   '}{opt['text']}", True, (255, 230, 80) if i == option_index else (255, 255, 255)), (x_pos, y_pos))
            pg.display.flip()

            for event in pg.event.get():
                if event.type == pg.QUIT: pg.quit(); sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_x: running_dialogue = False; current_key = None; break
                    if cur["type"] == "text" and event.key == pg.K_z:
                        if char_index < len(target_text): char_index = len(target_text); displayed_text = target_text
                        else: index += 1; page_init = True
                    elif cur["type"] == "choice":
                        if event.key == pg.K_UP: option_index = (option_index - 1) % len(cur["options"])
                        if event.key == pg.K_DOWN: option_index = (option_index + 1) % len(cur["options"])
                        if event.key == pg.K_z:
                            selected = cur["options"][option_index]
                            if "next" in selected:
                                current_key = selected["next"]
                                if selected["next"] == "end" or selected["next"].startswith("buy_"): running_dialogue = False
                                else: current_pages = self.dialogue_data[selected["next"]]; index = 0; option_index = 0; page_init = True
                            else: running_dialogue = False
        return current_key

class Player(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.Surface((30, 30)); self.image.fill((255, 100, 100)); self.rect = self.image.get_rect(topleft=(x, y)); self.speed = 5
    def move(self, keys):
        if keys[pg.K_LEFT]: self.rect.x -= self.speed
        if keys[pg.K_RIGHT]: self.rect.x += self.speed
        if keys[pg.K_UP]: self.rect.y -= self.speed
        if keys[pg.K_DOWN]: self.rect.y += self.speed

def pack_inventory_for_save(inventory_dict):
    save_list = []
    for key, count in inventory_dict.items():
        if count > 0 and key in ITEM_DB: item_data = ITEM_DB[key].copy(); item_data["count"] = count; save_list.append(item_data)
    return save_list

def main():
    player = Player(400, 300)
    dlg_sys = DialogueSystem(screen, font, small_font, DIALOGUES)

    # 1. 讀檔：只讀取進度，忽略 loaded_pos (座標)
    try:
        game_data, loaded_inv_list, _, loaded_scene = load_game_from_file()
    except Exception as e:
        print(f"[系統] 讀檔異常 ({e})，重置為 HOME"); game_data = GameData(); loaded_inv_list = []; loaded_scene = "HOME"

    scene = loaded_scene if loaded_scene else "HOME"
    inventory = { "nut": 0, "drink": 0, "rune": 0 }

    # ★ 關鍵：測試版的起始座標寫死在場景預設點，完全不讀取存檔裡的數字
    if scene == "HOME": player.rect.topleft = (400, 300)
    elif scene == "forest_b": player.rect.topleft = (380, 520)
    else: player.rect.topleft = (400, 300)

    reverse_map = {v['name']: k for k, v in ITEM_DB.items()}
    if loaded_inv_list:
        for item in loaded_inv_list:
            c_name = item.get('name')
            if c_name in reverse_map: inventory[reverse_map[c_name]] = item.get('count', 0)

    print(f"[系統] 測試系統啟動。當前場景: {scene}。")
    
    if scene == "HOME" and (loaded_scene is None or loaded_scene == "HOME") and game_data.total_playtime < 0.1: dlg_sys.show("wake_up")

    home_triggers = { "document": pg.Rect(200, 200, 50, 50), "wire": pg.Rect(500, 400, 50, 50), "coat": pg.Rect(200, 400, 50, 50), "crayon": pg.Rect(500, 200, 50, 50), "door": pg.Rect(350, 550, 100, 20) }
    world_triggers = { "shop": pg.Rect(600, 400, 80, 80), "dock": pg.Rect(600, 100, 80, 80), "lake": pg.Rect(100, 400, 100, 100), "sign": pg.Rect(380, 50, 40, 40), "home_in": pg.Rect(350, 550, 100, 20), "cliff": pg.Rect(50, 50, 100, 50) }

    poem_seen = False; boat_unlocked = False; investigated_items = set(); can_leave_home = False
    running = True
    while running:
        clock.tick(60); player.move(pg.key.get_pressed())
        for event in pg.event.get():
            if event.type == pg.QUIT: running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_z: 
                if scene == "HOME":
                    for k, r in home_triggers.items():
                        if player.rect.colliderect(r) and k!="door":
                            if k not in investigated_items:
                                investigated_items.add(k); dlg_sys.show(f"{k}")
                                if len(investigated_items) == 4: dlg_sys.show("cat"); can_leave_home = True
                            else: dlg_sys.show(f"{k}") # 已調查過則顯示一般內容
                    if player.rect.colliderect(home_triggers["door"]):
                        if can_leave_home:
                            dlg_sys.show("go_out"); scene = "forest_b"; player.rect.topleft = (380, 500)
                            # ★ 切換場景存檔：座標傳 None，絕對不改大地圖位置
                            save_game_to_file(game_data, pack_inventory_for_save(inventory), None, "forest_b")
                        else: dlg_sys.show("locked_door")
                elif scene == "forest_b":
                    if player.rect.colliderect(world_triggers["shop"]):
                        in_shop = True; current_key = "store"
                        while in_shop:
                            res = dlg_sys.show(current_key, current_money=game_data.money)
                            if res is None or res == "end": in_shop = False
                            elif res.startswith("buy_") and res != "buy_menu":
                                item_key = res.split("_")[1]; cost = 3 if item_key in ["nut", "drink"] else 5
                                if game_data.money >= cost:
                                    game_data.money -= cost; inventory[item_key] += 1
                                    # ★ 商店存檔：調用 update_shop_data，其內部已設定不改座標
                                    update_shop_data(game_data.money, pack_inventory_for_save(inventory))
                                    current_key = "buy_success"
                                else: current_key = "buy_fail"
                            else: current_key = res
                    elif player.rect.colliderect(world_triggers["dock"]):
                        if dlg_sys.show("dock")=="boat_yes" and not poem_seen: dlg_sys.show("poem"); poem_seen=True; boat_unlocked=True
                    elif player.rect.colliderect(world_triggers["lake"]): dlg_sys.show("lake_intro_unlock" if boat_unlocked else "lake_intro")
                    elif player.rect.colliderect(world_triggers["sign"]): dlg_sys.show("signpost")
                    elif player.rect.colliderect(world_triggers["cliff"]): dlg_sys.show("cliff")
                    elif player.rect.colliderect(world_triggers["home_in"]):
                        scene = "HOME"; player.rect.topleft = (380, 500)
                        # ★ 切換場景存檔：座標傳 None
                        save_game_to_file(game_data, pack_inventory_for_save(inventory), None, "HOME")

        screen.fill((0, 0, 0))
        if scene == "HOME":
            screen.fill((50, 40, 30)); 
            for k, r in home_triggers.items(): pg.draw.rect(screen, (200, 200, 200) if k!="door" else (100, 50, 0), r)
        elif scene == "forest_b":
            screen.fill((40, 100, 40)); 
            for k, r in world_triggers.items(): 
                c = (200, 200, 0) if k=="shop" else (100, 100, 200) if k=="dock" else (0, 200, 255) if k=="lake" else (139, 69, 19) if k=="sign" else (100, 50, 0) if k=="home_in" else (100, 100, 100)
                pg.draw.rect(screen, c, r) if k!="lake" else pg.draw.ellipse(screen, c, r)

        screen.blit(player.image, player.rect)
        screen.blit(small_font.render(f"測試模式 | 場景: {scene} | 錢: {game_data.money} | 堅果:{inventory['nut']} 飲料:{inventory['drink']}", True, (255, 255, 255)), (10, 10))
        pg.display.flip()

    pg.quit()

if __name__ == "__main__": main()