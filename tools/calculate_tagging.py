# coding=utf-8

import os
import sys
import pandas as pd
from datetime import datetime
import time
import fnmatch
import json
import math
from tools.read_and_write_json import loadTag,saveTag

def getAllDataDir(input_data_path):
    "get all dir in data"
    file_list=[]
    for file in os.listdir(input_data_path):
        dir_file = os.path.join(input_data_path, file)

        if (os.path.isdir(dir_file)):
            h = os.path.split(dir_file)
            file_list.append(h[1])
    return file_list

if __name__ == '__main__':

    dir_path =  "/media/sensetime/FieldTest/data/pipeline_test_ARH/"
    file_list = getAllDataDir(dir_path)
    tag_list = {}
    for file_path in file_list:
        # if not os.path.exists(dir_path+file_path+'/data-tag.json'):
        #     continue
        # case_json = loadTag(dir_path+file_path+'/screen_cast/','case_finder.json')
        # if case_json =={} or case_json ==[]:
        #     continue
        # print(file_path)
        # case_json = case_json[0]
        # print(case_json)
        # for ego_tag in case_json["ego_tags"]:
        #     if not ego_tag in tag_list.keys():
        #         tag_list[ego_tag] =0
        #     tag_list[ego_tag] +=1
        tprofile =  "bash ~/tprofiler/resolve_everything.bash "
        input_path = dir_path+file_path
        output_path = dir_path+file_path+'/tprofile_result'
        os.system(tprofile+input_path+' '+output_path)


    #     data_tag = loadTag(dir_path+file_path,'/data-tag.json')
    #     if data_tag =={}:
    #         continue
    #     if "backup" in data_tag.keys():
    #         data_tag = data_tag["backup"][0]["data_tag"]
    #
    #
    #     test_time = data_tag["origin_record_tag"][0]["start_format"]
    #     aa=data_tag["origin_record_tag"][0]["modules"]
    #     if aa==[]:
    #         module="FT"
    #     else:
    #         module= aa[0]
    #     test_time_h = test_time.split(":",-1)[0]
    #     print(module)
    #     if int(test_time_h)>9 and int(test_time_h)<18:
    #         if not module+"day" in tag_list.keys():
    #             tag_list[module+"day"] =0
    #         tag_list[module + "day"] +=1
    #     else:
    #         if not module+"night" in tag_list.keys():
    #             tag_list[module+"night"] =0
    #         tag_list[module + "night"] += 1
    # saveTag("/media/sensetime/FieldTest",tag_list,"/tag_list1.json")





