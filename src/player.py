import pygame
from data.settings import GRAVITY  ,PLAYER_HEIGHT, PLAYER_WIDTH  , WINDOW_WIDTH , WINDOW_HEIGHT 
class Player(pygame.sprite.Sprite): 
    # basiaclly all the classes inside Models will inherit from the p sprite class  
    def __init__(self , pos , groups ): 
        super().__init__ (groups) # basically binding the character to the groups it needs to be part of 
        # groups - groups character belongs to - useful for drawing things collectively
        # pos - is the position at which it will spawn basically 
        self.image = pygame.Surface((PLAYER_WIDTH,PLAYER_HEIGHT) )# basically ou character is a square 
        self.image.fill('red') # made the rectangle red 
        self.rect = self.image.get_rect(topleft=pos)
        self.speed = 4
        self.y_velocity = 0 
        self.on_ground = False 
        # basically the speed at which the object is moving upwards
    def update(self):
        self.horizontal_movement()
        self.check_boundaries()
        self.verticalJump()
        self.apply_gravity()
        

        

    def horizontal_movement(self):
        clicked_buttons = pygame.key.get_pressed()
        if clicked_buttons[pygame.K_LEFT]:
            self.rect.x -= self.speed  # based on the character we speed we set 
        if clicked_buttons[pygame.K_RIGHT]:
            self.rect.x += self.speed 
    def apply_gravity(self):
        # gravity always applies and gravity logic involves applying acceleration to speed and changing position using speed 
        self.y_velocity += GRAVITY  # gravity is positive since the larger the value the closer you are to ground 
        self.rect.y += self.y_velocity # position changes based on speed basically the speed at which you are going up decreases until you stop going up any more 
        if self.rect.bottom >= WINDOW_HEIGHT : # because in some frames for a split second the character might be at 601 not 600 
            self.rect.bottom = WINDOW_HEIGHT # we are setting it back at so that it stand perfectly on ground 
            self.y_velocity = 0 # the character goes at rest vertically 
            self.on_ground = True # fires the fglag that it is at the ground 
    def check_boundaries(self):
        # this is the clamping method 
        rect_object =pygame.Rect(0,0, WINDOW_WIDTH, WINDOW_HEIGHT ) # tells pygame the boundaries 
        self.rect.clamp_ip(rect_object ) 
        # now we are enforcing the boundary every frame 
        #
    def verticalJump(self):
        clicked_buttons = pygame.key.get_pressed()
        print(clicked_buttons[pygame.K_SPACE])
        if clicked_buttons[pygame.K_SPACE] and  self.on_ground  : # if the character is on the ground it jumps 
            # the character only jump if it is in the ground
            self.y_velocity = -10
            self.on_ground = False  # then the flag is down 

