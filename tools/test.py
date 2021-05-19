# coding=utf-8

import os
import sys
import json
import fnmatch
from read_and_write_json import loadTag,saveTag


def getMatchedFilePaths(dir_path, pattern="*", formats=[".json"], recursive=False):
    "get all the files in <dir_path> with specified pattern"
    files = []
    data_dir = os.path.normpath(os.path.abspath(dir_path))
    #try:
    for f in os.listdir(data_dir):
        current_path = os.path.join(os.path.normpath(data_dir), f)
        if os.path.isdir(current_path) and recursive:
            files += getMatchedFilePaths(current_path, pattern, formats,
                                              recursive)
        elif fnmatch.fnmatch(f,
                             pattern) and os.path.splitext(f)[-1] in formats:
            files.append(current_path)
    return files
    # except OSError:
    #     print("path error")
    #     return []



def main():
    statics_result ={"test_duration":0,
                     "test_mileage":0,
                     'route':{

                     },
                     "record_tag":{
                     }}
    vnumber = {
        "fewer_objects":0,
        "normal_objects":0,
        "many_objects":0
    }
    dir_path = "/media/sensetime/FieldTest1/data/04_02_CN-009_ARH/"
    tag_list = getMatchedFilePaths(dir_path,'module_*','.json',True)

    print(len(tag_list))
    result_list = {}
    i = 0
    for tag_path in tag_list:
        tag_data = loadTag(tag_path,'')
        if tag_data is None:
            continue

        for cpu_core in tag_data["module_eval"]:
            if cpu_core not in result_list:
                result_list[cpu_core]= {}
                result_list[cpu_core]["stddev_frame_rate"] =0
                result_list[cpu_core]["avg_frame_rate"] = 0
            if tag_data["module_eval"][cpu_core]["stddev_frame_rate"] is not None and \
                    tag_data["module_eval"][cpu_core]["avg_frame_rate"] is not None:
                result_list[cpu_core]["stddev_frame_rate"] = \
                    result_list[cpu_core]["stddev_frame_rate"]+tag_data["module_eval"][cpu_core]["stddev_frame_rate"]
                result_list[cpu_core]["avg_frame_rate"] = \
                    result_list[cpu_core]["avg_frame_rate"] + tag_data["module_eval"][cpu_core]["avg_frame_rate"]


        # if "test_duration" in tag_data.keys():
        #     statics_result["test_duration"]+=tag_data["test_duration"]
        # if "test_mileage" in tag_data.keys() and tag_data["test_mileage"]>0 and tag_data["test_mileage"]<200:
        #     statics_result["test_mileage"]+=tag_data["test_mileage"]
        # if "origin_record_tag" in tag_data.keys() and tag_data["origin_record_tag"] != []:
        #     for record_tag in tag_data["origin_record_tag"]:
        #         if not record_tag["tag_en"] in statics_result["record_tag"].keys():
        #             statics_result["record_tag"][record_tag["tag_en"]] = 0
        #         statics_result["record_tag"][record_tag["tag_en"]] +=1
        # if 'route' in tag_data.keys():
        #     if tag_data['route'] not in statics_result["route"]:
        #         statics_result["route"][tag_data['route']] =0
        #     statics_result["route"][tag_data['route']] += 1

        i+=1
        print(i)
    for core in result_list:
        result_list[core]["avg_frame_rate"] =  result_list[core]["avg_frame_rate"]/5
        result_list[core]["stddev_frame_rate"] = result_list[core]["stddev_frame_rate"] / 5
    saveTag(dir_path,result_list,'result.json')
        # if "global_tag" in tag_data.keys():
        #     for tag in tag_data["global_tag"]:
        #         if tag in ["fewer_objects","normal_objects","many_objects"]:
        #             vnumber[tag] +=1


    # with open('/media/sensetime/FieldTest1/data/result.txt', 'w') as fw:
    #     for path in result_list:
    #         fw.write(path + '\n')




    saveTag(dir_path,vnumber,'statics_result_12.json')

if __name__ == '__main__':
    main()