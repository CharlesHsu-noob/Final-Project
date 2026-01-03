import pygame as pg
import XddObjects as xo
import path_dictionary as pd

def setup(game:xo.VAR) ->xo.VAR:
    forest_h=xo.VAR()
    forest_h.npc_list=[]
    forest_h.wall_list=[]
    forest_h.door_list=[]
    ratio=game.zoom_ratio
    wall_visible=False

    forest_h.black_bg = pg.Surface(game.screen.get_size())
    forest_h.black_bg.fill((0, 0, 0))
    forest_h.bg=xo.mapObject(pd.forest_path["h"], (0, 0), (2900 * 0.8, 1300 * 0.8))
    #forest_f.bg=xo.mapObject(pd.forest_path["d"], (0, 0), (1920 * 0.8, 1080 * 0.8))

    #game.char_u.map_x, game.char_u.map_y = game.state_pos["forest_b"]
    #npc_object


    #wall
    forest_h.wall_top=xo.wallObject(pd.barrier_path,
                                    0,
                                    (forest_h.bg.rect.width / 2, 150),
                                    (forest_h.bg.rect.width, 600),
                                    wall_visible)
    forest_h.wall_list.append(forest_h.wall_top)
    forest_h.wall_bottom=xo.wallObject(pd.barrier_path,
                                    0,
                                    (forest_h.bg.rect.width / 2, 950),
                                    (forest_h.bg.rect.width, 200),
                                    wall_visible)
    forest_h.wall_list.append(forest_h.wall_bottom)
    #door
    forest_h.door_forest_g=xo.doorObject(pd.door_path,
                                         (forest_h.bg.rect.w + 10, 680),
                                         (25,400),
                                         "forest_g",
                                         False)
    forest_h.door_list.append(forest_h.door_forest_g)
    forest_h.door_labg_a=xo.doorObject(pd.door_path,
                                         (156,700),
                                         (25,320),
                                         "labg_a",
                                         False)
    forest_h.door_list.append(forest_h.door_labg_a)

    return forest_h

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