import pickle
import matplotlib.pyplot as plt
import yaml
import numpy as np

with open("general-settings.yaml", 'r') as read_buffer:
    settings_dct = yaml.load(read_buffer, Loader=yaml.Loader)

with open("user-input.yaml", 'r') as read_buffer:
    dct = yaml.load(read_buffer, Loader=yaml.Loader)
l = []
for key, sd in dct.items():
    l.append([
        int(sd['slave id']),
        float(sd['period']),
        float(sd['setpoint resolution']),
        key,
        sd['units']])

l = sorted(l)
y0 = 0
fig, axs = plt.subplots(nrows=2, ncols=1)
axs[1].set_xlabel("$t-t_0$")
axs[1].set_ylabel("Normalized and offset flow rates")
axs[0].set_ylabel("Flow rates")

# note: plt.update is inefficient, especially since the data is unlikely to change as frequently as the refresh rate
# if necessary, put a condition on plot updating that the data has changed
# between reads
if settings_dct['plot all periods']:
    l1 = []
    l2 = []
    for i in range(settings_dct['number of slaves']):
        with open("comms/m-s{}.pickle".format(i + 1), 'rb') as read_buffer:
            data = pickle.load(read_buffer)
            y = data['setpoints']
            t0 = data['t0']
            dt = data['dt']
            p = l[i][1]
            spr = l[i][2]

            x = np.arange(0, len(y)) * dt
            x += t0
            l1.append(axs[0].plot(
                x, y, label="{} {}".format(l[i][-2], l[i][-1]))[0])
            l2.append(axs[1].plot(x,
                                  (y - y.mean()) / y.max() + 0.1 * (settings_dct['number of slaves'] - i),
                                  label="{} {}".format(l[i][-2],
                                                       l[i][-1]))[0])
    plt.legend()
    while True:
        for i in range(5):
            with open("comms/m-s{}.pickle".format(i + 1), 'rb') as read_buffer:
                data = pickle.load(read_buffer)
            y = data['setpoints']
            t0 = data['t0']
            dt = data['dt']
            p = l[i][1]
            spr = l[i][2]

            x = np.arange(0, len(y)) * dt
            x += t0
            l1[i].set_data(x, y)
            l2[i].set_data(x, (y - y.mean()) / y.max() + 0.1 *
                           (settings_dct['number of slaves'] - i))

        plt.pause(settings_dct['plot refresh time'])
else:
    l1 = []
    l2 = []
    for i in range(settings_dct['number of slaves']):
        with open("comms/m-s{}.pickle".format(i + 1), 'rb') as read_buffer:
            data = pickle.load(read_buffer)
            y = data['setpoints']
            t0 = data['t0']
            dt = data['dt']
            p = l[i][1]
            spr = l[i][2]

            x = np.arange(0, len(y)) * dt
            x += t0
            n = int(p / spr)
            x = x[:n]
            y = y[:n]
            l1.append(axs[0].plot(
                x, y, label="{} {}".format(l[i][-2], l[i][-1]))[0])
            l2.append(axs[1].plot(x,
                                  (y - y.mean()) / y.max() + 0.1 * (settings_dct['number of slaves'] - i),
                                  label="{} {}".format(l[i][-2],
                                                       l[i][-1]))[0])
    plt.legend()
    while True:
        for i in range(5):
            with open("comms/m-s{}.pickle".format(i + 1), 'rb') as read_buffer:
                data = pickle.load(read_buffer)
            y = data['setpoints']
            t0 = data['t0']
            dt = data['dt']
            p = l[i][1]
            spr = l[i][2]

            x = np.arange(0, len(y)) * dt
            x += t0
            n = int(p / spr)
            x = x[:n]
            y = y[:n]
            l1[i].set_data(x, y)
            l2[i].set_data(x, (y - y.mean()) / y.max() + 0.1 *
                           (settings_dct['number of slaves'] - i))

        plt.pause(settings_dct['plot refresh time'])

plt.show()
