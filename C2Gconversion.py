import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.pyplot import figure
from itertools import permutations
import sys
from math import radians
import time

#custom modules
sys.path.append('./modules')
import ind_tools
import gcode_conversion as gcc
from trigonometrics_in_degrees import *
from init_parse import init_parse

import random

#needed later
functions = ['sin','cos','tan']

'''
TODO
1) riferimento grafico con matplotlib - IMPORTANTE
2) finire opzioni
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
Setting up plots, canvases and data lists
'''
if GRAPHICS:
    plt.ion()
fig = plt.figure()
sub1 = fig.add_subplot(221)
sub2 = fig.add_subplot(222)
sub3 = fig.add_subplot(223)


x = []
y = []
z = []


'''
Sets input and output files
'''
fin = open(dicinit['input'],'r')
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
print('Y\t->\t%s\tTransversal direction'%axes[1])
print('X\t->\t%s\tDepth'%axes[2])



'''
Parsing of the CAD file. It returns:
param - dictionary containing the first section of the file
ut - list of dictionaries with all the user_taper mathematical expressions
seg - list of dictionaries with the content of each segment section
'''
param, ut, seg = ind_tools.cad_parser(fin)

'''
Converts the dictionary entries corresponding to the first section of the .ind file
to variables. It's needed by the eval() function.
'''

for i in range(4):
    for content in list(param):
        try:
            exec('%s = %s'%(content,param[content]))
        except NameError as ne:
            ne = str(ne).split('\'')[1]

            '''
            We have three possibilities about the nature of the missing name:
            1)Is a mathematical function that needs to be imported
            2)Is a variable just placed further down the .ind file
            3)Is an irrelevant string that can be discarded
            '''
            '''
            try:
                #case 1)
                #functions.append(ne)
                #exec('from math import %s'%ne)
            except ImportError:
                #case 2) and 3). Just 'pass' is enough
                pass
            '''



'''
Converts extremes of segments from symbolic expression to number
'''
for n,segment in enumerate(seg):
    for i in segment:
        first = i.split('_')[0]
        if first == 'position':
            try:
                segment[i] = segment[i].split('_')[2]
            except IndexError:
                continue
        elif first.split('.')[0] == 'end' or first.split('.')[0] == 'begin':
            try:
                ind = eval(segment[i].split(' ')[5])
                pos = segment[i].split(' ')[3]
                rel = segment[i].split(' ')[1]
                ax = i.split('.')[1]
                pos += '.' + ax
                segment[i] = str(eval(rel) + eval(seg[ind-1][pos]))
            except IndexError:
                segment[i] = str(eval(segment[i]))



'''
Units conversion
'''
ind_tools.unit_conversion(seg,float(dicinit['conv_factor']))

'''
The same with user_taper functions. This procedure is divided in N parts:
1. Strip the expression from all the mathematical symbols (i.e. (,),+,-,*,/)
2. eval() all the variable-dependent expressions, and imports mathematical functions
'''

for t in ut:

    #t['expression'] = t['expression'].replace('360','2*pi')

    expr = t['expression']
    for i in expr:
        expr = expr.replace('z',' ')
        if i == '(' or i == ')' or i == '+' or i == '-' or i == '*' or i == '/':
            expr = expr.replace(i,' ')
        expr = expr.replace('  ',' ')
        expr_ls = expr.split(' ')


    #strip the list from spaces, numbers and mathematical functions
    expr_ls = [x for x in expr_ls if (bool(x) == True)]
    expr_ls = [x for x in expr_ls if not x.isdigit()]

    #print(expr_ls)


    for e in expr_ls:
        if e in functions:
            continue
        else:
            try:
                t['expression'] = t['expression'].replace(e,str(eval(e)))
            except NameError as ie:
                ie = str(ie).split('\'')[1]
                exec('from math import %s'%ie)

for t in ut:
    t['expression'] = t['expression'].replace('z','(z/(segment[\'end.z\'] - segment[\'begin.z\']))')
    t['expression'] = '(' + t['expression'] + ')*(segment[\'end.y\'] - segment[\'begin.y\'])'


'''
little debug feature, to see if the .ind file is written correctly
'''
'''
index = 0
for j, segj in enumerate(seg):
        for k,segk in enumerate(seg[n:]):
            condition = (segk['begin.x'] == segj['end.x'] and
                         segk['begin.y'] == segj['end.y'] and
                         segk['begin.z'] == segj['end.z'])

            if condition:
                if DEBUG == 1:
                    print(condition)
                    #print(segj['end.x'],segj['end.y'],segj['end.z'])
                    #print(segk['begin.x'],segk['begin.y'],segk['begin.z'])
                index += 1
                break


#if index == 0 and len(begins) != len(seg):
#    print('.ind file error. Abort.')
 #    exit(-1)
'''

'''
Reconstructing the waveguides
i.e. checks how many waveguides are simulated
by counting the segments having begin.z = 0
'''
begins = ind_tools.wg_reconstruction(seg)


'''
xi = []
yi = []
xf = []
yf = []
lines = []

not_begins = [x for x in seg if x['begin.z'] != 0]

import numpy as np
#exit(-1)

fig = plt.figure()
plt.xlabel('transversal - x')
plt.ylabel('depth - y')
for b in not_begins:
    print(b['number'],b['end.z'],b['end.y'],b['end.x'])
    xi.append(b['begin.x'])
    yi.append(b['begin.y'])
    xf.append(b['end.x'])
    yf.append(b['end.y'])



plt.plot(xi,yi,'ro',label='begin')
plt.plot(xf,yf,'bo',label='end')
plt.legend(loc='upper right')
plt.show()

exit(-1)
'''
'''
Printing of declaration of variables on the gcode file
'''
if VERBOSE==1:
    print('\nStart printing on file...\n')
#prints declarations on g-code file
output.write('DVAR')
for key, val in gcodeinit.items():
    if key=='DWELL':
        continue
    output.write(' $%s'%key)
output.write('\n\n')

output.write('ENABLE X Y Z\nINC\nDWELL %s\n\n'%(gcodeinit['DWELL']))

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

for n,beg in enumerate(begins):

    paragon = beg

    #moves laser head to begin of segment
    output.write('\n\n///Moves head to begin of segment///\n\n')
    output.write('\nLINEAR %s %s %s %s %s %s*$RIN F $SPEED\n'%(axes[0],paragon['begin.z'],
                                                               axes[1],paragon['begin.y'],
                                                               axes[2],paragon['begin.x']))

    print('Print section nr. %s - beginning'%beg['number'])
    output.write('\n\n/////Printing section %s////////\n\n'%paragon['number'])
    gcc.print_acceleration_correction_beginning(acc_correction,axes,output)
    x,y,z = gcc.print_segment(paragon,ut,dicinit,acc_correction,axes,output)

    '''
    Outputs the segment on screen via matplotlib
    '''

    if GRAPHICS:
        sub1.plot(z,x,color='green',linewidth=1)
        sub2.plot(y,x,color='red',linewidth=1)
        sub3.plot(z,y,color='blue',linewidth=50)

        x = []
        y = []
        z = []

        fig.canvas.draw()
        fig.canvas.flush_events()

        time.sleep(.5)


    for j,segment in enumerate(seg):

        condition = (segment['begin.x'] == paragon['end.x'] and
                     segment['begin.y'] == paragon['end.y'] and
                     segment['begin.z'] == paragon['end.z'])
        if condition:
            paragon = segment
            output.write('\n\n/////Printing section %s////////\n\n'%paragon['number'])
            print('Print section nr. %s'%segment['number'])
            x,y,z = gcc.print_segment(paragon,ut,dicinit,acc_correction,axes,output)

            if GRAPHICS:
                sub1.plot(z,x,color='green',linewidth=1)
                sub2.plot(y,x,color='red',linewidth=1)
                sub3.plot(z,y,'bo')

                x = []
                y = []
                z = []

                fig.canvas.draw()
                fig.canvas.flush_events()
                time.sleep(.5)

            break
    else:
        gcc.print_acceleration_correction_end(acc_correction,axes,output)
        output.write('\n\n///Returns to origin///\n\n')
        output.write('\nLINEAR %s -%s %s -%s %s -%s*$RIN F $SPEED\n'%(axes[0],paragon['end.z'],
                                                                      axes[1],paragon['end.y'],
                                                                      axes[2],paragon['end.x']))


x = []
y = []
z = []

output.write('\nABORT X Y Z\n')

'''
Waits for user input to end the script
'''
input('\nPress any key to end script.')
