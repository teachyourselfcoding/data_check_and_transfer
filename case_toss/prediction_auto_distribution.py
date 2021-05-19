# coding=utf-8

import os
import sys
import fnmatch
sys.path.append("..")
from tools.read_and_write_json import loadTag,saveTag
from modules_evaluation.generate_evaluation_result import generatePredictionEval


def getCaseTime(dir_path):
    data_tag = loadTag(dir_path,'data-tag.json')
    if data_tag is None:
        return 123456
    return data_tag["origin_record_tag"][0]["start"]/1000

def getMatchedFilePaths( dir_path, pattern="*", formats=[".avi"], recursive=False):
    "get all the files in <dir_path> with specified pattern"
    files = []
    data_dir = os.path.normpath(os.path.abspath(dir_path))
    try:
        for f in os.listdir(data_dir):
            current_path = os.path.join(os.path.normpath(data_dir), f)
            if os.path.isdir(current_path) and recursive:
                files += getMatchedFilePaths(current_path, pattern, formats,
                                                  recursive)
            elif fnmatch.fnmatch(f,
                                 pattern) and os.path.splitext(f)[-1] in formats:
                files.append(current_path)
        return files
    except OSError:
        print("os error")
        return []

def JudgeInvalid(eval_result_path,id_list):
    moved_tag = loadTag(eval_result_path,'moved_id.json')
    if moved_tag is None or "invalid" not in moved_tag.keys():
        return ""

    if moved_tag["static"] == []:
        return ""
    for id in id_list:
        if id in moved_tag["static"]:
            return "3DPerception"
    return ""

def padMain(dir_path,config_,record_tag):

    if record_tag["modules"] != [] and record_tag["modules"] != ["FT"]:
        return record_tag
    screen_path = os.path.join(dir_path, 'screen_cast')
    eval_result_path = os.path.join(dir_path, 'prediction_evaluation/result')
    case_finer_tag = loadTag(screen_path, 'case_finder.json')
    pp_obstacle_tag = loadTag(screen_path, 'obstacle.json')

    if case_finer_tag is None or pp_obstacle_tag is None :
        return record_tag
    generatePredictionEval(dir_path, config_,casetime=case_finer_tag["end_timestamp"])

    eval_bad_case_tag = loadTag(eval_result_path, 'bad_cases.json')
    if eval_bad_case_tag is None:
        return record_tag
    pp_obstacle_id = []
    eval_bad_case_id = {"id_list":[]}
    intime_bad_case_list =[]

    if "wrong_timestamp" in case_finer_tag.keys():
        case_timestamp = case_finer_tag["wrong_timestamp"]
    else:
        case_timestamp = getCaseTime(dir_path)
    case_timestamp = int(case_timestamp*1000)
    for obj_id in pp_obstacle_tag["id_list"].keys():
        pp_obstacle_id.append(obj_id)
    # id_list = getMatchedFilePaths(dir_path+'/screen_cast',"*",[".id"])
    # if id_list == []:
    #     print("id is none")
    # #     return record_tag
    # real_id = os.path.basename(id_list[0]).split('.')[0]
    # print(real_id)
    for bad_case_time in eval_bad_case_tag.keys():
        if int(bad_case_time) > case_timestamp - 500 and int(bad_case_time) < case_timestamp:
            intime_bad_case_list.append(eval_bad_case_tag[bad_case_time])
    print pp_obstacle_id
    for intime_case in intime_bad_case_list:
        bb =[]
        # for label in intime_case["labels"]:
        #     for aa in label.keys():
        #         bb.append(aa)
        # if intime_case["id"] == [] or bb == ['ConsistencyDisplacementError']:
        #     continue
        for id in intime_case["id"] :
            # print(id, pp_obstacle_id)
            eval_bad_case_id["id_list"].append(id)
            if str(id) in pp_obstacle_id:
                #print id
                record_tag["modules"].append("Prediction")
                # for label in intime_case["labels"]:
                #     for metrc in label.keys():
                #         if metrc in record_tag["labels"].keys():
                #             if record_tag["labels"][metrc] > label[metrc] or metrc =="LaneChangeWrong" or metrc =="TurnWrong":
                #                 #print(id,metrc,label[metrc])
                #                 pass
                #             else:
                #                 record_tag["labels"][metrc] = label[metrc]
                #                 #print(id,metrc,label[metrc])
                #         else:
                #             record_tag["labels"][metrc] = label[metrc]
                        #print(id, metrc, label[metrc])
    record_tag["modules"] = list(set(record_tag["modules"]))
    #record_tag["labels"] = list(set(record_tag["labels"]))
    saveTag(screen_path,eval_bad_case_id,'eval_bad_case_id.json')
    if record_tag["modules"] == []:
        module = JudgeInvalid(eval_result_path,pp_obstacle_id)
        if module != "":
            record_tag["modules"].append(module)
    return record_tag

def getAllDataDir(input_data_path):
    "get all dir in data"
    file_list=[]
    for file in os.listdir(input_data_path):
        dir_file = os.path.join(input_data_path, file)

        if (os.path.isdir(dir_file)):
            h = os.path.split(dir_file)
            file_list.append(h[1])
    return file_list


if __name__ == '__main__':
    config_ = loadTag("../config/data_pipeline_config.json", '')
    input_path = "/media/sensetime/FieldTest/data/DAP_ARH/"
    dir_list = getAllDataDir(input_path)
    for dir_name in dir_list:
        dir_path = os.path.join(input_path,dir_name)
        data_tag = loadTag(dir_path,'data-tag.json')
        print(dir_path)
        if data_tag is None:

            continue
        record_tag = data_tag["origin_record_tag"][0]
        record_tag["modules"] =[]
        record_tag["labels"] = {}

        record_tag = padMain(dir_path,config_,record_tag)

        print "\033[1;32m [INFO] module \033[0m ", dir_path, record_tag["modules"]










