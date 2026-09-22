from game_funcs import *
import game_engine
import random

#Set this first to decide the world dimensions
set_game_size(1600, 900)

#was 1600, 900

#Below is where most of your code will be written
death = "pixel-death.mp3"
win_song = "8-bit-win-theme.mp3"
shard_collect = "shard-pickup.mp3"

#Scene
instructions = print_text("Use A and D or < and > to move", 50)
collecting = print_text("Collect Shards or survive to win!", 50)
place_element(instructions, 20, 20)
place_element(collecting, 20, 70)

#title = print_heading("Title", 75)
add_background("planet_bg2.jpg")
bg_music = play_music("Attack-on-Moon-Final.mp3")

#Player
Player_score = 0
player_astronaut = add_image("astronaut_player.png", 250)
place_element(player_astronaut, 30, 600)
set_collider(player_astronaut, width = 100, height = 150)
wasd_move(player_astronaut, speed = 200, filtered_keys = ["w", "s"])
arrows_move(player_astronaut, speed = 200, filtered_keys = ['up', 'down'])
bind_to_screen(player_astronaut)

#functions
def lose_screen():
    clear()
    print_heading(f"You Died \n Score: {Player_score}", 100)
    play_audio(death)
    
def win_screen():
    clear()
    print_heading(f"You Win! \n Score: {Player_score}", 100)
    play_audio(win_song)
    
def Score():
    global Player_score
    play_audio(shard_collect)
    remove_el(shards[0])
    del shards[0]
    Player_score = Player_score + 1
    if Player_score == 15:
        win_screen()        
            
#Shards
shards = []
def spawn_shards():
    shard = add_image("shard.png", 100)
    resize_image(shard, 250)
    shards.append(shard)
    place_element(shard, random.randint(75,1525), 600)
    #was 75, 1525
    set_solid(shard, False)
    set_collider(shard, 150, 150)
    detect_collision(player_astronaut, shard, Score)


#Asteroids
asteroids = []
def spawn_asteroids(i):
    asteroid = add_image("asteroid_fire.png", 200)
    asteroids.append(asteroid)
    place_element(asteroid, random.randint(0,1600), 1000)
    #was 0, 1600
    animate_y(asteroid, -200, 1000, 1, False, 200)
    set_collider(asteroid, width = 60, height = 150)
    detect_collision(asteroid, player_astronaut, lose_screen)
    if i == 19:
        win_screen()

#Calling Functions
spawn_shards()
set_interval(spawn_asteroids, 1.5, range(0, 20))
    

# WARNING: For advanced students/game requirements
# Called once per frame (there are 60 frames per second)
# DO NOT CHANGE FUNCTION NAME
def update():
    if len(shards) == 0:
        spawn_shards()
    pass

#DO NOT EDIT BELOW 
game_engine.start(update)