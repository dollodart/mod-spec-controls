"""
Checksum for the CM400.

Using operations on binary string representations of numbers is much
less efficient than bitwise operators on the numbers (which are of
course binary in the memory). It turns out to not matter in this
application.

"""

def ascii_sum(string):
    return sum([ord(x) for x in string])


def negate(x):
    y = ''
    for i in x:
        if i == '0':
            y += '1'
        else:
            y += '0'
    return y


def bin_add(x):
    l = len(x)

    if x[-1] == '0':
        return ''.join(x[:-1]) + '1'

    for c in range(l):
        i = l - c - 1
        if x[i] == '0':
            return ''.join(x[:i]) + '1' + '0' * c

    return '1' + '0' * l


def two_complement(b):
    return bin_add(negate(b))


def checksum(response):
    cs = response[-2:]
    r = response[2:-2]
    s = ascii_sum(r)
    # efficiently:
    # tc = ~s + 1
    # tc %= 256
    # if tc == int(cs, base=16):
    #     return True
    # return False
    b = bin(s)
    tc = two_complement(b)
    tc_hex = hex(int(tc, base=2))
    # take the modulus w.r.t. 256 = take the last two digits of hex representation 
    # since 16^2 = 256
    tc_hex = tc_hex[-2:]
    tc_hex = int(tc_hex, base=16)
    cs = int(cs, base=16)
    if tc_hex == cs:
        return True
    return False
