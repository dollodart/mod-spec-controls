import subprocess
import serial
import pandas as pd
from datetime import datetime
from time import sleep, time

t_sep = 0.05  
check_interval = 15
delay = 0.0 * 60

# if you use readlines, you must specify a timeout
timeout = 0.1
#syr1 = serial.Serial('/dev/ttyUSB0', timeout=timeout)
#syr2 = serial.Serial('/dev/ttyUSB1', timeout=timeout)
from virtual import DummySer
syr1 = syr2 = DummySer()

df = pd.read_csv('legato-input.csv', comment='#')
sp1, sp2, times = df['v1 (ul/min)'].tolist(), df['v2 (ul/min)'].tolist(), (df['t (min)'] * 60.).tolist()
ninj = len(df)

print(f'# of injections = {ninj:.0f}')
print('total time = {sum(t) / 3600.:.1f}hr')

print('syringe 1 make and model:')
syr1.write('syrmanu\r'.encode('ascii'))
sleep(t_sep)
for line in syr1.readlines():
    print(line.decode('ascii').lstrip('01:'))

print('syringe 1 flow rates (ul/min)')
print(','.join(str(x) for x in df['v1 (ul/min)']))
print('syringe 1 infusion volume (mL)')
print((df['v1 (ul/min)'] * df['t (min)'] / 1000.).sum())

print('syringe 2 make and model:')
syr2.write('syrmanu\r'.encode('ascii'))
sleep(t_sep)
for line in syr2.readlines():
    print(line.decode('ascii').lstrip('01:'))
print('syringe 2 flow rates (ul/min)')
print(','.join(str(x) for x in df['v2 (ul/min)']))
print('syringe 2 infusion volume (mL)')
print((df['v2 (ul/min)'] * df['t (min)'] / 1000.).sum())


cont = input('continue (Y/n)?')

if cont.lower() == 'n':
    raise Exception("aborting")

log = open(f'logs/legato-{datetime.now().timestamp()}.csv', 'w') 
log.write('t,v1 (ul/min),v2 (ul/min),x1EtOH (%),x1AA (%),x2EtOH (%),x2AA (%)\n')

sleep(t_sep)
syr1.write('dim 100\r'.encode('ascii'))
sleep(t_sep)
syr2.write('dim 100\r'.encode('ascii'))

const = {}
with open('legato-input.csv', 'r') as inputs:
    first_line = inputs.readline()
    first_line = first_line.replace('#', '').replace('%', '').replace('K', '').split(',')
    for item in first_line:
        key, value = item.split('=')
        const[key] = float(value)
print(const)
syr1.write('stp\r'.encode('ascii'))
syr2.write('stp\r'.encode('ascii'))
print(f'start={datetime.now().ctime()}')

for minute in range(int(delay / 60.)):
    print(f'minute {minute + 1:.0f}/{delay / 60.:.0f} of delay')
    sleep(60)


def write_pumps(sp1, sp2, sptime):
    try:
        syr1.write('stp\r'.encode('ascii')); sleep(t_sep)
        syr2.write('stp\r'.encode('ascii')); sleep(t_sep)
        syr1.write('cvolume\r'.encode('ascii')); sleep(t_sep)
        syr2.write('cvolume\r'.encode('ascii')); sleep(t_sep)
        syr1.write('ctvolume\r'.encode('ascii')); sleep(t_sep)
        syr2.write('ctvolume\r'.encode('ascii')); sleep(t_sep)
        syr1.write('ctime\r'.encode('ascii')); sleep(t_sep)
        syr2.write('ctime\r'.encode('ascii')); sleep(t_sep)
        syr1.write('cttime\r'.encode('ascii')); sleep(t_sep)
        syr2.write('cttime\r'.encode('ascii')); sleep(t_sep)
        syr1.write(f'tvolume {sp1*sptime/60.:.1f} ul\r'.encode('ascii')); sleep(t_sep)
        syr2.write(f'tvolume {sp2*sptime/60.:.1f} ul\r'.encode('ascii')); sleep(t_sep)
        syr1.write(f'irate {sp1} ul/min\r'.encode('ascii')); sleep(t_sep)
        syr2.write(f'irate {sp2} ul/min\r'.encode('ascii')); sleep(t_sep)
        syr1.write('run\r'.encode('ascii')); sleep(t_sep)
        syr2.write('run\r'.encode('ascii'))
        return True
    except Exception as e:
        print(e)


t00 = time()

for i in range(ninj):
    ts = times[i]
    write_pumps(sp1[i], sp2[i], ts)
    print(f'datetime = {datetime.now().ctime()}',
          f'time set={ts:.2f}sec',
          f'pump1={sp1[i]:.2f}ul/min',
          f'pump2={sp2[i]:.2f}ul/min', sep=' ')
    log.write(f'{time()},'
              f'{sp1[i]:.8f},'
              f'{sp2[i]:.8f},'
              f'{const["x1EtOH"]:.8f},'
              f'{const["x1AA"]:.8f},'
              f'{const["x2EtOH"]:.8f},'
              f'{const["x2AA"]:.8f}')

    sleep(ts)

# the following loop could be used to read the value and ensure it works (since there is no checksum)
# however I haven't found it to be necessary for the ACM device, which may implicitly evaluate checksums

#    t0 = time()
#    while time() < t0 + ts:
#        syr1.readlines()
#        syr1.write('irate\r'.encode('ascii'))
#        lines = syr1.readlines()
#        val1 = -1
#        val2 = -1
#        for line in lines:
#            line = line.decode('ascii')
#            line = line.replace('01:', '')
#            line = line.replace('02:', '')
#            if 'ul/min' in line:
#                try:
#                    val1 = float(line.split(' ')[0])
#                except Exception as e:
#                    print(e)
#        syr2.readlines()
#        syr2.write('irate\r'.encode('ascii'))
#        lines = syr2.readlines()
#        for line in lines:
#            line = line.decode('ascii')
#            line = line.replace('01:', '')
#            line = line.replace('02:', '')
#            if 'ul/min' in line:
#                try:
#                    val2 = float(line.split(' ')[0])
#                except Exception as e:
#                    print(e)
#        with open('log.txt', 'a') as log:
#            log.write(
#                '{0:.8f},{1:.8f},{2:.8f},{3:.8f},{4:.8f},{5:.8f},{6:.8f}\n'.format(
#                    time(),
#                    val1,
#                    val2,
#                    const['x1EtOH'],
#                    const['x1AA'],
#                    const['x2EtOH'],
#                    const['x2AA']))
#        sleep(check_interval)

syr1.write('stp\r'.encode('ascii')); sleep(t_sep)
syr2.write('stp\r'.encode('ascii'))
print('stop={datetime.now().ctime()}')
log.close()
