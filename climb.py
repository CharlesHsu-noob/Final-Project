def update(screen_w,screen_h):
    import pygame as pg
    import sys
    import os

    # ================= 初始化 =================
    pg.init()

    # --- 世界大小（邏輯用，不變） ---
    WORLD_WIDTH, WORLD_HEIGHT = 1350, 600

    # --- 實際視窗大小 ---
    WINDOW_WIDTH, WINDOW_HEIGHT = screen_w, screen_h
    screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pg.display.set_caption("Climbing Game")

    clock = pg.time.Clock()
    FPS = 60

    # --- 虛擬畫面（所有遊戲內容畫在這） ---
    world_surface = pg.Surface((WORLD_WIDTH, WORLD_HEIGHT), pg.SRCALPHA)

    # --- 等比例縮放計算 ---
    scale_x =1.536 
    scale_y =1.8 
    SCALE =1.536 

    scaled_width =2074 
    scaled_height =921 
    offset_x = (WINDOW_WIDTH - scaled_width) // 2
    offset_y = (WINDOW_HEIGHT - scaled_height) // 2 +8


    # ================= 顏色 =================
    BLACK = (0, 0, 0)
    
    # 載入圖片 (略過未變動部分...)
    try:
        bg_img_raw = pg.image.load(os.path.join("image", "forest_e.png")).convert()
        bg_img_full = pg.transform.scale(bg_img_raw, (2000, 3500))
    except:
        bg_img_full = pg.Surface((2000, 3500)) # 防呆

    try:
        player_img = pg.image.load(os.path.join("image", "chuchutest", "u_stand.png")).convert_alpha()
    except:
        player_img = pg.Surface((48, 64)) # 防呆

    PLAYER_WIDTH = 48
    PLAYER_HEIGHT = 64
    player_img = pg.transform.scale(player_img, (PLAYER_WIDTH, PLAYER_HEIGHT))
    PLAYER_WIDTH = 16
    char_half_w=24

    # ================= 玩家設定 =================
    class char(pg.sprite.Sprite):
        def __init__(self,image:pg.surface.Surface,player_x,player_y):
            super().__init__()
            self.image=image
            self.rect=self.image.get_rect(center=(player_x,player_y))

    # [修改] 這裡設定你要往下移多少像素
    SHIFT_DOWN = 67  # <--- 修改這個數字，越大越往下，負數則往上

    player_x = 1050
    player_y = 200 + SHIFT_DOWN # [修改] 玩家初始位置也要跟著下移，不然會摔死
    bg_scroll_anchor_y = 300 
    BG_SCROLL_ANCHOR_INITIAL = bg_scroll_anchor_y
    player_vx = 0
    player_vy = 0
    char_u=char(player_img,player_x,player_y)
    MOVE_SPEED = 2
    JUMP_SPEED = -11
    GRAVITY = 0.6

    # 跳躍控制
    jump_pressed = False
    COYOTE_TIME = 0.12
    time_since_ground = 0

    # --- 跳躍冷卻設定 ---
    JUMP_COOLDOWN = 750  
    last_jump_time = -750

    # ================= 平台設定 =================
    class platOb(pg.sprite.Sprite):
        def __init__(self,image:pg.surface.Surface,pos:tuple[int,int]):
            super().__init__()
            self.image=image
            self.rect=self.image.get_rect(center=pos)
    PLATFORM_WIDTH = 80
    PLATFORM_HEIGHT = 15

    # [修改] 原始座標列表 (保持不變)
    raw_platform_positions = [
        (-60, 322),(20, 322),(100, 322),(180, 322),(260, 322),(340, 322),(420, 322),
        (500, 322),(580, 322),(660, 322),(740, 322),(820, 322),(900, 322),(980, 322),
        (1060, 322),(1140, 322),(1220, 322),(1300, 322),
        (550, 240),(850, 230),(650, 160),(700, 90),(630, 10),
        (550, -80),(620, -160),(760, -230),(800, -300),(750, -380),
        (700, -450),(620, -530),(550, -590),(490, -640),(400, -693),(350, -693),(290, -693),(210, -693),(130, -693),
    ]

    # [修改] 自動計算新的座標：將所有 Y 加上 SHIFT_DOWN
    platform_positions = [(x, y + SHIFT_DOWN) for x, y in raw_platform_positions]

    # [修改] 原始隱藏岩石座標
    raw_hidden_rock_coords = [
        (350, -693),(290, -693), (210, -693), (130, -693)
    ]
    # [修改] 自動計算新的隱藏岩石座標
    hidden_rock_coords = [(x, y + SHIFT_DOWN) for x, y in raw_hidden_rock_coords]

    platforms = [pg.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT) for x, y in platform_positions]
    ground = platforms[:18]

    try:
        rock_img = pg.image.load(os.path.join("image", "forest_rock.png")).convert_alpha()
        rock_img = pg.transform.scale(rock_img, (PLATFORM_WIDTH, PLATFORM_HEIGHT))
    except:
        rock_img = pg.Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))

    platform_object=[]
    for pos in platform_positions:
        wall=platOb(rock_img,pos)
        platform_object.append(wall)

    # ================= 左側隱形牆壁設定 =================
    # [修改] 牆壁的位置也加上 SHIFT_DOWN 比較保險
    debug_wall = pg.Rect(350, 100 + SHIFT_DOWN, 40, 6000)

    platforms.append(debug_wall)
    # ========================================================


    # ================= 判斷是否站在平台 =================
    offset_for_plat_x=48
    def is_on_platform(px, py):
        for plat in platforms:
            if plat.colliderect(px, py,PLAYER_WIDTH,PLAYER_HEIGHT):
                return True
        return False

    # ================= 捲動設定 =================
    SCROLL_UP_TRIGGER_Y = WORLD_HEIGHT * 0.35
    SCROLL_DOWN_TRIGGER_Y = 250

    # [修改] 初始地板高度 (用於捲動限制)，這也需要更新
    # 原本是 322，現在變成 322 + SHIFT_DOWN
    INITIAL_GROUND_Y = 322 + SHIFT_DOWN 

    # ================= 遊戲主迴圈 =================
    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        current_time = pg.time.get_ticks()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                pg.quit()
                sys.exit()

        # ---------- 操作 ----------
        keys = pg.key.get_pressed()
        player_vx = 0
        if keys[pg.K_LEFT]:
            player_vx = -MOVE_SPEED
        if keys[pg.K_RIGHT]:
            player_vx = MOVE_SPEED

        # ---------- 土狼時間 ----------
        if is_on_platform(player_x, player_y):
            time_since_ground = 0
        else:
            time_since_ground += dt

        # ---------- 跳躍 ----------
        if keys[pg.K_SPACE]:
            if not jump_pressed and time_since_ground <= COYOTE_TIME:
                if current_time - last_jump_time > JUMP_COOLDOWN:
                    player_vy = JUMP_SPEED
                    jump_pressed = True
                    time_since_ground = COYOTE_TIME + 1
                    last_jump_time = current_time
        else:
            jump_pressed = False

        # ---------- 水平移動 ----------
        player_x += player_vx
        player_rect = pg.Rect(
            player_x - PLAYER_WIDTH // 2,
            player_y - PLAYER_HEIGHT,
            PLAYER_WIDTH,
            PLAYER_HEIGHT
        )

        # 碰撞檢測
        for i in range(len(platforms)):
            plat = platforms[i]
            if player_rect.colliderect(plat):
                if player_vx > 0:
                    player_x = plat.left - PLAYER_WIDTH // 2
                elif player_vx < 0:
                    player_x = plat.right + PLAYER_WIDTH // 2

        # ---------- 垂直移動 ----------
        player_vy += GRAVITY
        player_y += player_vy

        player_rect = pg.Rect(
            player_x - PLAYER_WIDTH // 2,
            player_y - PLAYER_HEIGHT,
            PLAYER_WIDTH,
            PLAYER_HEIGHT
        )

        for plat in platforms:
            if player_rect.colliderect(plat):
                if player_vy > 0:
                    player_y = plat.top
                    player_vy = 0
                    time_since_ground = 0
                elif player_vy < 0:
                    player_y = plat.bottom + PLAYER_HEIGHT
                    player_vy = 0

        # ---------- 邊界 ----------
        player_x = max(
            PLAYER_WIDTH ,
            min(WORLD_WIDTH - PLAYER_WIDTH // 2, player_x)
        )

        # ---------- 向上捲動 ----------
        if player_y < SCROLL_UP_TRIGGER_Y:
            scroll = SCROLL_UP_TRIGGER_Y - player_y
            int_scroll = int(scroll)
            player_y += int_scroll
            for plat in platforms:
                plat.y += int_scroll

            new_hidden_coords = []
            for h_coord in hidden_rock_coords:
                new_hidden_coords.append((h_coord[0], h_coord[1] + int_scroll))
            hidden_rock_coords = new_hidden_coords

            bg_scroll_anchor_y += int_scroll

        # ---------- 向下捲動 ----------
        # [修改] 這裡使用了動態計算後的 INITIAL_GROUND_Y
        if player_y > SCROLL_DOWN_TRIGGER_Y:
            raw_scroll = player_y - SCROLL_DOWN_TRIGGER_Y
            int_scroll = int(raw_scroll)

            # 確保不會捲動超過地板初始位置
            if platforms[0].y - int_scroll < INITIAL_GROUND_Y:
                int_scroll = platforms[0].y - INITIAL_GROUND_Y

            if int_scroll > 0:
                player_y -= int_scroll
                for plat in platforms:
                    plat.y -= int_scroll

                new_hidden_coords = []
                for h_coord in hidden_rock_coords:
                    new_hidden_coords.append((h_coord[0], h_coord[1] - int_scroll))
                hidden_rock_coords = new_hidden_coords

                bg_scroll_anchor_y -= int_scroll
                bg_scroll_anchor_y = max(bg_scroll_anchor_y, BG_SCROLL_ANCHOR_INITIAL)


        # ================= 繪製（畫在 world_surface） =================
        world_surface.fill((0, 0, 0, 0))

        for plat in platforms:
            if plat == debug_wall:
                pass 
            elif plat in ground:
                pass
            elif plat.topleft in hidden_rock_coords:
                pass
            else:
                world_surface.blit(rock_img, plat.topleft)

        blit_offset_y=5
        blit_offset_x=15
        world_surface.blit(
            player_img,
            (player_x - PLAYER_WIDTH // 2-blit_offset_x, player_y - PLAYER_HEIGHT+blit_offset_y)
        )

        # ================= 縮放顯示 =================
        scaled_surface = pg.transform.smoothscale(
            world_surface,
            (scaled_width, scaled_height)
        )

        screen.fill(BLACK)

        # 背景繪製
        bg_scroll_speed = 2.0
        bg_start_y = 480 - 3500
        bg_y = bg_start_y + (bg_scroll_anchor_y) * bg_scroll_speed

        if bg_y > 0: bg_y = 0
        if bg_y < 1080 - 3500: bg_y = 1080 - 3500

        bg_x = (WINDOW_WIDTH - 2000) // 2
        screen.blit(bg_img_full, (bg_x, bg_y))

        screen.blit(scaled_surface, (offset_x, offset_y))
        pg.display.flip()

        char_u.rect=char_u.image.get_rect(center=(player_x,player_y))

        if player_x<238:
           break
        print(player_x)

    