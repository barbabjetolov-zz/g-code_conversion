''' testing Edoardo's code


['LINEAR', 'X', '0.001000', 'Y', '0.000094', 'Z', '0.000000*$RIN', 'F', '$SPEED']
'''

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys

x = [0.]
y = [0.]
z = [0.]

#print(x[-1])
g_code_file = open(sys.argv[1])

line_counter = 0
max_line = 10000 # max line to go to

for line in g_code_file:
    line_counter +=1
    if line_counter < max_line:
        printing = line.split()
        try:
            if printing[0] == 'LINEAR':

                x.append(float(printing[2])+float(x[-1]))
                y.append(float(printing[4])+float(y[-1]))
                test = printing[6].split('*')
                z.append(float(test[0])+float(z[-1]))
        except:
            continue
            #print(printing)
#print(y)
#print(len(y))
#print(len(z))

step = 3
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x[::step], y[::step], z[::step])
plt.show()
