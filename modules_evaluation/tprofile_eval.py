# coding=utf-8

import os
import json
import sys
import fnmatch
from tools.read_and_write_json import loadTag,saveTag

def moduleProfileParse(dir_path,tprofile_name,tprofile_case,result):
    case_json = loadTag(os.path.join(dir_path,'tprofile_result'),tprofile_name)
    if case_json is None or case_json ==[]:
        return tprofile_case,result
    for case in case_json:
        if not case in tprofile_case:
            tprofile_case.append(case)
        if "modules" in case.keys():
            for module in case["modules"]:
                if not module in result.keys():
                    result[module] = 0
                result[module] += 1
    return tprofile_case,result


def labelAdd(dir_path, profile_label,label_name):
    labels = loadTag(os.path.join(dir_path,'tprofile_result'),label_name)
    return dict(profile_label, **labels)



def main(dir_path):
    tprofile_case = []
    result = {}
    tprofile_result = []
    profile_label = {}
    #try:
    tprofile_case,result = moduleProfileParse(dir_path,'module_tprofile_case.json',tprofile_case,result)
    tprofile_case, result = moduleProfileParse(dir_path, 'sensor_tprofile_case.json', tprofile_case, result)
    tprofile_case, result = moduleProfileParse(dir_path, 'cpu_usage/cpu_tprofile_case.json', tprofile_case, result)
    profile_label = labelAdd(dir_path,profile_label,'tprofile_result.json')
    profile_label = labelAdd(dir_path, profile_label, 'cpu_usage/tprofile_result.json')

    saveTag(os.path.join(dir_path,'screen_cast'),tprofile_case,'tprofile_result.json')
    # except Exception as e:
    #     print("tprofile_eval error")
    for module in result.keys():
        if result[module] > 2:
            tprofile_result.append(module+'_tprofile_abnormal')
    return profile_label,tprofile_result,tprofile_case


if __name__ == '__main__':
    dir_path = "/media/sensetime/FieldTest/data/tprofile/2020_09_11_10_23_13_AutoCollect/"
    main(dir_path)