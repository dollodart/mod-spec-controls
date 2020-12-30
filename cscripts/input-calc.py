import numpy as np

# properties
mwAA = 44.0
mwEtOH = 46.1
rhoAA = 0.784
rhoEtOH = 0.789
sccm2mmpm = 1. / 22.4  # sccm to mmol/min

# inputs
total_press = 101.15 # kPa
xH2 = 15. / total_press
x1EtOH = 1. / (1. + 1.)
x2EtOH = 1. / (0. + 1.)
x1AA = 1. - x1EtOH
x2AA = 1. - x2EtOH
xEtOHs = np.array([1.0, 0.27, 0.8, 1.5, 1.0, 2.7, 2.0, 3.5, 1.0]) / total_press
xAAs = np.array([0.27]) / total_press
temps = [503] # K
Ftots = [140.] # sccm

time = 35.
repetitions = 5


log = open('log.csv', 'w')
log.write(f'#x1EtOH={x1EtOH*100:.2f}%'
         f',x2EtOH={x2EtOH*100:.2f}%'
         f',x1AA={x1AA*100:.2f}%'
         f',x2AA={x2AA*100:.3f}%\n')

log.write('t (min),'
         'pEtOH (kPa),'
         'pAA (kPa),'
         'ptot(reac.) (kPa),'
         'pH2 (kPa),'
         'pHe (kPa),'
         'FHe (sccm),'
         'FH2 (sccm),'
         'Ftot (sccm),'
         'v1 (ul/min),'
         'v2 (ul/min),'
         'vtot (ul/min),'
         '1/FAA (1/sccm),'
         'T (K)\n')

mwa = mwEtOH
mwb = mwAA
rhoa = rhoEtOH
rhob = rhoAA
cum_time = 0
counter = 0
inf_vol_1 = 0.
inf_vol_2 = 0.
tot = len(temps) * len(xAAs) * len(xEtOHs) * len(Ftots)

for temp in temps:
    for xAA in xAAs:
        for xEtOH in xEtOHs:
            for Ftot in Ftots:
                if Ftot < 2.7:
                    Ftot /= ((2.7 / total_press) / xEtOH)**0.5
                xa = xEtOH
                xb = xAA
                xa2 = x2EtOH
                xa1 = x1EtOH
                xb2 = x2AA
                xb1 = x1AA

                det = (xa2 * xb1 - xa1 * xb2)
                F1 = 1. / det * (xa2 * xb - xb2 * xa) * Ftot
                F2 = 1. / det * (-xa1 * xb + xb1 * xa) * Ftot
                FH2 = Ftot * xH2
                FHe = Ftot - FH2 - F1 - F2

                F1 *= sccm2mmpm
                F2 *= sccm2mmpm

                vol_flow_1 = F1 * xa1 * mwa / rhoa + F1 * xb1 * mwb / rhob 
                vol_flow_2 = F2 * xa2 * mwa / rhoa + F2 * xb2 * mwb / rhob

                # reverse calculation
                print('reverse calculations')
                print('F1 =? F1prog  F2 =? F2prog')
                F1c = vol_flow_1 / (xa1 * mwa / rhoa + xb1 * mwb / rhob)
                F2c = vol_flow_2 / (xa2 * mwa / rhoa + xb2 * mwb / rhob)
                print(f'{F1:.2f} =? {F1c:.2f}  {F2:.2f} =? {F2c:.2f}')
                F1 /= sccm2mmpm
                F2 /= sccm2mmpm
                xa = (F1 * xa1 + F2 * xa2) / (F1 + F2 + FH2 + FHe)
                xb = (F1 * xb1 + F2 * xb2) / (F1 + F2 + FH2 + FHe)
                print('xEtOH/% =? xEtOH_prog/%  xAA/% =? xAA_prog/%')
                print(f'{100*xa:.2f} =? {100*xEtOH:.2f}  {100*xb:.2f} =? {100*xAA:.2f}')

                row = [time,
                       xEtOH * total_press,
                       xAA * total_press,
                       (xEtOH + xAA) * total_press,
                       xH2 * total_press,
                       FHe / Ftot * total_press,
                       FHe,
                       FH2,
                       Ftot,
                       vol_flow_1,
                       vol_flow_2,
                       vol_flow_1 + vol_flow_2,
                       1 / (xAA * Ftot),
                       temp]

                if counter == 0 or counter == tot:
                    for rep in range(repetitions + 3):
                        print(','.join(f'{x:.3f}' for x in row), file=log)
                        cum_time += time
                        inf_vol_1 += vol_flow_1 * time / 1000.
                        inf_vol_2 += vol_flow_2 * time / 1000.
                else:
                    for rep in range(repetitions):
                        print(','.join(f'{x:.3f}' for x in row), file=log)
                        cum_time += time
                        inf_vol_1 += vol_flow_1 * time / 1000.
                        inf_vol_2 += vol_flow_2 * time / 1000.
                counter += 1

print('#Total Infusion Time = '
      f'{cum_time:.1f}min = {cum_time/60.:.1f}hr',file=log)
print(f'#Infusion Volume 1 = {inf_vol_1:.1f}mL', file=log)
print(f'#Infusion Volume 2 = {inf_vol_2:.1f}mL', file=log)
log.close()
