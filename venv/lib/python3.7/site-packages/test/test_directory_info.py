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
import os
import unittest
import time
import csv
from cnspy_csv2dataframe.TimestampCSV2DataFrame import TimestampCSV2DataFrame
from cnspy_script_utils.directory_info import *

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_data')


class DirectoryInfo_Test(unittest.TestCase):
    def test_get_list_of_dir(self):
        list = get_list_of_dir(directory=SAMPLE_DATA_DIR)
        self.assertTrue(len(list) == 2)
        print('got: ' + str(list))

    def test_get_list_of_files(self):
        list = get_list_of_files(directory=str(SAMPLE_DATA_DIR + '/dir1/sub_dir1'))
        self.assertTrue(len(list) == 2)
        print('got: ' + str(list))


if __name__ == "__main__":
    unittest.main()
