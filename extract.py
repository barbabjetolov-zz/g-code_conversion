import numpy as np
from numpy import pi
import sys
from scipy.interpolate import RegularGridInterpolator

#import single math functions (the easiest way)
from math import sin

#arrays for indexes
taper = []
segment =[]

#arrays for content
strings1 = []
strings2 = []
param = []
expression = []
segment_content = dict()

interp = []

b_e = []

output = open('out.txt','a+')

def expr_to_f(expression,x,y,z):
    #x and z are exchanged, because G-code
    print(x,z)
    x, z = z, x
    print(x,z)
    return eval(expression)

def print_line(file,limits):
    file.write('$do1.x = 1\n')
    file.write('LINEAR X %f Y %f Z %f F $SPEED\n'%(limits[5]-limits[4],limits[3]-limits[2],limits[1]-limits[0])  )
    file.write('$do1.x = 0\n')

def test(x,y,z):
    return x+y+z

def expression_to_grid(expression, content,Npts):
    lin = np.linspace(0,L,Npts)
    data = expr_to_f(expression,*np.meshgrid(lin,lin,lin,indexing='ij',sparse=True))
    #for l in lin:
    #    print(expr_to_f(expression,1,2,3))
    #print(test(*np.meshgrid(lin,lin,lin,sparse=True)))

#function that interpolates the user_taper function
def interpolation(expression,linear,bz,ez,dz,file):
    file.write('$do1.x=1\n') #opens shutter
    for i in np.arange(0,ez+dz,dz):
        z = i
        #print(i)
        x = z/eval(linear)
        y = eval(expression)
        if i!=0:
            #prints linear movements
            file.write('LINEAR X %f Y %f Z %f F $SPEED\n'%(z-zi,y-yi,x-xi))
        zi = z
        xi = x
        yi = y
    file.write('$do1.x = 0\n') #closes shutter

#conversion in G-code with INC prescription
def G_conversion(dx, points, file):
    file.write('$do1.x = 1\n') #opens shutter
    for i in range(1,len(points)):
        file.write('LINEAR X 0 Y %f Z %f F $SPEED\n'%(points[i]-points[i-1],dx))
    file.write('$do1.x = 0\n') #closes shutter


#reads file input
with open(sys.argv[1]) as f:
    content = f.readlines()
content = [x.strip( ) for x in content]
#content = filter(None, content)

#looks for first section

for n,s in enumerate(content):
    s=s.split(' ')[0]
    if s=='width':
        e1s=n
        break


#gets parameters - the script can tell if it's a float or a string
k=0
#xrange

try:
    for i in range(e1s+1):
        #print(i)
        param.append(float(content[i].split(' ')[2]))
        k=k+1
except ValueError:
    strings1.append(content[i].split(' ')[2])

print(strings1)
print(param)

#looks for user_taper/s section/s
for n,s in enumerate(content):
    if s=='end user_taper':
        taper.append(n)

print('Found %d user_taper section/s'%len(taper))

#gets the taper formula
for index in taper:
    k=index
    while k>0:
        k=k-1
        s=content[k].split(' ')[0]
        if s=='expression':
            expression.append(content[k].split(' ')[2])
            #print 'ok'
        break


#looks for segment section/s
for n,s in enumerate(content):
    if s=='end segment':
        segment.append(n)

print('Found %d segment section/s'%len(segment))

L = param[0]

for index in segment:
    k=index-1;
    while content[k].split(' ')[0]!='segment':
        segment_content[content[k].split(' ')[0]] = content[k].split(' ')[2]
        k=k-1

    b_e = [eval(segment_content['begin.x']),eval(segment_content['end.x']),eval(segment_content['begin.y']),eval(segment_content['end.y']),eval(segment_content['begin.z']),eval(segment_content['end.z'])]
    print(b_e)

    #check if there are non "position_taper" things.
    if 'position_taper' and 'position_x_taper' and 'position_y_taper' not in segment_content:
        print_line(output,b_e)
        print('linear')

    else:
        print('function')
        if 'position_taper' not in segment_content:
            print('z')
        if 'position_y_taper' not in segment_content:
            print('y')
        if 'position_x_taper' not in segment_content:
            print('x')
            linearx = '(%s/%s)'%(segment_content['end.z'],segment_content['end.x'])

        interpolation(expression[0],linearx,eval(segment_content['begin.z']),eval(segment_content['end.z']),1e-2,output)
