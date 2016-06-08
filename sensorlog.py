#!/usr/bin/env python

import sys
import argparse
import spidev
import opc
import time
import threading
import signal
import datetime

opc_cols = ['Bin {0}'.format(i) for i in range(0,16)]
opc_cols.extend(['Bin{0} MToF'.format(i) for i in range(1,2,8)])
opc_cols.extend(['PM1', 'PM10', 'PM2.5', 'SFR', 'Sampling Period'])

def usage():
    print('{0} [OPTIONS]'.format(__file__))

class StoppableThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self._stopevent = threading.Event()

    def stop(self):
        self._stopevent.set()

class OPC_Thread(StoppableThread):
    def __init__(self, period, logfile, verbose):
        super().__init__()
        self.period = period
        self.logfile = logfile
        self.verbose = verbose

        print('Logging to {0} every {1} seconds'.format(self.logfile, self.period))

        spi = spidev.SpiDev()
        spi.open(0, 0)
        spi.mode = 1
        spi.max_speed_hz = 500000

        self.alphasense = opc.OPCN2(spi)

        # Turn the opc ON
        self.alphasense.on()

    def logreading(self, append=True):
        hist = self.alphasense.histogram()

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
    parser = argparse.ArgumentParser(description='Log OPC readings to a csv file.')
    parser.add_argument('-l', metavar='logfile', default='opc-log.csv')
    parser.add_argument('-t', metavar='period', type=int, default=20)
    parser.add_argument('-v', action='store_true', help='print logged data to stdout')

    args = parser.parse_args()
    opcthread = OPC_Thread(args.t, args.l, args.v)

    try:
        opcthread.start()
        signal.pause()
    except KeyboardInterrupt:
        print('\nExiting...')
        opcthread.stop()
        opcthread.join()
        sys.exit(0)

if __name__ == "__main__":
    main()
