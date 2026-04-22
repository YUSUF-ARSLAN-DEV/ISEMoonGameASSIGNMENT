import pygame 
import src.player 

# basically the game loop 
check = True 

all_sprites = pygame.sprite.Group() #a  group that bounds all existing sprites in theg ame 
pygame.init() 
screen = pygame.display.set_mode((800,600))
user = src.player.Player((0,0),all_sprites) 
while check == True :
    screen.fill('black')
    user.input()
    all_sprites.draw(screen)
    pygame.display.flip()
    
    

