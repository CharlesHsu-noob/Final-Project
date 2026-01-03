import pygame as pg
import XddObjects as xo
import path_dictionary as pd

def setup(game:xo.VAR) ->xo.VAR:
    forest_c=xo.VAR()
    forest_c.npc_list=[]
    forest_c.wall_list=[]
    forest_c.door_list=[]
    ratio=game.zoom_ratio
    wall_visible=False

    forest_c.black_bg = pg.Surface(game.screen.get_size())
    forest_c.black_bg.fill((0, 0, 0))
    forest_c.bg=xo.mapObject(pd.forest_path["c"], (0, 0), (5000 * 0.8, 1300 * 0.8))

    #game.char_u.map_x, game.char_u.map_y = game.state_pos["forest_b"]
    #npc_object

    #wall
    forest_c.wall_top_right=xo.wallObject(pd.barrier_path,
                                       0,
                                        (2780, 220),
                                       (2300, 500),
                                        wall_visible)
    forest_c.wall_list.append(forest_c.wall_top_right)
    forest_c.wall_top_left=xo.wallObject(pd.barrier_path,
                                       0,
                                       (170, 220),
                                       (2300, 500),
                                        wall_visible)
    forest_c.wall_list.append(forest_c.wall_top_left)
    forest_c.wall_bottom=xo.wallObject(pd.barrier_path,
                                       0,
                                        (2000, 1000),
                                       (4000, 300),
                                        wall_visible)
    forest_c.wall_list.append(forest_c.wall_bottom)
    #door
    forest_c.door_forest_b=xo.doorObject(pd.door_path,
                                         (4000, 697),
                                         (30, 333),
                                        "forest_b",
                                         False)
    forest_c.door_list.append(forest_c.door_forest_b)
    forest_c.door_forest_d=xo.doorObject(pd.door_path,
                                         (0, 697),
                                         (30, 333),
                                         "forest_d",
                                         False)
    forest_c.door_list.append(forest_c.door_forest_d)
    forest_c.door_forest_e=xo.doorObject(pd.door_path,
                                         (1504, 10),
                                         (333, 20),
                                         "forest_e",
                                         False)
    forest_c.door_list.append(forest_c.door_forest_e)
    return forest_c

def update(game:xo.VAR,scene:dict,font,forest_c:xo.VAR) -> dict:
    movequeue: list = game.MoveKeyQueue
    game.last_map_x = game.char_u.map_x
    game.last_map_y = game.char_u.map_y
    game.screen.blit(forest_c.black_bg, (0, 0))
    xo.move_update(
        game,
        scene,
        font,
        game.char_u,
        movequeue,
        forest_c.bg,
        forest_c.npc_list,
        forest_c.wall_list,
        forest_c.door_list
    )

    if game.play_animation:
        xo.draw_scene(game,
                      forest_c.bg,
                      forest_c.npc_list,
                      forest_c.door_list,
                      game.char_u,
                      forest_c.wall_list,
                      )
        frozen = game.screen.copy()
        xo.scene_fade_in(game, frozen)
        game.play_animation = False

    return scene