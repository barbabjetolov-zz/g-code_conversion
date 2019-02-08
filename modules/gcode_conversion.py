import numpy as np
from numpy import pi
import sys


'''
Function that splits the user_taper function in pieces,
and prints it out as a series of linear movementsself.
x and z axis are exchanged, because of differences in notation between CAD and the laser machine
'''
def interpolation(linear,expression,segment,dz,file,ref_index):
    bz = eval(segment['begin.z'])
    ez = eval(segment['end.z'])
    for i in np.arange(bz,ez+dz,dz): #ez+dz is needed in order for the loop to stop at 'ez'
        z = i
        x = z*linear
        '''
        This section imports automatically all the mathematical functions
        '''
        while True:
            try:
                y = eval(expression)
            except NameError as e:
                e = str(e).split('\'')[1]
                exec('from math import %s'%e)
                y = eval(expression)
                continue
            else:
                break
        zi = xi = yi = 0
        if i!=0:
            #Saves the first set of coordinates and prints linear movements
            file.write('LINEAR X %f Y %f Z %f F $SPEED\n'%(z-zi,ref_index*(y-yi),x-xi))
        zi = z
        xi = x
        yi = y

def print_line(file,segment, ref_index):
    limits = [eval(segment['begin.x']),eval(segment['end.x']),
           eval(segment['begin.y']),eval(segment['end.y']),
           eval(segment['begin.z']),eval(segment['end.z'])]

    file.write('LINEAR X %f Y %f Z %f F $SPEED\n'%(limits[5]-limits[4],ref_index*(limits[3]-limits[2]),limits[1]-limits[0]))
