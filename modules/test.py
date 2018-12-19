import numpy as np
from numpy import pi
import sys
from scipy.interpolate import RegularGridInterpolator

def interpolation(expression,linear,bz,ez,dz,file):
    file.write('$do1.x=1\n') #opens shutter
    for i in np.arange(0,ez+dz,dz):
        z = i
        #print(i)
        x = z/eval(linear)
        y = eval(expression)
        if i!=0:
            #prints linear movements
            file.write('LINEAR X %f Y %f Z %f F $SPEED\n'%(z-zi,y-yi,x-xi))
        zi = z
        xi = x
        yi = y
    file.write('$do1.x = 0\n') #closes shutter

def expr_to_f(expression,x,y,z):
    #x and z are exchanged, because G-code
    print(x,z)
    x, z = z, x
    print(x,z)
    return eval(expression)

def print_line(file,limits):
    file.write('$do1.x = 1\n')
    file.write('LINEAR X %f Y %f Z %f F $SPEED\n'%(limits[5]-limits[4],limits[3]-limits[2],limits[1]-limits[0])  )
    file.write('$do1.x = 0\n')

def test(x,y,z):
    return x+y+z

def expression_to_grid(expression, content,Npts):
    lin = np.linspace(0,L,Npts)
    data = expr_to_f(expression,*np.meshgrid(lin,lin,lin,indexing='ij',sparse=True))
    #for l in lin:
    #    print(expr_to_f(expression,1,2,3))
    #print(test(*np.meshgrid(lin,lin,lin,sparse=True)))

#function that interpolates the user_taper function

#conversion in G-code with INC prescription
def G_conversion(dx, points, file):
    file.write('$do1.x = 1\n') #opens shutter
    for i in range(1,len(points)):
        file.write('LINEAR X 0 Y %f Z %f F $SPEED\n'%(points[i]-points[i-1],dx))
    file.write('$do1.x = 0\n') #closes shutter
