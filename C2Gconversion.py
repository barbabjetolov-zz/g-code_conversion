import numpy as np
import sys
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pydoc

#import single math functions (the easiest way)
#from math import sin, cos, tan, asin, acos, atan, sqrt
from numpy import pi

#custom modules
sys.path.append('./modules')
import ind_tools
import gcode_conversion as gcc
from init_parse import init_parse

#needed later
functions = []

'''
Check for options
'''
for n,i in enumerate(sys.argv):
    '''
    Init file
    '''
    if i == '-i' or i == '--init':
        dicinit = init_parse(sys.argv[n+1])
    else:
        dicinit = init_parse('init')

    '''
    gcode init file
    '''
    if i == '-g' or i == '--ginit':
        gcodeinit = init_parse(sys.argv[n+1])
    else:
        gcodeinit = init_parse('gcode_init')

    '''
    Verbosity
    '''
    if i == '-nv' or i == '--non-verbose':
        VERBOSE = 0
    else:
        VERBOSE = 1

    '''
    Debug
    '''
    if i == '-d' or i == '--debug':
        DEBUG = 1
    else:
        DEBUG = 0

'''
Sets input and output files
'''
input = open(dicinit['input'],'r')
output = open(dicinit['output'],'w')

'''
Print of incipit
'''
if VERBOSE == 1:
    print('\nRSOFT-CAD to G_CODE conversion script\n')
    print('Released under MIT license\n')

if VERBOSE == 1:
    print('Processing file \'%s\'\n'%dicinit['input'])

'''
Parsing of the CAD file. It returns:
param - dictionary containing the first section of the file
ut - list of dictionaries with all the user_taper mathematical expressions
seg - list of dictionaries with the content of each segment section
'''
param, ut, seg = ind_tools.cad_parser(input)

'''
Converts the dictionary entries corresponding to the first section of the .ind file
to variables. It's needed by the eval() function
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

            try:
                #case 1)
                functions.append(ne)
                exec('from math import %s'%ne)
            except ImportError:
                #case 2) and 3). Just 'pass' is enough
                pass


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
The same with user_taper functions. This procedure is divided in N parts:
1. Strip the expression from all the mathematical symbols (i.e. (,),+,-,*,/)
2.
'''

for t in ut:

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
            #print(e,str(eval(e)))
            t['expression'] = t['expression'].replace(e,str(eval(e)))


'''
Reconstructing the waveguides
'''
begins = ind_tools.wg_reconstruction(seg)

#seg[0], seg[int(begins[0]['number'])-1] = seg[int(begins[0]['number'])-1], seg[0]
if DEBUG==1:
    print(begins[0],seg[0])

#exit(-1)
'''
little debug feature, to see if the .ind file is written correctly
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

if index == 0 and len(begins) != len(seg):
    print('.ind file error. Abort.')
    exit(-1)

#print([s for s in seg if s['number'] == '2'])
#print([s for s in seg if s['number'] == '9'])


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

#just casting correction values to float, for convenience
ref_index = float(dicinit['ref_index'])
acc_correction = float(dicinit['acc_correction'])


'''
Most important part of the script: printing segments on file
It begins from the lower ones (lower y) and continues with the upper ones
Prints one full waveguide at a time
'''

index = 0

for n,beg in enumerate(begins):

    paragon = beg

    gcc.print_acceleration_correction_beginning(acc_correction,output)
    print('Print section nr. %s - beginning'%beg['number'])
    gcc.print_segment(paragon,ut,dicinit,ref_index,acc_correction,output)


    index += 1

    for j,segment in enumerate(seg):

        condition = (segment['begin.x'] == paragon['end.x'] and
                     segment['begin.y'] == paragon['end.y'] and
                     segment['begin.z'] == paragon['end.z'])
        if condition:
            #print(condition)
            paragon = segment
            print('Print section nr. %s'%segment['number'])
            gcc.print_segment(paragon,ut,dicinit,ref_index,acc_correction,output)
            break
    else:
        gcc.print_acceleration_correction_end(acc_correction,output)

        #exit(-1)
        #output.write('///////////////\n//Printing section %d\n////////////////\n'%(j*len(seg)+k))
    '''
    b_e = [eval(segment['begin.x']),eval(segment['end.x']),
           eval(segment['begin.y']),eval(segment['end.y']),
           eval(segment['begin.z']),eval(segment['end.z'])]

    if n == 0:
        bfr = b_e

    if n != 0:
        #brings the laser head at the beginning of the segment (does this really work?)
        output.write('\n//returns the head at the beginning of the segment\n')
        output.write('LINEAR X %f Y %f Z %f F $SPEED\n'%(b_e[0] - bfr[0], ref_index*(b_e[2] - bfr[2]), b_e[4] - bfr[4]))



    distx = b_e[0] - b_e[1]
    disty = b_e[3] - b_e[2]
    distz = b_e[5] - b_e[4]

    if VERBOSE==1:
        print('Printing section n. %d.'%(n+1))


    #begin 'while' loop and open shutter
    output.write('WHILE $SCAN LT $NSCANS\n')

    #adds laser head acceleration correction at the beginning of the waveguide
    if b_e[4] == 0:
        output.write('//moves the head before acc correction\n')
        output.write('LINEAR X -%f Y 0 Z 0 F $SPEED\n'%acc_correction)
        output.write('$do1.x = 1\n\n') #opens shutter
        output.write('//acceleration correction\n')
        output.write('LINEAR X %f Y 0 Z 0 F $SPEED\n'%acc_correction)

    if 'position_taper' and 'position_y_taper' not in segment:
        print('\tStraight line.')
        output.write('\n//print line\n')
        gcc.print_line(output,segment,ref_index)

    else:
        print('\tFollowing taper function n. %s'%segment['position_taper'])
        #computes the slope of the linear part
        m = segment['end.x'] + '-' + segment['begin.x'] + '/' + segment['end.z'] + '-' + segment['begin.z']
        linearx = eval(m)

        #associates the segment with its user_taper function
        for it in ut:
            if it['number'] == segment['position_taper']:
                expression = it['expression']
        output.write('\n//print interpolated function\n')
        gcc.interpolation(linearx,expression,segment,eval(dicinit['dz']),output,ref_index)
        output.write('\n//end interpolated function\n')
    #adds laser head acceleration compensation at the end of the waveguide
    try:
        if seg[n+1]['begin.z'] == '0':
            output.write('\n//accel correction at the end\n')
            output.write('LINEAR X 0 Y 0 Z %f F $SPEED\n'%acc_correction)
            output.write('\n$do1.x = 0\n') #closes shutter
    except IndexError: #prints this line anyway, but only if the printed segment is the very last
        output.write('\n//accel correction at the end\n')
        output.write('LINEAR X 0 Y 0 Z %f F $SPEED\n'%acc_correction)
        output.write('\n$do1.x = 0\n') #closes shutter

    #finalizes 'while' loop
    output.write('$SCAN = $SCAN + 1\n')
    #output.write('LINEAR X -%f Y -%f Z -%f\n'%(distz,disty,distx))
    output.write('LINEAR Y $SCANSTEP F 0.1\n')
    output.write('END WHILE\n')
    '''
output.write('ABORT X Y Z\n')
