#!/usr/bin/python

import sys
import struct

EPSILON = 0.02

SAMPLE_RATE = 44100

ZERO_BIT_IN_SECS = 0.1
ONE_BIT_IN_SECS = 0.2

NEW_MINUTE_BEEP_THRESHOLD = 1.7


def read_word(inf):
    return struct.unpack('<l', inf.read(struct.calcsize('=l')))[0]


def read_words(inf):
    word = read_word(inf)
    while True:
        yield word
        word = read_word(inf)


def average(words, num):
    try:
        return 1.0*sum(abs(next(words)) for i in xrange(num))/num
    except struct.error:
        raise EOF


def sgn(num):
    return -1 if num < 0 else 1 if num > 0 else 0


def steps(length):
    count = 0
    while True:
        yield count
        count += length


def in_vicinity(num, center):
    return abs(num-center) < EPSILON


class SignalError(Exception):
    pass


class EOF(Exception):
    pass


class DCF77(object):
    amplitude_factor = 0.3
    block_length = 100

    def __init__(self, filename=None):
        if not filename:
            print 'Reading from stdin...'
            filename = '/dev/stdin'
        else:
            print 'Reading from file {}...'.format(filename)
        self.filename = filename
        self.lasts = [0]*3
        self.data = True
        self.bits = []
        self.start = 0
        self.end = 0
        self.minute_started = False

    def went_down(self, ave):
        return ave < self.amplitude_factor*self.lasts[0] and not self.data

    def went_up(self, ave):
        return self.lasts[0] < self.amplitude_factor*ave and self.data

    def start_new_minute(self):
        print
        if self.minute_started:
            yield ''.join(self.bits)
            self.bits = []
        self.minute_started = True
        print '*** New minute started. ***'

    def process_carrier(self, step):
        self.start = step
        time = 1.0*(self.start-self.end)/SAMPLE_RATE
        if time > NEW_MINUTE_BEEP_THRESHOLD:
            for answer in self.start_new_minute():
                yield answer
        self.data = True

    def append(self, bit):
        self.bits.append(bit)
        sys.stdout.write(bit)

    def process_bit(self, time):
        if in_vicinity(time, ZERO_BIT_IN_SECS):
            self.append('0')
        elif in_vicinity(time, ONE_BIT_IN_SECS):
            self.append('1')
        else:
            raise SignalError

    def process_silence(self, step):
        self.end = step
        time = 1.0*(self.end-self.start)/SAMPLE_RATE
        if self.minute_started:
            self.process_bit(time)
            sys.stdout.flush()
        self.data = False

    def process_block(self, block, step):
        if self.went_down(block):
            for answer in self.process_carrier(step):
                yield answer
        elif self.went_up(block):
            self.process_silence(step)
        self.lasts.pop(0)
        self.lasts.append(block)

    def run(self):
        with open(self.filename) as inf:
            words = read_words(inf)
            for step in steps(self.block_length):
                ave = average(words, self.block_length)
                for answer in self.process_block(ave, step):
                    yield answer
