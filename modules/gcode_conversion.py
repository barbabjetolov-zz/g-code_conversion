import numpy as np
from numpy import pi
import sys
from math import sin, cos


'''
Function that splits the user_taper function in pieces,
and prints it out as a series of linear movements
'''
def interpolation(linear,expression,segment,dz,file):
    bz = eval(segment['begin.z'])
    ez = eval(segment['end.z'])
    for i in np.arange(bz,ez+dz,dz):
        z = i
        x = z*linear
        y = eval(expression)
        zi = xi = yi = 0
        if i!=0:
            #prints linear movements
            file.write('LINEAR X %f Y %f Z %f F $SPEED\n'%(z-zi,y-yi,x-xi))
        zi = z
        xi = x
        yi = y

def print_line(file,segment):
    limits = [eval(segment['begin.x']),eval(segment['end.x']),
           eval(segment['begin.y']),eval(segment['end.y']),
           eval(segment['begin.z']),eval(segment['end.z'])]

    file.write('LINEAR X %f Y %f Z %f F $SPEED\n'%(limits[5]-limits[4],limits[3]-limits[2],limits[1]-limits[0]))
