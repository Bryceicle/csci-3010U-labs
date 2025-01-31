# -*- coding: utf-8 -*-
"""
Using Python Numerical Integrators

Author: Faisal Z. Qureshi
Web: http://www.vclab.ca
"""

import numpy as np

state = np.array([100.0, 0.0]) # Initial state
                               # state[0] = pos, state[1] = velocity
t = 0.0                        # time
m = 100                        # mass
g = 9.8                        # acceleration due to gravity

def f(t, state, arg1, arg2):
    # t = time
    # state[0] = position
    # state[1] = velocity
    # arg = extra arguments, where needed
    #    here, we are passing the value of g and mass m
    #    arg1 = mass
    #    arg2 = g
    
    force = - arg1 * arg2                        # -ve, since gravity points downwards

    dstate = np.array([ state[1], force/arg1 ])  # dstate[0] = velocity
                                                 # dstate[1] = force / mass
    
    return dstate

from scipy.integrate import ode

solver = ode(f)
solver.set_integrator('dop853')

solver.set_initial_value(state, t) # Recall that state contains
                                   # the initial state, t contains
                                   # the initial time

solver.set_f_params(m, g)          # These parameters will become available to
                                   # function f as arg1 and arg2

dt = 0.1   # seconds

for i in range(10):
    if solver.successful():
        solver.integrate(solver.t + dt)
        
    state = solver.y   # The new state of the particle
    t = solver.t       # The new time (t + dt)

    print('Time', t)
    print('State', state)    

