"""

Tests for the time set correction so that for the same phase angle set at different times, the phase angle is relative to t0 (and all other pumps).

"""
import sys
import os
parent = '/'.join(os.getcwd().split('/')[:-1])
sys.path.insert(0,parent)
from funcs import *
import matplotlib.pyplot as plt

plt.figure()
dct={'period':300,'setpoint resolution':1,'shape':'sine','amplitude':1,'offset':1,'pump time':300,'phase':0}
x=np.linspace(0,300,301)
n=8
for c,time0 in enumerate(np.linspace(0,300,n+1)):
    print("Roll of independent variable={0}".format(-1*c*int(300/n)))
    plt.plot(np.roll(x,-1*c*int(300/n)),
            get_waveform(time0,dct)+0.1*c,'o',label=str(time0))
plt.legend()
plt.show()
