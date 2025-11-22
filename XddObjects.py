import pygame as pg
import random,math,os

from pygame import Surface

# --- 為了跨平台相容性而進行的路徑設定 ---
#script_dir = os.path.dirname(os.path.abspath(__file__))
#base_dir = os.path.dirname(script_dir)

'''
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
#將父目錄路徑添加到 Python 的搜尋路徑中
#sys.path.insert(0, ...) 將路徑添加到清單的最前面
sys.path.insert(0, base_dir)
import XddObjects as xo
'''
#init
#screeninfo=pg.display.Info()
#w,h=screeninfo.current_w,screeninfo.current_h-80
#screen = pg.display.set_mode((w,h))

class VAR:
    def __init__(self):
        '''
        this is for global variable in diffenent file
        make it easy to transform data between in multiple files
        '''
        pass

def collision_by_mask_with_mouse(rect,mask):
    mouse_pos = pg.mouse.get_pos()
    # 計算滑鼠相對於圖片的偏移量
    offset_x = mouse_pos[0] - rect.x
    offset_y = mouse_pos[1] - rect.y

    if rect.collidepoint(mouse_pos):# 如果滑鼠在矩形內，檢查遮罩
        # 這裡使用 try-except 是為了避免滑鼠座標超出遮罩範圍時的索引錯誤
        try:
            if mask.get_at((offset_x, offset_y)):
                return True
            else:
                return False
        except IndexError:
            # 座標超出遮罩範圍，通常表示滑鼠在矩形邊緣
            return False
    return False

class moveObject(pg.sprite.Sprite):
    def __init__(self,picture_paths,center,size,v,israndom):
        super().__init__()
        self.image=pg.transform.scale(
            pg.image.load(
                os.path.join(
                    picture_paths)).convert_alpha(),
            size)
        self.rect=self.image.get_rect(center=center)
        if israndom:
            self.pos=(random.randint(20,70))
            self.pos=math.radians(self.pos)
        else:
            self.pos=0
        self.dx=v*math.cos(self.pos)
        self.dy=v*math.sin(self.pos)
        
    def update(self,screen):
        self.rect.x+=self.dx
        self.rect.y+=self.dy
        if(self.rect.left<=0 or self.rect.right>=screen.get_width()):
            self.dx*=-1
        if(self.rect.top<=0 or self.rect.bottom>=screen.get_height()):
            self.dy*=-1

class buttonObject(pg.sprite.Sprite):
    def __init__(self,picture_paths,center,size):
        super().__init__()
        self._is_held=False# 內部狀態：追蹤滑鼠是否正按在按鈕上
        self.ispress=False
        self.images = [
            pg.transform.scale(pg.image.load(os.path.join(picture_paths[0])).convert_alpha(), size),
            pg.transform.scale(pg.image.load(os.path.join(picture_paths[1])).convert_alpha(), size),
            pg.transform.scale(pg.image.load(os.path.join(picture_paths[2])).convert_alpha(), size)
        ]
        self.image=self.images[0]
        self.rect=self.image.get_rect(center=center)
        self.mask=pg.mask.from_surface(self.image)
    def update(self):
        self.ispress = False
        mouse_pos = pg.mouse.get_pos()
        mouse_down = pg.mouse.get_pressed()[0]
        #is_mouse_over = self.rect.collidepoint(mouse_pos)
        is_mouse_over=collision_by_mask_with_mouse(self.rect,self.mask)

        if is_mouse_over:
            if mouse_down:
                # 情況1: 滑鼠在按鈕上，且正被按住
                self.image = self.images[2] 
                self._is_held = True
            else:
                # 情況2: 滑鼠在按鈕上，但沒有被按住
                self.image = self.images[1] 
                # 如果上一幀是按住的狀態，代表滑鼠剛被釋放，這就是一次 "點擊"
                if self._is_held:
                    self.ispress = True
                self._is_held = False
        else:
            # 情況3: 滑鼠不在按鈕上
            self.image = self.images[0]
            self._is_held = False

class sliderRailObject(pg.sprite.Sprite):
    def __init__(self,picture_paths,center,size):
        super().__init__()
        self.image=pg.transform.scale(
            pg.image.load(
                os.path.join(
                    picture_paths)).convert_alpha(),
            size)
        self.rect=self.image.get_rect(center=center)
        self.minx=self.rect.left
        self.maxx=self.rect.right

class sliderTwistObject(pg.sprite.Sprite):
    def __init__(self,picture_paths,center,size,min_val,max_val,default_val,rail):
        super().__init__()
        self.rail=rail
        self.min_val=min_val
        self.max_val=max_val
        self.current_val=default_val
        #self.isdrag=False
        self.last_press=False
        self.image=pg.transform.scale(
            pg.image.load(
                os.path.join(
                     picture_paths)).convert_alpha(),
            size)
        self.rect=self.image.get_rect(center=center)
        self.rect.centerx=self.rail.minx+\
                            (self.rail.maxx-self.rail.minx)*\
                            (self.current_val-self.min_val)/(self.max_val-self.min_val)
    def update(self):
        minx=self.rail.minx
        maxx=self.rail.maxx
        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()[0]
        if mouse_pressed:
            if self.rect.collidepoint(mouse_pos):
                self.isdrag=True
        else:
            self.isdrag=False
        #move logic
        if self.isdrag:
            self.rect.centerx = mouse_pos[0]
            # Clamp the position to the rail's boundaries
            minx = self.rail.minx
            maxx = self.rail.maxx
            if self.rect.centerx < minx:
                self.rect.centerx = minx
            if self.rect.centerx > maxx:
                self.rect.centerx = maxx
            self.current_val=self.min_val+\
                            (self.max_val-self.min_val)*\
                            (self.rect.centerx-minx)/(maxx-minx)
            
class Slider:
    def __init__(
        self, x, y, w, h,
        min_val=0, max_val=1, init_val=0.5,
        bg_color=(180,180,180),     # ← 背景條顏色
        fill_color=(100,200,100),   # ← 已填滿顏色
        handle_color=(50,150,50)    # ← 滑塊顏色
    ):
        self.rect = pg.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.value = init_val
        self.handle_radius = 10
        self.dragging = False

        # 顏色屬性
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.handle_color = handle_color

    def draw(self, screen):
        # 畫底條
        pg.draw.rect(screen, self.bg_color, self.rect, border_radius=5)

        # 畫已填滿的部分
        fill_w = int(self.rect.w * self.value)
        pg.draw.rect(screen, self.fill_color, (self.rect.x, self.rect.y, fill_w, self.rect.h), border_radius=5)

        # 畫滑塊
        handle_x = self.rect.x + fill_w
        handle_y = self.rect.y + self.rect.h // 2
        pg.draw.circle(screen, self.handle_color, (handle_x, handle_y), self.handle_radius)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pg.MOUSEMOTION:
            if self.dragging:
                rel_x = event.pos[0] - self.rect.x
                self.value = max(0, min(1, rel_x / self.rect.w))

    def get_value(self):
        return self.value

class characterObject(pg.sprite.Sprite):
    def __init__(self,picture_paths_stand,picture_paths_move,default_center,size):
        super().__init__()
        self.map_x=0
        self.map_y=0
        self.images = [] 
        self.moves=[]
        self.move_index=0
        self.flipx=0
        self.flipy=0
        try:
            for path in picture_paths_stand:
                self.images.append(pg.transform.scale(
                    pg.image.load(
                        path
                        ).convert_alpha(),size))
            self.image = self.images[0]
        except pg.error:
            self.image = pg.Surface(size)
            self.image.fill((0, 255, 0)) # Green placeholder
        try:
            for path in picture_paths_move:
                self.moves.append(pg.transform.scale(
                    pg.image.load(
                        path).convert_alpha(),size))
        except pg.error:
            self.image = pg.Surface(size)
            self.image.fill((0, 255, 0)) # Green placeholder
        self.v=8
        self.rect=self.image.get_rect(center=default_center)
        self.is_move=False
        self.move_state="left"
        self.mask=pg.mask.from_surface(self.image)
        self.mask_rect=self.mask.get_rect(center=default_center)
        self.half_w=self.mask_rect.width/2
        self.half_h=self.mask_rect.height/2
        self.char_half=[self.half_w,self.half_h]
    def update(self,pressKeyQueue):
        self.move_character = False
        self.is_move = False
        self.last_move_state = self.move_state
        self.dx, self.dy = 0, 0

        # 處理按鍵輸入
        if pressKeyQueue:
            latest_key = pressKeyQueue[-1]
            
            if latest_key == pg.K_w:
                self.map_y-=self.v
                self.dy = -self.v
                self.move_state = "up"
                self.is_move = True
                self.flipy = 1
            elif latest_key == pg.K_s:
                self.map_y+=self.v
                self.dy = self.v
                self.move_state = "down"
                self.is_move = True
                self.flipy = 0
            elif latest_key == pg.K_a:
                self.map_x-=self.v
                self.dx = -self.v
                self.move_state = "left"
                self.is_move = True
                self.flipx = 0
            elif latest_key == pg.K_d:
                self.map_x+=self.v
                self.dx = self.v
                self.move_state = "right"
                self.is_move = True
                self.flipx = 1
        
        # 更新動畫
        if self.move_index >= len(self.moves) * 7:
            self.move_index = 0
            
        if not self.is_move:
            self.image = pg.transform.flip(self.images[0], self.flipx, self.flipy)
            self.move_index = 0
        else:
            if self.move_index // 4 == 0 or self.move_index // 4 == 1:
                real_index = 0
            elif self.move_index // 4 == 2 or self.move_index // 4 == 3:
                real_index = 1
            self.image = pg.transform.flip(self.moves[real_index], self.flipx, self.flipy)
            self.move_index += 1

        # 更新遮罩
        if self.last_move_state != self.move_state:
            self.mask = pg.mask.from_surface(self.image)
            self.rect=self.image.get_rect(center=(self.map_x,self.map_y))
            self.last_move_state=self.move_state
            self.half_w=self.mask_rect.width/2
            self.half_h=self.mask_rect.height/2

class npcObject(pg.sprite.Sprite):
    def __init__(self,picture_paths,center,size):
        '''
        :param center: the pos on the map(map x,map y)
        '''
        super().__init__()
        self.images = []
        for path in picture_paths:
            self.images.append(pg.transform.scale(
                pg.image.load(
                    path).convert_alpha(),size))
        self.image=self.images[0]
        #self.rect=self.image.get_rect(center=center)
        self.map_x,self.map_y=center
        self.image_w=self.image.get_width()
        self.image_h=self.image.get_height()
    def update(self,camera_x,camera_y,w,h):
        self.need_draw=False
        if self.map_x-camera_x<=w+self.image_w/2 and self.map_y-camera_y<=h+self.image_h/2\
            and self.map_x-camera_x>=0-self.image_w/2 and self.map_y-camera_y>=0-self.image_h/2:
            self.need_draw=True
            self.rect=self.image.get_rect(center=(self.map_x-camera_x,self.map_y-camera_y))

class mapObject(pg.sprite.Sprite):
    def __init__(self,picture_path,center,size):
        super().__init__()   
        self.image=pg.transform.scale(
            pg.image.load(
                os.path.join(
                    picture_path)).convert_alpha(),
            size)
        self.rect=self.image.get_rect(center=center)
        self.map_w=self.rect.width
        self.map_h=self.rect.height
    def update(self):
        pass# deal in in_game()
        '''self.rect.x-=dx
        self.rect.y-=dy
        if self.rect.top>0:
            self.rect.top=0
        elif self.rect.bottom<h:
            self.rect.bottom=h
        if self.rect.left>0:
            self.rect.left=0
        elif self.rect.right<w:
            self.rect.right=w'''

class wallObject(pg.sprite.Sprite):
    def __init__(self,picture_paths,picture_index,center,size,visible):
        super().__init__()
        self.images = []
        for path in picture_paths:
            self.images.append(pg.transform.scale(
                pg.image.load(
                    os.path.join(path)
                    ).convert_alpha(),size))
        self.image=self.images[picture_index]
        self.rect=self.image.get_rect(center=(10000,10000))#初始位置放在看不到的地方
        self.map_x,self.map_y=center
        self.mask=pg.mask.from_surface(self.image)
        self.mask_rect=self.mask.get_rect(center=center)
        self.half_w=self.mask_rect.width/2
        self.half_h=self.mask_rect.height/2
        self.need_deter=False
        self.visible=visible
    def update(self,camera_x,camera_y,w,h):
        self.need_deter=False#需要判定=false
        #和npc一樣的判斷邏輯
        if self.map_x-camera_x<=w+self.half_w and self.map_y-camera_y<=h+self.half_h\
            and self.map_x-camera_x>=0-self.half_w and self.map_y-camera_y>=0-self.half_h:
            self.need_deter=True
            self.rect=self.image.get_rect(center=(self.map_x-camera_x,self.map_y-camera_y))

class doorObject(pg.sprite.Sprite):
    def __init__(self,picture_paths,center,size,target_state,visible):
        super().__init__()
        self.images=[]
        for path in picture_paths:
            self.images.append(pg.transform.scale(
                pg.image.load(
                    os.path.join(path)).convert_alpha(),size))
        self.image=self.images[0]
        self.rect=self.image.get_rect(center=(10000,10000))
        self.target=target_state
        self.visible=visible
        self.need_deter=False
        self.map_x,self.map_y=center
        self.mask=pg.mask.from_surface(self.image)
        self.mask_rect=self.mask.get_rect(center=center)
        self.half_w=self.mask_rect.width/2
        self.half_h=self.mask_rect.height/2
    def update(self,camera_x,camera_y,w,h):
        self.need_deter=False#需要判定=false
        #和npc一樣的判斷邏輯
        if self.map_x-camera_x<=w+self.half_w and self.map_y-camera_y<=h+self.half_h\
            and self.map_x-camera_x>=0-self.half_w and self.map_y-camera_y>=0-self.half_h:
            self.need_deter=True
            self.rect=self.image.get_rect(center=(self.map_x-camera_x,self.map_y-camera_y))

class ColorCycler:
    """
    自動管理計數器，用正弦波實現平滑的 RGB 循環顏色變換。
    """
    def __init__(self, speed: float = 0.02):
        self.counter = 0.0
        self.speed = speed

    def get_color(self) -> tuple[int, int, int]:
        """
        更新計數器並回傳當前的彩虹循環顏色。
        """
        # 1. 更新計數器
        self.counter += self.speed
        if self.counter>=10000:
            self.counter=0
        time = self.counter

        # 2. 計算 R, G, B 分量 (使用不同的相位差)
        R = math.sin(time) * 127.5 + 127.5
        G = math.sin(time + 2 * math.pi / 3) * 127.5 + 127.5
        B = math.sin(time + 4 * math.pi / 3) * 127.5 + 127.5

        # 3. 確保 R, G, B 值在 0-255 的整數範圍內
        return int(R), int(G), int(B)


#--------------------------------------------------------------------------------------------
#universal function
def draw_scene(game,bg,npc_list,door_list,char,wall_list):#依照圖層序排列
    game.screen.blit(bg.image,bg.rect)
    for npc in npc_list:
        if npc.need_draw:
                game.screen.blit(npc.image,npc.rect)
    for door in door_list:
        if door.need_deter and door.visible:
            game.screen.blit(door.image,door.rect)
    game.screen.blit(char.image,char.rect)
    for wall in wall_list:
        if wall.need_deter and wall.visible:
                game.screen.blit(wall.image,wall.rect)


def wall_collision(char,wall_list,last_map_x,last_map_y): #need rewrite
    wall_rect_corretion_x=20#校正空氣牆
    wall_rect_corretion_y=3
    return_x=char.map_x
    return_y=char.map_y
    for wall in wall_list:
        if wall.need_deter:
            if char.map_x+char.half_w>wall.map_x-wall.half_w +wall_rect_corretion_x and\
                char.map_x-char.half_w<wall.map_x+wall.half_w -wall_rect_corretion_x and\
                abs(char.map_y-wall.map_y)<char.half_h+wall.half_h -wall_rect_corretion_y:
                return_x=last_map_x
            if char.map_y+char.half_h>wall.map_y-wall.half_h +wall_rect_corretion_y and\
                char.map_y-char.half_h<wall.map_y+wall.half_h -wall_rect_corretion_y and\
                abs(char.map_x-wall.map_x)<char.half_w+wall.half_w -wall_rect_corretion_x:
                return_y=last_map_y
    return return_x,return_y

def boundary_deter(char,bg,char_half):
    return_x=char.map_x
    return_y=char.map_y
    if char.map_x < char_half[0]:
        return_x = char_half[0]
    elif char.map_x > bg.map_w - char_half[0]:
        return_x = bg.map_w - char_half[0]
    if char.map_y < char_half[1]:
        return_y = char_half[1]
    elif char.map_y > bg.map_h - char_half[1]:
        return_y = bg.map_h - char_half[1]
    return return_x,return_y

def door_update(game,char,door_list,camera_x,camera_y) -> bool:
    for door in door_list:
        door.update(camera_x,camera_y,game.w,game.h)
        if door.need_deter and door.visible:
            game.screen.blit(door.image, door.rect)
        if abs(door.rect.centerx-char.rect.centerx)<char.half_w and\
            abs(door.rect.centery-char.rect.centery)<char.half_h:
            frozen=game.screen.copy()
            if char.move_state=="up":
                char.map_y+=30
            elif char.move_state=="down":
                char.map_y-=30
            if char.move_state=="left":
                char.map_x+=30
            elif char.move_state=="right":
                char.map_x-=30
            game.state_pos[game.game_state]=char.map_x,char.map_y
            char.map_x,char.map_y=game.state_pos[door.target]
            scene_fade_out(frozen)
            game.game_state=door.target
            break_function: bool=True
            return break_function
    return False

def scene_fade_out(game,frozen):#fill black
    fade_surface = pg.Surface(game.screen.get_size())
    fade_surface = fade_surface.convert() # 為了更快的 blit 速度
    fade_surface.fill((0, 0, 0)) # 填滿黑色
    for alpha in range(0,86):
        game.screen.blit(frozen, (0, 0))
        fade_surface.set_alpha(alpha*3)
        game.screen.blit(fade_surface, (0, 0))
        pg.display.update()

def scene_fade_in(game,frozen,blit:tuple[int,int]=(0,0)):#clean black
    '''
    :param blit: ? whats this?
    '''
    fade_surface = pg.Surface(game.screen.get_size())
    fade_surface = fade_surface.convert() # 為了更快的 blit 速度
    fade_surface.fill((0, 0, 0)) # 填滿黑色
    for alpha in range(85,-1,-1):
        game.screen.blit(frozen, blit)
        fade_surface.set_alpha(alpha*3)
        game.screen.blit(fade_surface, blit)
        pg.display.update()

def move_update(game,font,char,moveKeyQueue,bg,npc_list,wall_list,door_list):
    char.update(moveKeyQueue)
    #2. 邊界判定
    char.map_x,char.map_y=boundary_deter(char,bg,char.char_half)

    #2.1 牆壁碰撞
    char.map_x,char.map_y=wall_collision(char, wall_list,game.last_map_x,game.last_map_y)

     # 3. 根據角色的世界座標計算攝影機的理想位置 (目標是讓角色保持在螢幕中央)
    camera_x = char.map_x - game.w / 2#由 camera_x+w/2=map_x 推導而來
    camera_y = char.map_y - game.h / 2#由 camera_y+h/2=map_y 推導而來

    #4.1 將攝影機限制在地圖邊界內，避免顯示地圖外的黑色區域
    if camera_x < 0:
        camera_x = 0
    elif camera_x > bg.map_w - game.w:
        camera_x = bg.map_w - game.w
    if camera_y < 0:
        camera_y = 0
    elif camera_y > bg.map_h - game.h:
        camera_y = bg.map_h - game.h

    # 4.2. 根據攝影機的位置，更新地圖的螢幕位置 (地圖的移動方向與攝影機相反)
    bg.rect.x = -camera_x
    bg.rect.y = -camera_y
    game.screen.blit(bg.image,bg.rect)
    #4.3
    for npc in npc_list:
        npc.update(camera_x,camera_y,game.w,game.h)
        if npc.need_draw:
            game.screen.blit(npc.image, npc.rect)
    for wall in wall_list:
        wall.update(camera_x,camera_y,game.w,game.h)
        if wall.need_deter and wall.visible:
            game.screen.blit(wall.image, wall.rect)
    if door_update(game,char,door_list,camera_x,camera_y):return

    # 6. 根據攝影機位置和角色的世界座標，計算角色在螢幕上的最終位置
    char.rect.centerx = char.map_x - camera_x
    char.rect.centery = char.map_y - camera_y

    #draw
    '''
    put all object draw to their own update to avoid high complexity 
    '''
    game.screen.blit(char.image, char.rect)
    pos_text=f"pos:({str(char.map_x)},{str(char.map_y)})"
    pos_surface=font.pos.render(pos_text,True,game.rainbow_text_color.get_color())
    game.screen.blit(pos_surface,(10,10))
