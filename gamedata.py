import json
import os
import time
from datetime import datetime

# ==========================================
# 設定存檔路徑：saves/save_0.json
# ==========================================
SAVE_FOLDER = "saves"
SAVE_FILENAME = "save_0.json"
SAVE_PATH = os.path.join(SAVE_FOLDER, SAVE_FILENAME)

class GameData:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.chapter = 1
        self.money = 100
        self.total_playtime = 0.0
        self._session_start = time.time()
        self.volume = 0.5
        self.sfx_volume = 0.5
        self.party_data = [
            {"name": "U", "desc": "內向 不擅交流", "hp": 80, "max_hp": 100, "runes": []},
            {"name": "K", "desc": "???", "hp": 45, "max_hp": 60, "runes": []},
            {"name": "W", "desc": "???", "hp": 60, "max_hp": 70, "runes": []},
            {"name": "C", "desc": "???", "hp": 50, "max_hp": 60, "runes": []}, 
            {"name": "O", "desc": "???", "hp": 110, "max_hp": 120, "runes": []}  
        ]
        self.upgrade_log = []

    def get_playtime(self): 
        return self.total_playtime + (time.time() - self._session_start)

    def to_dict(self, inventory_list, player_pos, current_scene):
        save_inv = [{k:v for k,v in item.items() if k!="icon"} for item in inventory_list]
        return {
            "chapter": self.chapter, 
            "money": self.money, 
            "playtime": self.get_playtime(), 
            "volume": self.volume, 
            "sfx_volume": self.sfx_volume, 
            "party_data": self.party_data, 
            "upgrade_log": self.upgrade_log, 
            "timestamp": datetime.now().strftime("%m/%d %H:%M"),
            "inventory": save_inv, 
            "player_pos": player_pos, 
            "scene_name": current_scene
        }

    def load_from_dict(self, data):
        self.chapter = data.get("chapter", 1)
        self.money = data.get("money", 0)
        self.total_playtime = data.get("playtime", 0.0)
        self.volume = data.get("volume", 0.5)
        self.sfx_volume = data.get("sfx_volume", 0.5)
        self.party_data = data.get("party_data", self.party_data)
        for char in self.party_data:
            if "runes" not in char: char["runes"] = []
        self.upgrade_log = data.get("upgrade_log", [])
        self._session_start = time.time()
        return data.get("inventory", []), data.get("player_pos", None), data.get("scene_name", None)

# ==========================================
# 商店專用更新函式 (只改錢跟物品，不碰座標)
# ==========================================
def update_shop_data(money, inventory_list):
    if not os.path.exists(SAVE_PATH):
        return

    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 只改這兩項
        data["money"] = money
        data["inventory"] = [{k:v for k,v in item.items() if k!="icon"} for item in inventory_list]

        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"[系統] 商店交易存檔成功 (金錢: {money})")
    except Exception as e:
        print(f"[系統] 商店存檔失敗: {e}")

# ==========================================
# 一般存檔功能 (切換場景用，支援保留舊座標)
# ==========================================
def save_game_to_file(game_data, inventory_list, player_pos, scene_name):
    if scene_name == "world": scene_name = "forest_b"

    # ★ 座標保護：如果 player_pos 是 None，就讀取舊檔的座標
    final_pos = player_pos
    if final_pos is None:
        if os.path.exists(SAVE_PATH):
            try:
                with open(SAVE_PATH, "r", encoding="utf-8") as f_old:
                    old_data = json.load(f_old)
                    final_pos = old_data.get("player_pos", (0, 0))
            except:
                final_pos = (0, 0)
        else:
            final_pos = (0, 0)

    data = game_data.to_dict(inventory_list, final_pos, scene_name)
    
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)

    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"[系統] 場景存檔成功 -> {SAVE_PATH} (場景: {scene_name}, 座標保持: {final_pos})")
    except Exception as e:
        print(f"[系統] 存檔失敗: {e}")

# ==========================================
# 讀檔功能
# ==========================================
def load_game_from_file():
    game_data = GameData()
    inventory_list = []
    player_pos = None
    scene_name = "HOME" 

    if os.path.exists(SAVE_PATH):
        try:
            with open(SAVE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                inventory_list, player_pos, loaded_scene = game_data.load_from_dict(data)
                if loaded_scene: scene_name = loaded_scene
                if scene_name == "world": scene_name = "forest_b"
                print(f"[系統] 讀檔成功 ({SAVE_PATH})！場景: {scene_name}")
        except Exception as e:
            print(f"[系統] 讀檔錯誤，將開始新遊戲: {e}")
            scene_name = "HOME"
    else:
        print(f"[系統] 找不到 {SAVE_PATH}，建立新遊戲。")
    
    return game_data, inventory_list, player_pos, scene_name