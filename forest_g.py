import pygame as pg
import XddObjects as xo
import path_dictionary as pd

def setup(game:xo.VAR) ->xo.VAR:
    forest_g=xo.VAR()
    forest_g.npc_list=[]
    forest_g.wall_list=[]
    forest_g.door_list=[]
    ratio=game.zoom_ratio
    wall_visible=False

    forest_g.black_bg = pg.Surface(game.screen.get_size())
    forest_g.black_bg.fill((0, 0, 0))
    forest_g.bg=xo.mapObject(pd.forest_path["g"], (0, 0), (4800 * 0.8, 1600 * 0.8))
    #forest_f.bg=xo.mapObject(pd.forest_path["d"], (0, 0), (1920 * 0.8, 1080 * 0.8))

    #game.char_u.map_x, game.char_u.map_y = game.state_pos["forest_b"]
    #npc_object


    #wall
    forest_g.wall_top=xo.wallObject(pd.barrier_path,
                                    0,
                                    (forest_g.bg.rect.width / 2, 140),
                                    (forest_g.bg.rect.width, 600),
                                    wall_visible)
    forest_g.wall_list.append(forest_g.wall_top)
    forest_g.wall_bottom_right=xo.wallObject(pd.barrier_path,
                                       0,
                                       (forest_g.bg.rect.width *0.85, 1060),
                                       (forest_g.bg.rect.width*0.52, 400),
                                       wall_visible)
    forest_g.wall_list.append(forest_g.wall_bottom_right)
    forest_g.wall_bottom_left=xo.wallObject(pd.barrier_path,
                                       0,
                                       (forest_g.bg.rect.width *0.225, 1060),
                                       (forest_g.bg.rect.width*0.6, 400),
                                       wall_visible)
    forest_g.wall_list.append(forest_g.wall_bottom_left)
    forest_g.wall_down_mid=xo.wallObject(pd.barrier_path,
                                       0,
                                       (forest_g.bg.rect.w*0.55, 1160),
                                       (700, 100),
                                       wall_visible)
    forest_g.wall_list.append(forest_g.wall_down_mid)
    #door
    forest_g.door_forest_f=xo.doorObject(pd.door_path,
                                         (forest_g.bg.rect.w+10,680),
                                         (25,400),
                                         "forest_f",
                                         False)
    forest_g.door_list.append(forest_g.door_forest_f)
    forest_g.door_forest_h=xo.doorObject(pd.door_path,
                                         (0,680),
                                         (25,300),
                                         "forest_h",
                                         False)
    forest_g.door_list.append(forest_g.door_forest_h)

    return forest_g

def update(game:xo.VAR,scene:dict,font,forest_g:xo.VAR) -> dict:
    movequeue: list = game.MoveKeyQueue
    game.last_map_x = game.char_u.map_x
    game.last_map_y = game.char_u.map_y
    game.screen.blit(forest_g.black_bg, (0, 0))
    xo.move_update(
        game,
        scene,
        font,
        game.char_u,
        movequeue,
        forest_g.bg,
        forest_g.npc_list,
        forest_g.wall_list,
        forest_g.door_list
    )

    if game.play_animation:
        xo.draw_scene(game,
                      forest_g.bg,
                      forest_g.npc_list,
                      forest_g.door_list,
                      game.char_u,
                      forest_g.wall_list,
                      )
        frozen = game.screen.copy()
        xo.scene_fade_in(game, frozen)
        game.play_animation = False

    return scene