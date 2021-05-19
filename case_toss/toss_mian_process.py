# coding=utf-8

import os
import json
from toss_for_obstacle import TossForObstacle
from toss_for_tl import TossForTL
from toss_for_other import TossForOther
from toss_for_system import TossForSystem
from tools.read_and_write_json import loadTag,saveTag



class TossMain():
    def __init__(self,config_,auto_module_,pred_eval_thresh):
        self.config_ = config_
        self.auto_module_ = auto_module_
        self.system_toss = TossForSystem(self.config_, self.auto_module_)
        self.tl_toss = TossForTL(self.config_,self.auto_module_)
        self.obstalce_toss = TossForObstacle(self.config_,self.auto_module_,pred_eval_thresh)
        self.other_toss = TossForOther(self.config_,self.auto_module_)

    def removeRedundModule(self,record_tag):
        record_tag["modules"] = list(set(record_tag["modules"]))
        record_tag["labels"] = list(set(record_tag["labels"]))
        print (record_tag["modules"])
        return record_tag


    def readTossTag(self,dir_path):
        toss_tag = loadTag(dir_path,"screen_cast/case_tag.json")
        if toss_tag is None or toss_tag == []:
            return False,toss_tag
        return True,toss_tag

    def mainToss(self,local_eval_tag,dir_path,record_tag,slice_data_tag):

        if not record_tag['tag_en'] in ['take_over','Emergency_brake']:
            return record_tag
        if slice_data_tag["route"] == "default":
            return record_tag

        _,toss_tag = self.readTossTag(dir_path)
        if not _:
            return record_tag

        # check if system problem
        record_tag, status = self.system_toss.system_main(dir_path, record_tag, toss_tag)
        if status:
            print ("\033[1;32m [INFO]\033[0m ", "Confirm System Problem")
            return self.removeRedundModule(record_tag)

        # check if traffic light problem
        record_tag, status = self.tl_toss.tl_main(dir_path, record_tag, toss_tag)
        if status:
            print ("\033[1;32m [INFO]\033[0m ", "Confirm Traffic Light Problem")
            return self.removeRedundModule(record_tag)

        # check if obstacle problem
        record_tag, status = self.obstalce_toss.obstacle_main(local_eval_tag, dir_path, record_tag, toss_tag)
        if status:
            print ("\033[1;32m [INFO]\033[0m ", "Confirm Obstacle Problem")
            return self.removeRedundModule(record_tag)

        # check if other problem
        record_tag, status = self.other_toss.other_main(dir_path,record_tag,local_eval_tag, toss_tag)
        if status:
            print ("\033[1;32m [INFO]\033[0m ", "Confirm Other Problem")
            return self.removeRedundModule(record_tag)

        # check if there is repeated module in record_tag["modules"]
        return self.removeRedundModule(record_tag)
