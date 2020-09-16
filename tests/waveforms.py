import sys
import os
parent = '/'.join(os.getcwd().split('/')[:-1])
sys.path.insert(0,parent)
from funcs import *
import matplotlib.pyplot as plt

plt.figure()
plt.plot(generate_waveform('sine',phase_shift=0))
plt.plot(generate_waveform('sine',phase_shift=90))
plt.show()
