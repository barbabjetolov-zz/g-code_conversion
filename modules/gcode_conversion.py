import numpy as np
from numpy import pi
import sys

from math import sin

def interpolation(var,linear,expression,seg,dz,file):
    L = var
    bz = eval(seg['begin.z'])
    ez = eval(seg['end.z'])
    for i in np.arange(bz,ez+dz,dz):
        z = i
        x = z*linear
        y = eval(expression)
        if i!=0:
            #prints linear movements
            file.write('LINEAR X %f Y %f Z %f F $SPEED\n'%(z-zi,y-yi,x-xi))
        zi = z
        xi = x
        yi = y

def print_line(file,limits):
    file.write('LINEAR X %f Y %f Z %f F $SPEED\n'%(limits[5]-limits[4],limits[3]-limits[2],limits[1]-limits[0]))
