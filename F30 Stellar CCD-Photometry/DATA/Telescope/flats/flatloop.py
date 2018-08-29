#!/usr/bin/python

import numpy as np
import os
import time

fileName = "flat_I"
obsNames = "Mathieu_Quirinus"
timex = 0.3

for i in range(5):
    os.system('ccdread -C 0 -b 2 -g 5 -T -F {fileName} -e {expTime} -o {fileName}{expTime} -u {obsNames} -O -C 1'.format(fileName=fileName, expTime=str(timex), obsNames=obsNames))
    print "Preparing for next image - don't interrupt now!"

