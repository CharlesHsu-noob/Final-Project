import pygame as pg
import XddObjects as xo
import path_dictionary as pd

def setup(game:xo.VAR) ->xo.VAR:
    forest_d=xo.VAR()
    forest_d.npc_list=[]
    forest_d.wall_list=[]
    forest_d.door_list=[]
    ratio=game.zoom_ratio
    wall_visible=False

    forest_d.black_bg = pg.Surface(game.screen.get_size())
    forest_d.black_bg.fill((0, 0, 0))
    forest_d.bg=xo.mapObject(pd.forest_d_debug_path,(0,0),(2133*0.72,1200*0.72))
    #forest_d.bg=xo.mapObject(pd.forest_path["d"], (0, 0), (1920 * 0.8, 1080 * 0.8))

    #game.char_u.map_x, game.char_u.map_y = game.state_pos["forest_b"]
    #npc_object

    forest_d.boat=xo.npcObject(pd.forest_path["boat"],
                               (675,500),
                               (156*1.6*ratio,341*1.6*ratio))
    forest_d.npc_list.append(forest_d.boat)
    #wall
    forest_d.wall_lake_major=xo.wallObject(pd.barrier_path,
                                    0,
                                    (360, 500),
                                    (800,1080),
                                    wall_visible)
    forest_d.wall_list.append(forest_d.wall_lake_major)
    forest_d.wall_lake_up_major=xo.wallObject(pd.barrier_path,
                                              0,
                                              (800,100),
                                              (400,500),
                                              wall_visible)
    forest_d.wall_list.append(forest_d.wall_lake_up_major)
    forest_d.wall_lake_up_senior=xo.wallObject(pd.barrier_path,
                                               0,
                                               (1028,250),
                                               (120,220),
                                               wall_visible)
    forest_d.wall_list.append(forest_d.wall_lake_up_senior)
    forest_d.wall_lake_up_third=xo.wallObject(pd.barrier_path,
                                              0,
                                              (1000,50),
                                              (50,220),
                                              wall_visible)
    forest_d.wall_list.append(forest_d.wall_lake_up_third)
    forest_d.wall_lake_down_major=xo.wallObject(pd.barrier_path,
                                                0,
                                                (884,778),
                                                (400,350),
                                                wall_visible)
    forest_d.wall_list.append(forest_d.wall_lake_down_major)
    #door
    forest_d.door_forest_c=xo.doorObject(pd.door_path,
                                         (forest_d.bg.rect.width, forest_d.bg.rect.height * 0.67),
                                         (30, forest_d.bg.rect.height * 0.32),
                                        "forest_c",
                                         False)
    forest_d.door_list.append(forest_d.door_forest_c)

    return forest_d

def update(game:xo.VAR,scene:dict,font,forest_d:xo.VAR) -> dict:
    movequeue: list = game.MoveKeyQueue
    game.last_map_x = game.char_u.map_x
    game.last_map_y = game.char_u.map_y
    game.screen.blit(forest_d.black_bg, (0, 0))
    xo.move_update(
        game,
        scene,
        font,
        game.char_u,
        movequeue,
        forest_d.bg,
        forest_d.npc_list,
        forest_d.wall_list,
        forest_d.door_list
    )

    if game.play_animation:
        xo.draw_scene(game,
                      forest_d.bg,
                      forest_d.npc_list,
                      forest_d.door_list,
                      game.char_u,
                      forest_d.wall_list,
                      )
        frozen = game.screen.copy()
        xo.scene_fade_in(game, frozen)
        game.play_animation = False

    return scene