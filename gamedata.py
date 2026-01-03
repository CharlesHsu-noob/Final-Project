import json
import os
import time
from datetime import datetime

# ==========================================
# 設定預設存檔路徑
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
        
        # -------------------------------------------------
        # 時間計算變數
        # -------------------------------------------------
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

    # 取得當前真實總時數 (累積 + 本次)
    def get_real_playtime(self):
        current_session_time = time.time() - self._session_start
        return self.total_playtime + current_session_time

    def to_dict(self, inventory_list, player_pos, scene_name):
        # -------------------------------------------------
        # 【修復】存檔前過濾掉無法存檔的圖片物件 (Surface)
        # -------------------------------------------------
        clean_inventory = []
        for item in inventory_list:
            clean_item = {k: v for k, v in item.items() if k != 'icon'}
            clean_inventory.append(clean_item)

        real_playtime = self.get_real_playtime()
        
        return {
            "chapter": self.chapter,
            "money": self.money,
            "playtime": real_playtime,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "volume": self.volume,
            "sfx_volume": self.sfx_volume,
            "party": self.party_data,
            "inventory": clean_inventory, 
            "player_pos": player_pos,
            "scene_name": scene_name
        }

    def load_from_dict(self, data):
        self.chapter = data.get("chapter", 1)
        self.money = data.get("money", 100)
        
        self.total_playtime = data.get("playtime", 0.0)
        self._session_start = time.time()
        
        self.volume = data.get("volume", 0.5)
        self.sfx_volume = data.get("sfx_volume", 0.5)
        self.party_data = data.get("party", self.party_data)
        
        inventory_list = data.get("inventory", [])
        player_pos = data.get("player_pos", (0, 0))
        scene_name = data.get("scene_name", "home")
        
        return inventory_list, player_pos, scene_name

# ==========================================
# 【新功能】局部更新專用函式 (取代原本的 Shop 更新)
#  可以用來更新：金錢、背包、設定、隊伍血量...等任何欄位
# ==========================================
def update_specific_data(updates_dict, filename=None):
    """
    使用範例:
    update_specific_data({
        "money": 50,
        "inventory": updated_inventory_list
    })
    """
    target_path = filename if filename else SAVE_PATH
    
    # 如果檔案不存在，無法進行局部更新，直接跳出
    if not os.path.exists(target_path):
        print(f"[系統] 找不到存檔 {target_path}，無法進行局部更新。")
        return

    try:
        # 1. 讀取舊檔案
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 2. 根據傳入的字典進行更新
        for key, value in updates_dict.items():
            # 特殊處理：如果是更新背包，過濾掉圖片物件 (icon)
            if key == "inventory":
                clean_inventory = [{k: v for k, v in item.items() if k != 'icon'} for item in value]
                data[key] = clean_inventory
            else:
                # 其他欄位直接覆蓋 (例如 money, volume 等)
                data[key] = value

        # 3. 寫回檔案
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        # 印出這次更新了哪些欄位
        print(f"[系統] 局部存檔成功！更新項目: {list(updates_dict.keys())}")

    except Exception as e:
        print(f"[系統] 局部更新失敗: {e}")

# ==========================================
# 一般完整存檔功能 
# ==========================================
def save_game_to_file(game_data, inventory_list, player_pos, scene_name, filename=None):
    target_path = filename if filename else SAVE_PATH
    
    if scene_name == "world": scene_name = "forest_b"

    final_pos = player_pos
    # 防呆：如果傳入座標為空，嘗試從舊檔抓取，避免座標歸零
    if final_pos is None:
        if os.path.exists(target_path):
            try:
                with open(target_path, "r", encoding="utf-8") as f_old:
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
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"[系統] 完整存檔成功 -> {target_path} (場景: {scene_name})")
    except Exception as e:
        print(f"[系統] 存檔失敗: {e}")

# ==========================================
# 讀檔功能
# ==========================================
def load_game_from_file(filename=None):
    target_path = filename if filename else SAVE_PATH
    
    game_data = GameData()
    inventory_list = []
    player_pos = None
    scene_name = "HOME" 

    if os.path.exists(target_path):
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                inventory_list, player_pos, loaded_scene = game_data.load_from_dict(data)
                
                if loaded_scene: scene_name = loaded_scene
                if scene_name == "world": scene_name = "forest_b"
                print(f"[系統] 讀檔成功 ({target_path})！場景: {scene_name}")
        except Exception as e:
            print(f"[系統] 讀檔錯誤，將開始新遊戲: {e}")
            scene_name = "HOME"
    else:
        print(f"[系統] 找不到 {target_path}，建立新遊戲。")
    
    return game_data, inventory_list, player_pos, scene_name