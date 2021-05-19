
import os
import sys
sys.path.append("..")
from tools.read_and_write_json import loadTag,saveTag

import multiprocessing


from tagging_main_process import TaggingMain
from threadpool import ThreadPool, makeRequests


pool = ThreadPool(int(multiprocessing.cpu_count() * 0.6))
config = loadTag("/home/sensetime/Codes/data_check_and_transfer/config/data_pipeline_config.json","")
auto_module_ = loadTag('/home/sensetime/Codes/data_check_and_transfer/config/auto_module.json', '')
tag_module = loadTag(tag_file_name='/home/sensetime/Codes/data_check_and_transfer/config/tag_module.json')
tag_test = TaggingMain(pool,config,auto_module_,tag_module)


dir_path = "/media/sensetime/FieldTest2/data/04_20_CN-013_ARH/2021_04_20_11_31_09_AutoCollect_slice/DPC/take_over/2021_04_20_10_45_02"
tag = loadTag(dir_path,"data-tag.json")


case_tagging_list = [{"input_dir": dir_path,
                    "module_name": "take_over",
                    "input_timestamp": 1618886702,
                    "tagging_module": 3}]

tag_test.tagMain(tag["global_tag"],dir_path,case_tagging_list)
