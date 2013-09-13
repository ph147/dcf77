#!/usr/bin/python

'''
SAMPLE: Freitag, 13.09.13, 17:26
'''
SAMPLE = '01011001101010100100101100101111010011001010110010110010000'


WEEKDAYS = ('Sonntag', 'Montag', 'Dienstag', 'Mittwoch',
            'Donnerstag', 'Freitag', 'Samstag', 'Sonntag')


def decode(bits):
    assert bits[0] == '0' and bits[20] == '1'
    minutes, hours, day_of_month, weekday, month, year = map(
        convert_block,
        (bits[21:28], bits[29:35], bits[36:42], bits[42:45],
         bits[45:50], bits[50:58])
    )
    print '{dow}, {dom:02}.{mon:02}.{y}, {h:02}:{m:02}'.format(
        h=hours, m=minutes, dow=WEEKDAYS[weekday],
        dom=day_of_month, mon=month, y=year,
    )


def convert_ones(bits):
    return sum(2**i for i, bit in enumerate(bits) if bit == '1')


def convert_tens(bits):
    return 10*convert_ones(bits)


def right_parity(bits, parity_bit):
    num_of_ones = sum(int(bit) for bit in bits)
    return num_of_ones % 2 == int(parity_bit)


class ParityError(Exception):
    pass


def convert_block(bits, parity=False):
    if parity and not right_parity(bits[:-1], bits[-1]):
        raise ParityError
    ones = bits[:4]
    tens = bits[4:]
    return convert_tens(tens) + convert_ones(ones)



def main():
    decode(SAMPLE)


if __name__ == '__main__':
    main()
