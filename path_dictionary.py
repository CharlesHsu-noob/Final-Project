import os
import pygame as pg
#font

#background
start_menu_bg_path=os.path.join("image","menu","start_menu","main_bg.png")
home_bg_path=os.path.join("image","map","home","home_bg.png")

#debug background
home_debug_bg_path=os.path.join("image","map","home","home_bg_debug.png")

#start menu(button)
lamp_path=[os.path.join("image","menu","start_menu","lamp.png"),
           os.path.join("image","menu","start_menu","lamp_slct.png"),
           os.path.join("image","menu","start_menu","lamp_slct.png")]
notebook_path=[os.path.join("image","menu","start_menu","nb.png"),
               os.path.join("image","menu","start_menu","nb_slct.png"),
               os.path.join("image","menu","start_menu","nb_slct.png")]

#character
char_u_stand_path=[os.path.join("image","char","U","u_stand.png")]
char_u_move_path=[os.path.join("image","char","U","u_s_r.png"),
                  os.path.join("image","char","U","u_s_l.png")]

#universal object
barrier_path=[os.path.join("image","map","150px-barrier.png")]

#CH1-1 Home
cable_path=[os.path.join("image","map","home","cable.png")]
coat_path=[os.path.join("image","map","home","coat.png")]
crayon_path=[os.path.join("image","map","home","crayon.png")]
paper_path=[os.path.join("image","map","home","paper.png")]