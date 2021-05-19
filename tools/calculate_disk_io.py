# coding=utf-8

import os
import sys
import time
import rosbag


def copyTestFile():
    start_time = time.time()
    cmd = ''.join(['cp -r /media/sensetime/FieldTest2/data/12_26_CN-013_ARH/2020_12_26_17_11_35_AutoCollect /media/sensetime/FieldTest1/today/'])
    os.system(cmd)
    time_cost = time.time() - start_time
    print(time_cost)

copyTestFile()