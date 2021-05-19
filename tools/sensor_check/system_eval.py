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
    statics_result ={}
    vnumber = {
        "fewer_objects":0,
        "normal_objects":0,
        "many_objects":0
    }
    dir_path = "/media/sensetime/FieldTest1/data/04_10_CN-013_ARH/"
    tag_list = getMatchedFilePaths(dir_path,'cpu_resu*','.json',True)

    print(len(tag_list))
    i = 0
    result_list = []
    for tag_path in tag_list:
        i+=1
        tag_data = loadTag(tag_path,'')
        if tag_data is None:
            continue


        if "backup" in tag_data.keys():
            tag_data = tag_data["backup"][0]["data_tag"]
            tag_data["test_date"] = tag_data["test_date"].replace('-', '_')
        print (tag_data)
        for core in tag_data:
            if core not in statics_result:
                statics_result[core]=0
            statics_result[core]+=tag_data[core]

        # for core in tag_data["sensor_eval"]:
        #     if core not in statics_result:
        #         statics_result[core]={}
        #         statics_result[core]["stddev_frame_rate"] = 0
        #         statics_result[core]["avg_frame_rate"] = 0
        #     statics_result[core]["stddev_frame_rate"] += tag_data["sensor_eval"][core]["stddev_frame_rate"]
        #     statics_result[core]["avg_frame_rate"] += tag_data["sensor_eval"][core]["avg_frame_rate"]
        # for core in tag_data["module_eval"]:
        #     if core not in statics_result:
        #         statics_result[core] = {}
        #         statics_result[core]["stddev_frame_rate"] = 0
        #         statics_result[core]["avg_frame_rate"] = 0
        #     statics_result[core]["stddev_frame_rate"] += tag_data["module_eval"][core]["stddev_frame_rate"]
        #     statics_result[core]["avg_frame_rate"] += tag_data["module_eval"][core]["avg_frame_rate"]

        print(i)
    for core in statics_result:
        # statics_result[core]["stddev_frame_rate"] = statics_result[core]["stddev_frame_rate"]/i
        # statics_result[core]["avg_frame_rate"] = statics_result[core]["avg_frame_rate"] / i
        statics_result[core]=statics_result[core]/i
    saveTag(dir_path,statics_result,'result.json')



    saveTag(dir_path,vnumber,'statics_result_12.json')

if __name__ == '__main__':
    main()