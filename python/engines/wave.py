from math import sin, pi, log
from numpy import zeros, linspace
from scitools.numpyutils import iseq

c = 1
L = 100

def I(x):   
    return sin(2*x*pi/L)  

def f(x,t): 
    return 0

def solver0(I, f, c, L, n, dt, tstop):
    # f is a function of x and t, I is a function of x
    x = linspace(0, L, n+1) # grid points in x dir
    dx = L/float(n)
    if dt <= 0: dt = dx/float(c) # max time step
    C2 = (c*dt/dx)**2 # help variable in the scheme
    dt2 = dt*dt

    up = zeros(n+1) # NumPy solution array
    u = up.copy() # solution at t-dt
    um = up.copy() # solution at t-2*dt

    t = 0.0
    for i in iseq(0,n):
        u[i] = I(x[i])
    for i in iseq(1,n-1):
        um[i] = u[i] + 0.5*C2*(u[i-1] - 2*u[i] + u[i+1]) + \
                dt2*f(x[i], t)

    um[0] = 0; um[n] = 0

    while t <= tstop:
          t_old = t; t += dt
          # update all inner points:
          for i in iseq(start=1, stop=n-1):
              up[i] = - um[i] + 2*u[i] + \
                      C2*(u[i-1] - 2*u[i] + u[i+1]) + \
                      dt2*f(x[i], t_old)

          # insert boundary conditions:
          up[0] = 0; up[n] = 0
          # update data structures for next step
          um = u.copy(); u = up.copy()
    return u


def get_point(tstop = 1, x = 0):
    dt = 0.1
    a = solver0(I, f, c, L, 1, dt, tstop)
    return (x, a[0] * 50)

def get_line(tstop = 1, points = 1):
    dt = 0.1
    a = solver0(I, f, c, L, points, dt, tstop)
    return a
