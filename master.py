"""
Initialization and Master Loop

The purpose of the master loop is to check the user inputs files for
changes and write the setpoints for each pump to a file along with
a reset command for the slave loops to stop their current setpoint
assignments and use the new ones. The master loop remembers the time it
issued the last reset command (when initialized, all slaves are given
first a reset command) to each slave, and so it can correctly set the
phase angle relative to all other slaves. The master loop updates more
often than the slave reads to ensure no double reading. The iteration time
without waiting is around 12 milliseconds.

"""

# initialization
import sys
import yaml
import pickle
from time import time, sleep
from funcs import get_waveform
l = yaml.Loader

t00 = time()
maxdt = -1
with open("user-input.yaml", 'r') as read_buffer:
    dct0 = yaml.load(read_buffer, Loader=l)
for key in dct0.keys():
    with open("comms/m-s{}-reset.pickle".format(dct0[key]['slave id']), 'wb') as write_buffer:
        write_buffer.write(pickle.dumps(True))
    with open("comms/m-s{}.pickle".format(dct0[key]['slave id']), 'wb') as write_buffer:
        wf = get_waveform(0., dct0[key])
        dt = dct0[key]['setpoint resolution']
        if dt > maxdt:
            maxdt = dt
        write_buffer.write(pickle.dumps({'setpoints': wf, 'dt': dt, 't0': 0}))

with open("general-settings.yaml", 'r') as read_buffer:
    settings_dct = yaml.load(read_buffer, Loader=l)

# care for object mutability
time_per_iter = maxdt * \
    settings_dct['update frequency to setpoint resolution ratio']

while True:
    ti0 = time()
    with open("user-input.yaml", 'r') as read_buffer:
        dct = yaml.load(read_buffer, Loader=l)
    for key in dct.keys():
        if dct[key] != dct0[key]:
            with open("comms/m-s{}-reset.pickle".format(dct[key]['slave id']), 'wb') as write_buffer:
                write_buffer.write(pickle.dumps(True))
            with open("comms/m-s{}.pickle".format(dct[key]['slave id']), 'wb') as write_buffer:
                t0 = time() - t00
                wf = get_waveform(t0, dct[key])
                dt = dct[key]['setpoint resolution']
                write_buffer.write(pickle.dumps(
                    {'setpoints': wf, 'dt': dt, 't0': t0}))
        else:  # this is redundant writing
            with open("comms/m-s{}-reset.pickle".format(dct[key]['slave id']), 'wb') as write_buffer:
                write_buffer.write(pickle.dumps(False))

    ti = time() - ti0
    print("{:.1f}".format(1000 * ti))
    if ti > time_per_iter:
        raise Exception(
            "The master loop iteration time is greater than the allowed time per iteration")
    dct0 = dct
    sleep(time_per_iter - ti)
