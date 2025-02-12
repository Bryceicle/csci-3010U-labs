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
        self.pos = [0.0, 0.0]
        self.vel = [0.0, 0.0]
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
        pass
    
    def set_pos(self, pos):
        self.pos = np.array(pos)
        
    def set_vel(self, vel):
        self.vel = np.array(vel)
        
    def setup(self): #initialize the ode solver function for the body
        self.state = np.array([self.pos[0], self.pos[1],self.vel[0], self.vel[1]])
        self.solver.set_initial_value(self.state, self.t)