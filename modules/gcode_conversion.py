import sys
from trigonometry_in_degrees import *
from numpy import pi

'''
Range for float numbers. Useful for long loops, to avoid memory errors
'''
def frange(start,stop,step):
    while start < stop:
        yield float(start)
        start += step

'''
Function that splits the user_taper function in pieces,
and prints it out as a series of G01 movements.
x and z axis are exchanged, because of differences in notation between CAD and the laser machine
'''
def interpolation(expression,segment,dz,axes,file):

    lx = []
    ly = []
    lz = []

    bz = segment['begin.z']
    ez = segment['end.z']

    zi=0
    yi=0
    xi=0

    expression = expression.replace('z','z/(segment[\'end.z\'] - segment[\'begin.z\'])')

    for i in frange(bz,ez,dz):
        z = i
        '''
        Rescaling of the function
        '''
        x = eval(expression)*(segment['end.x'] - segment['begin.x']) + segment['begin.x']
        y = eval(expression)*(segment['end.y'] - segment['begin.y']) + segment['begin.y']

        '''
        file.write('G01 %s %f %s %f %s %f*$RIN F $SPEED\n'%(axes[0],z-zi,
                                                               axes[1],y-yi,
                                                               axes[2],x-xi))

        '''
        lx.append(z)
        ly.append(y)
        lz.append(x)

        zi = z
        xi = x
        yi = y

    return lx,ly,lz


def print_line(file,segment,axes):
    limits = [segment['begin.x'],segment['end.x'],
              segment['begin.y'],segment['end.y'],
              segment['begin.z'],segment['end.z']]

    file.write('G01 %s %f %s %f %s (%f + (%f*$SLOPEX)+(%f*$SLOPEY))*$RIN F $SPEED\n'%(axes[0],limits[5]-limits[4],
                                                                                         axes[1],limits[3]-limits[2],
                                                                                         axes[2],limits[1]-limits[0],
                                                                                         limits[5]-limits[4],limits[3]-limits[2]))

    return [segment['end.z'],segment['begin.z']], [segment['begin.y'],segment['end.y']], [segment['begin.x'],segment['end.x']]

'''
Function that prints acceleration correction at the beginning of the waveguide
'''
def print_acceleration_correction_beginning(acc_correction,axes,output):
    #the head is automatically positioned at the beginning of the first segment
    output.write('\t//moves the head before acc correction\n')
    output.write('\tG01 %s %f %s 0 %s (%f*$SLOPEX)*$RIN F $SPEED\n'%(axes[0],-acc_correction,axes[1],axes[2],-acc_correction))
    output.write('\t$do1.x = 1\n\n') #opens shutter
    output.write('\t//acceleration correction\n')
    output.write('\tG01 %s %f %s 0 %s (%f*$SLOPEX)*$RIN F $SPEED\n'%(axes[0],acc_correction,axes[1],axes[2],-acc_correction))

def print_acceleration_correction_end(acc_correction,axes,output):
    output.write('\n\t//acceleration correction at the end of waveguide//\n')
    output.write('\tG01 %s %f %s 0 %s (%f*$SLOPEX)*$RIN F $SPEED\n'%(axes[0],acc_correction,axes[1],axes[2],-acc_correction))
    output.write('\t$do1.x = 0\n\n') #closes shutter
    #output.write('\tG01 %s %f %s 0 %s 0 F $SPEED\n'%(axes[0],-acc_correction,axes[1],axes[2]))

def print_segment(segment,ut,dicinit,acc_correction,axes,output):

    if ('position_taper' and 'position_y_taper' not in segment) or segment['position_taper'] == 'TAPER_G01':

        output.write('\n//print line\n')
        x,y,z = print_line(output,segment,axes)

    elif segment['position_taper'] != 'TAPER_ARC':

        '''
        Associates the segment with its user_taper function
        '''
        for it in ut:
            if it['number'] == segment['position_taper']:
                expression = it['expression']

        '''
        Outputs the G01 movements composing the functions
        '''
        x,y,z = interpolation(expression,segment,eval(dicinit['dz']),axes,output)


    return x,y,z

def points2gcode(dx,y,z,output,axes):

    output.write('\n\t//print interpolated function\n')
    for i in range(len(y[1:])):
        output.write('\tG01 %s %f %s %f %s (%f + (%f*$SLOPEX)+(%f*$SLOPEY))*$RIN F $SPEED\n'%(axes[0],dx,
                                                                                                 axes[1],y[i+1] - y[i],
                                                                                                 axes[2],z[i+1] - z[i],
                                                                                                 dx, y[i+1] - y[i]))
    output.write('\n\t//end interpolated function\n')
