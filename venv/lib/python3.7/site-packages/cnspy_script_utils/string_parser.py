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
import re


def string_to_list(string, pattern):
    """
    parsing a string for a specific patter
    example:
    p = 'ATTR_{0}_LVL_{1}_RUN_{2}_EST_{3}.bag'
    s = 'ATTR_12_LVL_2_RUN_4_EST_5.bag'
    res = string_to_list(string=s, pattern=p)  # ['12', '2', '4', '5']

    Input:
    string -- string
    patter -- string, containing {0...N} place holders

    Output:
    res   -- list,  containing N elements
    """
    regex = re.sub(r'{(.+?)}', r'(?P<_\1>.+)', pattern)
    res = re.search(regex, string)
    if res is None:
        return []
    return list(res.groups())


#
def string_to_dict(string, pattern):
    """
    parsing a string for a specific patter
    reference:
    * https://stackoverflow.com/a/36838374,
    * answered by: https://stackoverflow.com/users/698289/danh

    example:
    p = 'ATTR_{attrnum}_LVL_{lvlnum}_RUN_{runnum}_EST_{estnum}.bag'
    s = 'ATTR_12_LVL_2_RUN_4_EST_5.bag'
    res = string_to_dict(string=s, pattern=p)  # {'attrnum': '1', 'runnum': '3', 'estnum': '4', 'lvlnum': '2'}

    Input:
    string -- string
    patter -- string, containing {0...N} place holders

    Output:
    res   -- dict,  containing N tuples
    """

    regex = re.sub(r'{(.+?)}', r'(?P<_\1>.+)', pattern)
    values = list(re.search(regex, string).groups())
    keys = re.findall(r'{(.+?)}', pattern)
    _dict = dict(zip(keys, values))
    return _dict


