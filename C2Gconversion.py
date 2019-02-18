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
To ask Rob:
1) units
2) where does the laser head start?
3) acceleration correction - with or without derivative
4) what do the while loops do
5) wether and how to add the $SCANSTEP
'''

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

if DEBUG==1:
    print(begins[0],seg[0])

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
    output.write('\nLINEAR X %s Y %s*$RIN Z %s F $SPEED\n'%(paragon['begin.z'],paragon['begin.y'],paragon['begin.x']))

    print('Print section nr. %s - beginning'%beg['number'])
    output.write('\n\n/////Printing section %s////////\n\n'%paragon['number'])
    gcc.print_acceleration_correction_beginning(acc_correction,output)
    print('%s - %s'%(beg['begin.z'],beg['end.z']))
    gcc.print_segment(paragon,ut,dicinit,acc_correction,output)


    for j,segment in enumerate(seg):

        condition = (segment['begin.x'] == paragon['end.x'] and
                     segment['begin.y'] == paragon['end.y'] and
                     segment['begin.z'] == paragon['end.z'])
        if condition:
            #print(condition)
            paragon = segment
            output.write('\n\n/////Printing section %s////////\n\n'%paragon['number'])
            print('Print section nr. %s'%segment['number'])
            #print('%s - %s'%(segment['begin.z'],segment['end.z']))
            gcc.print_segment(paragon,ut,dicinit,acc_correction,output)
            break
    else:
        gcc.print_acceleration_correction_end(acc_correction,output)
        #returns laser head to (0,0,0)
        output.write('\n\n///Returns to origin///\n\n')
        output.write('\nLINEAR X -%s Y -%s*$RIN Z -%s F $SPEED\n'%(paragon['end.z'],paragon['end.y'],paragon['end.x']))


output.write('\nABORT X Y Z\n')
