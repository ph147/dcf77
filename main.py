#!/usr/bin/python

from decode import decode
from reader import DCF77


'''
$ pacat --record | python main.py
'''

FILE = 'dcf77-17-25.raw'


def main():
    reader = DCF77(FILE)
    for minute in reader.run():
        decode(minute)


if __name__ == '__main__':
    main()
