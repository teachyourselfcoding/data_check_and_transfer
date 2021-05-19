# coding=utf-8

import os
import sys
import subprocess
sys.path.append("..")
# reload(sys)
# sys.setdefaultencoding('utf8')




class TossForOther():
    def __init__(self,config_,auto_module_):
        self.config_ = config_
        self.auto_module_ = auto_module_

    def other_main(self,dir_path,record_tag,eval_tag,toss_tag):
        status = False
        for label in record_tag["labels"]:
            if label in ["场景变化"]:
                record_tag["modules"].append("Road")
                status = True
            if label in ["标注错误"]:
                if record_tag["tag_en"] == "take_over":
                    record_tag["modules"].append("System")
                    status = True
                if record_tag["tag_en"] == "Emergency_brake":
                    record_tag["modules"].append("Control")
                    status = True
        return record_tag,status