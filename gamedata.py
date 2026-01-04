import json
import os
import time
from datetime import datetime

# ==========================================
# 設定預設存檔路徑
# ==========================================
SAVE_FOLDER = "saves"
# 預設檔名保留給全域函式使用，GameData 實體會使用自己的 file_path
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
    # ★ 修改 1: 初始化接收 slot_index (預設 0)
    def __init__(self, slot_index=0):
        self.slot_index = slot_index
        # 動態決定檔名
        self.file_name = f"save_{slot_index}.json"
        self.file_path = os.path.join(SAVE_FOLDER, self.file_name)
        
        self.reset()
        
        # 初始化時嘗試讀檔，傳入計算好的路徑
        if os.path.exists(self.file_path):
            load_game_from_file(self, self.file_path)
        else:
            print(f"[System] 存檔 {self.file_name} 不存在，將使用新遊戲設定。")
    
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
        # 如果傳入 None (例如自動存檔沒拿到背包)，嘗試用空 list 避免報錯
        if inventory_list is None: inventory_list = []
        
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
    # ★ 修改 2: save 方法支援傳入參數並寫入指定檔案
    # ==========================================
    def save(self, inventory_list=None, player_pos=None, scene_name="home"):
        """
        主程式呼叫此方法進行存檔
        會自動寫入 self.file_path 指定的檔案 (save_0.json, save_1.json...)
        """
        if inventory_list is None: inventory_list = []
        if player_pos is None: player_pos = (0, 0)
        
        # 呼叫全域函式，但傳入此物件專屬的路徑
        save_game_to_file(self, inventory_list, player_pos, scene_name, filename=self.file_path)

    # 為了保持 load 邏輯的一致性，新增一個實例方法 (雖主要邏輯在 __init__)
    def load_from_file(self):
        return load_game_from_file(self, self.file_path)


# ==========================================
# 局部更新專用函式 (保留不變)
# ==========================================
def update_specific_data(updates_dict, filename=None):
    # 若沒指定 filename，使用預設 (save_0)
    # 注意：如果想支援多存檔，外部呼叫此函式時需要傳入正確的 path
    target_path = filename if filename else SAVE_PATH
    
    if not os.path.exists(target_path):
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
            
        print(f"[系統] 局部存檔成功！更新項目: {list(updates_dict.keys())} -> {target_path}")

    except Exception as e:
        print(f"[系統] 局部更新失敗: {e}")

# ==========================================
# 解鎖並立刻存檔 (保留不變，建議外部呼叫時傳入 GameData 物件)
# ==========================================
def unlock_and_save(game_data, unlock_key, value=True):
    # 1. 更新記憶體中的狀態
    if unlock_key in game_data.unlock_flags:
        game_data.unlock_flags[unlock_key] = value
        print(f"[劇情] 解鎖項目: {unlock_key} -> {value}")
        
        # 2. 立刻寫入硬碟 (局部更新)
        # 注意：這裡使用 game_data.file_path 來確保寫入正確的存檔槽
        path = getattr(game_data, 'file_path', None)
        update_specific_data({
            "unlock_flags": game_data.unlock_flags
        }, filename=path)
    else:
        print(f"[系統] 錯誤：無效的解鎖 Key -> {unlock_key}")

# ==========================================
# 一般完整存檔功能 (保留不變)
# ==========================================
def save_game_to_file(game_data, inventory_list, player_pos, scene_name, filename=None):
    target_path = filename if filename else SAVE_PATH
    
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)

    if scene_name == "world": scene_name = "forest_b"

    final_pos = player_pos
    if final_pos is None or final_pos == (0,0):
        if os.path.exists(target_path):
            try:
                with open(target_path, "r", encoding="utf-8") as f_old:
                    old_data = json.load(f_old)
                    if player_pos is None: 
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
# 讀檔功能 (保留不變)
# ==========================================
def load_game_from_file(game_data_instance, filename=None):
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