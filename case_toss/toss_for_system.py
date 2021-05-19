# coding=utf-8



import os
import sys
sys.path.append("..")



class TossForSystem():
    def __init__(self,config_,auto_module_):
        self.config_ = config_
        self.auto_module_ = auto_module_

    def checkNodeStatus(self,record_tag,toss_tag):
        status = False
        for nodelet, status, in toss_tag["node_state"].items():
            for error_code in [0,3,4,5]:
                if error_code in status:
                    record_tag["labels"].append(nodelet+"_crashed")
                    status = True
                    return record_tag,status
        return record_tag, status



    def system_main(self,dir_path,record_tag,toss_tag):
        status = False
        if toss_tag is None or toss_tag == [] or "node_state" not in toss_tag:
            return record_tag,status
        record_tag, status = self.checkNodeStatus(record_tag,toss_tag)
        return record_tag,status