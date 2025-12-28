import pygame as pg
import XddObjects as xo
import path_dictionary as pd

def setup(game:xo.VAR) ->xo.VAR:
    forest_a=xo.VAR()
    forest_a.npc_list=[]
    forest_a.wall_list=[]
    forest_a.door_list=[]
    ratio=game.zoom_ratio
    wall_visible=False

    forest_a.black_bg = pg.Surface(game.screen.get_size())
    forest_a.black_bg.fill((0, 0, 0))
    forest_a.bg=xo.mapObject(pd.forest_path["a"],(0,0),(2800*1,1300*1))

    #game.char_u.map_x, game.char_u.map_y = game.state_pos["forest_a"]

    #npc_object
    forest_a.sign=xo.npcObject(pd.forest_path["sign"],
                               (2060,555),
                               (115*1.3*ratio,164*1.3*ratio))
    forest_a.npc_list.append(forest_a.sign)
    #wall
    forest_a.wall_bottom=xo.wallObject(pd.barrier_path,
                                       0,
                                       (forest_a.bg.rect.width*0.5, 1185),
                                       (forest_a.bg.rect.width, 300),
                                       wall_visible)
    forest_a.wall_list.append(forest_a.wall_bottom)
    forest_a.wall_top_left=xo.wallObject(pd.barrier_path,
                                       0,
                                       (643, 278),
                                       (1700, 700),
                                       wall_visible)
    forest_a.wall_list.append(forest_a.wall_top_left)
    forest_a.wall_top_right=xo.wallObject(pd.barrier_path,
                                       0,
                                       (2387, 278),
                                       (1300, 700),
                                       wall_visible)
    forest_a.wall_list.append(forest_a.wall_top_right)
    #door
    forest_a.door_home=xo.doorObject(pd.door_path,
                                         (1600,350),
                                         (50,50),
                                         "home",
                                         False)
    forest_a.door_list.append(forest_a.door_home)
    forest_a.door_forest_b=xo.doorObject(pd.door_path,
                                         (0,forest_a.bg.rect.height*0.65),
                                         (30,forest_a.bg.rect.height*0.3),
                                         "forest_b",
                                         False)
    forest_a.door_list.append(forest_a.door_forest_b)
    return forest_a

def update(game:xo.VAR,scene:dict,font,forest_a:xo.VAR) -> dict:
    movequeue: list = game.MoveKeyQueue
    game.last_map_x = game.char_u.map_x
    game.last_map_y = game.char_u.map_y
    game.screen.blit(forest_a.black_bg, (0, 0))
    xo.move_update(
        game,
        scene,
        font,
        game.char_u,
        movequeue,
        forest_a.bg,
        forest_a.npc_list,
        forest_a.wall_list,
        forest_a.door_list
    )

    if game.play_animation:
        xo.draw_scene(game,
                      forest_a.bg,
                      forest_a.npc_list,
                      forest_a.door_list,
                      game.char_u,
                      forest_a.wall_list,
                      )
        frozen = game.screen.copy()
        xo.scene_fade_in(game, frozen)
        game.play_animation = False

    return scene