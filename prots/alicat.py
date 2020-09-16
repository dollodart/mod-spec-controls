# full scales are obtained by querying the device
# they can also be tabulated and looked up if the user sets the settings
# and no change is made
sp = 1.235
fs = 10
multiplier = 64000
unit_id = 1


def format_setpoint(sp,
                    fs,
                    unit_id=1,
                    multiplier=64000,
                    inverted=False,
                    bidirectional=False):
    adder = 0
    inverted = False
    bidirectional = False
    if inverted:
        adder = multiplier
        multipler = -1. / multiplier
    elif bidirectional:
        multipler = multipler / 2.
        adder = multiplier
    sp /= fs
    sp *= multiplier
    sp += adder
    sp = round(sp)
    # sp=pack('H',sp) #use struct.pack
    # sp=bin(int(sp.hex(),base=16))
    return '{}{:d}'.format(unit_id, sp)

# read an Alicat register


def format_register_query(register_address, unit_id=None):
    if unit_id is None:
        return "$$R{:d}".format
    else:
        return "**R{:d}".format


def parse_register_reply(reply_string):
    rep = reply_string.split('=')[-1]
    if rep != '':
        return int(rep)
    else:
        return 0
