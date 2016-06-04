#!/usr/bin/env python

import sys
import getopt
import spidev
import opc
from time import sleep

def main(argv):
	spi = spidev.SpiDev()
	spi.open(0, 0)
	spi.mode = 1
	spi.max_speed_hz = 500000

	alphasense = opc.OPCN2(spi)

	# Turn the opc ON
	alphasense.on()

	sleep(1)

	# Read the information string
	print (alphasense.read_info_string())

	sleep(10)

	# Read the histogram
	print (alphasense.histogram())

	sleep(1)

	# Turn the opc OFF
	alphasense.off()

if __name__ == "__main__":
	main(sys.argv[1:])
