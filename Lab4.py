# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 18:15:34 2025

@author: Allen
"""
import pygame, sys
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import ode

# set up the colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
GREY = (255/2,255/2,255/2)

#constants
k = 10 #spring coefficent
c = 0.2 #damping coefficent
g = 9.8 #coefficent of gravity
l = 10 #rest length of spring

# clock object that ensure that animation has the same
# on all machines, regardless of the actual machine speed.
clock = pygame.time.Clock()

class SpringMass(pygame.sprite.Sprite):
    
    def __init__(self, name, color, mass=1, radius=1):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([radius*2, radius*2])
        self.image.fill(BLACK)
        pygame.draw.circle(self.image, color, (radius, radius), radius, radius)

        self.rect = self.image.get_rect()
        self.pos = np.array([0.0, 0.0])
        self.vel = np.array([0.0, 0.0])
        self.spring1 = np.array([np.inf, np.inf]) #point or weight to left of weight, set to np.inf if no point or weight to left
        self.spring2 = np.array([np.inf, np.inf]) # point or weight to right of weight, set to np.inf if no point or weight to right
        self.radius = radius
        self.name = name
        self.mass = mass #arg1
        self.k = k #arg2
        self.c = c #arg3
        self.g = g #arg4
        self.l = l #arg5
        self.t = 0.0
        
        
        self.solver = ode(self.f) # set up ode solver
        self.solver.set_integrator('dop853') # set solver to use RK4
        self.solver.set_f_params(self.mass, self.k, self.c, self.g, self.l)
        
    def f(self, t, state, arg1, arg2, arg3, arg4, arg5):
        posWeight = np.array([state[0], state[1]])
        posSpring1 = self.spring1
        posSpring2 = self.spring2
        vel = np.array([state[2], state[3]])
        
        if vel[0] == 0 and vel[1] == 0: #check if velocity is zero
            fFriction = np.array([0,0])
        else:
            velUnitVector = vel/np.sqrt((vel[0])**2 + (vel[1])**2)
            fFriction = -arg3 * vel #calculate force of damping friction
        
        if posSpring1[0] == np.inf: #check if spring 1 is in simulation
            fSpring1 = np.array([0,0])
        else:
            spring1 = posWeight - posSpring1
            spring1Length = np.sqrt((posWeight[0]-posSpring1[0])**2+(posWeight[1]-posSpring1[1])**2)
            deformation1 = spring1Length - arg5
            unitVector1 = spring1/spring1Length
            fSpring1 = (-arg2 * deformation1 * unitVector1) + fFriction #calculate force of spring 1 including damping
            
                
        if posSpring2[0] == np.inf: #check if spring 2 is in simulation
            fSpring2 = np.array([0,0])
        else:
            spring2 = posWeight - posSpring2
            spring2Length = np.sqrt((posWeight[0]-posSpring2[0])**2+(posWeight[1]-posSpring2[1])**2)
            deformation2 = spring2Length - arg5
            unitVector2 = spring2/spring2Length
            fSpring2 = (-arg2 * deformation2 * unitVector2) + fFriction #calculate force of spring 2 including damping

        fGrav = arg1 * (-arg4) #calculate force of gravity
        
        fNet = [fSpring1[0] + fSpring2[0], fSpring1[1] + fSpring2[1] + fGrav] #calculate net force 

        dstate = np.array([vel[0], vel[1], 1/arg1 * fNet[0], 1/arg1 * fNet[1]]) #calculate change in position and velocity
        return dstate
    
    def set_pos(self, pos):
        self.pos = np.array(pos)
        
    def set_vel(self, vel):
        self.vel = np.array(vel)
        
    def set_spring1(self, spring1):
        if isinstance(spring1, SpringMass):
            self.spring1 = spring1.pos
        else:
            self.spring1 = np.array(spring1)
        
    def set_spring2(self, spring2):
        if isinstance(spring2, SpringMass):
            self.spring2 = spring2.pos
        else:
            self.spring2 = np.array(spring2)
        
    def setupOde(self): #initialize the ode solver function for the body
        self.state = np.array([self.pos[0], self.pos[1],self.vel[0], self.vel[1]])
        self.solver.set_initial_value(self.state, self.t)
        
    def updateWeight(self, dt): 
        if self.solver.successful(): # solve the ode to find the change in position and velocity for self
            self.solver.integrate(self.solver.t + dt)
                
        self.state = self.solver.y # set state to the updated position and velocty
        self.t = self.solver.t # update time
                
        self.pos[0] = self.state[0] # update the postion and velocity values
        self.pos[1] = self.state[1]
        self.vel[0] = self.state[2]
        self.vel[1] = self.state[3]
        
        
class weightSystem:
    def __init__(self, win_width, win_height):
        self.win_width = win_width
        self.win_height = win_height
        self.w, self.h = 2.6*l, 2.6*l 
        self.weights_dict = {}
        self.weights = pygame.sprite.Group()
        self.dt = 0.033

    def add_weight(self, weight):
        self.weights_dict[weight.name] = weight
        self.weights.add(weight)

    def to_screen(self, pos):
        x = int(pos[0] + self.win_width/2)
        y = int(pos[1] + self.win_height/2)
        return [x, self.win_height - y]

    def update(self):
        for w in self.weights_dict:
            # Compute positions for screen
            wgt = self.weights_dict[w]
            wgt.updateWeight(self.dt)
            p = self.to_screen(wgt.pos)

            # Update sprite locations
            wgt.rect.x, wgt.rect.y = p[0], p[1]
        self.weights.update()

    def draw(self, screen):
        self.weights.draw(screen)
        
def main():

    print ('Press q to quit')
    
    # Initializing pygame
    pygame.init()
    win_width = 640
    win_height = 640
    screen = pygame.display.set_mode((win_width, win_height))  # Top left corner is (0,0)
    pygame.display.set_caption('Weights Connected by Springs')
    

    # Create a system object, which will hold our weight objects
    system = weightSystem(win_width, win_height)

    weight1 = SpringMass('weight1', RED)
    weight2 = SpringMass('weight2', GREEN)
    
    weight1.set_pos([10, 10])
    weight2.set_pos([20, -2])
    weight1.set_spring1([0,0])
    weight1.set_spring2(weight2)
    weight2.set_spring1(weight1)
    weight1.setupOde()
    weight2.setupOde()
    

    system.add_weight(weight1)
    system.add_weight(weight2)

    while True:
        clock.tick(30)    

        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            pygame.quit()
            sys.exit(0)
        else:
            pass

        system.update()
        screen.fill(BLACK) # clear the background
        pygame.draw.line(screen, GREY, [0, win_height/2], [win_width, win_height/2])
        pygame.draw.line(screen, GREY, [win_width/2, 0], [win_width/2, win_height])
        system.draw(screen)
        pygame.display.flip()
        
    pygame.quit()


if __name__ == '__main__':
    main()