import pygame as pg
import XddObjects as xo
import path_dictionary as pd

def setup(game:xo.VAR) ->xo.VAR:
    labg_d=xo.VAR()
    labg_d.npc_list=[]
    labg_d.wall_list=[]
    labg_d.door_list=[]
    ratio=game.zoom_ratio
    wall_visible=False

    labg_d.black_bg = pg.Surface(game.screen.get_size())
    labg_d.black_bg.fill((0, 0, 0))
    labg_d.bg=xo.mapObject(pd.labg_path["d"], (0, 0), (1920 * 0.8, 2880 * 0.8))

    #game.char_u.map_x, game.char_u.map_y = game.state_pos["forest_b"]
    #npc_object

    #wall
    labg_d.wall_left=xo.wallObject(pd.barrier_path,
                                     0,
                                     (labg_d.bg.rect.width / 4-60, labg_d.bg.rect.height/2),
                                     (labg_d.bg.rect.width/3, labg_d.bg.rect.height),
                                     wall_visible)
    labg_d.wall_list.append(labg_d.wall_left)
    labg_d.wall_right=xo.wallObject(pd.barrier_path,
                                     0,
                                     (labg_d.bg.rect.width *3/ 4+60, labg_d.bg.rect.height/2),
                                     (labg_d.bg.rect.width/3, labg_d.bg.rect.height),
                                     wall_visible)
    labg_d.wall_list.append(labg_d.wall_right)
    labg_d.wall_top=xo.wallObject(pd.barrier_path,
                                     0,
                                     (744,328),
                                     (labg_d.bg.rect.width/3, 200),
                                     wall_visible)
    labg_d.wall_list.append(labg_d.wall_top)
    #door
    labg_d.door_labg_c=xo.doorObject(pd.door_path,
                                     (744,labg_d.bg.rect.height),
                                     (330,20),
                                    "labg_c",
                                     wall_visible)
    labg_d.door_list.append(labg_d.door_labg_c)
    return labg_d

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