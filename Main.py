import pygame 
import src.player 
from data.settings import initial_x_y_position 

# basically the game loop 
check = True 

all_sprites = pygame.sprite.Group() #a  group that bounds all existing sprites in theg ame 
pygame.init() 
screen = pygame.display.set_mode((800,600))
user = src.player.Player(initial_x_y_position ,all_sprites) 
while check == True :
    for event in pygame.event.get() :
        if event.type == pygame.QUIT : 
            pygame.QUIT 
    screen.fill('black')
    user.update() 
    all_sprites.draw(screen)
    pygame.display.flip()
    
    

