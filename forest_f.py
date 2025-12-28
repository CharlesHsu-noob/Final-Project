import pygame as pg
import XddObjects as xo
import path_dictionary as pd

def setup(game:xo.VAR) ->xo.VAR:
    forest_f=xo.VAR()
    forest_f.npc_list=[]
    forest_f.wall_list=[]
    forest_f.door_list=[]
    ratio=game.zoom_ratio
    wall_visible=False

    forest_f.black_bg = pg.Surface(game.screen.get_size())
    forest_f.black_bg.fill((0, 0, 0))
    forest_f.bg=xo.mapObject(pd.forest_path["f"], (0, 0), (2500 * 0.8, 1300 * 0.8))
    #forest_f.bg=xo.mapObject(pd.forest_path["d"], (0, 0), (1920 * 0.8, 1080 * 0.8))

    #game.char_u.map_x, game.char_u.map_y = game.state_pos["forest_b"]
    #npc_object


    #wall
    forest_f.wall_top=xo.wallObject(pd.barrier_path,
                                    0,
                                    (forest_f.bg.rect.width/2,140),
                                    (forest_f.bg.rect.width,600),
                                    wall_visible)
    forest_f.wall_list.append(forest_f.wall_top)
    forest_f.wall_bottom=xo.wallObject(pd.barrier_path,
                                       0,
                                       (forest_f.bg.rect.width/2,1000),
                                       (forest_f.bg.rect.width,300),
                                       wall_visible)
    forest_f.wall_list.append(forest_f.wall_bottom)
    #door
    forest_f.door_forest_e=xo.doorObject(pd.door_path,
                                         (2000,680),
                                         (25,300),
                                         "forest_e",
                                         False)
    #forest_f.door_list.append(forest_f.door_forest_e)
    forest_f.door_forest_g=xo.doorObject(pd.door_path,
                                         (10,680),
                                         (25,300),
                                         "forest_g",
                                         False)
    forest_f.door_list.append(forest_f.door_forest_g)

    return forest_f

def update(game:xo.VAR,scene:dict,font,forest_f:xo.VAR) -> dict:
    movequeue: list = game.MoveKeyQueue
    game.last_map_x = game.char_u.map_x
    game.last_map_y = game.char_u.map_y
    game.screen.blit(forest_f.black_bg, (0, 0))
    xo.move_update(
        game,
        scene,
        font,
        game.char_u,
        movequeue,
        forest_f.bg,
        forest_f.npc_list,
        forest_f.wall_list,
        forest_f.door_list
    )

    if game.play_animation:
        xo.draw_scene(game,
                      forest_f.bg,
                      forest_f.npc_list,
                      forest_f.door_list,
                      game.char_u,
                      forest_f.wall_list,
                      )
        frozen = game.screen.copy()
        xo.scene_fade_in(game, frozen)
        game.play_animation = False

    return scene