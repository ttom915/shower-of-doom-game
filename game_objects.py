import math
import os
import pygame
import game_engine as ge

class Element():
    def __init__(self, x= 0, y = 0):
        self.x = x
        self.y = y
        ge.elements.append(self)

    def place(self, x, y):
        self.x = x
        self.y = y
        if hasattr(self, "rect"):
            self.rect.x = x + self.col_offset[0]
            self.rect.y = y + self.col_offset[1]

    # def set_on_click(self, func):

class Entity(pygame.sprite.Sprite, Element):
    def __init__(self, img_name, x=0, y=0, width = None):
        pygame.sprite.Sprite.__init__(self)
        Element.__init__(self, x, y)
        self.image = ge.imgs[img_name]
        scale = 1
        if width != None:
            scale = width/self.image.get_width()
            self.image = pygame.transform.scale_by(self.image, scale)
        
        self.origin_image = self.image
        ge.entities.append(self)
        self.move = []
        self.scale = scale
        self.solid = False
        self.angle = 0

    def add_move_keys(self, keys, speed):
        self.move.extend(keys)
        self.speed = speed
        if not hasattr(self, "velocity"):
            self.velocity = pygame.math.Vector2()

    def place(self, x, y):
        self.x = int(x)
        self.y = int(y)
        if hasattr(self, "bounds"):
            if hasattr(self, "rect"):
                self.rect.x = self.x + self.col_offset[0]
                self.rect.y = self.y + self.col_offset[1]
            rect = hasattr(self, "rect") and self.rect or pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
            if rect.left < self.bounds[0]:
                self.x += (self.bounds[0] - rect.left)
            elif rect.right > self.bounds[1]:
                self.x += (self.bounds[1] - rect.right)
            if rect.top < self.bounds[2]:
                self.y += (self.bounds[2] - rect.top)
            elif rect.bottom > self.bounds[3]:
                self.y += (self.bounds[3] - rect.bottom)
        if hasattr(self, "rect"):
            self.rect.x = self.x + self.col_offset[0]
            self.rect.y = self.y + self.col_offset[1]
    
    def rotate(self, angle):
        self.angle += angle
        self.image = pygame.transform.rotate(self.origin_image, self.angle)
    
    def change_scale(self, width):
        scale = width/self.image.get_width()
        self.origin_image = pygame.transform.scale_by(self.origin_image, scale)
        self.rotate(0)
        if hasattr(self, "rect"):
            self.rect = self.rect.scale_by(scale)
            self.rect.x = self.x + self.col_offset[0]
            self.rect.y = self.y + self.col_offset[1]
        self.scale = scale

    def update_inputs(self, keys_held):
        move_input = pygame.math.Vector2()
        for key in keys_held:
            if key in self.move:
                if key == "w" or key == "up":
                    move_input.y = 1
                if key == "a" or key == "left":
                    move_input.x = -1
                if key == "s" or key == "down":
                    move_input.y = -1
                if key == "d" or key == "right":
                    move_input.x = 1
                if key == "space" and self.is_grounded() and self.velocity.y == 0:
                    self.velocity.y = -self.jump_speed
        if move_input.length() != 0:
            self.move_input = move_input.normalize()
        else:
            self.move_input = move_input
        # elif hasattr(self, "move_input"):
        #     del self.move_input

    def update_movement(self, tick_time):
        if hasattr(self, "x_anim") and self.x_anim["turns"] > 0:
            self.velocity.x = Entity.__animate_val(self.x_anim, self.x, tick_time)
        if hasattr(self, "y_anim") and self.y_anim["turns"] > 0:
            self.velocity.y = Entity.__animate_val(self.y_anim, self.y, tick_time)
        if hasattr(self, "move_input") and not (hasattr(self, "x_anim") and self.x_anim["turns"] > 0):
            self.velocity.x = self.move_input.x * (hasattr(self, 'speed') and self.speed or 0)
            if not hasattr(self, "gravity"):
                self.velocity.y = -self.move_input.y * self.speed
        if hasattr(self, "gravity"):
            if not self.is_grounded():
                self.velocity.y += self.gravity * tick_time
            else:
                self.velocity.y = min(0, self.velocity.y)
            if hasattr(self, "floor_height") and self.feet_point[1] + self.velocity.y * tick_time > self.floor_height:
                self.place(self.x, self.floor_height + (self.y - self.feet_point[1])) 
                self.velocity.y = min(0, self.velocity.y)
        if self.velocity.x != 0 or self.velocity.y != 0:
            self.place(self.x + self.velocity.x * tick_time, self.y + self.velocity.y * tick_time)

    def update_rotational_movement(self, tick_time):
        if hasattr(self, "rotation_anim") and self.rotation_anim["turns"] > 0:
            self.angular_velocity = Entity.__animate_val(self.rotation_anim, self.angle, tick_time)
            self.rotate(self.angular_velocity * tick_time)
        elif hasattr(self, "rotation_anim"):
            self.angular_velocity = 0

    def update_collision(self):
        for target, func in self.col_funcs.items():
            if target != self and self.rect.colliderect(target) and target in ge.entities:
                self.rect_color = "Green"
                target.rect_color = "Green"
                func()
        if self.solid:
            self.solid_colliders = []
            for target in ge.solid_entities:
                if target != self and self.rect.colliderect(target):
                    self.rect_color = "Green"
                    target.rect_color = "Green"
                    self.solid_colliders.append(target)

    #assumes that you are already colliding
    #assumes target is a static object
    def collision_handeler(self, target):
        def abs_min(val1, val2):
            if abs(val1) < abs(val2):
                return val1
            else:
                return val2
        def sign(val):
            return val / abs(val)

        # find the smallest correction needed to no longer be colliding
        x_correction_dist = abs_min(target.rect.right - self.rect.left, target.rect.left - self.rect.right)
        y_correction_dist = abs_min(target.rect.bottom - self.rect.top, target.rect.top - self.rect.bottom)
        if abs(x_correction_dist) < abs(y_correction_dist):
            if hasattr(target, "velocity"):
                x_correction_dist /= 2
            if hasattr(self, "x_anim") and self.x_anim['end_on_col']:
                Entity.__finish_anim(self.x_anim)
            self.place(self.x + x_correction_dist, self.y)
        else:
            if hasattr(target, "velocity"):
                y_correction_dist /= 2
            if hasattr(self, "y_anim") and self.y_anim['end_on_col']:
                Entity.__finish_anim(self.y_anim)
            self.place(self.x, self.y + y_correction_dist)

    def set_collider(self, width: int = None, height: int = None, x_offset = None, y_offset = None):
        if width == None:
            width = self.image.get_width()
        if height == None:
            height = self.image.get_height()
        self.rect = pygame.Rect(self.x, self.y, width, height)
        self.col_offset = [x_offset or 0, y_offset or 0]
        self.__center_collider_offset(x_offset == None, y_offset == None)
        self.col_funcs = {}
        self.rect_color = "Red"
        self.rect.x += self.col_offset[0]
        self.rect.y += self.col_offset[0]

    def set_x_animation(self, initial_x: int, final_x: int, turns: int, alternate: bool, speed: int, end_on_collision: bool = False):
        if not hasattr(self, "velocity"):
            self.velocity = pygame.math.Vector2()
        self.place(initial_x, self.y)
        self.x_anim = {"initial": initial_x, 
                    "final": final_x, 
                    "turns": turns, 
                    "alternate": alternate, 
                    "speed": speed,
                    "end_on_col": end_on_collision}
    def set_y_animation(self, initial_y: int, final_y: int, turns: int, alternate: bool, speed: int, end_on_collision: bool = False):
        if not hasattr(self, "velocity"):
            self.velocity = pygame.math.Vector2()
        self.place(self.x, initial_y)
        self.y_anim = {"initial": initial_y, 
                    "final": final_y, 
                    "turns": turns, 
                    "alternate": alternate, 
                    "speed": speed,
                    "end_on_col": end_on_collision}
        
    def set_rotate_animation(self, angle: float, turns: int, alternate: bool, time: int, end_on_collision: bool = False):
        if not hasattr(self, "angular_velocity"):
            self.angular_velocity = 0
        self.rotation_anim = {"initial": self.angle, 
                            "final": self.angle + angle, 
                            "turns": turns, 
                            "alternate": alternate, 
                            "speed": (angle - self.angle)/time,
                            "end_on_col": end_on_collision}
        
    def set_solid(self, is_solid):
        if not hasattr(self, "rect"):
            self.set_collider()
        self.solid = is_solid
        if is_solid and self not in ge.solid_entities:
            ge.solid_entities.append(self)
        elif not is_solid and self in ge.solid_entities:
            ge.solid_entities.remove(self)

    def update_jump(self, height, time, add_floor = True):
        if not hasattr(self, "velocity"):
            self.velocity = pygame.math.Vector2()
        if not hasattr(self, "rect"):
            self.set_collider()
        def calc_gravity(height, time):
            return 2 * height / (time/2) ** 2
        def calc_jump_speed(height, time, gravity):
            t_h = time/2
            return height/t_h + gravity * (t_h ** 2)/2

        self.feet_points = (self.rect.centerx, self.rect.bottom + 2)
        self.jumps = True
        self.jump_height = height
        self.gravity = calc_gravity(height, time)
        self.jump_speed = calc_jump_speed(height, time, self.gravity)
        if add_floor:
            self.floor_height = self.rect.bottom
        if "space" not in self.move:
            self.move.append("space")
    def is_grounded(self):
        self.feet_point = (self.rect.centerx, self.rect.bottom + 2)
        all_points = [self.feet_point, (self.rect.left, self.rect.bottom + 2), (self.rect.right, self.rect.bottom + 2)]
        if hasattr(self, "floor_height") and self.feet_point[1] >= self.floor_height:
            return True
        elif self.solid == True:
            for point in all_points:
                for entity in ge.solid_entities:
                    if entity != self and entity.rect.collidepoint(point):
                        return True
        return False
    
    def render(self, screen):
        screen.blit(self.image, [self.x, self.y])
         
    def __animate_val(animation, current_value, tick_time):
        new_val = None
        finished_turn = False
        positive_move = animation["initial"] < animation["final"]
        if positive_move:
            new_val = current_value + animation["speed"] * tick_time
            if new_val >= animation["final"]:
                new_val = (not animation['alternate'] and animation["initial"]) or animation["final"]
                finished_turn = True
        else:
            new_val = current_value - animation["speed"] * tick_time
            if new_val <= animation["final"]:
                new_val = (not animation['alternate'] and animation["initial"]) or animation["final"]
                finished_turn = True
        if finished_turn:
            Entity.__finish_anim(animation)
            if animation['turns'] == 0:
                return 0
        return (new_val - current_value)/tick_time
    
    def __finish_anim(animation):
        animation['turns'] -= 1
        if animation['turns'] > 0 and animation['alternate']:
            animation['final'], animation['initial'] = animation['initial'], animation['final']

    def __center_collider_offset(self, center_x = True, center_y = True):
        img_width, img_height = self.image.get_width(), self.image.get_height()
        col_width, col_height = self.rect.width, self.rect.height
        if center_x:
            self.col_offset[0] = (img_width - col_width)/2
        if center_y:
            self.col_offset[1] = (img_height - col_height)/2





class Text(Element):
    def __init__(self, text, font_size, x=0, y=0, centered = False):
        self.font = pygame.font.SysFont("Calbri", font_size)
        Element.__init__(self, x, y)
        self.text = text
        self.font_size = font_size
        ge.texts.append(self)
        self.rendered_text = self.font.render(text, True, "White")
        self.centered = centered

    def update_text(self, updated_text):
        self.text = updated_text
        self.rendered_text = self.font.render(self.text, True, "White")

    def get_pos(self):
        if self.centered:
            text_rect = self.rendered_text.get_rect(center=(ge.screen_width/2, ge.screen_height/2))
            self.x = text_rect.x
            self.y = text_rect.y
        return (self.x, self.y)

    def set_collider(self):
        self.rect = pygame.Rect(self.x, self.y, self.rendered_text.get_width(), self.rendered_text.get_height())
        self.rect_color = "Red"

class InputText(Element):
    def __init__(self, prompt, font_size):
        self.font = pygame.font.SysFont("Calbri", font_size)
        self.prompt = prompt
        self.font_size = font_size
        self.input = ""
        self.rendered_text = self.font.render(prompt, True, "Gray")
        text_rect = self.rendered_text.get_rect(center=(ge.screen_width/2, ge.screen_height/2))
        Element.__init__(self, text_rect.x, text_rect.y)

    def update_prompt(self, updated_prompt):
        self.prompt = updated_prompt
        text_rect = self.rendered_text.get_rect(center=(ge.screen_width/2, ge.screen_height/2))
        self.rendered_text = self.font.render(updated_prompt, True, "Gray")

    def receive_input(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.input = self.input[:-1] 
        elif event.key == pygame.K_RETURN:
            return True
        else: 
            self.input += event.unicode

        if len(self.input == 0):
            self.rendered_text = self.font.render(self.prompt, True, "Gray")
        else:
            self.rendered_text = self.font.render(self.input, True, "White")
        return False
    
    def get_input_text(self):
        return self.input