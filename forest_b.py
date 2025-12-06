import pygame as pg
import XddObjects as xo
import path_dictionary as pd

def setup(game:xo.VAR) ->xo.VAR:
    forest_b=xo.VAR()
    forest_b.npc_list=[]
    forest_b.wall_list=[]
    forest_b.door_list=[]
    ratio=game.zoom_ratio
    wall_visible=True

    forest_b.black_bg = pg.Surface(game.screen.get_size())
    forest_b.black_bg.fill((0, 0, 0))
    forest_b.bg=xo.mapObject(pd.forest_path["b"], (0, 0), (3000 * 0.8, 2300 * 0.8))

    #game.char_u.map_x, game.char_u.map_y = game.state_pos["forest_b"]
    #npc_object

    #door
    forest_b.door_forest_a=xo.doorObject(pd.door_path,
                                        (forest_b.bg.rect.width,forest_b.bg.rect.height*0.35),
                                        (30,forest_b.bg.rect.height * 0.25),
                                        "forest_a",
                                        True)
    forest_b.door_list.append(forest_b.door_forest_a)
    forest_b.door_forest_c=xo.doorObject(pd.door_path,
                                         (0, forest_b.bg.rect.height * 0.8),
                                         (30, forest_b.bg.rect.height * 0.25),
                                         "forest_c",
                                         True)
    forest_b.door_list.append(forest_b.door_forest_c)
    print("forest_b set up success.")
    return forest_b

def update(game:xo.VAR,scene:dict,font,forest_b:xo.VAR) -> dict:
    movequeue: list = game.MoveKeyQueue
    game.last_map_x = game.char_u.map_x
    game.last_map_y = game.char_u.map_y
    game.screen.blit(forest_b.black_bg, (0, 0))
    xo.move_update(
        game,
        scene,
        font,
        game.char_u,
        movequeue,
        forest_b.bg,
        forest_b.npc_list,
        forest_b.wall_list,
        forest_b.door_list
    )

    if game.play_animation:
        xo.draw_scene(game,
                      forest_b.bg,
                      forest_b.npc_list,
                      forest_b.door_list,
                      game.char_u,
                      forest_b.wall_list,
                      )
        frozen = game.screen.copy()
        xo.scene_fade_in(game, frozen)
        game.play_animation = False

    return scene