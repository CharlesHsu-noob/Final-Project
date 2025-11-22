#font and bgm
import os
def music_setup(game):
    game.music_playlist={
        "start_menu":os.path.join("voice","bgm","start_menu.wav")
    }
    game.current_music=None