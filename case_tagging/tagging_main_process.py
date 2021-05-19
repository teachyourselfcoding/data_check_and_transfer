# coding=utf-8

import os
import sys
sys.path.append("..")
import parse_obstacle_tag
from tag_msg_parser import ParseMessage
from tag_generater import TagGenerate
from threadpool import ThreadPool, makeRequests
from tools.read_and_write_json import loadTag,saveTag

class TaggingMain():
    def __init__(self,pool,config_,auto_module,tag_module):
        self.pool = pool
        self.config_ = config_
        self.parse_msg = ParseMessage(self.config_,auto_module,tag_module)
        self.generate_tag = TagGenerate(self.config_,tag_module)


    def readDataTagJson(self,dir_path):
        data_tag = loadTag(dir_path,"data-tag.json")
        if data_tag is None or data_tag == []:
            return []
        if "backup" in data_tag:
            data_tag = data_tag["backup"][0]["data_tag"]
        return data_tag


    def getTagProcess(self,origin_path,global_tag,case_info):
        dir_path = case_info["input_dir"]
        data_tag = self.readDataTagJson(dir_path)
        record_tag = data_tag["origin_record_tag"][0]
        self.parse_msg.parseMsgMain(dir_path,global_tag, record_tag)
        # self.generate_tag.tagGenerateMain(dir_path,record_tag)


    def tagMain(self,global_tag,dir_path, case_tagging_list):
        print ("\033[1;32m [INFO]\033[0m case tagging ing .........\n")
        input_list = []
        for case_info in case_tagging_list:
            input_list.append(([dir_path, global_tag, case_info], None))
        try:
            requests = makeRequests(self.getTagProcess, input_list)
            [self.pool.putRequest(req) for req in requests]
            self.pool.wait()
        except Exception as e:
            return
        print ("\033[1;32m [INFO]\033[0m case tagging successfully\n")