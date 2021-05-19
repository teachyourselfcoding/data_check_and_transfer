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
########################################################################################################################
import os


def get_list_of_dir(directory):
    """
    returns a list of folders  within the `directory`

    Input:
    directory -- string

    Output:
    dir_list   -- list
    """

    directory = os.path.abspath(directory)
    l = os.listdir(directory)
    dir_list = []
    for e in l:
        e = os.path.abspath(os.path.join(directory, e))
        if os.path.isdir(e):
            dir_list.append(e)

    return dir_list


def get_list_of_files(directory):
    """
    returns a list of files within the `directory`

    Input:
    directory -- string

    Output:
    file_list   -- list
    """

    directory = os.path.abspath(directory)
    l = os.listdir(directory)
    file_list = []
    for e in l:
        e = os.path.abspath(os.path.join(directory, e))
        if os.path.isfile(e):
            file_list.append(e)

    return file_list


