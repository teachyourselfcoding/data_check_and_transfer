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

def case_finder(input_path,output_path,module_id = 2,object_id=0,input_timestamp=123,input_nsec=123,before_secs=5,after_seconds=1):
    senseauto_path = "~/ws/repo_pro/senseauto"
    case_finder_path = os.path.join(senseauto_path,
                                    'build/modules/simulator/tools/scenario_log_tools/case_finder')
    case_finder_cmd = "{} {} {} {} {} {} {} {} {}".format(
        case_finder_path,
        input_path,
        os.path.join(output_path, 'case_finder.json'),
        str(module_id),
        str(object_id),
        str(input_timestamp),
        str(input_nsec),
        str(before_secs),
        str(after_seconds))
    print case_finder_cmd,'\n'
    os.system(case_finder_cmd)

def getAllDataDir(input_data_path):
    "get all dir in data"
    file_list=[]
    for file in os.listdir(input_data_path):
        dir_file = os.path.join(input_data_path, file)

        if (os.path.isdir(dir_file)):
            h = os.path.split(dir_file)
            file_list.append(h[1])
    return file_list

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
    dir_path = "/media/sensetime/FieldTest2/aaa/"
    tag_list = getAllDataDir(dir_path)

    print(len(tag_list))
    i = 0
    result_list = []
    for tag_path in tag_list:
        # tag_data = loadTag(tag_path,'')
        # if tag_data is None:
        #     continue
        tag_path= os.path.join(dir_path,tag_path)
        bin_path =  os.path.join(tag_path,'simulator_scenario/simulator_scenario_log.bin')
        try:
            case_finder(bin_path, tag_path, 0)
        except:
            continue
        object_number = getObjectNumber(tag_path)
        if object_number !=0 and object_number != []:
            result_list+=object_number

        # if "backup" in tag_data.keys():
        #     tag_data = tag_data["backup"][0]["data_tag"]
        #     tag_data["test_date"] = tag_data["test_date"].replace('-', '_')
        #
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
        # i+=1
        # print(i)
    result_list = sorted(result_list,reverse = True)
    print(result_list)
    statics_result["object_number"] = result_list
    #statics_result["object_size"] = sum(result_list)/len(result_list)
    saveTag(dir_path,statics_result,'result.json')


def getObjectNumber(dir_path):

    object_count = loadTag(dir_path, 'object_count.json')
    number = []
    try:
        for count in object_count["Object_number"]:
            for a in count:
                number.append(count[a])
        #object_size = number / len(object_count["Object_number"])
    except:
        return 0

    # if object_size < 800:
    #     tag_info['global_tag'].append("fewer_objects")
    # elif object_size > 800 and object_size < 1800:
    #     tag_info['global_tag'].append("normal_objects")
    # elif object_size > 1800:
    #     tag_info['global_tag'].append("many_objects")
    return number


    saveTag(dir_path,vnumber,'statics_result_12.json')

if __name__ == '__main__':
    main()