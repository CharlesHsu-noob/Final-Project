import pygame as pg
import XddObjects as xo
import path_dictionary as pd

def setup(game:xo.VAR) ->xo.VAR:
    forest_c=xo.VAR()
    forest_c.npc_list=[]
    forest_c.wall_list=[]
    forest_c.door_list=[]
    ratio=game.zoom_ratio
    wall_visible=True

    forest_c.black_bg = pg.Surface(game.screen.get_size())
    forest_c.black_bg.fill((0, 0, 0))
    forest_c.bg=xo.mapObject(pd.forest_path["c"], (0, 0), (5000 * 0.8, 1300 * 0.8))

    #game.char_u.map_x, game.char_u.map_y = game.state_pos["forest_b"]
    #npc_object

    #door
    forest_c.door_forest_b=xo.doorObject(pd.door_path,
                                         (forest_c.bg.rect.width, forest_c.bg.rect.height * 0.67),
                                         (30, forest_c.bg.rect.height * 0.32),
                                        "forest_b",
                                         True)
    forest_c.door_list.append(forest_c.door_forest_b)
    forest_c.door_forest_d=xo.doorObject(pd.door_path,
                                         (0, forest_c.bg.rect.height * 0.67),
                                         (30, forest_c.bg.rect.height * 0.3),
                                         "forest_d",
                                         True)
    forest_c.door_list.append(forest_c.door_forest_d)
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