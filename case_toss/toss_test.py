# coding=utf-8

import os
import json
from toss_for_obstacle import TossForObstacle
from toss_for_tl import TossForTL
from toss_for_other import TossForOther
from toss_for_system import TossForSystem
from tools.read_and_write_json import loadTag,saveTag


from toss_mian_process import TossMain
from threadpool import ThreadPool, makeRequests

config = loadTag("/home/sensetime/Codes/data_check_and_transfer/config/data_pipeline_config.json","")
auto_module_ = loadTag('/home/sensetime/Codes/data_check_and_transfer/config/auto_module.json', '')
tag_module = loadTag(tag_file_name='/home/sensetime/Codes/data_check_and_transfer/config/tag_module.json')

dir_path = "/media/sensetime/FieldTest2/data/04_20_CN-013_ARH/2021_04_20_11_31_09_AutoCollect_slice/DPC/take_over/2021_04_20_10_45_02"

pred_eval_thresh ={}
case_toss = TossMain(config,auto_module_, pred_eval_thresh)

case_tagging_list = [{"input_dir": dir_path,
                    "module_name": "take_over",
                    "input_timestamp": 1618886702,
                    "tagging_module": 3}]
data_tag = loadTag(dir_path,"data-tag.json")
record_tag = {u'labels': [u'\u5371\u9669\u63a5\u7ba1', u'\u969c\u788d\u7269\u95ee\u9898'], u'modules': [], u'start_format': u'10:45:02', u'tag_en': u'take_over', u'start': 1618886702131, u'tag': u'\u63a5\u7ba1', u'lat': 0, u'lng': 0}

case_toss.mainToss({},dir_path,record_tag,data_tag)