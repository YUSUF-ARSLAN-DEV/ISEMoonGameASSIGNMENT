import pygame
from data.settings import GRAVITY  , GROUND_Y
class Player(pygame.sprite.Sprite): 
    # basiaclly all the classes inside Models will inherit from the p sprite class  
    def __init__(self , pos , groups ): 
        super().__init__ (groups) # basically binding the character to the groups it needs to be part of 
        # groups - groups character belongs to - useful for drawing things collectively
        # pos - is the position at which it will spawn basically 
        self.image = pygame.Surface((32,32) )# basically ou character is a square 
        self.image.fill('red') # made the rectangle red 
        self.rect = self.image.get_rect(topleft=pos)
        self.speed = 1
        self.y_velocity = 0 
        self.on_ground = False 
        # basically the speed at which the object is moving upwards
    def update(self):
        self.horizontal_movement()
        self.verticalJump()
        self.apply_gravity()
        self.check_boundaries()

        

    def horizontal_movement(self):
        clicked_buttons = pygame.key.get_pressed()
        if clicked_buttons[pygame.K_LEFT]:
            self.rect.x -= self.speed  # based on the character we speed we set 
        if clicked_buttons[pygame.K_RIGHT]:
            self.rect.x += self.speed 
    def apply_gravity(self):
        # think of gravity as something that 
        # constatntly changes y_velocity 
        if self.rect.bottom < GROUND_Y:
             self.y_velocity += GRAVITY # 
        else :
            self.rect.bottom = GROUND_Y  # now the character is at the ground 
            self.on_ground = True 
            self.y_velocity = 0 # the character is not moving downwards any more 
        self.rect.y += self.y_velocity 
    def check_boundaries(self):
        # this is the clamping method 
        rect_object =pygame.Rect(0,0,800,GROUND_Y) # tells pygame the boundaries 
        self.rect.clamp_ip(rect_object ) 
        # now we are enforcing the boundary every frame 
        #
    def verticalJump(self):
        clicked_buttons = pygame.key.get_pressed()
        
        if clicked_buttons[pygame.K_SPACE] and  self.rect.bottom == GROUND_Y :
            # the character only jump if it is in the ground
            self.on_ground = False 
            self.y_velocity = -5  # veloctiy should only increas when the button is clicked 
            # since we do not magically float up 
        
