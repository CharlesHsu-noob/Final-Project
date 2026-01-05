import XddObjects as xo
def update(sc_w,sc_h,main=xo.VAR()) ->xo.VAR :
    import pygame as pg
    import math
    import sys
    import os

    pg.init()

    # ----------------- 參數 -----------------
    GRID_SIZE = 79
    COLS = 16
    ROWS = 6
    WIDTH, HEIGHT = 1920, 1080
    FPS = 60
    PLAYER_SPEED = 300  # 平滑移動速度（px/sec）
    OFFSET_X = 330
    OFFSET_Y = 460
    # 動畫速度控制 (毫秒 ms)
    ANIMATION_DELAY = 150

    # 顏色
    WHITE = (245, 245, 245)
    BLACK = (20, 20, 20)
    GRAY = (200, 200, 200)
    DARK_GRAY = (160, 160, 160)
    GREEN = (80, 200, 120)
    RED = (220, 50, 50)
    BLUE = (60, 140, 220)
    YELLOW = (235, 210, 80)

    font = pg.font.SysFont("Microsoft JhengHei", 18)
    overlay_font = pg.font.SysFont("Microsoft JhengHei", 96)

    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Bob - Turret Level")

    clock = pg.time.Clock()

    # --- 載入背景 (注意資料夾改為 picture 以保持統一) ---
    try:
        bg_img = pg.image.load(os.path.join('picture', 'labb_g.png')).convert()
    except:
        # 如果找不到，嘗試讀取 image 資料夾 (相容舊路徑)
        bg_img = pg.image.load(os.path.join('image', 'labb_g.png')).convert()
    bg_img = pg.transform.scale(bg_img, (WIDTH, HEIGHT))

    # --- 載入圖片資源 (通用縮放邏輯) ---
    def load_and_scale(path, scale_factor, rotate=0):
        try:
            img = pg.image.load(os.path.join('picture', path)).convert_alpha()
        except:
            try:
                img = pg.image.load(os.path.join('image', path)).convert_alpha()
            except:
                s = pg.Surface((GRID_SIZE, GRID_SIZE), pg.SRCALPHA)
                s.fill((255, 0, 255, 128))  # 紫色方塊代表缺圖
                img = s
        
        target_size = int(GRID_SIZE * scale_factor)
        img = pg.transform.scale(img, (target_size, target_size))
        if rotate:
            img = pg.transform.rotate(img, rotate)
        return img

    # --- 雷射發射器圖片 ---
    try:
        laser_emitter_base_blue = pg.image.load(os.path.join('picture', 'lab_laser_top_2.png')).convert_alpha()
        laser_emitter_base_red = pg.image.load(os.path.join('picture', 'lab_laser_top_3.png')).convert_alpha()
    except:
        laser_emitter_base_blue = pg.image.load(os.path.join('image', 'lab_laser_top_2.png')).convert_alpha()
        laser_emitter_base_red = pg.image.load(os.path.join('image', 'lab_laser_top_3.png')).convert_alpha()

    laser_emitter_base_blue = pg.transform.scale(laser_emitter_base_blue, (int(GRID_SIZE * 1.5), int(GRID_SIZE * 1.5)))
    laser_emitter_base_red = pg.transform.scale(laser_emitter_base_red, (int(GRID_SIZE * 1.5), int(GRID_SIZE * 1.5)))

    # --- 玩家手持鏡子圖片 ---
    try:
        mirror_hold_image = pg.image.load(os.path.join('picture', 'lab_mirror_whole.png')).convert_alpha()
    except:
        mirror_hold_image = pg.image.load(os.path.join('image', 'lab_mirror_whole.png')).convert_alpha()
    mirror_hold_image = pg.transform.scale(mirror_hold_image, (int(GRID_SIZE * 0.6), int(GRID_SIZE * 0.6)))


    # ==========================================
    # [修改重點] 載入統一的玩家圖片序列並等比例縮放
    # ==========================================
    player_images = []
    image_files = ["u_stand.png", "u_s_l.png", "u_s_r.png"]
    # 嘗試從 picture 資料夾讀取 (如果你的圖在 chuchutest 子資料夾，請保留 chuchutest)
    img_path_bases = [os.path.join("picture", "chuchutest"), os.path.join("image", "chuchutest"), "picture", "image"]

    # 設定目標高度：大約兩格 (1.9倍)
    PLAYER_TARGET_HEIGHT = int(GRID_SIZE * 1.9)

    # 尋找正確的路徑
    found_base = ""
    for base in img_path_bases:
        if os.path.exists(os.path.join(base, "u_stand.png")):
            found_base = base
            break

    if not found_base:
        print("Warning: Player images not found!")
        found_base = "picture" # Fallback

    for f_name in image_files:
        try:
            full_path = os.path.join(found_base, f_name)
            original = pg.image.load(full_path).convert_alpha()

            # 計算等比例縮放
            old_w, old_h = original.get_size()
            if old_h > 0:
                scale_factor = PLAYER_TARGET_HEIGHT / old_h
                new_w = int(old_w * scale_factor)
                
                # 使用 smoothscale 進行高品質縮放
                scaled_img = pg.transform.smoothscale(original, (new_w, PLAYER_TARGET_HEIGHT))
                player_images.append(scaled_img)
            else:
                player_images.append(original)

        except Exception as e:
            print(f"無法載入 {f_name}: {e}")
            fallback = pg.Surface((PLAYER_TARGET_HEIGHT//2, PLAYER_TARGET_HEIGHT), pg.SRCALPHA)
            pg.draw.rect(fallback, BLUE, (0,0,PLAYER_TARGET_HEIGHT//2, PLAYER_TARGET_HEIGHT))
            player_images.append(fallback)

    # 確保至少有一張圖
    if not player_images:
        fallback = pg.Surface((GRID_SIZE, int(GRID_SIZE*1.9)), pg.SRCALPHA)
        pg.draw.rect(fallback, BLUE, fallback.get_rect())
        player_images = [fallback, fallback, fallback]


    # --- 載入鏡子的底圖 ---
    try:
        mirror_base_image = pg.image.load(os.path.join('picture', 'lab_mirror_tile.png')).convert_alpha()
    except:
        mirror_base_image = pg.image.load(os.path.join('image', 'lab_mirror_tile.png')).convert_alpha()
    mirror_base_image = pg.transform.scale(mirror_base_image, (GRID_SIZE, GRID_SIZE))

    # --- 鏡子圖片載入與處理 ---
    try:
        img_original = pg.image.load(os.path.join('picture', 'lab_mirror_b.png')).convert_alpha()
    except:
        img_original = pg.image.load(os.path.join('image', 'lab_mirror_b.png')).convert_alpha()
    img_original = pg.transform.scale(img_original, (GRID_SIZE, GRID_SIZE))

    # 45 度圖片
    img_45 = img_original
    # 135 度圖片
    img_135 = pg.transform.rotate(img_original, 90) 
        
    mirror_images = {
        45: img_45,
        135: img_135
    }

    # ----------------- 載入音效 -----------------
    try:
        hit_sound = pg.mixer.Sound(os.path.join('voice', 'bgm', 'snake_d.ogg'))
    except:
        try:
            hit_sound = pg.mixer.Sound(os.path.join('voice', 'sound effects', 'snake_d.ogg'))
        except:
            print("Warning: snake_d.ogg not found")
            hit_sound = None

    # ----------------- 旋轉控制參數 -----------------
    turret_angle = 0.0       
    turret_speed = 30.0      
    turret_direction = 1     
    cycle_start_time = pg.time.get_ticks() 

    # ----------------- 資料結構 -----------------
    class Tile:
        def __init__(self, col, row, can_place=True):
            self.col = col
            self.row = row
            self.can_place = can_place
            self.mirror = None

        @property
        def center(self):
            return (
                OFFSET_X + self.col * GRID_SIZE + GRID_SIZE // 2,
                OFFSET_Y + self.row * GRID_SIZE + GRID_SIZE // 2
            )

        @property
        def rect(self):
            return pg.Rect(OFFSET_X + self.col * GRID_SIZE, 
                        OFFSET_Y + self.row * GRID_SIZE, 
                        GRID_SIZE, GRID_SIZE)

    class Mirror:
        def __init__(self, angle_deg=45):
            self.angle = angle_deg

        def get_image(self):
            return mirror_images.get(self.angle)

        def get_base_image(self):
            return mirror_base_image

        def endpoints(self, center):
            cx, cy = center
            half = GRID_SIZE * 0.45
            a = math.radians(self.angle)
            dx = math.cos(a) * half
            dy = math.sin(a) * half
            return ((cx - dx, cy - dy), (cx + dx, cy + dy))

    class Player:
        def __init__(self, col=1, row=1):
            self.col = col
            self.row = row
            self.x =959 #OFFSET_X + col * GRID_SIZE + GRID_SIZE//2
            self.y =289 #OFFSET_Y + row * GRID_SIZE + GRID_SIZE//2
            self.holding = None
            self.adjust_mode = False
            
            # --- 動畫參數 ---
            self.facing_right = True  # 面向右邊
            self.anim_index = 0       # 目前動畫幀數 (0=站立, 1=走1, 2=走2)
            self.animation_timer = 0  # 動畫計時器
            self.is_moving = False    # 是否正在移動

        @property
        def pos(self):
            return (int(self.x), int(self.y))
        
        # [修改重點] 新增手部判定座標 (統一邏輯)
        @property
        def hand_pos(self):
            h = PLAYER_TARGET_HEIGHT
            # 手部在圖片中的位置 = 頂部 + 65% 高度
            hand_y = (self.y - h // 2) + (h * 0.65)
            return (int(self.x), int(hand_y))

        def update_logic_position(self):
            self.col = int((self.x - OFFSET_X) // GRID_SIZE)
            self.row = int((self.y - OFFSET_Y) // GRID_SIZE)

    # ----------------- 建地圖 -----------------
    grid = [[Tile(c, r) for r in range(ROWS)] for c in range(COLS)]

    # 示範鏡子
    grid[0][5].mirror = Mirror(45)
    grid[0][4].mirror = Mirror(45)
    grid[0][3].mirror = Mirror(45)

    player = Player(1, 1)

    # 雷射來源
    laser_source = (OFFSET_X + GRID_SIZE//2 +10, OFFSET_Y + GRID_SIZE//2)
    laser_direction = (1.0, 0.3)

    emitter_hitbox_w = int(GRID_SIZE * 0.6)
    emitter_hitbox_h = int(GRID_SIZE * 0.6)

    # ----------------- 助手函式 -----------------
    def draw_laser_emitter(base_img, angle):
        rotated_img = pg.transform.rotate(base_img, -angle)
        rect = rotated_img.get_rect(center=laser_source)
        screen.blit(rotated_img, rect.topleft)

    def draw_grid():
        board_rect = pg.Rect(OFFSET_X, OFFSET_Y, COLS*GRID_SIZE, ROWS*GRID_SIZE)
        pg.draw.rect(screen, BLACK, board_rect, 3) 
        for c in range(COLS):
            for r in range(ROWS):
                t = grid[c][r]
                # 只畫格線
                pg.draw.rect(screen, GRAY, t.rect, 1)

    def draw_shadow_mirrors(last_mirrors):
        if not last_mirrors:
            return
        s = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        for c, r, ang in last_mirrors:
            if 0 <= c < COLS and 0 <= r < ROWS:
                t = grid[c][r]
                img = mirror_images.get(ang)
                if img:
                    shadow_img = img.copy()
                    shadow_img.set_alpha(80) 
                    s.blit(shadow_img, t.rect.topleft)
                else:
                    m = Mirror(ang)
                    p1, p2 = m.endpoints(t.center)
                    pg.draw.line(s, (255, 255, 100, 80), p1, p2, 6)
        screen.blit(s, (0, 0))

    def draw_shadow_laser(last_laser_path):
        if len(last_laser_path) < 2:
            return
        s = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        pg.draw.lines(s, (255, 0, 0, 80), False, last_laser_path, 3)
        screen.blit(s, (0, 0))

    def draw_tiles_contents():
        for c in range(COLS):
            for r in range(ROWS):
                t = grid[c][r]
                if t.can_place:
                    pg.draw.rect(screen, DARK_GRAY, t.rect, 2)
                if t.mirror:
                    base_img = t.mirror.get_base_image()
                    if base_img:
                        screen.blit(base_img, t.rect.topleft)
                    img = t.mirror.get_image()
                    if img :
                        screen.blit(img, t.rect.topleft)
                    else:
                        p1, p2 = t.mirror.endpoints(t.center)
                        pg.draw.line(screen, BLACK, p1, p2, 6)
                        pg.draw.line(screen, YELLOW, p1, p2, 2)

    # ==========================================
    # [修改重點] draw_player 使用新動畫與手部位置
    # ==========================================
    def draw_player(dt):
        x, y = player.pos

        # 1. 根據動畫索引選取圖片
        idx = player.anim_index % len(player_images)
        base_img = player_images[idx]

        # 2. 處理轉向
        if player.facing_right:
            current_img = pg.transform.flip(base_img, True, False)
        else:
            current_img = base_img

        # 3. 計算繪製位置 (圖片中心對齊玩家座標)
        w, h = current_img.get_width(), current_img.get_height()
        draw_x = x - w // 2
        draw_y = y - h // 2
        
        screen.blit(current_img, (draw_x, draw_y))

        # 4. 繪製手持鏡子 (對齊手部位置)
        if player.holding:
            holding_img = mirror_hold_image.copy()
            if player.holding.angle == 45:
                holding_img = pg.transform.rotate(holding_img, 90)

            m_w = holding_img.get_width()
            m_h = holding_img.get_height()
            
            m_draw_x = x - m_w // 2
            
            # 使用 65% 高度作為手持位置 (需與 hand_pos 邏輯一致)
            hand_offset_y = int(h * 0.65) 
            m_draw_y = draw_y + hand_offset_y - m_h // 2

            screen.blit(holding_img, (m_draw_x, m_draw_y))

    def point_near_line(point, p1, p2, threshold):
        px, py = point
        x1, y1 = p1
        x2, y2 = p2
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return False
        t = ((px-x1)*dx + (py-y1)*dy) / (dx*dx + dy*dy)
        t = max(0, min(1, t))
        nx = x1 + t * dx
        ny = y1 + t * dy
        return math.hypot(px-nx, py-ny) <= threshold

    def reflect_vector(vx, vy, x1, y1, x2, y2):
        dx, dy = x2-x1, y2-y1
        nx, ny = -dy, dx 
        l = math.hypot(nx, ny)
        if l == 0:
            return vx, vy
        nx, ny = nx/l, ny/l
        dot = vx*nx + vy*ny
        return (vx - 2*dot*nx, vy - 2*dot*ny)

    def fire_laser_and_get_path():
        path = []
        max_steps = 6000
        step_size = 5.0

        lx, ly = float(laser_source[0]), float(laser_source[1])
        vx, vy = laser_direction
        mag = math.hypot(vx, vy)
        if mag == 0:
            return path, 0
        ux, uy = vx/mag, vy/mag
        start_offset = max(emitter_hitbox_w, emitter_hitbox_h) * 0.5 + 8
        x, y = lx + ux * start_offset, ly + uy * start_offset
        vx, vy = ux * step_size, uy * step_size

        reflections = 0
        screen_rect = pg.Rect(0, 0, WIDTH, HEIGHT)

        for _ in range(max_steps):
            x += vx
            y += vy
            path.append((x, y))

            if x < 0 or x > WIDTH or y < 0 or y > HEIGHT:
                break

            c = int((x - OFFSET_X) // GRID_SIZE)
            r = int((y - OFFSET_Y) // GRID_SIZE)
            hit = False
            
            for dc in (-1, 0, 1):
                for dr in (-1, 0, 1):
                    cc = c + dc
                    rr = r + dr
                    if 0 <= cc < COLS and 0 <= rr < ROWS:
                        t = grid[cc][rr]
                        if t.mirror:
                            p1, p2 = t.mirror.endpoints(t.center)
                            if point_near_line((x, y), p1, p2, 8):
                                vx, vy = reflect_vector(vx, vy, *p1, *p2)
                                reflections += 1
                                if reflections > 40:
                                    return path, reflections
                                x += vx*0.6
                                y += vy*0.6
                                path.append((x, y))
                                hit = True
                                break
                if hit:
                    break
        return path, reflections

    def draw_laser_path(path):
        if len(path) < 2:
            return
        pg.draw.lines(screen, RED, False, path, 5)

    def tile_at_pixel(px, py):
        c = int((px - OFFSET_X) // GRID_SIZE)
        r = int((py - OFFSET_Y) // GRID_SIZE)
        if 0 <= c < COLS and 0 <= r < ROWS:
            return grid[c][r]
        return None

    # ----------------- 主 loop -----------------
    laser_path_cache = []
    laser_reached_goal = False
    last_laser_path = []
    last_mirrors = []
    last_fire_time = 0
    fire_check_pending = False
    freeze_active = False
    player_max_hp = 100
    player_hp = 100
    damage_applied_for_shot = False
    game_over = False
    last_reflections_count = 0

    cycle_start_time = pg.time.get_ticks()

    running = True
    while running:
        dt = clock.tick(FPS)
        now = pg.time.get_ticks()
        elapsed = now - cycle_start_time
        current_time = pg.time.get_ticks()
        elapsed_time = current_time - cycle_start_time

        current_base_img = laser_emitter_base_blue
        PHASE_BLUE = 5000 
        PHASE_RED = 1000  
        TOTAL_CYCLE = PHASE_BLUE + PHASE_RED 
        FREEZE_DURATION = 500 

        if elapsed_time < PHASE_BLUE:
            dx_track = player.x - laser_source[0]
            dy_track = player.y - laser_source[1]
            turret_angle = math.degrees(math.atan2(dy_track, dx_track))

        rad = math.radians(turret_angle)
        laser_direction = (math.cos(rad), math.sin(rad))

        freeze_active = (elapsed_time >= (TOTAL_CYCLE - FREEZE_DURATION) and elapsed_time < TOTAL_CYCLE)

        if elapsed_time < PHASE_BLUE:
            current_base_img = laser_emitter_base_blue
        elif elapsed_time < TOTAL_CYCLE:
            current_base_img = laser_emitter_base_red
        elif elapsed_time >= TOTAL_CYCLE:
            last_mirrors = [
                (c, r, grid[c][r].mirror.angle)
                for c in range(COLS)
                for r in range(ROWS)
                if grid[c][r].mirror
            ]
            laser_path_cache, last_reflections_count = fire_laser_and_get_path()
            last_laser_path = laser_path_cache[:]
            last_fire_time = current_time
            fire_check_pending = True
            r_hit = GRID_SIZE // 3
            if not damage_applied_for_shot:
                for (px, py) in laser_path_cache:
                    if math.hypot(px - player.x, py - player.y) <= r_hit:
                        player_hp = max(0, player_hp - 25)
                        damage_applied_for_shot = True
                        if hit_sound:
                            hit_sound.play()
                        break
            if player_hp <= 0:
                game_over = True
            cycle_start_time = current_time
            current_base_img = laser_emitter_base_blue
            freeze_active = False
            damage_applied_for_shot = False

        # ----------------- 事件 -----------------
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    for c in range(COLS):
                        for r in range(ROWS):
                            grid[c][r].mirror = None
                    grid[0][5].mirror = Mirror(45)
                    grid[0][4].mirror = Mirror(45) 
                    grid[0][3].mirror = Mirror(45)
                    player.holding = None
                    player.adjust_mode = False
                    laser_path_cache = []
                    laser_reached_goal = False
                    last_laser_path = []
                    last_mirrors = []
                    cycle_start_time = pg.time.get_ticks()
                    player_hp = player_max_hp
                    game_over = False
                    # [修改重點] 重置動畫狀態
                    player.anim_index = 0
                    player.facing_right = True

                # -------- E 互動（撿/放/調整）使用 hand_pos --------
                if event.key == pg.K_e:
                    # 使用手部座標來判定格子
                    t = tile_at_pixel(*player.hand_pos)
                    
                    if player.adjust_mode:
                        if t and t.can_place and t.mirror is None and player.holding:
                            t.mirror = player.holding
                            player.holding = None
                            player.adjust_mode = False
                            laser_path_cache = []
                            laser_reached_goal = False
                    else:
                        if player.holding is None and t and t.mirror:
                            player.holding = t.mirror
                            t.mirror = None
                            laser_path_cache = []
                            laser_reached_goal = False
                        elif player.holding and t and t.can_place and t.mirror is None:
                            player.adjust_mode = True
                            laser_path_cache = []
                            laser_reached_goal = False
                            player.is_moving = False # 調整時停止移動

                if event.key == pg.K_q and player.adjust_mode:
                    player.adjust_mode = False
                    laser_path_cache = []

                if event.key in (pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT):
                    if player.adjust_mode and player.holding:
                        player.holding.angle = 135 if player.holding.angle == 45 else 45
                        laser_path_cache = []

        # --- 移動與動畫更新 ---
        player.is_moving = False # 先預設為沒移動
        
        if not player.adjust_mode and not freeze_active and not game_over:
            keys = pg.key.get_pressed()
            dx = dy = 0
            if keys[pg.K_LEFT]: 
                dx -= 1
                player.facing_right = False
            if keys[pg.K_RIGHT]: 
                dx += 1
                player.facing_right = True
            if keys[pg.K_UP]: 
                dy -= 1
            if keys[pg.K_DOWN]: 
                dy += 1

            if dx or dy:
                player.is_moving = True
                laser_path_cache = []
                laser_reached_goal = False
                l = math.hypot(dx, dy)
                if l != 0:
                    dx /= l
                    dy /= l
                player.x += dx * PLAYER_SPEED * (dt / 1000)
                player.y += dy * PLAYER_SPEED * (dt / 1000)

                min_x = 0 
                max_x = screen.get_width()
                min_y = 100
                max_y = screen.get_height()-130
                player.x = max(min_x, min(max_x, player.x))
                player.y = max(min_y, min(max_y, player.y))
                player.update_logic_position()

        # [修改重點] 動畫計時器更新
        if player.is_moving:
            player.animation_timer += dt
            if player.animation_timer >= ANIMATION_DELAY:
                player.animation_timer = 0
                player.anim_index += 1
                # 在 1 (走1) 和 2 (走2) 之間循環
                if player.anim_index > 2:
                    player.anim_index = 1
        else:
            # 靜止時回到站立圖 (索引 0)
            player.anim_index = 0
            player.animation_timer = 0

        if fire_check_pending and (pg.time.get_ticks() - last_fire_time) >= 500:
            cx, cy = laser_source
            hitbox = pg.Rect(cx - emitter_hitbox_w // 2, cy - emitter_hitbox_h // 2, emitter_hitbox_w, emitter_hitbox_h)
            hit = False
            for (px, py) in laser_path_cache:
                if hitbox.collidepoint(int(px), int(py)):
                    hit = True
                    break
            laser_reached_goal = (hit and last_reflections_count >= 3)
            fire_check_pending = False

        # ================== 畫畫面 ==================
        screen.fill(BLACK)
        screen.blit(bg_img, (0, 0))
        draw_grid()
        draw_shadow_laser(last_laser_path)
        draw_shadow_mirrors(last_mirrors)
        draw_tiles_contents()
        
        # 繪製玩家 (使用新函數)
        draw_player(dt)
        
        bar_w = 200
        bar_h = 20
        bx, by = 300, 200
        pg.draw.rect(screen, (60, 60, 60), (bx, by, bar_w, bar_h))
        fill_w = int(bar_w * (player_hp / player_max_hp))
        pg.draw.rect(screen, (200, 50, 50), (bx, by, fill_w, bar_h))
        screen.blit(font.render(f"HP: {player_hp}/{player_max_hp}", True, BLACK), (bx + 210, by))

        if not laser_path_cache:
            lx, ly = laser_source
            dx, dy = laser_direction
            m = math.hypot(dx, dy)
            if m != 0:
                ux, uy = dx/m, dy/m
                start_offset = max(emitter_hitbox_w, emitter_hitbox_h) * 0.5 + 8
                sx, sy = lx + ux * start_offset, ly + uy * start_offset
                end_p = (sx + ux * 60, sy + uy * 60)
                pg.draw.line(screen, (200, 50, 50), (sx, sy), end_p, 3)

        draw_laser_emitter(current_base_img, turret_angle)

        # [修改重點] UI 提示使用 hand_pos
        cur_tile = tile_at_pixel(*player.hand_pos)
        if cur_tile and cur_tile.mirror:
            screen.blit(font.render("按E撿起鏡子", True, BLACK), (30, 45))
        elif player.holding and cur_tile and cur_tile.can_place and cur_tile.mirror is None and not player.adjust_mode:
            screen.blit(font.render("按E可調整鏡子角度", True, BLACK), (30, 45))

        if player.adjust_mode and player.holding:
            # 調整模式顯示
            target_rect = cur_tile.rect if cur_tile else pg.Rect(0,0,0,0)
            img = player.holding.get_image()
            if img:
                screen.blit(img, target_rect.topleft)
            else:
                p1, p2 = player.holding.endpoints(cur_tile.center)
                pg.draw.line(screen, BLACK, p1, p2, 6)
                pg.draw.line(screen, YELLOW, p1, p2, 2)
            screen.blit(font.render("調整模式: 方向鍵=旋轉, E=確認, Q=取消", True, BLACK), (300, HEIGHT - 30))
            screen.blit(font.render(f"角度: {player.holding.angle}°", True, BLACK), (WIDTH - 160, HEIGHT - 30))

        if not laser_path_cache:
            lx, ly = laser_source
            vx, vy = laser_direction
            mag = math.hypot(vx, vy)
            if mag != 0:
                nx, ny = vx/mag, vy/mag
                start_offset = max(emitter_hitbox_w, emitter_hitbox_h) * 0.5 + 8
                sx, sy = lx + nx * start_offset, ly + ny * start_offset
                tip_len = 40
                end_pos = (sx + nx*tip_len, sy + ny*tip_len)
                pg.draw.line(screen, (180,60,60), (sx, sy), end_pos, 4)

        if game_over:
            overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            t = overlay_font.render("失敗 - 按 R 重來", True, RED)
            tr = t.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(t, tr.topleft)
        
        time_left = max(0, 6000 - elapsed_time) / 1000
        timer_color = RED if elapsed_time >= 5000 else BLACK
        screen.blit(font.render(f"下次發射: {time_left:.1f}秒", True, timer_color), (WIDTH - 220, 10))

        if laser_path_cache:
            draw_laser_path(laser_path_cache)
            if laser_reached_goal and not game_over:
                overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
                overlay.fill((0, 0, 0, 140))
                screen.blit(overlay, (0, 0))
                t = overlay_font.render("成功!", True, GREEN)
                tr = t.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(t, tr.topleft)
                

        legend = [
            "方向鍵: 移動 / 轉動鏡子 (調整模式)",
            "E: 撿起 / 放置",
            "Q: 取消調整",
            "R: 重新開始 (重置計時)",
            "                            要利用到三個鏡子才算通關!!!"
        ]
        for i, s in enumerate(legend):
            screen.blit(font.render(s, True, RED), (10, HEIGHT - 110 + i*18))


        print(player.pos)

        pg.display.flip()


if __name__=="__main__":
    import sys
    import pygame as pg
    pg.init()
    screeninfo=pg.display.Info()
    w,h=screeninfo.current_w,screeninfo.current_h
    update(w,h)
    pg.quit()
    sys.exit()