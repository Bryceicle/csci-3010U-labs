"""
author: Faisal Z. Qureshi
email: faisal.qureshi@ontariotechu.ca
website: http://www.vclab.ca
license: BSD
"""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
from scipy.integrate import ode

# Setup figure
fig = plt.figure(1)
ax = plt.axes(xlim=(0, 300), ylim=(-200, 1000))
plt.grid()
line, = ax.plot([], [], '-')
time_template = 'time = %.1fs'
time_text = ax.text(0.05, 0.9, '', transform=ax.transAxes)
plt.title('Ball-Floor-Collision: Height vs. Time')
plt.xlabel('Time')
plt.ylabel('Height')


# Background for each function
def init():
    line.set_data([], [])
    time_text.set_text('')
    return line, time_text,

# Called at each frame
def animate(i, ball):
    line.set_xdata(np.append(line.get_xdata(), ball.t))
    line.set_ydata(np.append(line.get_ydata(), ball.state[0]))
    time_text.set_text(time_template % ball.t)

    ball.update()
    return line, time_text,

# Ball simulation - bouncing ball
class Ball:
    def __init__(self, height):

        # You don't need to change y, vy, g, dt, t and mass
        self.state = [height, 0]
        self.h_init = height
        self.g = 9.8
        self.dt = 0.033
        self.t = 0
        self.mass = 1

        self.tol_distance = 0.00001

        # We plan to use rk4
        self.solver = ode(self.f)
        self.solver.set_integrator('dop853')
        self.solver.set_initial_value(self.state, self.t)

    def f(self, t, y):
        return [y[1], -self.g]

    def is_collision(self, state):
        return state[0] <= 0

    def respond_to_collision(self, state, t):
        vy_col = np.sqrt(2*self.g*self.h_init)
        return [0+self.tol_distance, vy_col], t

    def update(self):
        new_state = self.solver.integrate(self.t + self.dt)

        # Collision detection
        if not self.is_collision(new_state):
            self.state = new_state
            self.t += self.dt
        else:
            print(self.state)
            state_after_collision, collision_time = self.respond_to_collision(new_state, self.t+self.dt)
            self.state = state_after_collision
            self.t = collision_time
            self.solver.set_initial_value(self.state, self.t)

ball = Ball(height=100)

# blit=True - only re-draw the parts that have changed.
# repeat=False - stops when frame count reaches 999
# fargs=(ball,) - a tuple that can be used to pass extra arguments to animate function
anim = animation.FuncAnimation(fig, animate, fargs=(ball,), init_func=init, frames=3000, interval=10, blit=True, repeat=False)
#plt.savefig('bouncing-ball-trace', format='png')

# Save the animation as an mp4.  For more information, see
# http://matplotlib.sourceforge.net/api/animation_api.html
# anim.save('basic_animation.mp4', fps=30, extra_args=['-vcodec', 'libx264'])

plt.show()