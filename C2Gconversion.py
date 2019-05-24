import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.pyplot import figure
from itertools import permutations
import argparse
import numpy
import sys
import time
import os

from numpy import pi

#custom modules
sys.path.append('./modules')
import ind_tools
import gcode_conversion as gcc
from init_parse import init_parse
from trigonometry_in_degrees import *

'''
# TODO:
-linspace instead of frange
-gcode parser
-rimuovere primo punto delle guide d'onda
-report on gcode plotters
'''

'''
Check for options
'''
if '-i' in sys.argv:
    index = sys.argv.index('-i')
    dicinit = init_parse(sys.argv[index+1])
else:
    dicinit = init_parse('init')
##################################################################
if '-g' in sys.argv:
    index = sys.argv.index('-i')
    gcodeinit = init_parse(sys.argv[index+1])
else:
    gcodeinit = init_parse('gcode_init')
##################################################################
if '-axes' in sys.argv:
    index = sys.argv.index('-axes')
    axes = sys.argv[index+1]
    if axes not in [''.join(p) for p in permutations('XYZ')]:
        print('Axes not chosen correctly. Abort.')
        exit(-1)
else:
    axes = 'XYZ'
##################################################################
if '-graphic' in sys.argv:
    GRAPHICS = 1
else:
    GRAPHICS = 0
##################################################################
VERBOSE = 1
DEBUG = 0


'''
Setting up plots, canvas and data lists
'''
if GRAPHICS:
    plt.ion()


fig,axs = plt.subplots(2,2,figsize=(10,10))

axs[0,0].set_xlabel(axes[2])
axs[0,0].set_ylabel(axes[0])
axs[0,1].set_xlabel(axes[1])
axs[0,1].set_ylabel(axes[0])
axs[1,0].set_xlabel(axes[2])
axs[1,0].set_ylabel(axes[1])

axs[-1, -1].axis('off')

'''
All colors, except white
For the matplotlib output
'''
colors = ['b','g','r','c','m','y','k']

'''
Array initialization
'''
x = []
y = []
z = []


'''
Sets input and output files
'''
f_input = open(dicinit['input'],'r')
output = open(dicinit['output'],'w')

'''
Handling of errors
'''
if 'input' not in dicinit:
    print('Input file unspecified. Need to provide a beamprop .ind file. Abort.')
    exit(-1)

'''
Print of incipit
'''
print('\nRSOFT-CAD to G_CODE conversion script\n\n')
print('Processing file \'%s\'\n'%dicinit['input'])

'''
Messages
'''
print('The script operates the axis transformation:')
print('.ind\t  \tgcode')
print('Z\t->\t%s\tScanning direction'%axes[0])
print('Y\t->\t%s\tDepth'%axes[1])
print('X\t->\t%s\tTransversal direction'%axes[2])



'''
Parsing of the CAD file. It returns:
paramList - dictionary containing the first section of the file
usrTaperList - list of dictionaries with all the user_taper mathematical expressions
segList - list of dictionaries with the content of each segment section
'''
paramList, usrTaperList, segList = ind_tools.cad_parser(f_input)

'''
Converts the dictionary entries corresponding to the first section of the .ind file
to variables. It's needed by the eval() function.
'''

for i in range(4):
    for content in list(paramList):
        try:
            exec('%s = %s'%(content,paramList[content]))
        except NameError as ne:
            ne = str(ne).split('\'')[1]


'''
Converts extremes of segments from symbolic expression to number
'''
for n,segment in enumerate(segList):
    for i in segment:
        first = i.split('_')[0]
        if first == 'position':
            try:
                segment[i] = segment[i].split('_')[2]
            except IndexError:
                continue
        elif first.split('.')[0] == 'end' or first.split('.')[0] == 'begin':
            try:
                '''
                Some segment extremes are relative to others
                This part computes
                '''

                rel = segment[i].split(' ')[1]
                ax = i.split('.')[1]
                pos = segment[i].split(' ')[3] + '.' + ax
                ind = eval(segment[i].split(' ')[5])

                segment[i] = eval(rel) + segList[ind-1][pos]
            except IndexError:
                segment[i] = eval(segment[i])


'''
Reconstructing the waveguides
i.e. checks how many waveguides are simulated
by counting the segments having begin.z = 0
'''
begins = ind_tools.wg_reconstruction(segList)


'''
Printing of declaration of variables on the gcode file
'''
if VERBOSE==1:
    print('\nStart printing on file...\n')

output.write('DVAR')
for key, val in gcodeinit.items():
    if key=='DWELL':
        continue
    output.write(' $%s'%key)
output.write('\n\n')

output.write('ENABLE X Y Z\nG91\nDWELL %s\n\n'%(gcodeinit['DWELL']))

for key, val in gcodeinit.items():
    if key=='DWELL':
        continue
    output.write('$%s = %s\n'%(key,val))
output.write('\n')
output.write('$SCAN = 0\n')

acc_correction = float(dicinit['acc_correction'])


'''
Most important part of the script: printing segments on file
It begins from the lower ones (lower y) and continues with the upper ones
Prints one full waveguide at a time

---ASSUMES LASER HEAD STARTS AT (0,0,0)---

'''

global paragon
counter = 0
for n,beg in enumerate(begins):

    counter += 1


    paragon = beg

    '''
    Moves laser head to begin of segment
    '''
    output.write('\n\n///Moves head to begin of segment///\n\n')
    output.write('\nG01 %s %s %s %s %s (%s + (%s*$SLOPEX) + (%s*$SLOPEY))*$RIN F $SPEED\n'%(axes[0],paragon['begin.z'],
                                                                                               axes[1],paragon['begin.y'],
                                                                                               axes[2],paragon['begin.x'],
                                                                                               paragon['begin.z'],paragon['begin.y']))

    print('Print section nr. %s'%beg['number'])
    output.write('\n\n/////Printing section %s////////\n\n'%paragon['number'])
    '''
    Initializes while loop
    '''
    output.write('WHILE $SCAN LT $SCANNO\n')
    gcc.print_acceleration_correction_beginning(acc_correction,axes,output)

    '''
    Output acceleration correction on screen
    '''
    if GRAPHICS:
        x.append(paragon['begin.z'] - acc_correction)
        x.append(paragon['begin.z'])
        y.append(paragon['begin.y'])
        y.append(paragon['begin.y'])
        z.append(paragon['begin.x'])
        z.append(paragon['begin.x'])


        axs[0,0].plot(z,x,color='k',linewidth=1)
        axs[0,1].plot(y,x,color='k',linewidth=1)
        axs[1,0].plot(z,y,color='k',linewidth=1)

        x = []
        y = []
        z = []

        fig.canvas.draw()
        fig.canvas.flush_events()


    x,y,z = gcc.print_segment(paragon,usrTaperList,dicinit,acc_correction,axes,output)

    gcc.points2gcode(float(dicinit['dz']),y,z,output,axes)

    '''
    Output of segment on screen
    '''
    if GRAPHICS:
        axs[0,0].plot(z,x,color=colors[n%len(colors)],linewidth=1)
        axs[0,1].plot(y,x,color=colors[n%len(colors)],linewidth=1)
        axs[1,0].plot(z,y,color=colors[n%len(colors)],linewidth=1)

        x = []
        y = []
        z = []

        fig.canvas.draw()
        fig.canvas.flush_events()


    for j,segment in enumerate(segList):

        condition = (segment['begin.x'] == paragon['end.x'] and
                     segment['begin.y'] == paragon['end.y'] and
                     segment['begin.z'] == paragon['end.z'])

        if condition:
            paragon = segment
            output.write('\n\n/////Printing section %s////////\n\n'%paragon['number'])
            print('Print section nr. %s'%segment['number'])
            x,y,z = gcc.print_segment(paragon,usrTaperList,dicinit,acc_correction,axes,output)

            gcc.points2gcode(float(dicinit['dz']),y,z,output,axes)

            if GRAPHICS:
                axs[0,0].plot(z,x,color=colors[n%len(colors)],linewidth=1)
                axs[0,1].plot(y,x,color=colors[n%len(colors)],linewidth=1)
                axs[1,0].plot(z,y,color=colors[n%len(colors)],linewidth=1)

                x = []
                y = []
                z = []

                fig.canvas.draw()
                fig.canvas.flush_events()





    else:
        gcc.print_acceleration_correction_end(acc_correction,axes,output)
        output.write('\t$SCAN = $SCAN + 1\n')
        output.write('ENDWHILE\n')

        if GRAPHICS:
            z.append(paragon['end.z'])
            z.append(paragon['end.z'] + acc_correction)
            y.append(paragon['end.y'])
            y.append(paragon['end.y'])
            x.append(paragon['end.x'])
            x.append(paragon['end.x'])

            axs[0,0].plot(x,z,color='k',linewidth=1)
            axs[0,1].plot(y,z,color='k',linewidth=1)
            axs[1,0].plot(x,y,color='k',linewidth=1)

            x = []
            y = []
            z = []


            fig.canvas.draw()
            fig.canvas.flush_events()

        output.write('\n\n///Returns to origin///\n\n')
        output.write('\nG01 %s %s %s %s %s (%s + (%s*$SLOPEX) + (%s*$SLOPEY))*$RIN F $SPEED\n'%(axes[0],-paragon['end.z'],
                                                                                                   axes[1],-paragon['end.y'],
                                                                                                   axes[2],-paragon['end.x'],
                                                                                                   -paragon['begin.z'],-paragon['begin.y']))


x = []
y = []
z = []

output.write('\nABORT X Y Z\n')

'''
Waits for user input to end the script
'''
input('\nPress ENTER to end script.')
