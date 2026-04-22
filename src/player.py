import pygame

class Player(pygame.sprite.Sprite): 
    # basiaclly all the classes inside Models will inherit from the p sprite class  
    def __init__(self , pos , groups ): 
        super().__init__ (groups) # basically binding the character to the groups it needs to be part of 
        # groups - groups character belongs to - useful for drawing things collectively
        # pos - is the position at which it will spawn basically 
        self.image = pygame.Surface((32,32) )# basically ou character is a square 
        self.image.fill('red') # made the rectangle red 
        self.rect = self.image.get_rect(topleft=pos)
        self.speed = 5 
    def input(self): # basically accepting user input to modeify the character 
        # reading input :yea  
        for event in pygame.event.get():
            if event.type == pygame.quit : 
                pygame.Quit 
        Keys = pygame.key.get_pressed() 
        # keys is a boolean list 
        if Keys[pygame.K_LEFT] :
            self.rect.x -= self.speed  # move to the left by 5px
        if Keys[pygame.K_UP]:
            self.rect.y -= self.speed # move up by 5px 
        if Keys [pygame.K_DOWN] :
            self.rect.y += self.speed # move down by 5px 
        if Keys[pygame.K_RIGHT] :
            self.rect.x += self.speed # move right by 5px 

    # in pygame top left  = 0 , 0 in essence so 
    # as y increase the character goes down 