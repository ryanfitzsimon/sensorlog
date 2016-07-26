#!/usr/bin/env python

import sys
import argparse
import spidev
import opc
import time
import threading
import signal
import datetime
import smbus
import serial

opc_cols = ['Bin {0}'.format(i) for i in range(0, 16)]
opc_cols.extend(['Bin{0} MToF'.format(i) for i in range(1, 2, 8)])
opc_cols.extend(['PM1', 'PM10', 'PM2.5', 'SFR', 'Sampling Period'])

I2C_ADDR = 0x1e


class StoppableThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self._stopevent = threading.Event()

    def stop(self):
        self._stopevent.set()


class Log_Thread(StoppableThread):
    def __init__(self, period, logfile, verbose):
        super().__init__()
        self.period = period
        self.logfile = logfile
        self.verbose = verbose

        print('Logging to {0} every {1} seconds'
              .format(self.logfile, self.period))

        spi = spidev.SpiDev()
        spi.open(0, 0)
        spi.mode = 1
        spi.max_speed_hz = 500000

        self.mag = smbus.SMBus(1)
        self.gps = serial.Serial('/dev/ttyAMA0', timeout=0)
        self.alphasense = opc.OPCN2(spi)

        # Turn the opc ON
        self.alphasense.on()

    def logreading(self, append=True):
        hist = self.alphasense.histogram()

        # Compass Read Example
#        print(self.mag.read_byte_data(I2C_ADDR, 1))

        # GPS Read Example
#        print(self.gps.read(1))

        if append:
            f = open(self.logfile, 'a')
        else:
            f = open(self.logfile, 'w')
            cols = ['Time']
            cols.extend(opc_cols)
            if self.verbose:
                print(','.join(cols))
            f.write(','.join(cols) + '\n')

        vals = [str(datetime.datetime.now())]
        vals.extend([str(hist[k]) for k in opc_cols])

        if self.verbose:
            print(','.join(vals))
        f.write(','.join(vals) + '\n')
        f.close()

    def run(self):
        time.sleep(1)

        self.logreading(False)

        i = 0
        while(not self._stopevent.isSet()):

            if i == self.period:
                # Reset counter
                i = 0
                self.logreading()

            i = i + 1

            # Sleep for a second
            time.sleep(1)

        # Turn the opc OFF
        self.alphasense.off()
        return


def main():
    parser = argparse.ArgumentParser(
          description='Log OPC readings to csv file.')
    parser.add_argument('-l', metavar='logfile', default='opc-log.csv')
    parser.add_argument('-t', metavar='period', type=int, default=20)
    parser.add_argument('-v', action='store_true',
                        help='print logged data to stdout')

    args = parser.parse_args()
    logthread = Log_Thread(args.t, args.l, args.v)

    try:
        logthread.start()
        signal.pause()
    except KeyboardInterrupt:
        print('\nExiting...')
        logthread.stop()
        logthread.join()
        sys.exit(0)

if __name__ == "__main__":
    main()
