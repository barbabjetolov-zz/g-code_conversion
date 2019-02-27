import sys
from trigonometry_in_degrees import *
from numpy import *

'''
Range for float numbers. Useful for long loops, to avoid memory errors
'''
def frange(start,stop,step):
    while start < stop:
        yield float(start)
        start += step

'''
Function that splits the user_taper function in pieces,
and prints it out as a series of linear movements.
x and z axis are exchanged, because of differences in notation between CAD and the laser machine
'''
def interpolation(expression,segment,dz,axes,file):

    lx = []
    ly = []
    lz = []

    #output = open('temp.out','w+')
    bz = segment['begin.z']
    ez = segment['end.z']

    zi=0
    yi=0
    xi=0

    expression = expression.replace('z','z/(segment[\'end.z\'] - segment[\'begin.z\'])')


    for i in frange(bz,ez+bz,dz):
        z = i
        '''
        Rescaling of the function
        '''
        x = eval(expression)*(segment['end.x'] - segment['begin.x']) + segment['begin.x']
        y = eval(expression)*(segment['end.y'] - segment['begin.y']) + segment['begin.y']

        file.write('LINEAR %s %f %s %f*$RIN %s %f F $SPEED\n'%(axes[0],z-zi,
                                                               axes[1],y-yi,
                                                               axes[2],x-xi))

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

    file.write('LINEAR %s %f %s %f*$RIN %s %f F $SPEED\n'%(axes[0],limits[5]-limits[4],
                                                           axes[1],limits[3]-limits[2],
                                                           axes[2],limits[1]-limits[0]))

    return [segment['end.z'],segment['begin.z']], [segment['begin.y'],segment['end.y']], [segment['begin.x'],segment['end.x']]

'''
Function that prints acceleration correction at the beginning of the waveguide
'''
def print_acceleration_correction_beginning(acc_correction,axes,output):
    #the head is automatically positioned at the beginning of the first segment
    output.write('//moves the head before acc correction\n')
    output.write('LINEAR %s -%f %s 0 %s 0 F $SPEED\n'%(axes[0],acc_correction,axes[1],axes[2]))
    output.write('$do1.x = 1\n\n') #opens shutter
    output.write('//acceleration correction\n')
    output.write('LINEAR %s %f %s 0 %s 0 F $SPEED\n'%(axes[0],acc_correction,axes[1],axes[2]))

def print_acceleration_correction_end(acc_correction,axes,output):
    output.write('\n//acceleration correction at the end of waveguide//\n')
    output.write('LINEAR %s %f %s 0 %s 0 F $SPEED\n'%(axes[0],acc_correction,axes[1],axes[2]))
    output.write('$do1.x = 0\n\n') #closes shutter
    output.write('LINEAR %s -%f %s 0 %s 0 F $SPEED\n'%(axes[0],acc_correction,axes[1],axes[2]))

def print_segment(segment,ut,dicinit,acc_correction,axes,output):

    #initializing while loop
    output.write('\n\nWHILE $SCAN LT $NSCAN\n\n')

    if ('position_taper' and 'position_y_taper' not in segment) or segment['position_taper'] == 'TAPER_LINEAR':
        #print(segment['begin.x'],segment['begin.y'],segment['begin.z'])
        #print(segment['end.x'],segment['end.y'],segment['end.z'])
        output.write('\n//print line\n')
        x,y,z = print_line(output,segment,axes)

    elif segment['position_taper'] != 'TAPER_ARC':
        #linearx = (segment['end.x'] - segment['begin.x'])/(segment['end.z'] - segment['begin.z'])
        #segment['linear'] = linearx

        '''
        Associates the segment with its user_taper function
        '''
        for it in ut:
            if it['number'] == segment['position_taper']:
                expression = it['expression']

        '''
        Outputs the linear movements composing the functions
        '''
        output.write('\n//print interpolated function\n')
        x,y,z = interpolation(expression,segment,eval(dicinit['dz']),axes,output)
        output.write('\n//end interpolated function\n')

    output.write('\n\n$SCAN = $SCAN +1\n')
    output.write('LINEAR Y $SCANSEP\n')
    output.write('ENDWHILE\n\n')

    return x,y,z
