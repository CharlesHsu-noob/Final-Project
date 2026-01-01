import pygame as pg
import sys

# ==========================
# 1. 介面與參數設定
# ==========================
WIDTH, HEIGHT = 800, 600

UI_SETTINGS = {
    "BOX_COLOR": (20, 20, 20),
    "BORDER_COLOR": (255, 255, 255),
    "BOX_X": 50,
    "BOX_Y": HEIGHT - 180,
    "BOX_W": WIDTH - 100,
    "BOX_H": 160,
    "TEXT_X": 30,
    "TEXT_Y": 30,
    "OPTION_X": 50,
    "OPTION_START_Y": 40,
    "OPTION_SPACING": 35,
    "TYPING_SPEED": 30,
    "COL_GAP": 350,
}

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("RPG 完整版：提示簡化版")

# 設定字體
try:
    font_path = "C:\\Windows\\Fonts\\msjh.ttc"
    font = pg.font.Font(font_path, 24)
    small_font = pg.font.Font(font_path, 20)
except:
    font = pg.font.Font(None, 32)
    small_font = pg.font.Font(None, 24)

clock = pg.time.Clock()

# ==========================
# 2. 劇情腳本數據
# ==========================
DIALOGUES = {
    # --- 懸崖 ---
    "cliff": [
        {"type": "text", "content": "墨星往上爬了"},
        {"type": "text", "content": "之後要買個貓爬架給牠"},
        {"type": "end"}
    ],

    # --- 湖泊區域 ---
    "lake_intro": [
        {"type": "text", "content": "一個生機蓬勃的湖泊"},
        {"type": "jump", "next": "lake_menu"} 
    ],
    "lake_intro_unlock": [
        {"type": "text", "content": "一個生機蓬勃的湖泊"},
        {"type": "jump", "next": "lake_menu_unlock"} 
    ],
    "lake_menu": [
        {"type": "choice", "options": [{"text": "釣魚", "next": "no_rod"}, {"text": "離開", "next": "exit_prompt"}]}
    ],
    "lake_menu_unlock": [
        {"type": "choice", "options": [{"text": "搭船", "next": "boat"}, {"text": "釣魚", "next": "no_rod_unlock"}, {"text": "離開", "next": "exit_prompt"}]}
    ],
    "boat": [{"type": "end"}],
    "no_rod": [{"type": "text", "content": "你發現你沒有釣竿"}, {"type": "jump", "next": "lake_menu"}],
    "no_rod_unlock": [{"type": "text", "content": "你沒有釣竿 只能看著魚發呆"}, {"type": "jump", "next": "lake_menu_unlock"}],
    "exit_prompt": [{"type": "text", "content": "於是你轉身向山裡走去"}, {"type": "end"}],

    # --- 路標 & 碼頭 ---
    "signpost": [
        {"type": "text", "content": "   <---森林 小鎮--->   "},
        {"type": "text", "content": "墨星怕人 絕對不可能往鎮上走 我應該去森林裡找牠"},
        {"type": "end"}
    ],
    "dock": [
        {"type": "text", "content": "要搭船嗎？"},
        {"type": "choice", "options": [{"text": "是", "next": "boat_yes"}, {"text": "否", "next": "end"}]}
    ],
    "boat_yes": [{"type": "end"}],
    "poem": [{"type": "text", "content": "我願順流而下 找尋她的方向"}, {"type": "end"}],

    # --- 商店 ---
    "store": [
        {
            "type": "choice",
            "options": [
                {"text": "購物", "next": "buy_menu"}, 
                {"text": "對話", "next": "busnessman_talk"},
                {"text": "離開", "next": "end"}
            ]
        }
    ],
    "buy_menu": [
        {
            "type": "choice",
            "options": [
                {"text": "堅果棒 3$", "next": "buy_nut"}, 
                {"text": "能量飲料 3$", "next": "buy_drink"},
                {"text": "空白符文 5$", "next": "buy_rune"},
                {"text": "返回", "next": "store"}
            ]
        }
    ],
    "buy_nut": [{"type": "end"}],   
    "buy_drink": [{"type": "end"}], 
    "buy_rune": [{"type": "end"}], 

    "buy_success": [
        {"type": "text", "content": "交易成功！"},
        {"type": "jump", "next": "buy_menu"}
    ],
    "buy_fail": [
        {"type": "text", "content": "你的錢不夠..."},
        {"type": "jump", "next": "buy_menu"}
    ],

    "busnessman_talk": [
        {
            "type": "choice",
            "options": [
                {"text": "你是誰", "next": "who_are_you"}, 
                {"text": "為什麼有人會想在這種地方開店阿", "next": "why_here"},
                {"text": "返回", "next": "store"}
            ]
        }
    ],
    "who_are_you": [{"type": "text", "content": "一個提供幫助的人。"}, {"type": "jump", "next": "busnessman_talk"}],
    "why_here": [{"type": "text", "content": "為什麼會有人想要來這種地方玩啊。"}, {"type": "jump", "next": "busnessman_talk"}],

    # --- 家 (Home) ---
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

# ==========================
# 3. 對話系統類別
# ==========================
class DialogueSystem:
    def __init__(self, screen, font, small_font, dialogue_data):
        self.screen = screen
        self.font = font
        self.small_font = small_font
        self.dialogue_data = dialogue_data
        self.clock = pg.time.Clock()

    def _draw_box(self):
        box = pg.Rect(UI_SETTINGS["BOX_X"], UI_SETTINGS["BOX_Y"], UI_SETTINGS["BOX_W"], UI_SETTINGS["BOX_H"])
        pg.draw.rect(self.screen, UI_SETTINGS["BOX_COLOR"], box)
        pg.draw.rect(self.screen, UI_SETTINGS["BORDER_COLOR"], box, 2)
        return box

    def show(self, key, current_money=None):
        if key not in self.dialogue_data: return None

        bg_snap = self.screen.copy()
        current_pages = self.dialogue_data[key]
        current_key = key 
        
        index = 0
        option_index = 0
        
        displayed_text = ""
        target_text = ""
        char_index = 0
        last_typing_time = 0
        page_init = True
        running_dialogue = True

        while running_dialogue:
            current_time = pg.time.get_ticks()
            self.clock.tick(60)

            if index >= len(current_pages): break
            cur = current_pages[index]

            if cur["type"] == "jump":
                if cur["next"] in self.dialogue_data:
                    current_key = cur["next"]
                    current_pages = self.dialogue_data[cur["next"]]
                    index = 0; option_index = 0; page_init = True; continue
                else: break

            if cur["type"] == "end": break

            if page_init:
                if cur["type"] == "text":
                    target_text = cur["content"]
                    displayed_text = ""
                    char_index = 0
                    last_typing_time = current_time
                page_init = False

            if cur["type"] == "text":
                if char_index < len(target_text):
                    if current_time - last_typing_time > UI_SETTINGS["TYPING_SPEED"]:
                        char_index += 1
                        displayed_text = target_text[:char_index]
                        last_typing_time = current_time
                else:
                    displayed_text = target_text

            self.screen.blit(bg_snap, (0, 0))
            box = self._draw_box()
            
            # 顯示金錢
            if current_money is not None:
                money_str = f"持有金錢: ${current_money}"
                money_surf = self.small_font.render(money_str, True, (255, 223, 0))
                money_rect = money_surf.get_rect(topright=(box.right - 30, box.y + 20))
                self.screen.blit(money_surf, money_rect)

            # ★ 修改：簡化提示文字
            hint_str = "X 取消/關閉   Z 確認/繼續"
            hint_render = self.small_font.render(hint_str, True, (150, 150, 150))
            # 靠右下對齊
            hint_rect = hint_render.get_rect(bottomright=(box.right - 20, box.bottom - 15))
            self.screen.blit(hint_render, hint_rect)

            # 繪製內容
            if cur["type"] == "text":
                t = self.font.render(displayed_text, True, (255, 255, 255))
                self.screen.blit(t, (box.x + UI_SETTINGS["TEXT_X"], box.y + UI_SETTINGS["TEXT_Y"]))

            elif cur["type"] == "choice":
                use_double_col = len(cur["options"]) > 3
                for i, opt in enumerate(cur["options"]):
                    if use_double_col:
                        col = 0 if i < 3 else 1
                        row = i if i < 3 else i - 3
                        x_pos = box.x + UI_SETTINGS["OPTION_X"] + (col * UI_SETTINGS["COL_GAP"])
                        y_pos = box.y + UI_SETTINGS["OPTION_START_Y"] + (row * UI_SETTINGS["OPTION_SPACING"])
                    else:
                        x_pos = box.x + UI_SETTINGS["OPTION_X"]
                        y_pos = box.y + UI_SETTINGS["OPTION_START_Y"] + (i * UI_SETTINGS["OPTION_SPACING"])

                    color = (255, 230, 80) if i == option_index else (255, 255, 255)
                    prefix = "> " if i == option_index else "  "
                    line = self.font.render(f"{prefix}{opt['text']}", True, color)
                    self.screen.blit(line, (x_pos, y_pos))
            
            pg.display.flip()

            for event in pg.event.get():
                if event.type == pg.QUIT: pg.quit(); sys.exit()
                
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_x: 
                        running_dialogue = False
                        current_key = None
                        break

                    if cur["type"] == "text":
                        if event.key == pg.K_z: 
                            if char_index < len(target_text):
                                char_index = len(target_text)
                                displayed_text = target_text
                            else:
                                index += 1
                                page_init = True

                    elif cur["type"] == "choice":
                        if event.key == pg.K_UP:
                            option_index = (option_index - 1) % len(cur["options"])
                        if event.key == pg.K_DOWN:
                            option_index = (option_index + 1) % len(cur["options"])
                        if event.key == pg.K_z:
                            selected = cur["options"][option_index]
                            if "next" in selected:
                                current_key = selected["next"] 
                                if selected["next"] == "end":
                                    running_dialogue = False
                                else:
                                    if selected["next"].startswith("buy_"): 
                                        running_dialogue = False
                                    else:
                                        current_pages = self.dialogue_data[selected["next"]]
                                        index = 0; option_index = 0; page_init = True
                            else:
                                running_dialogue = False
        
        return current_key

# ==========================
# 4. 主程式與角色
# ==========================
class Player(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.Surface((30, 30))
        self.image.fill((255, 100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 5
    def move(self, keys):
        if keys[pg.K_LEFT]: self.rect.x -= self.speed
        if keys[pg.K_RIGHT]: self.rect.x += self.speed
        if keys[pg.K_UP]: self.rect.y -= self.speed
        if keys[pg.K_DOWN]: self.rect.y += self.speed

def main():
    player = Player(400, 300)
    dlg_sys = DialogueSystem(screen, font, small_font, DIALOGUES)

    scene = "HOME"
    money = 100 
    
    inventory = {
        "nut": 0, "drink": 0, "rune": 0
    }
    
    poem_seen = False
    boat_unlocked = False
    investigated_items = set() 
    can_leave_home = False 

    home_triggers = {
        "document": pg.Rect(200, 200, 50, 50),
        "wire":     pg.Rect(500, 400, 50, 50),
        "coat":     pg.Rect(200, 400, 50, 50),
        "crayon":   pg.Rect(500, 200, 50, 50),
        "door":     pg.Rect(350, 550, 100, 20)
    }

    world_triggers = {
        "shop":     pg.Rect(600, 400, 80, 80), 
        "dock":     pg.Rect(600, 100, 80, 80),
        "lake":     pg.Rect(100, 400, 100, 100),
        "sign":     pg.Rect(380, 50, 40, 40),
        "home_in":  pg.Rect(350, 550, 100, 20),
        "cliff":    pg.Rect(50, 50, 100, 50)
    }

    dlg_sys.show("wake_up")

    running = True
    while running:
        clock.tick(60)
        player.move(pg.key.get_pressed())

        for event in pg.event.get():
            if event.type == pg.QUIT: running = False
            
            if event.type == pg.KEYDOWN and event.key == pg.K_z: 
                if scene == "HOME":
                    for item_name in ["document", "wire", "coat", "crayon"]:
                        if player.rect.colliderect(home_triggers[item_name]):
                            investigated_items.add(item_name)
                            if len(investigated_items) == 4:
                                dlg_sys.show(f"{item_name}")
                                dlg_sys.show(f"{item_name}_last")
                                dlg_sys.show(f"cat")
                                can_leave_home = True
                            else:
                                dlg_sys.show(item_name)
                    
                    if player.rect.colliderect(home_triggers["door"]):
                        if can_leave_home:
                            dlg_sys.show("go_out")
                            scene = "WORLD"; player.rect.topleft = (380, 500)
                        else:
                            dlg_sys.show("locked_door")

                elif scene == "WORLD":
                    if player.rect.colliderect(world_triggers["shop"]):
                        current_shop_key = "store" 
                        in_shop_loop = True 

                        while in_shop_loop:
                            result = dlg_sys.show(current_shop_key, current_money=money)

                            if result is None or result == "end":
                                in_shop_loop = False

                            elif result == "buy_nut":
                                if money >= 3:
                                    money -= 3; inventory["nut"] += 1; current_shop_key = "buy_success"
                                else: current_shop_key = "buy_fail"

                            elif result == "buy_drink":
                                if money >= 3:
                                    money -= 3; inventory["drink"] += 1; current_shop_key = "buy_success"
                                else: current_shop_key = "buy_fail"

                            elif result == "buy_rune":
                                if money >= 5:
                                    money -= 5; inventory["rune"] += 1; current_shop_key = "buy_success"
                                else: current_shop_key = "buy_fail"

                            else:
                                current_shop_key = result

                    elif player.rect.colliderect(world_triggers["dock"]):
                        res = dlg_sys.show("dock")
                        if res == "boat_yes":
                            if not poem_seen:
                                dlg_sys.show("poem")
                                poem_seen = True
                                boat_unlocked = True

                    elif player.rect.colliderect(world_triggers["lake"]):
                        if boat_unlocked:
                            dlg_sys.show("lake_intro_unlock")
                        else:
                            dlg_sys.show("lake_intro")
                    
                    elif player.rect.colliderect(world_triggers["sign"]):
                        dlg_sys.show("signpost")

                    elif player.rect.colliderect(world_triggers["cliff"]):
                        dlg_sys.show("cliff")

                    elif player.rect.colliderect(world_triggers["home_in"]):
                        scene = "HOME"; player.rect.topleft = (380, 500)

        screen.fill((0, 0, 0))
        if scene == "HOME":
            screen.fill((50, 40, 30))
            for k, rect in home_triggers.items():
                c = (200, 200, 200) if k != "door" else (100, 50, 0)
                pg.draw.rect(screen, c, rect)
        elif scene == "WORLD":
            screen.fill((40, 100, 40))
            pg.draw.rect(screen, (200, 200, 0), world_triggers["shop"])
            pg.draw.rect(screen, (100, 100, 200), world_triggers["dock"])
            pg.draw.ellipse(screen, (0, 200, 255), world_triggers["lake"])
            pg.draw.rect(screen, (139, 69, 19), world_triggers["sign"])
            pg.draw.rect(screen, (100, 50, 0), world_triggers["home_in"])
            pg.draw.rect(screen, (100, 100, 100), world_triggers["cliff"])

        screen.blit(player.image, player.rect)
        
        status = f"Money: {money} | Items: {inventory}"
        screen.blit(small_font.render(status, True, (255, 255, 255)), (10, 10))

        triggers = home_triggers if scene == "HOME" else world_triggers
        for rect in triggers.values():
            if player.rect.colliderect(rect):
                hint = small_font.render("Z", True, (255, 255, 255))
                screen.blit(hint, (player.rect.centerx - 5, player.rect.top - 25))

        pg.display.flip()

    pg.quit()

if __name__ == "__main__":
    main()