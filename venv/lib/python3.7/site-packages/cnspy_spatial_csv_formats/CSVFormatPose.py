#!/usr/bin/env python
# Software License Agreement (GNU GPLv3  License)
#
# Copyright (c) 2020, Roland Jung (roland.jung@aau.at) , AAU, KPK, NAV
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
########################################################################################################################
import os
import cnspy_spatial_csv_formats.PoseStructs as ps
from enum import Enum


class CSVFormatPose(Enum):
    Timestamp = 'Timestamp'
    TUM = 'TUM'  # TUM-Format stems from: https://vision.in.tum.de/data/datasets/rgbd-dataset/tools#evaluation
    PositionStamped = 'PositionStamped'
    PoseCov = 'PoseCov'
    PoseWithCov = 'PoseWithCov'
    none = 'none'

    # HINT: if you add an entry here, please also add it to the .list() method!

    def __str__(self):
        return self.value

    @staticmethod
    def list():
        return list([str(CSVFormatPose.Timestamp), str(CSVFormatPose.TUM), str(CSVFormatPose.PositionStamped),
                     str(CSVFormatPose.PoseCov),
                     str(CSVFormatPose.PoseWithCov),
                     str(CSVFormatPose.none)])

    @staticmethod
    def get_header(fmt):
        if str(fmt) == 'Timestamp':
            return ['#t']
        elif str(fmt) == 'TUM':
            return ['#t', 'tx', 'ty', 'tz', 'qx', 'qy', 'qz', 'qw']
        elif str(fmt) == 'PositionStamped':
            return ['#t', 'tx', 'ty', 'tz']
        elif str(fmt) == 'PoseCov':
            return ['#t', 'pxx', 'pxy', 'pxz', 'pyy', 'pyz', 'pzz', 'qrr', 'qrp', 'qry', 'qpp', 'qpy', 'qyy']
        elif str(fmt) == 'PoseWithCov':
            return ['#t', 'tx', 'ty', 'tz', 'qx', 'qy', 'qz', 'qw', 'pxx', 'pxy', 'pxz', 'pyy', 'pyz', 'pzz', 'qrr',
                    'qrp', 'qry', 'qpp', 'qpy', 'qyy']

        else:
            return ["# no header "]

    @staticmethod
    def get_format(fmt):
        if str(fmt) == 'Timestamp':
            return ['t']
        elif str(fmt) == 'TUM':
            return ['t', 'tx', 'ty', 'tz', 'qx', 'qy', 'qz', 'qw']
        elif str(fmt) == 'PositionStamped':
            return ['t', 'tx', 'ty', 'tz']
        elif str(fmt) == 'PoseCov':
            return ['t', 'pxx', 'pxy', 'pxz', 'pyy', 'pyz', 'pzz', 'qrr', 'qrp', 'qry', 'qpp', 'qpy', 'qyy']
        elif str(fmt) == 'PoseWithCov':
            return ['t', 'tx', 'ty', 'tz', 'qx', 'qy', 'qz', 'qw', 'pxx', 'pxy', 'pxz', 'pyy', 'pyz', 'pzz', 'qrr',
                    'qrp', 'qry', 'qpp', 'qpy', 'qyy']
        else:
            return ['no format']

    @staticmethod
    def get_num_elem(fmt):

        if str(fmt) == 'Timestamp':
            return 1
        elif str(fmt) == 'TUM':
            return 8
        elif str(fmt) == 'PositionStamped':
            return 4
        elif str(fmt) == 'PoseCov':
            return 13
        elif str(fmt) == 'PoseWithCov':
            return 20
        else:
            return None

    @staticmethod
    def parse(line, fmt):
        elems = line.split(",")
        if str(fmt) == 'Timestamp' or len(elems) == 1:
            return ps.sTimestamp(vec=[float(x) for x in elems[0:1]])
        elif str(fmt) == 'TUM' or len(elems) == 8:
            return ps.sTUMPoseStamped(vec=[float(x) for x in elems[0:8]])
        elif str(fmt) == 'PositionStamped' or len(elems) == 4:
            return ps.sPositionStamped(vec=[float(x) for x in elems[0:4]])
        elif str(fmt) == 'PoseCov' or len(elems) == 13:
            return ps.sPoseCovStamped(vec=[float(x) for x in elems[0:13]])
        elif str(fmt) == 'PoseWithCov' or len(elems) == 20:
            return ps.sTUMPoseWithCovStamped(vec=[float(x) for x in elems])
        else:
            return None

    @staticmethod
    def identify_format(fn):
        if os.path.exists(fn):
            with open(fn, "r") as file:
                header = str(file.readline()).rstrip("\n\r")
                for fmt in CSVFormatPose.list():
                    h_ = ",".join(CSVFormatPose.get_header(fmt))
                    if h_.replace(" ", "") == header.replace(" ", ""):
                        return CSVFormatPose(fmt)
                print("CSVFormatPose.identify_format(): Header unknown!\n\t[" + str(header) + "]")
        else:
            print("CSVFormatPose.identify_format(): File not found!\n\t[" + str(fn) + "]")
        return CSVFormatPose.none


