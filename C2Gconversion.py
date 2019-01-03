import numpy as np
import sys

#import single math functions (the easiest way)
from math import sin
from numpy import pi

#custom modules
sys.path.append('./modules')
from cad_parser import cad_parser
import gcode_conversion as gcc
from init_parse import init_parse

print('RSOFT-CAD to G_CODE conversion script\n')

#open and parse init files
for n,i in enumerate(sys.argv):
    if i == '-i' or i == '--init':
        dicinit = init_parse(sys.argv[n+1])
    else:
        dicinit = init_parse('init')

    if i == '-g' or i == '--ginit':
        gcodeinit = init_parse(sys.argv[n+1])
    else:
        gcodeinit = init_parse('gcode_init')

#set input and output
input = open(dicinit['input'],'r')
output = open(dicinit['output'],'w')

#parse cad input file
#param - dictionary
#ut & seg - lists of dictionaries
param, ut, seg = cad_parser(input)

L = eval(param['L'])

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


for n,content in enumerate(seg):

    b_e = [eval(content['begin.x']),eval(content['end.x']),eval(content['begin.y']),eval(content['end.y']),eval(content['begin.z']),eval(content['end.z'])]

    if n == 0:
        bfr = b_e

    output.write('LINEAR X %f Y %f Z %f\n'%(b_e[0] - bfr[0], b_e[2] - bfr[2], b_e[4] - bfr[4]))

    bfr = b_e

    distx = b_e[0] - b_e[1]
    disty = b_e[3] - b_e[2]
    distz = b_e[5] - b_e[4]

    #begin 'while' loop and open shutter
    output.write('WHILE $SCAN LT $NSCANS\n')
    output.write('$do1.x = 1\n\n') #opens shutter

    print('Outputting section n. %d'%(n+1))

    #check if there are non "position_taper" things.
    if 'position_taper' and 'position_x_taper' and 'position_y_taper' not in content:
        gcc.print_line(output,b_e)

    else:
        k = 0
        if 'position_x_taper' not in content:
            m = content['end.x'] + '-' + content['begin.x'] + '/' + content['end.z'] + '-' + content['begin.z']
            linearx = eval(m)

        gcc.interpolation(L,linearx,ut[k]['expression'],content,eval(dicinit['dz']),output)
        k = k+1

    output.write('\n$do1.x = 0\n') #closes shutter

    #finalizes 'while' loop
    output.write('$SCAN = $SCAN + 1\n')
    output.write('LINEAR X -%f Y -%f Z -%f\n'%(distz,disty,distx))
    output.write('LINEAR Y $SCANSTEP F 0.1\n')
    output.write('END WHILE\n')
output.write('ABORT X Y Z\n')
