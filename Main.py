import pygame 
import src.player 
import time 
from data.gameSetting import initial_x_y_position 

# basically the game loop 
check = True 

all_sprites = pygame.sprite.Group() #a  group that bounds all existing sprites in theg ame 
pygame.init() 
screen = pygame.display.set_mode((800,600))
user = src.player.Player(initial_x_y_position ,all_sprites) 
clock = pygame.time.Clock() 

while check == True :
    pygame.event.pump()
    print()
    screen.fill('black')
    user.update() 
    all_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(30) # setting the game to be 60 frames 

    

    

