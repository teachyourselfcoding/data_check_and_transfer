# coding=utf-8

import os
import sys
import subprocess
sys.path.append("..")
from tools.read_and_write_json import loadTag,saveTag


class TLAutoToss():
    def __init__(self,auto_module_):
        self.auto_module_ = auto_module_

    def tlProcess(self,dir_path,record_tag):
        status = False
        case_toss_file = os.path.join(dir_path, 'screen_cast/case_tag.json')
        case_toss_tag = loadTag(case_toss_file, '')
        if case_toss_tag is None or case_toss_tag == {}:
            return record_tag, status
        case_toss_tag["Attributes"] = {}
        case_toss_tag["Object_check"] = {}
        case_toss_tag["Attributes"]["object_problem"] = 0
        case_toss_tag["Attributes"]["traffic_light_problem"] = 0
        case_toss_tag["Object_check"]["object_pos"] = 0
        if record_tag['labels'] != []:
            for label in record_tag['labels']:
                if label in self.auto_module_["supply_label_contrast"]:
                    labeled_module = self.auto_module_["supply_label_contrast"][label]
                    case_toss_tag["Attributes"][labeled_module] = 1
                    if labeled_module == "traffic_light_problem":
                        try:
                            case_toss_tag["Pr_check"]["true_tl_label"] = self.auto_module_["label_to_number"][label]
                        except:
                            print("tl toss error")
        saveTag(case_toss_file, case_toss_tag, '')
        self.autoModuleDsitrib(dir_path)
        if not os.path.isfile(os.path.join(dir_path, 'screen_cast/auto_module.json')):
            return record_tag,status
        auto_module_tag = loadTag(os.path.join(dir_path, 'screen_cast/auto_module.json'), '')
        if auto_module_tag["Module"] != []:
            status = True
        if auto_module_tag["Module"] == ["C-TL"] and "红绿灯场景变化" in record_tag["labels"]:
            auto_module_tag["Module"] = ["Road"]
        for module in auto_module_tag["Module"]:
            record_tag["modules"].append(module)
        record_tag["modules"] = list(set(record_tag["modules"]))
        return record_tag,status

    def autoModuleDsitrib(self, input_path):
        scripts = "./case_toss/auto_sub_module "
        input_file = os.path.join(input_path, 'screen_cast/case_tag.json')
        output_file = os.path.join(input_path, 'screen_cast/auto_module.json')
        config_file = " config/ft_config.json"
        cmd = ''.join([scripts, input_file, ' ', output_file, config_file])
        child = subprocess.Popen(cmd, shell=True)
        child.wait()

class TossForTL():
    def __init__(self,config_,auto_module_):
        self.config_ = config_
        self.auto_module_ = auto_module_
        self.local_toss = TLAutoToss(self.auto_module_)

    def tl_main(self,dir_path,record_tag, toss_tag):
        record_tag,status = self.local_toss.tlProcess(dir_path,record_tag)
        if status:
            return record_tag,status
        return record_tag, status