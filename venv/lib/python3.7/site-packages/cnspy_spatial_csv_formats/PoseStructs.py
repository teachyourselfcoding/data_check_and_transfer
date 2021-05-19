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
# Requirements:
########################################################################################################################


class sTimestamp:
    def __init__(self, vec=None):
        assert (len(vec) == 1)
        self.t = vec[0]


class sTUMPoseStamped:
    def __init__(self, vec=None):
        assert (len(vec) == 8)
        self.t = vec[0]
        self.tx = vec[1]
        self.ty = vec[2]
        self.tz = vec[3]
        self.qx = vec[4]
        self.qy = vec[5]
        self.qz = vec[6]
        self.qw = vec[7]


class sPoseStamped:
    def __init__(self, vec=None):
        assert (len(vec) == 8)
        self.t = vec[0]
        self.tx = vec[1]
        self.ty = vec[2]
        self.tz = vec[3]
        self.qw = vec[4]
        self.qx = vec[5]
        self.qy = vec[6]
        self.qz = vec[7]


class sPositionStamped:
    def __init__(self, vec=None):
        assert (len(vec) == 4)
        self.t = vec[0]
        self.tx = vec[1]
        self.ty = vec[2]
        self.tz = vec[3]


class sPoseCovStamped:
    def __init__(self, vec=None):
        assert (len(vec) == 13)
        self.t = vec[0]
        self.pxx = vec[1]
        self.pxy = vec[2]
        self.pxz = vec[3]
        self.pyy = vec[4]
        self.pyz = vec[5]
        self.pzz = vec[6]
        self.qrr = vec[7]
        self.qrp = vec[8]
        self.qry = vec[9]
        self.qpp = vec[10]
        self.qpy = vec[11]
        self.qyy = vec[12]


class sTUMPoseWithCovStamped:
    def __init__(self, vec=None):
        assert (len(vec) == 20)
        self.t = vec[0]
        self.tx = vec[1]
        self.ty = vec[2]
        self.tz = vec[3]
        self.qx = vec[4]
        self.qy = vec[5]
        self.qz = vec[6]
        self.qw = vec[7]
        self.pxx = vec[8]
        self.pxy = vec[9]
        self.pxz = vec[10]
        self.pyy = vec[11]
        self.pyz = vec[12]
        self.pzz = vec[13]
        self.qrr = vec[14]
        self.qrp = vec[15]
        self.qry = vec[16]
        self.qpp = vec[17]
        self.qpy = vec[18]
        self.qyy = vec[19]


class sPoseWithCovStamped:
    def __init__(self, vec=None):
        assert (len(vec) == 20)
        self.t = vec[0]
        self.tx = vec[1]
        self.ty = vec[2]
        self.tz = vec[3]
        self.qw = vec[4]
        self.qx = vec[5]
        self.qy = vec[6]
        self.qz = vec[7]
        self.pxx = vec[8]
        self.pxy = vec[9]
        self.pxz = vec[10]
        self.pyy = vec[11]
        self.pyz = vec[12]
        self.pzz = vec[13]
        self.qrr = vec[14]
        self.qrp = vec[15]
        self.qry = vec[16]
        self.qpp = vec[17]
        self.qpy = vec[18]
        self.qyy = vec[19]
