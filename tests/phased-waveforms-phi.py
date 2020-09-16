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
dct={'period':300,'setpoint resolution':1,'shape':'sine','amplitude':1,'offset':1,'pump time':600,'phase':0}
x=np.arange(0,dct['pump time']+2*dct['setpoint resolution'],dct['setpoint resolution'])
n=8
for c,phi in enumerate(np.linspace(0,360,n+1)):
    dct['phase']=phi
    plt.plot(x,
            get_waveform(0.,dct),'o',label=str(phi))
plt.legend()
plt.show()
