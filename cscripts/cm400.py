from time import time, sleep
import pandas as pd
from datetime import datetime
#from checksum import checksum
checksum = lambda x: True # debug
import serial

# these are parameter labels for flow rates
write_parameter = 1
read_parameter = 3

port = '/dev/pts/3'
time_out = 0.5
time_sep = 0.25
delay = 0.0 * 60

# MFC labels (=hardware port number) to gas type and software port numbers
port_dict = {1: {'read': 1, 'write': 2},
             2: {'read': 3, 'write': 4}}
gas_dict = {1: 'He', 2: 'H2'}
fact_dict = {1: {'gas_fact': 1.44, 'cal_fact': 1.1},
             2: {'gas_fact': 1.04, 'cal_fact': 1.2}}


def read_set_check(mfc, desired_val):
    factor = fact_dict[mfc]['gas_fact'] * fact_dict[mfc]['cal_fact']
    nominal_val = desired_val / factor

    # read
    quer = query(port_dict[mfc]['read'], read_parameter)
    ser.write(quer); sleep(time_sep)
    read = ser.readline().decode('ascii').rstrip('\r\n'); sleep(time_sep)
    if not checksum(read):
        print(f'checksum not correct on return for read for mfc {mfc}')

    # set
    writ = write(port_dict[mfc]['write'], write_parameter, nominal_val)
    ser.write(writ); sleep(time_sep)
    read = ser.readline().decode('ascii').rstrip('\r\n'); sleep(time_sep)
    if not checksum(read):
        print(f'checksum not correct on return for write for mfc {mfc}')

    # check
    ret = float(read.split(',')[4].replace(' ', ''))  # returned set point
    cmd = command(port_dict[mfc]['write'], 'k')
    ser.write(cmd); sleep(time_sep)
    read = ser.readline().decode('ascii').rstrip('\r\n'); sleep(time_sep)
    if not checksum(read):
        print(f'checksum not correct on return for read for mfc {mfc}')
    pv = float(read.split(',')[6].replace(' ', ''))

    if abs((pv - ret) / ret) < 0.05:
        print('process value read is equal to setpoint within 5%')
        print(f'{gas_dict[mfc]},{desired_val:.2f},{datetime.now().ctime()}')
    else:
        print('process value read is NOT equal to setpoint')

    return f'{nominal_val:.8f}' # record the nominal value, not the desired value
    # the factors should be saved to the file making it irrelevant which is recorded


def query(port, parameter):
    return 'az{0}.{1:02d}p{2:02d}?\r\n'.format(
        controller_id, port, parameter).encode('ascii')


def write(port, parameter, value):
    return 'az{0}.{1:02d}p{2:02d}={3:.2f}\r\n'.format(
        controller_id, port, parameter, value).encode('ascii')


def command(port, command):
    return 'az{0}.{1:02d}{2}\r\n'.format(
        controller_id, port, command).encode('ascii')

# if you use readlines, you must specify a timeout
#ser = serial.Serial(PORT, timeout=TIMEOUT)
from virtual import DummySer
ser = DummySer() # debug

# startup (address query)
ser.write(b'azi\r')
azi = ser.readline().decode('ascii').rstrip('\r\n')
chk = checksum(azi)

if chk:
    print('first message succesful')
else:
    print('first message unsuccesful')

azi = azi.split(',')
print(f'Serial Number = {azi[1]}\n'
      f'Make = {azi[3]}\n'
      f'Model = {azi[4]}\n'
      f'Port Count = {azi[5]}\n'
      f'Firmware Version = {azi[6]}')

controller_id = azi[1]


df = pd.read_csv('cm400-input.csv', comment='#')
sp1, sp2, t = df['FHe (sccm)'].tolist(), df['FH2 (sccm)'].tolist(), df['t (min)'] * 60.

print(f'port number 1, {gas_dict[1]} gas, flows (sccm)')
print(sp1)
print(f'gas factor={fact_dict[1]["gas_fact"]:.2f}')
print(f'cal factor={fact_dict[1]["cal_fact"]:.2f}')

print(f'port number 2, {gas_dict[2]} gas, flows (sccm)')
print(sp2)
print(f'gas factor={fact_dict[1]["gas_fact"]:.2f}')
print(f'cal factor={fact_dict[1]["cal_fact"]:.2f}')

cont = input('continue (Y/n)?')

if cont.lower() == 'n':
    raise Exception

log =  open(f'logs/cm400-{datetime.now().timestamp()}.txt', 'w') 
log.write('t,f1 (sccm),f2 (sccm)\n')

for i in range(int(delay / 60.)):
    print(f'minute {i+1:n}/{delay // 60.:n} of delay')
    sleep(60)


for i in range(len(sp1)):
    ti = t[i]
    sp1i = sp1[i]
    sp2i = sp2[i]
    t0 = time()
    print(datetime.now().ctime())
    print(f'start Set Points {gas_dict[1]}={sp1[i]:.2f}sccm, {gas_dict[2]}={sp2[i]:.2f}sccm')
    while time() < t0 + ti:
        print(f'time in loop={(time() - t0)/60.:.1f}min')
        st = ''
        try:
            st += str(t0) + ','
            st += read_set_check(1, sp1i) + ','
            st += read_set_check(2, sp2i)
            log.write(st + '\n')
        except Exception as e:
            print(e)
        sleep(10*time_sep)
    print(f'end Set Points He={sp1[i]:.2f}sccm, H2={sp2[i]:.2f}sccm')

read_set_check(1, 15.0)
read_set_check(2, 0)
print('standby 15 sccm He set')

log.write('#' + str(gas_dict))
log.write('#' + str(fact_dict) + '\n')
log.close()
