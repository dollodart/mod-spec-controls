import numpy as np
import yaml
import pickle
from funcs import *
from time import sleep, time
slave_id = 5

# initialization
with open("general-settings.yaml", 'r') as read_buffer:
    settings_dct = yaml.load(read_buffer, Loader=yaml.Loader)
sleep(settings_dct['slave loop delay'])  # ensures the master loop gets started

# start communications with the device
t0 = time()
with open("user-input.yaml", 'r') as read_buffer:
    dct = yaml.load(read_buffer, Loader=yaml.Loader)

for key, sd in dct.items():
    if sd['slave id'] == slave_id:
        instr = find_instrument(
            sd['type'],
            port=sd['port'],
            baud_rate=sd['baud rate'],
            address=sd['address'])
        units = sd['units']
        break

# load the initial setpoints
with open("comms/m-s1.pickle", "rb") as read_buffer:
    params_dct = pickle.load(read_buffer)
setpoints = params_dct['setpoints'].tolist()
dt = params_dct['dt']

dti = time() - t0
if dti > dt:
    raise Exception(
        "The slave loop initialization time is greater than the allowed time to initialize")
sleep(dt - dti)
# slave loop
t = 0
t_check = dt * \
    float(settings_dct['update frequency to setpoint resolution ratio'])
# note: this will check as often as dt, when the master loop will check as
# often as maxdt. so if the pump time setpoint are significantly
# different, then there may be a problem

while True:
    t0 = time()
    if len(setpoints) == 0:  # assume a repetition if the setpoints run out
        with open("comms/m-s1.pickle", "rb") as read_buffer:
            params_dct = pickle.load(read_buffer)
        setpoints = params_dct['setpoints'].tolist()
        dt = params_dct['dt']

    if t > t_check:
        with open("comms/m-s1-reset.pickle", "rb") as read_buffer:
            resetQ = pickle.load(read_buffer)
        if resetQ:
            print('slave reset')
            with open("comms/m-s1.pickle", "rb") as read_buffer:
                params_dct = pickle.load(read_buffer)
            setpoints = params_dct['setpoints'].tolist()
            dt = params_dct['dt']
        t = 0
    sp = setpoints.pop(0)
    instr.flush()
    instr.write_rate(sp, units=units)
    t += dt
    dti = time() - t0
    if dti > dt:
        raise Exception(
            "The slave loop iteration time is greater than the allowed time per iteration")

    sleep(dt - (time() - t0))
