# coding=utf-8

import os
import sys
import parse_obstacle_tag

# reload(sys)
# sys.setdefaultencoding('utf8')
sys.path.append("..")
from tools.read_and_write_json import loadTag,saveTag


class ParseMessage():
    def __init__(self,config_,auto_module_, tag_module):
        self.config_ = config_
        self.auto_module_ = auto_module_
        self.tag_module_ = tag_module
        self.deserial_msg = os.path.join(self.config_["senseauto_path"],
            'senseauto-simulation/node/build/module/simulator/tools/scenario_log_tools/deserialize_msg')

    def execDesMsg(self, dir_path, record_tag):
        des_output_path = os.path.join(dir_path, 'screen_cast')
        case_sec = str(record_tag["start"])[:10]
        case_nsec = str(record_tag["start"])[10:]
        case_type = self.tag_module_[record_tag["tag_en"]]["case_type"]
        front_time = 20
        behind_time = 10
        des_msg_cmd = "{} {} {} {} {} {} {} {}".format(
            self.deserial_msg, dir_path, des_output_path,str(case_type),
            str(case_sec), str(case_nsec), str(front_time), str(behind_time))
        os.system(des_msg_cmd)


    def filterObjectId(self,object_id_list):
        max_distribution = 0
        id_dict = {}
        filted_list = []
        for objec_id in object_id_list:
            if not objec_id in id_dict.keys():
                id_dict[objec_id] = 0
            id_dict[objec_id] += 1

        for object in id_dict:
            if id_dict[object] > max_distribution:
                max_distribution = id_dict[object]
        for object in id_dict:
            if id_dict[object] == max_distribution or id_dict[object]>1:
                filted_list.append(object)
        return filted_list

    def processObstacleId(self,dir_path,record_tag):
        case_time = record_tag["start"]*1000
        result_tag = {"obstacle_id":[],
               "id_list":{}}
        dpc_file_path = ''.join([dir_path, 'dmppcl.bag'])
        tag_path = os.path.join(dir_path,'screen_cast')
        id_list = parse_obstacle_tag.parseProtoTag(dpc_file_path,case_time)
        obstacle_id_list = self.filterObjectId(id_list)

        result_tag["obstacle_id"] = obstacle_id_list
        if id_list != []:
            for id in id_list:
                if id not in result_tag["id_list"].keys():
                    result_tag["id_list"][id] = 0
                result_tag["id_list"][id] += 1
        saveTag(tag_path, result_tag, 'obstacle.json')


    def addWhetherInfo(self,global_tag,dir_path):
        tag_path = os.path.join(dir_path,"screen_cast")
        case_toss = loadTag(tag_path,"case_tag.json")
        if case_toss is None or global_tag == []:
            return
        whether_tag = 0
        for tag in global_tag:
            if tag not in ["阳光直射","阳光背射","凌晨","黄昏","夜晚有路灯","夜晚无路灯"]:
                continue
            if tag == "阳光直射" or tag == "阳光背射":
                whether_tag = 1
            elif tag == "黄昏":
                whether_tag = 2
            else:
                whether_tag = 3
        if "Global_label" not in case_toss.keys():
            case_toss["Global_label"] = {}
        case_toss["Global_label"]["day_time"] = whether_tag
        saveTag(tag_path,case_toss,'case_tag.json')


    def parseMsgMain(self,dir_path,global_tag,record_tag):
        self.execDesMsg(dir_path,record_tag)
        self.addWhetherInfo(global_tag,dir_path)
        self.processObstacleId(dir_path,record_tag)

