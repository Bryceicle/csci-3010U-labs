"""
author: Faisal Qureshi
email: faisal.qureshi@ontariotechu.ca
website: http://www.vclab.ca
license: BSD
"""

import pygame, sys
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import ode

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GREY = (255/2,255/2,255/2)

springLength = 10
springCoeff = 10
dampCoeff = 0.2

class RigidBody:

    def __init__(self, position, mass, springRest, springConst, dampCoeff, width):
        self.mass = mass  # - arg1
        self.width = width  # - arg2
        self.springRest = springRest # - arg3
        self.springConst = springConst # - arg4
        self.dampCoeff = dampCoeff # - arg5
        self.G = 9.81 # - arg6
        self.Ibody = np.identity(3)  # inertia tensor
        self.IbodyInv = np.linalg.inv(self.Ibody)  # inverse of inertia tensor
        self.v = np.zeros(3)  # linear velocity
        self.omega = np.zeros(3)  # angular velocity

        self.state = np.zeros(19)
        self.state[0:3] = position  # position of COM
        self.state[3:12] = np.identity(3).reshape([1, 9])  # rotation
        self.state[12:15] = self.mass * self.v  # linear momentum
        self.state[15:18] = np.zeros(3)  # angular momentum

        # Setting up the solver
        self.solver = ode(self.f)
        self.solver.set_integrator('dop853')
        self.solver.set_f_params(self.mass, self.width, self.springRest, self.springConst, self.dampCoeff, self.G, self.IbodyInv)

    def f(self, t, state, mass, width, springRest, springConst, dampCoeff, G, IbodyInv):
        rate = np.zeros(19)
        rate[0:3] = state[12:15] / mass  # dv = dx/dt

        _R = state[3:12].reshape([3, 3])
        _R = self.orthonormalize(_R)
        Iinv = np.dot(_R, np.dot(IbodyInv, _R.T))
        _L = state[15:18]
        omega = np.dot(Iinv, _L)

        forceG = (0, - mass * G, 0) # calculate force of gravity

        forceF = -dampCoeff * rate[0:3] # calculate damping force in spring

        p1 = np.matmul(state[6:15].reshape([3, 3]), np.array([0.5, 0.5, 0])) + state[0:3]  # position of point 1 (where spring attached) in world coordinates
        lenSpring = np.linalg.norm(p1)
        deformation = lenSpring - springRest
        springUnitVec = p1/lenSpring
        forceSpring = (-springConst * deformation * springUnitVec) + forceF # calculate force of spring if stretched/compressed

        forceUnitVec = forceSpring / np.linalg.norm(forceSpring)

        d = (p1 - (np.dot((state[0:3]-p1), forceUnitVec) * forceUnitVec)) - state[0:3]
        torque = np.cross(d, forceSpring)

        rate[3:12] = np.dot(self.star(omega), _R).reshape([1, 9])
        rate[12:15] = forceSpring + forceG
        rate[15:18] = torque
        return rate

    def star(self, v):
        vs = np.zeros([3, 3])
        vs[0][0] = 0
        vs[1][0] = v[2]
        vs[2][0] = -v[1]
        vs[0][1] = -v[2]
        vs[1][1] = 0
        vs[2][1] = v[0]
        vs[0][2] = v[1]
        vs[1][2] = -v[0]
        vs[2][2] = 0
        return vs;

    def orthonormalize(self, m):
        mo = np.zeros([3, 3])
        r0 = m[0, :]
        r1 = m[1, :]
        r2 = m[2, :]

        r0new = r0 / np.linalg.norm(r0)

        r2new = np.cross(r0new, r1)
        r2new = r2new / np.linalg.norm(r2new)

        r1new = np.cross(r2new, r0new)
        r1new = r1new / np.linalg.norm(r1new)

        mo[0, :] = r0new
        mo[1, :] = r1new
        mo[2, :] = r2new
        return mo

    def get_pos(self):
        return self.state[0:3]

    def get_p1(self):
        return np.matmul(self.state[6:15].reshape([3, 3]), np.array([0.5, 0.5, 0])) + self.state[0:3]  # position of point 1 (where spring attached) in world coordinates

    def get_rot(self):
        return self.state[3:12].reshape([3, 3])

    def get_angle_2d(self):
        v1 = [1, 0, 0]
        v2 = np.dot(self.state[3:12].reshape([3, 3]), v1)
        cosang = np.dot(v1, v2)
        axis = np.cross(v1, v2)
        return np.degrees(np.arccos(cosang)), axis

    def prn_state(self):
        print('Pos COM', self.state[0:3])
        print('Pos p1:', self.get_p1())
        print('Rot', self.state[3:12].reshape([3, 3]))
        print('P', self.state[13:15])
        print('L', self.state[15:18])


class Box2d(pygame.sprite.Sprite):
    def __init__(self, x, y, screen_height, imgfile):
        pygame.sprite.Sprite.__init__(self)

        self.w, self.h = springLength, springLength
        self.image = pygame.image.load(imgfile)
        self.image = pygame.transform.scale(self.image,[50,50])
        self.rect = self.image.get_rect()
        self.pos = (x,y)
        self.image_rot = self.image
        self.screen_height = screen_height

    def rotate(self, angle):
        self.image_rot = pygame.transform.rotate(self.image, angle)

    def to_screen(self, pos):
        return [pos[0]/10 + 320, pos[1]/10 + 320]

    def move(self, x, y):
        new_x = self.pos[0] + x
        new_y = self.pos[1] + y
        self.pos = (new_x, new_y)

    def draw(self, surface):
        rect = self.image_rot.get_rect()
        rect.center = self.to_screen(self.pos)
        rect.centery = self.screen_height - rect.centery
        surface.blit(self.image_rot, rect)


def main():
    # initializing pygame
    # pygame.mixer.init()
    pygame.init()

    clock = pygame.time.Clock()

    # some music
    # pygame.mixer.music.load('madame-butterfly.wav')

    # top left corner is (0,0)
    win_width = 640
    win_height = 640
    screen = pygame.display.set_mode((win_width, win_height))
    pygame.display.set_caption('2D projectile motion')

    #background = pygame.image.load('background-vertical.png')

    rb = RigidBody([10, 0, 0], 1, springLength, springCoeff, dampCoeff, 1)

    box = Box2d(rb.get_pos()[0], rb.get_pos()[1], win_height, 'square.png')

    cur_time = 0.0
    dt = 0.033

    rb.solver.set_initial_value(rb.state, cur_time)

    exploded = False
    while True:
        # 30 fps
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

        rb.state = rb.solver.integrate(cur_time)
        cur_time += dt

        angle, axis = rb.get_angle_2d()
        if axis[2] < 0:
            angle *= -1.

        pos = rb.get_pos()

        # clear the background, and draw the sprites
        screen.fill(BLACK)

        pygame.draw.line(screen, GREY, [0, win_height/2], [win_width, win_height/2])
        pygame.draw.line(screen, GREY, [win_width/2, 0], [win_width/2, win_height])
        #pygame.draw.line(screen, RED, [win_width/2,win_height/2], [rb.get_p1()[0]+320/, rb.get_p1()[1]+320])

        box.rotate(angle)
        box.move(pos[0], pos[1])
        box.draw(screen)
        pygame.display.update()
        rb.prn_state()


if __name__ == '__main__':
    main()