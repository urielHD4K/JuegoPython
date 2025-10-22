import os
import random
import pygame
from pygame.locals import *
from moviepy.editor import VideoFileClip
import numpy as np
from objects import World, Player, Button, draw_lines, load_level, draw_text, sounds

# Window setup
SIZE = WIDTH , HEIGHT= 1000, 650
tile_size = 50

pygame.init()
pygame.mixer.init()
win = pygame.display.set_mode(SIZE)
pygame.display.set_caption('Las Aventuras de')
clock = pygame.time.Clock()
FPS = 30

print("Iniciando carga de video...")
video_path = 'video/1.mp4'

full_path = os.path.abspath(video_path)
print(f"Buscando video en la ruta absoluta: {full_path}")

if not os.path.exists(full_path):
    clip = None
    intro_sound = None
else:
    intro_sound = None  
    try:
        # --- Paso 1: Cargar el video (esto ya funcionaba) ---
        clip = VideoFileClip(full_path).resize(width=WIDTH, height=HEIGHT)
        clip_duration_ms = clip.duration * 1000
        print("Video cargado correctamente. Procesando audio...")
        try:
            if clip.audio is None:
                print("El video no tiene pista de audio (clip.audio is None). Se reproducirá en silencio.")
                pass # intro_sound ya es None
            else:
                print("El video SÍ tiene pista de audio. Intentando procesar...")
                audio_array = clip.audio.to_soundarray(fps=44100, nbytes=2)
                
                if audio_array.size == 0:
                    print("La pista de audio está vacía (size 0). Se reproducirá en silencio.")
                    pass # intro_sound ya es None
                else:
                    if audio_array.ndim == 1:
                        audio_array = np.column_stack((audio_array, audio_array))
                    
                    intro_sound = pygame.mixer.Sound(buffer=audio_array)
                    print("Audio procesado correctamente. ¡Listo!")

        except Exception as audio_e:
            intro_sound = None # Nos aseguramos de que sea None

    except Exception as e:  
        clip = None
        intro_sound = None
bg1 = pygame.image.load('assets/BG1.jpg') 
bg2 = pygame.image.load('assets/BG1.jpg')
bg = bg1
sun = pygame.image.load('assets/luna.png')
jungle_dash = pygame.image.load('assets/title.png')
you_won = pygame.image.load('assets/won.png')


# loading level 1
level = 1
max_level = len(os.listdir('levels/'))
data = load_level(level)

player_pos = (10, 340)


# creating world & objects
water_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
forest_group = pygame.sprite.Group()
diamond_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
bridge_group = pygame.sprite.Group()
groups = [water_group, lava_group, forest_group, diamond_group, enemies_group, exit_group, platform_group,
            bridge_group]
world = World(win, data, groups)
player = Player(win, player_pos, world, groups)

# creating buttons
play= pygame.image.load('assets/play.png')
replay = pygame.image.load('assets/replay.png')
home = pygame.image.load('assets/home.png')
exit = pygame.image.load('assets/exit.png')
setting = pygame.image.load('assets/setting.png')

play_btn = Button(play, (128, 64), WIDTH//2 - WIDTH // 16, HEIGHT//2)
replay_btn  = Button(replay, (45,42), WIDTH//2 - 110, HEIGHT//2 + 20)
home_btn  = Button(home, (45,42), WIDTH//2 - 20, HEIGHT//2 + 20)
exit_btn  = Button(exit, (45,42), WIDTH//2 + 70, HEIGHT//2 + 20)


# function to reset a level
def reset_level(level):
    global cur_score
    cur_score = 0

    data = load_level(level)
    if data:
        for group in groups:
            group.empty()
        world = World(win, data, groups)
        player.reset(win, player_pos, world, groups)
# 10, 340
    return world

score = 0
cur_score = 0

# --- Modificación de estados del juego ---
if clip:  # Solo muestra la intro si el video se cargó correctamente
    show_intro = True
    main_menu = False  # El menú principal ahora va DESPUÉS de la intro
    intro_start_time = 0
    video_playing = False
else:
    show_intro = False # Omite la intro si falló la carga
    main_menu = True   # Ve directo al menú
# -------------------------------------

game_over = False
level_won = False
game_won = False
running = True

while running:
    
    # --- Manejo de eventos ---
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            if show_intro and intro_sound: 
                intro_sound.stop() 
        
        # Permite saltar la intro con cualquier tecla o clic
        if show_intro and (event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN):
            show_intro = False
            main_menu = True
            if intro_sound: 
                intro_sound.stop() 
    
    # --- Lógica de estados del juego ---
    
    if show_intro:
        if not video_playing:
            # --- LÓGICA CORREGIDA ---
            # Solo necesitamos que el 'clip' exista para empezar
            if clip: 
                # Ahora, SÍ el sonido existe, lo reproducimos
                if intro_sound:
                    intro_sound.play()
                
                # Pero el video se inicia sí o sí
                intro_start_time = pygame.time.get_ticks()
                video_playing = True
            else:
                # Esto solo pasa si el clip falló al cargar
                show_intro = False
                main_menu = True
            # --- FIN DE LA CORRECCIÓN ---

        # Calcula el tiempo actual del video
        # (Añadimos 'if video_playing' para evitar error si el clip no cargó)
        if video_playing:
            current_time_ms = pygame.time.get_ticks() - intro_start_time
        
            if not clip or current_time_ms >= clip_duration_ms:
                # El video terminó o no existe
                show_intro = False
                main_menu = True
                if intro_sound: 
                    intro_sound.stop() 
            else:
                # Muestra el frame actual del video
                try:
                    # Obtén el frame (tiempo en segundos)
                    frame = clip.get_frame(current_time_ms / 1000.0)
                    
                    # Convierte el frame (array de numpy) a una superficie de Pygame
                    # MoviePy usa (alto, ancho, 3) y Pygame (ancho, alto, 3)
                    frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                    win.blit(frame_surface, (0, 0))
                except Exception as e:
                    # Error al obtener el frame (suele pasar al final)
                    print(f"Error al obtener frame: {e}")
                    show_intro = False
                    main_menu = True
                    if intro_sound: 
                        intro_sound.stop() 

    else: # --- Lógica original de menú y juego ---
        
        pressed_keys = pygame.key.get_pressed()

        # displaying background & sun image
        win.blit(bg, (0,0))
        win.blit(sun, (40,40))
        world.draw()
        for group in groups:
            group.draw(win)

        # drawing grid
        # draw_lines(win)

        if main_menu:
            win.blit(jungle_dash, (WIDTH//2 - WIDTH//8, HEIGHT//4))

            play_game = play_btn.draw(win)
            if play_game:
                main_menu = False
                game_over = False
                game_won = False
                score = 0

        else:
            
            if not game_over and not game_won:
                
                enemies_group.update(player)
                platform_group.update()
                exit_group.update(player)
                if pygame.sprite.spritecollide(player, diamond_group, True):
                    sounds[0].play()
                    cur_score += 1
                    score += 1  
                draw_text(win, f'{score}', ((WIDTH//tile_size - 2) * tile_size, tile_size//2 + 10))
                
            game_over, level_won = player.update(pressed_keys, game_over, level_won, game_won)

            if game_over and not game_won:
                replay = replay_btn.draw(win)
                home = home_btn.draw(win)
                exit = exit_btn.draw(win)

                if replay:
                    score -= cur_score
                    world = reset_level(level)
                    game_over = False
                if home:
                    game_over = True
                    main_menu = True
                    bg = bg1
                    level = 1
                    world = reset_level(level)
                if exit:
                    running = False

            if level_won:
                if level <= max_level:
                    level += 1
                    game_level = f'levels/level{level}_data'
                    if os.path.exists(game_level):
                        data = []
                        world = reset_level(level)
                        level_won = False
                        score += cur_score

                    bg = random.choice([bg1, bg2])
                else:
                    game_won = True
                    bg = bg1
                    win.blit(you_won, (WIDTH//4, HEIGHT // 4))
                    home = home_btn.draw(win)

                    if home:
                        game_over = True
                        main_menu = True
                        level_won = False
                        level = 1
                        world = reset_level(level)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()