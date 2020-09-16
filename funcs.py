from classes import *
import numpy as np


def generate_waveform(
        shape,
        amplitude=1,
        offset=1,
        frequency=None,
        phase_shift=0,
        number_samples=1000):
    """

    Return a waveform to the given resolution.
    Doesn't require frequency (returns one period).

    """

    # phase shift is in degrees
    if shape == 'sine':
        func = np.sin
    elif shape == 'square':
        func = my_square
    elif shape == 'sawtooth':
        func = my_sawtooth
    else:
        raise Warning("Don't have waveform {0}".format(shape))
    y = amplitude * func(np.linspace(0., 1., number_samples)
                         * 2. * np.pi) + offset
    #print("phase shift={}".format(phase_shift))
    rc = int(round(phase_shift / 360. * number_samples))
    #print("roll of dependent variable={}".format(rc))
    return np.roll(y, rc)


def my_square(x):
    """

    Unit square wave with zero offset, assumes period 2 pi and returns one period.
    Input: numpy array
    Output: numpy array

    """

    # square this to get rid of the boolean representation
    return (x > np.pi)**2 - 0.5


def my_sawtooth(x):
    """

    Unit sawtooth with zero offset, assumes period 2 pi and returns one period

    Input: numpy array
    Output: numpy array

    """
    x = x[x < np.pi] / np.pi - 0.5
    return np.concatenate((x, x))


def get_waveform(time_start, dct):
    """

    Given a dictionary of the parameters and a time (measured relative
    to some point), returns repetitions of the waveform to be used as
    setpoint buffers (a numpy array) for the slave loops.

    The supplied phase is relative to other pumps. Therefore there is a
    phase correction to the given phase shift to account for the fact
    for set points generated at different times (changing the setpoint buffer after the master script has started).

    Input:
      time_start: time, float
      dct: dictionary of user inputs for the particular pump and its waveform
    Output:
      numpy array of waveform repeated as many periods as necessary for the pump time

    """

    frac_remainder = (time_start % dct['period']) / dct['period']
    frac_remainder *= 360
    phase_shift = int(round((dct['phase'] - frac_remainder))) % 360
    # print(frac_remainder,dct['phase'],phase_shift)
    number_samples = round(dct['period'] / dct['setpoint resolution']) + 1
    wf = generate_waveform(dct['shape'],
                           amplitude=dct['amplitude'],
                           offset=dct['offset'],
                           phase_shift=phase_shift,
                           number_samples=number_samples)
    number_periods = round(dct['pump time'] / dct['period'])
    return np.tile(wf, number_periods)


def find_instrument(typ, port, baud_rate, address):
    """

    A general instrument finding function. Takes a string and returns a
    class instance corresponding to that string. If no class is found,
    returns a dummy instrument.

    """

    if typ == 'hplc':
        return Hplc(port, baud_rate, address=address)
    elif typ == 'mfc':
        return Alicat(port, baud_rate, address=address)
    elif typ == 'legato':
        return Legato(port, baud_rate, address=address)
    else:
        return Instrument(port, baud_rate, address=address)
