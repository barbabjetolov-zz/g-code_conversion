import numpy as np
from numpy import pi
import sys


'''
Function that splits the user_taper function in pieces,
and prints it out as a series of linear movements.
x and z axis are exchanged, because of differences in notation between CAD and the laser machine
'''
def interpolation(linear,expression,segment,dz,file):
    bz = eval(segment['begin.z'])
    ez = eval(segment['end.z'])
    zi = xi = yi = 0
    for i in np.arange(bz,ez+dz,dz): #ez+dz is needed in order for the loop to stop at 'ez'
        z = i
        x = z*linear
        try:
            y = eval(expression)
        except NameError as e:
            e = str(e).split('\'')[1]
            exec('from math import %s'%e)
            y = eval(expression)
        except ValueError as ve:
            print(ve)
        if i!=0:
            #Saves the first set of coordinates and prints linear movements
            file.write('LINEAR X %f Y %f*$RIN Z %f F $SPEED\n'%(z-zi,y-yi,x-xi))
        zi = z
        xi = x
        yi = y

def print_line(file,segment):
    limits = [eval(segment['begin.x']),eval(segment['end.x']),
           eval(segment['begin.y']),eval(segment['end.y']),
           eval(segment['begin.z']),eval(segment['end.z'])]

    file.write('LINEAR X %f Y %f*$RIN Z %f F $SPEED\n'%(limits[5]-limits[4],limits[3]-limits[2],limits[1]-limits[0]))

'''
Function that prints acceleration correction at the beginning of the waveguide
'''
def print_acceleration_correction_beginning(acc_correction,output):
    #the head is automatically positioned at the beginning of the first segment
    output.write('//moves the head before acc correction\n')
    output.write('LINEAR X -%f Y 0 Z 0 F $SPEED\n'%acc_correction)
    output.write('$do1.x = 1\n\n') #opens shutter
    output.write('//acceleration correction\n')
    output.write('LINEAR X %f Y 0 Z 0 F $SPEED\n'%acc_correction)

def print_acceleration_correction_end(acc_correction,output):
    output.write('\n//acceleration correction at the end of waveguide//\n')
    output.write('LINEAR X %f Y 0 Z 0 F $SPEED\n'%acc_correction)
    output.write('$do1.x = 0\n\n') #closes shutter
    output.write('LINEAR X -%f Y 0 Z 0 F $SPEED\n'%acc_correction)

def print_segment(segment,ut,dicinit,acc_correction,output):

    #initializing while loop
    output.write('\n\nWHILE $SCAN LT $NSCAN\n\n')

    if ('position_taper' and 'position_y_taper' not in segment) or segment['position_taper'] == 'TAPER_LINEAR':
        #print('\tStraight line.')
        output.write('\n//print line\n')
        print_line(output,segment)

    elif segment['position_taper'] != 'TAPER_ARC':
        #print('\tFollowing taper function n. %s'%segment['position_taper'])
        #computes the slope of the linear part
        m = segment['end.x'] + '-' + segment['begin.x'] + '/' + segment['end.z'] + '-' + segment['begin.z']
        linearx = eval(m)

        #associates the segment with its user_taper function
        for it in ut:
            if it['number'] == segment['position_taper']:
                expression = it['expression']
        output.write('\n//print interpolated function\n')
        interpolation(linearx,expression,segment,eval(dicinit['dz']),output)
        output.write('\n//end interpolated function\n')

    output.write('\n\n$SCAN = $SCAN +1\nENDWHILE\n\n')
