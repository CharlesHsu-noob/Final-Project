import pygame as pg
import XddObjects as xo
import path_dictionary as pd

def setup(game:xo.VAR) ->xo.VAR:
    labg_c=xo.VAR()
    labg_c.npc_list=[]
    labg_c.wall_list=[]
    labg_c.door_list=[]
    ratio=game.zoom_ratio
    wall_visible=False

    labg_c.black_bg = pg.Surface(game.screen.get_size())
    labg_c.black_bg.fill((0, 0, 0))
    labg_c.bg=xo.mapObject(pd.labg_path["c"], (0, 0), (2000 * 0.8, 1080 * 0.8))

    #game.char_u.map_x, game.char_u.map_y = game.state_pos["forest_b"]
    #npc_object

    #wall
    labg_c.wall_bottom=xo.wallObject(pd.barrier_path,
                                     0,
                                     (labg_c.bg.rect.width / 2, 720),
                                     (labg_c.bg.rect.width, 200),
                                     wall_visible)
    labg_c.wall_list.append(labg_c.wall_bottom)
    labg_c.wall_top_left=xo.wallObject(pd.barrier_path,
                                       0,
                                       (labg_c.bg.rect.width / 4, 252),
                                       (labg_c.bg.rect.width*0.4, 200),
                                       wall_visible)
    labg_c.wall_list.append(labg_c.wall_top_left)
    labg_c.wall_top_right=xo.wallObject(pd.barrier_path,
                                       0,
                                       (labg_c.bg.rect.width *3/ 4, 252),
                                       (labg_c.bg.rect.width*0.4, 200),
                                       wall_visible)
    labg_c.wall_list.append(labg_c.wall_top_right)
    labg_c.wall_top_center=xo.wallObject(pd.barrier_path,
                                       0,
                                       (labg_c.bg.rect.width/2, 50),
                                       (labg_c.bg.rect.width*0.4, 200),
                                       wall_visible)
    labg_c.wall_list.append(labg_c.wall_top_center)
    #door
    labg_c.door_labg_b=xo.doorObject(pd.door_path,
                                       (labg_c.bg.rect.width, 502),
                                       (20,330),
                                       "labg_b",
                                       wall_visible)
    #labg_c.door_list.append(labg_c.door_labg_b)
    labg_c.door_labg_e=xo.doorObject(pd.door_path,
                                     (0,502),
                                     (30,330),
                                       "labg_e",
                                     wall_visible)
    labg_c.door_list.append(labg_c.door_labg_e)
    labg_c.door_labg_d=xo.doorObject(pd.door_path,
                                     (812,150),
                                     (230,50),
                                       "labg_d",
                                     wall_visible)
    labg_c.door_list.append(labg_c.door_labg_d)
    return labg_c

def update(game:xo.VAR,scene:dict,font,forest_c:xo.VAR) -> dict:
    movequeue: list = game.MoveKeyQueue
    if game.last_game_state=="labg_b":
        game.char_u.map_x,game.char_u.map_y=game.state_pos["labg_c"]
        print("set pos to labg_c(",game.state_pos["labg_c"],")")
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