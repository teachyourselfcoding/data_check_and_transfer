# coding=utf-8

import os
import sys
sys.path.append("..")
from tools.read_and_write_json import loadTag,saveTag




class TagGenerate():
    def __init__(self,config_, tag_module):
        self.config_ = config_
        self.tag_module_ = tag_module
        self.case_finder = os.path.join(self.config_["senseauto_path"],
            'senseauto-simulation/node/build/module/simulator/tools/scenario_log_tools/case_finder')

    def execCaseFinder(self, dir_path, record_tag):
        bin_file_path = os.path.join(dir_path, 'simulator_scenario/0/logger.bin')
        des_output_path = os.path.join(dir_path, 'screen_cast/case_finder.json')
        case_sec = str(record_tag["start"])[:10]
        front_time = 20
        behind_time = 10
        des_msg_cmd = "{} {} {} 2 {} {} {}".format(
            self.case_finder, bin_file_path, des_output_path,
            str(case_sec), str(front_time), str(behind_time))
        os.system(des_msg_cmd)

    def renameCaseTaggingTag(self, dir_path):
        case_output_path = os.path.join(dir_path,"screen_cast")
        case_finder = loadTag(case_output_path, 'case_finder.json')
        saved_ego_tags = []
        if case_finder == [] or case_finder is None:
            case_finder = {}
            saveTag(case_output_path, case_finder, 'case_finder.json')
            return
        if "obstacle_id" in case_finder[0] and case_finder[0]["obstacle_id"] == [""]:
            case_finder[0]["obstacle_id"] = []
        if "obstacle_id" in case_finder[0] and case_finder[0]["obstacle_id"] == ["0"]:
            case_finder[0]["obstacle_id"] = []
        if "ego_tags" in case_finder[0]:
            case_finder[0]["ego_tags"] = self.refineTag(case_finder[0]["ego_tags"])
            saved_ego_tags = case_finder[0]["ego_tags"]
        if "obstacle_vehicle_tags" in case_finder[0]:
            case_finder[0]["obstacle_vehicle_tags"] = self.refineTag(case_finder[0]["obstacle_vehicle_tags"])
        if "obstacle_vru_tags" in case_finder[0]:
            case_finder[0]["obstacle_vru_tags"] = self.refineTag(case_finder[0]["obstacle_vru_tags"])
        saveTag(case_output_path, case_finder[0], 'case_finder.json')
        return saved_ego_tags


    def addEgoTagToLabel(self,record_tag,ego_tags):

        case_tag = loadTag(record_tag["input_dir"], 'data-tag.json')
        if not "origin_record_tag" in case_tag.keys():
            return

        if not "labels" in case_tag["origin_record_tag"][0]:
            case_tag["origin_record_tag"][0]["labels"] = []
        if ego_tags is not None:
            for tag in ego_tags:
                case_tag["origin_record_tag"][0]["labels"].append(tag)
        saveTag(record_tag["input_dir"], case_tag, 'data-tag.json')


    def tagGenerateMain(self,dir_path,record_tag):
        self.execCaseFinder(dir_path,record_tag)
        ego_tags = self.renameCaseTaggingTag(dir_path)
        self.addEgoTagToLabel(record_tag,ego_tags)


