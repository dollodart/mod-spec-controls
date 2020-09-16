import sys
import os
parent = '/'.join(os.getcwd().split('/')[:-1])
sys.path.insert(0,parent)
from funcs import *
import matplotlib.pyplot as plt

plt.figure()
plt.plot(my_square(np.linspace(0,2*np.pi,1000)))
plt.plot(my_sawtooth(np.linspace(0,2*np.pi,1000)))
plt.show()
