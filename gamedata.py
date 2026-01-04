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

# ==========================================
# ★ 補救用資料庫
# ==========================================
FALLBACK_ITEM_DB = {
    "堅果棒": {"effect": "HP +20%"},
    "能量飲料": {"effect": "MP +3"},
    "空白符文": {"effect": "None"}
}

# ==========================================
# ★ [設定] 所有的解鎖狀態預設值
# ==========================================
DEFAULT_UNLOCK_FLAGS = {
    "intro_played": False,  # 是否看過開場 (醒來劇情)
    "home_door": False,     # 家門解鎖 (main.py: home_unlocked)
    "mountain_path": False, # 爬山路徑解鎖 (main.py: cliff_unlocked)
    "lake_boat": False,     # 湖泊搭船點解鎖 (main.py: boat_unlocked)
    "forest_depth": False   # 森林深處解鎖
}

class GameData:
    def __init__(self):
        self.reset()
        # 初始化時嘗試讀檔，若無檔案則保持 reset 狀態
        if os.path.exists(SAVE_PATH):
            load_game_from_file(self)
    
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
            {"name": "U", "desc": "內向 不擅交流", "hp": 100, "max_hp": 100, "mp": 10, "max_mp": 20, "runes": []},
            {"name": "K", "desc": "???", "hp": 0, "max_hp": 0, "mp": 0, "max_mp": 0, "runes": []},
            {"name": "W", "desc": "???", "hp": 0, "max_hp": 0, "mp": 0, "max_mp": 0, "runes": []},
            {"name": "C", "desc": "???", "hp": 0, "max_hp": 0, "mp": 0, "max_mp": 0, "runes": []}, 
            {"name": "O", "desc": "???", "hp": 0, "max_hp": 0, "mp": 0, "max_mp": 0, "runes": []}
        ]
        self.upgrade_log = []
        
        # ★ [新增] 解鎖狀態初始化 (複製一份預設值)
        self.unlock_flags = DEFAULT_UNLOCK_FLAGS.copy()

    # ==========================================
    # ★★★ 相容性屬性 (為了配合 main.py) ★★★
    # 這些屬性讓 main.py 可以用 .home_unlocked 讀取，
    # 但實際數值是存在 self.unlock_flags["home_door"] 裡
    # ==========================================
    @property
    def intro_played(self): return self.unlock_flags.get("intro_played", False)
    @intro_played.setter
    def intro_played(self, val): self.unlock_flags["intro_played"] = val

    @property
    def home_unlocked(self): return self.unlock_flags.get("home_door", False)
    @home_unlocked.setter
    def home_unlocked(self, val): self.unlock_flags["home_door"] = val

    @property
    def cliff_unlocked(self): return self.unlock_flags.get("mountain_path", False)
    @cliff_unlocked.setter
    def cliff_unlocked(self, val): self.unlock_flags["mountain_path"] = val

    @property
    def boat_unlocked(self): return self.unlock_flags.get("lake_boat", False)
    @boat_unlocked.setter
    def boat_unlocked(self, val): self.unlock_flags["lake_boat"] = val

    # 取得當前真實總時數
    def get_real_playtime(self):
        current_session_time = time.time() - self._session_start
        return self.total_playtime + current_session_time

    def to_dict(self, inventory_list, player_pos, scene_name):
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
            "scene_name": scene_name,
            "upgrade_log": self.upgrade_log,
            # ★ [新增] 存入解鎖狀態
            "unlock_flags": self.unlock_flags
        }

    def load_from_dict(self, data):
        self.chapter = data.get("chapter", 1)
        self.money = data.get("money", 100)
        
        self.total_playtime = data.get("playtime", 0.0)
        self._session_start = time.time()
        
        self.volume = data.get("volume", 0.5)
        self.sfx_volume = data.get("sfx_volume", 0.5)
        
        self.party_data = data.get("party", self.party_data)
        
        # 修復角色資料
        for char in self.party_data:
            if "mp" not in char:
                char["mp"] = int(char.get("hp", 10) * 0.5)
            if "max_mp" not in char:
                char["max_mp"] = int(char.get("max_hp", 20) * 0.5)
            if "runes" not in char:
                char["runes"] = []

        self.upgrade_log = data.get("upgrade_log", [])
        
        # ★ [新增] 讀取解鎖狀態 + 自動修復舊存檔
        loaded_flags = data.get("unlock_flags", {})
        # 確保每一個預設的 key 都在 (防止舊存檔缺 key)
        for key, default_val in DEFAULT_UNLOCK_FLAGS.items():
            if key not in loaded_flags:
                loaded_flags[key] = default_val
        self.unlock_flags = loaded_flags
        
        inventory_list = data.get("inventory", [])
        
        # 修復背包
        for item in inventory_list:
            if "effect" not in item:
                name = item.get("name", "")
                if name in FALLBACK_ITEM_DB:
                    item["effect"] = FALLBACK_ITEM_DB[name]["effect"]
                else:
                    item["effect"] = "None"

        player_pos = data.get("player_pos", (0, 0))
        scene_name = data.get("scene_name", "home")
        
        return inventory_list, player_pos, scene_name

    # ==========================================
    # ★ main.py 呼叫的存檔接口
    # ==========================================
    def save(self):
        """主程式呼叫此方法進行快速存檔"""
        # 這裡需要傳入 main 物件的資訊，但因為 gamedata 獨立
        # 我們假設這裡只存基礎資料，位置資訊可能需要從外部傳入
        # 為了相容，我們呼叫 save_game_to_file，但位置先暫時用預設
        # *注意*：最好在 main.py 裡呼叫 save_game_to_file 傳入完整資訊
        # 但為了不改壞 main.py，這裡先做一個簡單的存檔
        save_game_to_file(self, [], None, "unknown")


# ==========================================
# 局部更新專用函式
# ==========================================
def update_specific_data(updates_dict, filename=None):
    target_path = filename if filename else SAVE_PATH
    
    if not os.path.exists(target_path):
        # print(f"[系統] 找不到存檔 {target_path}，無法進行局部更新。")
        return

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for key, value in updates_dict.items():
            if key == "inventory":
                clean_inventory = []
                for item in value:
                    clean_item = {k: v for k, v in item.items() if k != 'icon'}
                    if "effect" not in clean_item:
                        name = clean_item.get("name", "")
                        clean_item["effect"] = FALLBACK_ITEM_DB.get(name, {}).get("effect", "None")
                    clean_inventory.append(clean_item)
                data[key] = clean_inventory
            else:
                data[key] = value

        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"[系統] 局部存檔成功！更新項目: {list(updates_dict.keys())}")

    except Exception as e:
        print(f"[系統] 局部更新失敗: {e}")

# ==========================================
# ★ [新功能] 解鎖並立刻存檔
#  用途：對話結束後呼叫此函式，會同時更新遊戲記憶體與硬碟存檔
# ==========================================
def unlock_and_save(game_data, unlock_key, value=True):
    # 1. 更新記憶體中的狀態
    if unlock_key in game_data.unlock_flags:
        game_data.unlock_flags[unlock_key] = value
        print(f"[劇情] 解鎖項目: {unlock_key} -> {value}")
        
        # 2. 立刻寫入硬碟 (局部更新)
        update_specific_data({
            "unlock_flags": game_data.unlock_flags
        })
    else:
        print(f"[系統] 錯誤：無效的解鎖 Key -> {unlock_key}")

# ==========================================
# 一般完整存檔功能 
# ==========================================
def save_game_to_file(game_data, inventory_list, player_pos, scene_name, filename=None):
    target_path = filename if filename else SAVE_PATH
    
    # 建立存檔資料夾
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)

    if scene_name == "world": scene_name = "forest_b"

    # 若沒有提供位置，嘗試讀取舊檔的位置，避免位置重置
    final_pos = player_pos
    if final_pos is None or final_pos == (0,0):
        if os.path.exists(target_path):
            try:
                with open(target_path, "r", encoding="utf-8") as f_old:
                    old_data = json.load(f_old)
                    if player_pos is None: # 只在完全沒傳入位置時使用舊位置
                        final_pos = old_data.get("player_pos", (0, 0))
            except:
                pass
    
    if final_pos is None: final_pos = (0, 0)

    data = game_data.to_dict(inventory_list, final_pos, scene_name)
    
    try:
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"[系統] 完整存檔成功 -> {target_path} (場景: {scene_name})")
    except Exception as e:
        print(f"[系統] 存檔失敗: {e}")

# ==========================================
# 讀檔功能
# ==========================================
def load_game_from_file(game_data_instance, filename=None):
    """
    讀取存檔並將資料填入傳入的 game_data_instance 物件中
    """
    target_path = filename if filename else SAVE_PATH
    
    inventory_list = []
    player_pos = (0, 0)
    scene_name = "home" 

    if os.path.exists(target_path):
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                inventory_list, player_pos, loaded_scene = game_data_instance.load_from_dict(data)
                
                if loaded_scene: scene_name = loaded_scene
                if scene_name == "world": scene_name = "forest_b"
                print(f"[系統] 讀檔成功 ({target_path})！場景: {scene_name}")
        except Exception as e:
            print(f"[系統] 讀檔錯誤，將維持預設值: {e}")
    else:
        print(f"[系統] 找不到 {target_path}，使用新遊戲設定。")
    
    return inventory_list, player_pos, scene_name