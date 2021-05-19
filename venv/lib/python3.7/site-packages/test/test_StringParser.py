#!/usr/bin/env python
# Software License Agreement (GNU GPLv3  License)
#
# Copyright (c) 2020, Roland Jung (roland.jung@aau.at) , AAU, KPK, NAV
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
import unittest
import time
import csv
from cnspy_csv2dataframe.TimestampCSV2DataFrame import TimestampCSV2DataFrame
from cnspy_script_utils.string_parser import *

class StringParser_Test(unittest.TestCase):
    def test_string_to_list(self):
        name = 'ATTR_12_LVL_2_RUN_4_EST_5.bag'
        p = 'ATTR_{0}_LVL_{1}_RUN_{2}_EST_{3}.bag'
        l = string_to_list(string=name, pattern=p)
        print('got: ' + str(l))

        self.assertTrue(l[0] == '12')
        self.assertTrue(l[1] == '2')
        self.assertTrue(l[2] == '4')
        self.assertTrue(l[3] == '5')

    def test_string_to_dict(self):
        p = 'ATTR_{attrnum}_LVL_{lvlnum}_RUN_{runnum}_EST_{estnum}.bag'
        s = p.format(attrnum=1, lvlnum=2, runnum=3, estnum=4)
        d = string_to_dict(string=s, pattern=p)

        print('got: ' + str(d), ' for: [' + s + ']')
        self.assertTrue(d['attrnum'] == '1')


if __name__ == "__main__":
    unittest.main()
