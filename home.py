import pygame as pg
import XddObjects as xo
import path_dictionary as pd

def setup(game:xo.VAR) -> xo.VAR :
    home=xo.VAR()
    home.npc_list=[]
    home.door_list=[]
    ratio=game.zoom_ratio

    home.black_bg=pg.Surface(game.screen.get_size())
    home.black_bg.fill((0,0,0))
    #game.bg=xo.mapObject(pd.home_bg_path)
    home.bg=xo.mapObject(pd.home_debug_bg_path,(0,0),(3430*0.85,1193*0.85))

    game.char_u=xo.characterObject(pd.char_u_stand_path,
                                   pd.char_u_move_path,
                                   (100,100),
                                   (270*ratio,360*ratio))#長寬好像相反?
    game.char_u.map_x,game.char_u.map_y=game.state_pos["home"]

    home.cable=xo.npcObject(pd.cable_path,
                            (5000,1500),
                            (118*ratio,57*ratio))
    home.npc_list.append(home.cable)
    home.coat=xo.npcObject(pd.coat_path,
                           (5000,1500),
                           (193*ratio,186*ratio))
    home.npc_list.append(home.coat)
    home.crayon=xo.npcObject(pd.crayon_path,
                             (5000,1500),
                             (42*ratio,63*ratio))
    home.npc_list.append(home.crayon)
    home.paper=xo.npcObject(pd.paper_path,
                            (5000,1500),
                            (94*ratio,90*ratio))
    return home

def update(game,font,home) -> None:
    movequeue:list=game.MoveKeyQueue
    game.last_map_x = game.char_u.map_x
    game.last_map_y = game.char_u.map_y
    game.screen.blit(home.black_bg,(0,0))
    xo.move_update(
        game,
        font,
        game.char_u,
        movequeue,
        home.bg,
        home.npc_list,
        [],
        []
    )
    if game.play_animation:
        xo.draw_scene(game.in_game_bg,
                   game.in_game_npc,
                   game.in_game_door,
                   game.kingnom,
                   game.in_game_wall,
                   game.empty_sprite_group)
        frozen=game.screen.copy()
        xo.scene_fade_in(game,frozen)
        game.play_animation=False
