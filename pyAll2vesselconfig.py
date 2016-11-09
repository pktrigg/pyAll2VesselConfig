import sys
sys.path.append("C:/development/Python/pyall")

import argparse
from datetime import datetime
import geodetic
from glob import glob
import math
import numpy as np
import pyall
import time
import os.path
import warnings

# ignore numpy NaN warnings when applying a mask to the images.
warnings.filterwarnings('ignore')

def main():
    parser = argparse.ArgumentParser(description='Read Kongsberg ALL file and create a point cloud file from DXYZ data.')
    parser.add_argument('-i', dest='inputFile', action='store', help='-i <ALLfilename> : input ALL filename to image. It can also be a wildcard, e.g. *.all')

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()

    print ("processing with settings: ", args)
    for filename in glob(args.inputFile):

        r = pyall.ALLReader(filename)
        pingCount = 0
        start_time = time.time() # time the process

        while r.moreData():
            # read a datagram.  If we support it, return the datagram type and aclass for that datagram
            # The user then needs to call the read() method for the class to undertake a fileread and binary decode.  This keeps the read super quick.
            TypeOfDatagram, datagram = r.readDatagram()
            # print("TypeOfDatagram:", TypeOfDatagram)
            # print(r.currentRecordDateTime())

            if TypeOfDatagram == 'I':
                datagram.read()
                #  print ("Lat: %.5f Lon: %.5f" % (datagram.Latitude, datagram.Longitude))

        print("Read Duration: %.3f seconds, InstallationRecordCount %d" % (time.time() - start_time),  InstallationRecordCount) # print the processing time. It is handy to keep an eye on processing performance.

def update_progress(job_title, progress):
    length = 20 # modify this to change the length
    block = int(round(length*progress))
    msg = "\r{0}: [{1}] {2}%".format(job_title, "#"*block + "-"*(length-block), round(progress*100, 2))
    if progress >= 1: msg += " DONE\r\n"
    sys.stdout.write(msg)
    sys.stdout.flush()

if __name__ == "__main__":
    main()

