#!/usr/bin/python

import os
import time

for _ in range(200):
  os.system('ccdread -E 20 -F dark_ -o dark')
  print "Waiting 30s -- abort now with Ctrl-C if you want."
  time.sleep(28)
  print "Preparing for next image - don't interrupt now!"
  time.sleep(2)
