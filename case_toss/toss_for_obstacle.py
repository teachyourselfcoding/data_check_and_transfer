# coding=utf-8

import os
import sys
import subprocess
sys.path.append("..")
from tools.read_and_write_json import loadTag,saveTag
from modules_evaluation.generate_evaluation_result import generatePredictionEval


class LocalizationAutoToss():

    def judgeIfOverLap(self,x1, y1, x2, y2):
        minx = min(x1, x2)
        maxy = max(y1, y2)
        if (maxy - minx) < (y1 - x1 + y2 - x2):
            return True
        return False

    def localModuleDistrib(self,auto_module_,record_tag, eval_tag, ):
        status = False
        if eval_tag is None or auto_module_ is None:
            return record_tag,status

        start = int(str(int(record_tag["start"] * 1000))[0:10]) - 15
        if "end" in record_tag:
            end = int(str(int(record_tag["end"] * 1000))[0:10]) + 15
        else:
            end = start + 30
        local_error_label = []
        for eval in eval_tag:
            eval_start = int(str(int(eval["start"] * 1000))[0:10])
            eval_end = int(str(int(eval["end"] * 1000))[0:10])
            if not self.judgeIfOverLap(start, end, eval_start, eval_end):
                continue
            for key in eval.keys():
                for error_label in auto_module_["local_threshold"]["error_list"]:
                    if key.split('(')[0] == error_label and eval[key] > auto_module_["local_threshold"][eval["tag_en"]]:
                        local_error_label.append(eval["tag_en"])

        if len(local_error_label) > 1:
            record_tag["modules"].append("Localization")
            status = True
        if local_error_label != []:
            for label in local_error_label:
                record_tag["labels"].append(label)
        if "large_time_gap" in local_error_label:
            record_tag["modules"].append("System")
            status = True
        return record_tag,status


class PredictionAutoToss():
    def __init__(self,pred_eval_thresh):
        self.pred_eval_thresh = pred_eval_thresh

    def getCaseTime(self,dir_path):
        data_tag = loadTag(dir_path, 'data-tag.json')
        if data_tag is None:
            return 123456
        return data_tag["origin_record_tag"][0]["start"] / 1000

    def JudgeInvalid(self,eval_result_path, id_list):
        moved_tag = loadTag(eval_result_path, 'moved_id.json')
        if moved_tag is None or "moved_id" not in moved_tag.keys():
            return ""
        # for id in id_list:
        #     if id in moved_tag["moved_id"]["static"]:
        #         return "3DPerception"
        return ""

    def processBadCase(self,bad_case):
        value = {}
        for single_case in bad_case:
            single_case = bad_case[single_case]
            for id_dict in single_case['id']:
                for id in id_dict.keys():
                    if not id in value.keys():
                        value[id] = {}
                        value[id]["type"] = id_dict[id]

                    for label in single_case["labels"]:
                        for label_key in label.keys():
                            label_label = label_key.split("_")[0]
                            label_id = label_key.split("_")[1]
                            if label_id != id:
                                continue
                            if not label_label in value[id].keys():
                                value[id][label_label] = label[label_key]
                            else:
                                if value[id][label_label] < label[label_key]:
                                    value[id][label_label] = label[label_key]
        return value

    def predMain(self,dir_path, config_, record_tag):
        map_object_num2type = {
            0: "veh",
            1: "veh",
            2: "ped",
            3: "cyc",
            4: "oth"
        }
        status = False
        if record_tag["modules"] != [] and record_tag["modules"] != ["FT"]:
            print("modules is not empty")
            return record_tag, status
        screen_path = os.path.join(dir_path, 'screen_cast')
        eval_result_path = os.path.join(dir_path, 'prediction_evaluation/result')

        case_finer_tag = loadTag(screen_path, 'case_finder.json')
        pp_obstacle_tag = loadTag(screen_path, 'obstacle.json')

        if case_finer_tag is None or pp_obstacle_tag is None or "wrong_timestamp" not in case_finer_tag.keys():
            return record_tag, status
        generatePredictionEval(dir_path, config_,casetime=case_finer_tag["wrong_timestamp"],input_id="1111")

        eval_bad_case_tag = loadTag(eval_result_path, 'bad_cases.json')
        if eval_bad_case_tag is None:
            return record_tag, status
        pp_obstacle_id = pp_obstacle_tag["obstacle_id"]

        value = self.processBadCase(eval_bad_case_tag)
        saveTag(eval_result_path, value, 'value.json')
        for id in value:
            if not int(id) in pp_obstacle_id:
                continue
            type = map_object_num2type[value[id]["type"]]
            threshold = self.pred_eval_thresh[type]
            if "TurnWrong" in value or "LaneChangeWrong" in value[id]:
                record_tag["modules"].append("Prediction")
                record_tag["labels"].append("LaneChangeWrong")
                status = True
                print(record_tag,status)
                return record_tag, status
            times = 0
            for label in threshold:
                if value[id].get(label) is None:
                    continue
                if value[id].get(label) > threshold[label]:
                    times += 1
            if value[id].get("ConsistencyDisplacementError") is not None:
                if type == "cyc":
                    if value[id].get("ConsistencyDisplacementError") > 2.4:
                        record_tag["modules"].append("Prediction")
                        status = True
                    if value[id].get("ConsistencyDisplacementError") > 0.8 and times > 0:
                        record_tag["modules"].append("Prediction")
                        status = True
                elif type == "veh":
                    if value[id].get("ConsistencyDisplacementError") > 5.0:
                        record_tag["modules"].append("Prediction")
                        status = True
                    if value[id].get("ConsistencyDisplacementError") > 1.0 and times > 0:
                        record_tag["modules"].append("Prediction")
                        status = True
                elif type == "ped":
                    if value[id].get("ConsistencyDisplacementError") > 1.5:
                        record_tag["modules"].append("Prediction")
                        status = True
                    if value[id].get("ConsistencyDisplacementError") > 0.5 and times > 0:
                        record_tag["modules"].append("Prediction")
                        status = True

            if not status:
                continue
            for label in value[id].keys():
                if label == "type":
                    continue
                if not label in record_tag["labels"]:
                    record_tag["labels"].append(label)
        if record_tag["modules"] == []:
            module = self.JudgeInvalid(eval_result_path, pp_obstacle_id)
            if module != "":
                record_tag["modules"].append(module)
                status = True
        print(record_tag,status)
        return record_tag,status

class TossForObstacle():
    def __init__(self,config_,auto_module_,pred_eval_thresh):
        self.local_toss = LocalizationAutoToss()
        self.preidction_toss = PredictionAutoToss(pred_eval_thresh)
        self.config_ = config_
        self.auto_module_ = auto_module_

    def obstacle_main(self,local_eval_tag,dir_path,record_tag,toss_tag):
        status = False
        for label in record_tag["labels"]:
            if label in ["误检", "漏检", "物体尺寸异常"]:
                record_tag["modules"].append("3DPerception")
                return record_tag,True
        record_tag,status = self.local_toss.localModuleDistrib(self.auto_module_,record_tag,local_eval_tag)
        if status:
            return record_tag,status
        for label in record_tag["labels"]:
            if label == "障碍物问题":
                record_tag,status = self.preidction_toss.predMain(dir_path, self.config_,record_tag)
                return record_tag,status
        return record_tag, status



if __name__ == '__main__':
    pred_eval_thresh = loadTag('../config/pred_eval_thresh.json', '')
    pred_toss = PredictionAutoToss(pred_eval_thresh)
    dir_path = '/media/sensetime/FieldTest1/data/error_ARH/2021_01_12_17_39_24'
    config_ =  loadTag('../config/data_pipeline_config.json','')
    record_tag = {
            "labels": [
                "StaticSpeed",
                "Straight",
                "InJunction",
                "\u5176\u4ed6"
            ],
            "modules": [],
            "start_format": "17:39:24",
            "tag_en": "take_over",
            "start": 1610444364000,
            "tag": "\u63a5\u7ba1",
            "lat": 30.886391957962203,
            "lng": 121.91399492616227
        }
    pred_toss.predMain(dir_path,config_,record_tag)





