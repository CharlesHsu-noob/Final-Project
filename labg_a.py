import pygame as pg
import XddObjects as xo
import path_dictionary as pd

def setup(game:xo.VAR) ->xo.VAR:
    labg_a=xo.VAR()
    labg_a.npc_list=[]
    labg_a.wall_list=[]
    labg_a.door_list=[]
    ratio=game.zoom_ratio
    wall_visible=False

    labg_a.black_bg = pg.Surface(game.screen.get_size())
    labg_a.black_bg.fill((0, 0, 0))
    labg_a.bg=xo.mapObject(pd.labg_path["a"], (0, 0), (3200 * 0.8, 1080 * 0.8))

    #game.char_u.map_x, game.char_u.map_y = game.state_pos["forest_b"]
    #npc_object

    #wall
    labg_a.wall_bottom=xo.wallObject(pd.barrier_path,
                                     0,
                                     (labg_a.bg.rect.width/2,720),
                                     (labg_a.bg.rect.width,200),
                                     wall_visible)
    labg_a.wall_list.append(labg_a.wall_bottom)
    labg_a.wall_top=xo.wallObject(pd.barrier_path,
                                     0,
                                     (labg_a.bg.rect.width/2,252),
                                     (labg_a.bg.rect.width,200),
                                     wall_visible)
    labg_a.wall_list.append(labg_a.wall_top)
    #door
    labg_a.door_forest_h=xo.doorObject(pd.door_path,
                                       (labg_a.bg.rect.width,502),
                                       (30,330),
                                       "forest_h",
                                       wall_visible)
    labg_a.door_list.append(labg_a.door_forest_h)
    labg_a.door_labg_b=xo.doorObject(pd.door_path,
                                       (0,502),
                                       (30,330),
                                       "labg_b",
                                       wall_visible)
    labg_a.door_list.append(labg_a.door_labg_b)
    return labg_a

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