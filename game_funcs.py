import sys
import pygame
import asyncio
import game_engine as ge
from game_objects import *


#   SETTING UP YOUR GAME AND ENVIRONMENT
#----------------------------------------

def set_game_size(width: int, height: int):
    """
    Sets the dimensions of the game window. These dimensions are also used as measurements for the world size.

    Args:
        width: the pixel width of the game/resolution
        height: the pixel height of the game/resolution
    """
    ge.screen_width = width
    ge.screen_height = height

def background_color(color: str | tuple[int]):
    """
    Sets the color of the background

    Args:
        color: a string containing the value of the color or a tuple containing the rgb values
    
    Examples:
        background_color("Black") # Sets the background color to a solid black
        background_color("Pink") # Sets the background color to pink
        backround_color("#42e0f5") # sets the background color to specific hex value
        background_color((255, 25, 100)) # sets the background color to a specific rgb value

    """
    ge.bckgrnd_color = color

def add_background(image: str, vertical_align = "top", horizontal_align = "left"):
    """
    Adds a background image using a file name contained in a string

    Args:
        image: a string containing the image file name and extension you want to use as a background
        vertical_align: Where to vertically center the view of your background. 
            Can be of values: "top", "bottom", "center" (Default value - "top")
        horizontal_align: Where to horizontally center the view of your background
            Can be of values: "left", right, "center" (Default value - "left")

    Example:
        add_background("desert-bg.png")
        add_background('background.jpg', horizontal_align = "center", vertical_align="bottom") # Using a larger image may require you to align your background so you see the part you want
    """
    ge.bckgrnd_image = ge.imgs[image]

    # crop the image to be the correct aspect ratio
    x_pos = 0
    y_pos = 0
    aspect = ge.screen_width / ge.screen_height
    bckgrnd_aspect = ge.bckgrnd_image.get_width() / ge.bckgrnd_image.get_height()
    new_width = ge.bckgrnd_image.get_width()
    new_height = ge.bckgrnd_image.get_height()
    # greater width than aspect ratio
    if bckgrnd_aspect > aspect:
        new_width = new_height * aspect
        if horizontal_align.lower() == "center":
            x_pos = (ge.bckgrnd_image.get_width() - new_width)/2
        elif horizontal_align.lower() == "right":
            x_pos = ge.bckgrnd_image.get_width() - new_width
    else:
        new_height = new_width / aspect
        if vertical_align.lower() == "center":
            y_pos = (ge.bckgrnd_image.get_height() - new_height)/2
        elif vertical_align.lower() == "bottom":
            y_pos = ge.bckgrnd_image.get_height() - new_height

    ge.bckgrnd_image = ge.bckgrnd_image.subsurface((x_pos, y_pos, new_width, new_height))

        
    ge.bckgrnd_image = pygame.transform.scale_by(ge.bckgrnd_image, ge.screen_width/ge.bckgrnd_image.get_width())
    ge.screen_height = ge.bckgrnd_image.get_height()
    ge.screen_width = ge.bckgrnd_image.get_width()

def clear():
    """
    Removes all elements from the game.
    """
    ge.entities.clear()
    ge.elements.clear()
    ge.texts.clear()
    ge.solid_entities.clear()

#   MISCELLANEOUS BUT IMPORTANT FUNCTION
#-------------------------------------------
def set_interval(func, seconds: float, my_range:range = range(sys.maxsize)):
    """
    Works just like a for loop, only with a delay before each iteration

    Args:
        func: The function called each iteration. 
            structure: Function must take in 1 argument - i the iteration variable of the for loop
    """
    ge.async_tasks.append({'func': func, 'iterations': list(my_range), 'curr_time': 0, 'stop_time': seconds})

#   TEXT FUNCTIONS
#-----------------------
def print_text(text: str, font_size: int) -> Text:
    """
    Adds a regular text element to the game display.

    Args:
        text: the string you want to display to the screen
        font_size: the size of the font

    Returns:
        The text element created from your input.
    """
    return Text(text, font_size)


def print_heading(text: str, font_size: int) -> Text:
    """
    Adds a heading text element that is auto centered.

    Args:
        text: the string you want to display to the screen
        font_size: the size of the font

    Returns:
        The text element created from your input.
    """
    
    return Text(text, font_size, centered=True)

def update_text(text_element: Text, updated_text: str, font_size: int = None):
    """
    Updates a text element (heading included) to a new string

    Args:
        text_element: the text element you desire to change
        updated_text: the string you want to display to the screen
        font_size: the size of the font

    Example:
        my_text = print_text("Hello world", 25)
        
        update_text(my_text, "Hi there")
    """
    text_element.update_text(updated_text)

#   ELEMENT FUNCTIONS
#-----------------------

def place_element(element: Element, x: int, y: int):
    """
    Moves an element (entity or text) to a new x and y position.
    
    Args:
        x: The int x position (pixel) you want to place the element.
        y: The int y position (pixel) you want to place the element.

    Example:
        my_image = add_image("pic.jpg", 200)
        place_element(my_image, 300, 100)
    """
    element.place(x, y)

def remove_el(element: Element):
    """
    Removes an element from the game.

    Args:
        element: The element being removed from the game.

    Example:
        demo = add_image("demo.png", 20)
        remove_el(demo)
    """
    ge.elements.remove(element)
    if element in ge.entities:
        ge.entities.remove(element)
    if element in ge.texts:
        ge.texts.remove(element)
    if element in ge.solid_entities:
        ge.solid_entities.remove(element)
    del element

def get_x(element: Element) -> int:
    """
    Gives the x position of the element.
    
    Args:
        element: The element that is being checked

    Returns:
        The x position of the element.
    """
    return element.x

def get_y(element: Element) -> int:
    """
    Gives the y position of the element.
    
    Args:
        element: The element that is being checked

    Returns:
        The y position of the element
    """
    return element.y

#   BASIC IMAGE/ENTITY FUNCTIONS
#--------------------------------

def add_image(image: str, width: int = None) -> Entity:
    """
    Adds an image-based entity to the game. This is used for adding things like players, entities, or even platforms.
    
    Args:
        image: The str of the image file name and extension (Ex: "mario.png")
        width: The int of the desired pixel width (height will be scaled to preserve the aspect ratio of image)

    Returns:
        The entity created using the image.

    Example:
        add_image("mario.png") # adds an image of mario
        add_image("mario.png", 200) # adds an image of mario with width of 200 pixels
    
    """
    return Entity(image, width = width)

def resize_image(image_element: Entity, new_width: float):
    """
    Changes the width of the image.

    Args:
        image_element: The entity you wish to resize
        new_width: The int of the desired pixel width (height will be scaled to preserve the aspect ratio of image)
    
    Example:
        mario = add_image("mario.png")
        resize_image(mario, 200) # sets mario's width to 200 pixels
    """
    image_element.change_scale(new_width)

def rotate_image(entity: Entity, rotation_degrees: float):
    """
    Rotates an entity by a given number of degrees.
    NOTE: THIS WILL NOT UPDATE THE COLLIDER. You must change the collider after rotating if you desire this.

    Args:
        entity: The entity you want to rotate.
        rotation_degrees: The number of degrees you want to rotate the entity.
    """
    entity.rotate(rotation_degrees)

#   AUDIO FUNCTIONS
#--------------------------------

def play_music(audio_file_name: str):
    """
    Plays and loops music of the given file.

    Args:
        audio_file_name: The audio file (and extension) to be played.

    Example:
        play_music("song.mp3")
    """
    pygame.mixer.music.load("./audio/" + audio_file_name)
    pygame.mixer.music.set_volume(ge.VOLUME / 100)
    pygame.mixer.music.play(1000)

def play_audio(audio_file_name):
    """
    Plays audio of the given file.

    Args:
        audio_file_name: The audio file (and extension) to be played.

    Example:
        play_audio("beep.mp3")
    """
    ge.audio[audio_file_name].play()

#   ENTITY COLLISION FUNCTIONS
#--------------------------------

def set_collider(element: Element, width = None, height = None, offset_x = None, offset_y = None):
    """
    Adds a colision box to an element. 
    
    This method is useful if you want custom collision box dimensions or if you wish to update the collider.
    Note: This will not make them physically solid. Use set_solid for that.

    Args:
        width: sets the width of the collision box
        height: sets the height of the collision box
        offset_x: shifts the x position of the collision box
        offset_y: shifts the y position of the collision box

    Example:
        player_dino = add_image('dino.gif', 300)

        set_collider(player_dino, width = 150, offset_x = 100)
    """
    if type(element) is Entity:
        element.set_collider(width, height, offset_x, offset_y)
    else:
        element.set_collider()

def set_solid(entity: Entity, is_solid = True):
    """
    Sets an entity to be physically solid or not. All other solid entities will not be able to pass through them and vice versa.
    This will automatically add a collider using the default parameters (if one is not already present)

    Args:
        entity: The entity you are making solid
        is_solid: (True by default) boolean value for whether the entity should be solid

    Example 1 - Making an entity solid:
        my_entity = add_image("alien.png")
        set_solid(my_entity)

    Example 2 - Making an entity non-solid:
        set_solid(my_entity, False)
    """
    entity.set_solid(is_solid)

def detect_collision(entity: Entity, target: Entity, function):
    """
    Adds collision detection between two elements.
    When a collision is detected, the function is called.

    Args:
        entity: The entity checking for collision with target.
        target: The entity that's being checked for collision.
    Example:
        bullet = add_image("bullet.png", 20)

        target = add_image("target.png", 50)

        def destroy():
        
            //code

        detect_collision(bullet, target, destroy);
    """
    if not hasattr(entity, "rect"):
        set_collider(entity)
    if not hasattr(target, "rect"):
        set_collider(target)
    
    entity.col_funcs[target] = function

def click(target: Entity, function):
    """
    Adds an on-click event to the entity:
    
    Args:
        target: the entity that is being checked for having been clicked.
        function: The function that will be called on the target when clicked.
            structure: example_function(target) # Must accept the target as a parameter

    Example:
        def die(target):
            remove_el(target)
        demo = add_image("demo.png", 300) 
        click(demo, die)
    """
    if not hasattr(target, "rect"):
        target.set_collider()
    target.on_click = function

#   ENTITY MOVEMENT FUNCTIONS
#--------------------------------

def wasd_move(entity: Entity, filtered_keys: list[str] = None, speed: int = 100):
    """
    Allows the user to move an entity with the W A S D keys.
    Updates the movement speed if entered.

    Args:
        entity: The entity you want to make movable by W A S D.
        filtered_keys: A list of keys you don't want to detect (useful for platformers).
        speed: The pixels per second you want the entity to move at.

    Example 1:
        demo = add_image("demo.png", 50)

        wasd_move(demo)

    Example 2 - only left and right movement:
        demo = add_image("demo.png", 50)

        wasd_move(demo, speed = 500, filtered_keys = ['w', 's'])
    """
    keys = ['w', 'a', 's', 'd']
    if filtered_keys != None:
        keys = [k for k in keys if k not in filtered_keys]
    entity.add_move_keys(keys, speed)

def arrows_move(element: Entity, filtered_keys: list[str] = None, speed: int = 100):
    """
    Allows the user to move an entity with the arrow keys.
    Updates the movement speed if entered.

    Args:
        entity: The entity you want to make movable by arrow keys.
        filtered_keys: A list of keys you don't want to detect (useful for platformers).
            key names: "up", "down", "left", "right"
        speed: The pixels per second you want the entity to move at.

    Example 1:
        demo = add_image("demo.png", 50)

        arrows_move(demo)

    Example 2 - only left and right movement:
        demo = add_image("demo.png", 50)

        arrows_move(demo, speed = 500, filtered_keys = ['up', 'down'])
    """
    keys = ['up', 'left', 'down', 'right']
    if filtered_keys != None:
        keys = [k for k in keys if k not in filtered_keys]
    element.add_move_keys(keys, speed)

def bind_to_screen(entity: Entity):
    """
    Forces a moving entity to be unable to leave the screen.

    Args:
        entity: The entity that you don't want to leave the screen.

    Example:
        demo = add_image("demo.png", 50)

        arrows_move(demo)

        bind_to_screen(demo)
    """
    add_bounds(entity, 0, ge.screen_width, 0, ge.screen_height)

def add_bounds(entity: Entity, left: int, right: int, top: int, bottom: int):
    """
    Forces a moving entity to be unable to leave the rectangle you define.

    Args:
        entity: The entity that you are binding movement for.
        left: The left most position the entity can possess.
        right: The right most postition the entity can possess.
        top: The highest point the entity can possess.
        bottom: The lowest point the entity can possess.

    Example:
        demo = add_image("demo.png", 50)

        arrows_move(demo)

        add_bounds(demo, 10, 1000, 300, 500)
    """
    entity.bounds = [left, right, top, bottom]

def jump(element: Entity, height: float, time: float, add_floor: bool = True):
    """
    Gives an entity the ability to jump using the space-bar.

    Args:
        height: The height the entity should be able to jump
        time: The total time the jump will take
        add_floor: Whether the entity will have at the y level they are currently standing.
        
    Example:
        demo = add_image("demo.png", 50)

        jump(demo, 100, 0.5)
        
    Example 2 - Useful if you only want your own platforms:
        demo = add_image("demo.png", 50)

        jump(demo, 100, 0.5, False)
    """
    element.update_jump(height, time, add_floor)

# def bounce(element, height):
#     pass

def animate_x(element: Entity, intial_x: int, final_x: int, turns: int, alternate: bool, speed: float, end_on_collision: bool = False):
    """
    Animates an element horizontaly.
    Args:
        element: element to be animated
        initial_x: starting point x value
        final_x: stopping point x value
        turns: number of repetitions - can be a number or this string "infinite"
        alternate: boolean to reverse on each repitition or not
        speed: speed of animation (pixels per second)
        end_on_collision: Whether a turn should end when a collision is encountered (False by default)

    Example:
        demo = add_image("ball.png", 30)

        animate_x(demo, 20, 80, 2, False, 100)
    """
    if turns == "infinite":
        turns = sys.maxsize
    element.set_x_animation(intial_x, final_x, turns, alternate, speed, end_on_collision)

def animate_y(element: Entity, intial_y: int, final_y: int, turns: int, alternate: bool, speed: float, end_on_collision: bool = False):
    """
    Animates an element vertically.
    Args:
        element: element to be animated
        initial_y: starting point y value
        final_y: stopping point y value
        turns: number of repetitions - can be a number or this string "infinite"
        alternate: boolean to reverse on each repitition or not
        speed: speed of animation (pixels per second)
        end_on_collision: Whether a turn should end when a collision is encountered (False by default)

    Example:
        demo = add_image("ball.png", 30)

        animate_y(demo, 10, 90, "Infinite", True, 100)
    """
    if turns == "infinite":
        turns = sys.maxsize
    element.set_y_animation(intial_y, final_y, turns, alternate, speed, end_on_collision)

def animate_rotate(entity: Entity, angle: float, turns: int, alternate: bool, turn_time: float, end_on_collision: bool = False):
    """
    Animates an element by rotation.
    Args:
        element: element to be animated
        angle: the number of degrees the entity will rotate.
        turns: number of repetitions - can be a number or this string "infinite"
        alternate: boolean to reverse on each repitition or not
        turn_time: The amount of time each turn will take.
        end_on_collision: Whether a turn should end when a collision is encountered (False by default)

    Example:
        demo = add_image("ball.png", 30)

        animate_rotate(demo, 10, "Infinite", False, 0.5)
    """
    if turns == "infinite":
        turns = sys.maxsize
    entity.set_rotate_animation(angle, turns, alternate, turn_time, end_on_collision)




# TODO: Figure out a good method for implementing text input
# def input(prompt, on_complete):
#     obj = InputText(prompt, 30)

#     return obj

# TODO: This may not be necessary but it could be useful to have a button
# def add_button(text):
#     pass



