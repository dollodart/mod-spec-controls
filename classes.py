from serial import Serial


class Flowcontroller(Serial):
    """

    The super class for all flow controllers.
    Is a subclass of the Serial object, and communications are started by the same __init__ as for Serial.

    """
    # initialization from super class is

    def write_rate(self, value, units):
        if units in self.allowed_units:
            if self.integerQ:
                value = int(round(value * self.multiplier))
            else:
                value = value * self.multiplier
#            print(self.cmd_format(value,units))
            self.write(self.cmd_format(value, units).encode('ascii'))
        else:
            raise Warning(
                "don't support units {} for {}".format(
                    units, self.name))
    # it is best to check set points and throw an error if they are not what
    # is expected

    def check_rate(self):
        pass
    # some pumps may require a flush to be ready for the next write command

    def flush(self):
        [self.write(x.encode('ascii')) for x in self.flush_cmds]


class Legato(Flowcontroller):
    """

    Legato class. Note the legato pump is problematic in that it records
    the volumes to be dispensed and over what time, and does not allow
    a rate only mode. Therefore the various time and volume parameters
    have to be set with with the flush_values command.

    """

    def __init__(self, port=None, baudrate=9600,
                 bytesize=8, parity='N', stopbits=1,
                 timeout=None, xonxoff=False, rtscts=False,
                 write_timeout=None, dsrdtr=False, inter_byte_timeout=None,
                 exclusive=None, address='A'):
        super(Legato, self).__init__(port, baudrate, bytesize,
                                     parity, stopbits, timeout,
                                     xonxoff, rtscts, write_timeout,
                                     dsrdtr, inter_byte_timeout, exclusive)
        self.address = address
        self.cmd_format = "irun {:.2f} {}\r".format
        self.multiplier = 1
        self.allowed_units = ['ul/min']
        self.name = 'legato'
        self.integerQ = False
        # can something like this be done, sending multiple lines to the serial
        # device?
        self.flush_cmds = [
            'stp\r',
            'cvolume\r',
            'ctvolume\r',
            'ctime\r',
            'cttime\r']


class Alicat(Flowcontroller):
    registers = {'flow': 0b00100101, 'pressure': 0b00100010}

    def __init__(self, port=None, baudrate=9600,
                 bytesize=8, parity='N', stopbits=1,
                 timeout=None, xonxoff=False, rtscts=False,
                 write_timeout=None, dsrdtr=False, inter_byte_timeout=None,
                 exclusive=None, address='A'):
        super(Alicat, self).__init__(port, baudrate, bytesize,
                                     parity, stopbits, timeout,
                                     xonxoff, rtscts, write_timeout,
                                     dsrdtr, inter_byte_timeout, exclusive)
        self.address = address
        self.cmd_format = (self.address + "S{:.2f}\r").format
        self.multiplier = 1
        self.allowed_units = ['sccm']
        self.name = 'alicat mfc'
        self.integerQ = False

        self.flush_cmds = []

        # this sets the register to flow mode (setpoints are for flows, not
        # pressure)
        self.register = 74
        self.write(
            '{}W122={:d}\r'.format(
                self.address,
                self.register).encode('ascii'))


class Hplc(Flowcontroller):
    def __init__(self, port=None, baudrate=9600,
                 bytesize=8, parity='N', stopbits=1,
                 timeout=None, xonxoff=False, rtscts=False,
                 write_timeout=None, dsrdtr=False, inter_byte_timeout=None,
                 exclusive=None, address='A'):
        super(Hplc, self).__init__(port, baudrate, bytesize,
                                   parity, stopbits, timeout,
                                   xonxoff, rtscts, write_timeout,
                                   dsrdtr, inter_byte_timeout, exclusive)
        self.address = address
        self.cmd_format = "RU{:03d}\r".format
        self.multiplier = 100
        self.allowed_units = ['ml/min']
        self.name = 'hplc'
        self.integerQ = True

        self.flush_cmds = []
