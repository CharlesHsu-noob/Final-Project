import pygame as pg
import XddObjects as xo
import path_dictionary as pd

def setup(game:xo.VAR) -> xo.VAR :
    home=xo.VAR()
    home.npc_list=[]
    home.wall_list=[]
    home.door_list=[]
    ratio=game.zoom_ratio
    wall_visible=False

    home.black_bg=pg.Surface(game.screen.get_size())
    home.black_bg.fill((0,0,0))
    home.bg=xo.mapObject(pd.home_bg_path,(0,0),(3430*0.85,1193*0.85))
    #home.bg=xo.mapObject(pd.home_debug_bg_path,(0,0),(3430*0.85,1193*0.85))

    game.char_u=xo.characterObject(pd.char_u_stand_path,
                                   pd.char_u_move_path,
                                   (100,100),
                                   (270*ratio,360*ratio))#長寬好像相反?
    game.char_u.map_x,game.char_u.map_y=game.state_pos["home"]

    #interact object
    size_raito=1.15
    ratio*=size_raito
    home.cable=xo.npcObject(pd.cable_path,
                            (1960,462),
                            (118*ratio,57*ratio))
    home.npc_list.append(home.cable)
    home.coat=xo.npcObject(pd.coat_path,
                           (1410,557),
                           (193*ratio,186*ratio))
    home.npc_list.append(home.coat)
    home.crayon=xo.npcObject(pd.crayon_path,
                             (779,625),
                             (42*ratio,63*ratio))
    home.npc_list.append(home.crayon)
    home.paper=xo.npcObject(pd.paper_path,
                            (2303,388),
                            (94*ratio,90*ratio))
    home.npc_list.append(home.paper)
    #wall
    home.wall_bed=xo.wallObject(pd.barrier_path,
                                0,
                                (2750,421),
                                (260,425),
                                wall_visible)
    home.wall_list.append(home.wall_bed)
    home.wall_desk=xo.wallObject(pd.barrier_path,
                                  0,
                                  (2219,400),
                                  (408,300),
                                  wall_visible)
    home.wall_list.append(home.wall_desk)
    home.wall_bookcase=xo.wallObject(pd.barrier_path,
                                     0,
                                     (1710,318),
                                     (310,350),
                                     wall_visible)
    home.wall_list.append(home.wall_bookcase)
    home.wall_tube=xo.wallObject(pd.barrier_path,
                                 0,
                                 (1400,410),
                                 (250,150),
                                 wall_visible)
    home.wall_list.append(home.wall_tube)
    home.wall_coach=xo.wallObject(pd.barrier_path,
                                  0,
                                  (545,880),
                                  (380,210),
                                  wall_visible)
    home.wall_list.append(home.wall_coach)
    home.wall_table = xo.wallObject(pd.barrier_path,
                                    0,
                                    (542, 590),
                                    (460, 120),
                                    wall_visible)
    home.wall_list.append(home.wall_table)
    home.wall_tv = xo.wallObject(pd.barrier_path,
                                    0,
                                    (542, 360),
                                    (600, 120),
                                    wall_visible)
    home.wall_list.append(home.wall_tv)
    #wall 四周牆壁
    home.wall_right=xo.wallObject(pd.barrier_path,
                                  0,
                                  (2860,home.bg.rect.height/2),
                                  (90,home.bg.rect.height),
                                  wall_visible)
    home.wall_list.append(home.wall_right)
    home.wall_left = xo.wallObject(pd.barrier_path,
                                    0,
                                    (55, home.bg.rect.height / 2),
                                    (120, home.bg.rect.height),
                                    wall_visible)
    home.wall_list.append(home.wall_left)
    home.wall_top=xo.wallObject(pd.barrier_path,
                                0,
                                (home.bg.rect.width/2,280),
                                (home.bg.rect.width,200),
                                wall_visible)
    home.wall_list.append(home.wall_top)
    home.wall_middle_up=xo.wallObject(pd.barrier_path,
                                      0,
                                      (home.bg.rect.width/2*1.05,500),
                                      (100,400),
                                      wall_visible)
    home.wall_list.append(home.wall_middle_up)
    home.wall_middle_down=xo.wallObject(pd.barrier_path,
                                        0,
                                        (home.bg.rect.width/2*1.05,890),
                                        (100,100),
                                        wall_visible)
    home.wall_list.append(home.wall_middle_down)
    home.wall_down_right=xo.wallObject(pd.barrier_path,
                                       0,
                                       (home.bg.rect.width/2*1.44,985),
                                       (home.bg.rect.width*0.7,150),
                                       wall_visible)
    home.wall_list.append(home.wall_down_right)
    home.wall_down_left = xo.wallObject(pd.barrier_path,
                                         0,
                                         (home.bg.rect.width / 2 * 0.25, 985),
                                         (home.bg.rect.width * 0.36, 150),
                                         wall_visible)
    home.wall_list.append(home.wall_down_left)
    #door
    home.door_forest_a=xo.doorObject(pd.door_path,
                                     (980,980),
                                     (100,50),
                                     "forest_a",
                                     True)
    home.door_list.append(home.door_forest_a)
    return home

def update(game,scene:dict,font,home) -> dict:
    movequeue:list=game.MoveKeyQueue
    game.last_map_x = game.char_u.map_x
    game.last_map_y = game.char_u.map_y
    game.screen.blit(home.black_bg,(0,0))
    scene=xo.move_update(
        game,
        scene,
        font,
        game.char_u,
        movequeue,
        home.bg,
        home.npc_list,
        home.wall_list,
        home.door_list
    )

    if game.play_animation:
        xo.draw_scene(game,
                   home.bg,
                   home.npc_list,
                   home.door_list,
                   game.char_u,
                   [],
                   )
        frozen=game.screen.copy()
        xo.scene_fade_in(game,frozen)
        game.play_animation=False

    return scene
