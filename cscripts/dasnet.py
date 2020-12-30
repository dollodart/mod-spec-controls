"""
The DASNET protocol, from Teledyne for controlling their ISCO series pumps, has the following fields:

destination|acknowledgement|message source|length|message|checksum|[CR]

destination is the 1-digit uin of the receiving instrument
acknowledgement is indication of succes of previous transmission. E=Error, B=Busy, R=received
message source is the UIN of the issueing instrument
length is the length of the message in 2 digit hexadecimal
message field is the information
checksum is a 2 digit hexadecimal which added to all other characters except control characters should sum to a factor of 256

All characters are converted to the ASCII equivalent and added, checksum is ascii-encoded as well.

User input: UNICODE 8-bit characters
Conversion 1: UNICODE 8-bit characters to ASCII 7-bit (gratis, since the first 127 characters of ASCII are that of unicode)
Conversion 2: ASCII to hex (only for arithmetic)
Sum all hex, add to end of ASCII frame as ascii-encoded number.

"""


def dasnet_checksum(s):
    """Ensures the checksum of the total message (ascii-encoding, excluding control characters) is modulo 256."""
    sm = sum([ord(x) for x in s])
    remd = sm % 256
    rremd = 256 - remd
    remh = '{0:x}'.format(rremd).upper()
    return remh


def dasnet_encode(spec):
    s = ''.join(spec)
    checksum = dasnet_checksum(s)
    s = '\r' + s + checksum + '\r'
    return s.encode('ascii')

if __name__ == '__main__':
    message_field = 'STOP'
    spec = ('1',  # destination
            'R',  # acknowledgement
            '3',  # message source
            '{0:02X}'.format(len(message_field)),  # length
            message_field  # message field
            )

    m = dasnet_encode(spec)
    print(repr(m))

    message_field = 'IDENTIFY'
    spec = ('6',  # destination
            'R',  # acknowledgement
            '0',  # message source
            '{0:02X}'.format(len(message_field)),  # length
            message_field # message field
            )
    m = dasnet_encode(spec)
    print(repr(m))

    message_field = 'CONST FLOW'
    spec = ('6',  # destination
            'R',  # acknowledgement
            '0',  # message source
            '{0:02X}'.format(len(message_field)),  # length
            message_field # message field
            )
    m = dasnet_encode(spec)
    print(repr(m))

    message_field = 'RUN'
    spec = ('6',  # destination
            'R',  # acknowledgement
            '0',  # message source
            '{0:02X}'.format(len(message_field)),  # length
            message_field # message field
            )

    m = dasnet_encode(spec)
    print(repr(m))
