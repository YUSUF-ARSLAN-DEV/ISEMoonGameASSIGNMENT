import pygame
import random
pygame.init()
 
win = pygame.display.set_mode((600,600))
clk = pygame.Clock()
 
class Particle():
 
    def __init__(self,x,y):
        self.rad = random.randint(2,10)
        self.rad_vel = random.uniform(0.5,1)
        self.x=x
        self.x_vel = random.uniform(-2,2)
 
        self.y=y
        self.y_vel = random.uniform(1,3)
 
        self.alpha = 255
        self.alph_vel = random.uniform(5,7)
 
        self.color=(0,0,0,self.alpha)
 
    def update(self):
        self.rad = pygame.math.clamp(self.rad+self.rad_vel,2,20)
        print(self.rad)
        self.x+=self.x_vel
        self.y-=self.y_vel
        surf = pygame.Surface((self.rad*2,self.rad*2),pygame.SRCALPHA).convert_alpha()
        self.alpha = pygame.math.clamp(self.alpha-self.alph_vel,0,255)
        r,g,b,_ = self.color
        self.color = (r,g,b,self.alpha)
        pygame.draw.circle(surf,self.color,surf.get_rect().center,self.rad)
        win.blit(surf,(self.x,self.y))
 
 
 
 
particles = []
running = True
while(running):
    dt = clk.tick(60)
    win.fill((250,250,250))
    for e in pygame.event.get():
        if(e.type==pygame.QUIT):
            running=False
            break
 
    if(pygame.mouse.get_pressed()[0]):
        particles.append(Particle(*pygame.mouse.get_pos()))
 
    for i in range(len(particles)):
        particles[i].update()
       
    try:
        for i in range(len(particles)):
            if(particles[i].alpha==0):
                p=particles[i]
                particles.remove(p)
    except:
        pass
 
    # print(len(particles))
    pygame.display.flip()
 
pygame.quit()