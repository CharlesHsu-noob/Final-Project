import pygame as pg
import XddObjects as xo
import path_dictionary as pd

def setup(game:xo.VAR) ->xo.VAR:
    forest_a=xo.VAR()
    forest_a.npc_list=[]
    forest_a.wall_list=[]
    forest_a.door_list=[]
    ratio=game.zoom_ratio
    wall_visible=True

    forest_a.black_bg = pg.Surface(game.screen.get_size())
    forest_a.black_bg.fill((0, 0, 0))
    forest_a.bg=xo.mapObject(pd.forest_path["a"],(0,0),(2800*1,1300*1))

    #game.char_u.map_x, game.char_u.map_y = game.state_pos["forest_a"]

    #door
    forest_a.door_home=xo.doorObject(pd.door_path,
                                         (1700,350),
                                         (50,50),
                                         "home",
                                         True)
    forest_a.door_list.append(forest_a.door_home)
    return forest_a

def update(game:xo.VAR,font,forest_a:xo.VAR) -> None:
    movequeue: list = game.MoveKeyQueue
    game.last_map_x = game.char_u.map_x
    game.last_map_y = game.char_u.map_y
    game.screen.blit(forest_a.black_bg, (0, 0))
    xo.move_update(
        game,
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