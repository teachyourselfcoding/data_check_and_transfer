# coding=utf-8
'''
prediction_evaluation_iteration.py
check the data format before upload
by Zheng Yaocheng

'''
import os
import sys
import json
from collections import defaultdict, deque
from tools.read_and_write_json import loadTag,saveTag

def main(dir_path,bad_result,record_tag):
    '''


    :param dir_path:
    :param label_list:
    :return:
    '''
    #try:

    data_tag = loadTag(record_tag["input_dir"])
    abnormal_ap_label = data_tag.get("origin_record_tag")[0]
    case_finder_json = loadTag(record_tag["input_dir"], tag_file_name='screen_cast/case_finder.json')
    if abnormal_ap_label == []:
        return 1
    bad_case_list = defaultdict(lambda :{})
    for bad_case_time in bad_result:
        bad_case_list[int(bad_case_time)] = bad_result[bad_case_time]["labels"]

    if len(bad_case_list) ==0:
        case_finder_json["ap_evaluation_result"]= []
        case_finder_json["has_found"] = False
    else:

        case_finder_json["ap_evaluation_result"] = generateEvluationScore(bad_case_list, abnormal_ap_label)
        if len(case_finder_json["ap_evaluation_result"]) !=0:
            case_finder_json["ap_evaluation_result"].append("HasFound")

    print ('\n-----', case_finder_json["ap_evaluation_result"], '\n')
    saveTag(record_tag["input_dir"], case_finder_json, '/screen_cast/case_finder.json')


    # except Exception as e:
    #     return False



def extractLabelList(data_tag):
    '''

    :param data_tag:
    :return:
    '''
    label_list = []
    origin_record_tag = data_tag.get("origin_record_tag")

    for case_name in origin_record_tag:
        if case_name['tag_en'] == 'abnormal_prediction_trajectory':
            label_list.append([case_name['start'] - 10000, case_name['start']])

    return label_list


def generateEvluationScore(bad_case_list, abnormal_ap_label):
    '''

    :param bad_case_list:
    :param label_list:
    :return:
    '''
    find_list=[]

    for bad_case_time in bad_case_list:

        if bad_case_time/1000 < abnormal_ap_label["start"]/1000 and bad_case_time > abnormal_ap_label["start"]/1000 -10:
            for label in bad_case_list[bad_case_time]:
                find_list.append(label)

    return list(set(find_list))


def judgeCaseTime(bad_case_time, label_list):
    '''

    :param bad_case_time:
    :param label_list:
    :return:
    '''
    for label in label_list:
        if bad_case_time < label[1] and bad_case_time > label[0]:
            return True
        else:
            continue
    return False


if __name__ == '__main__':
    dir_path = '/media/sensetime/FieldTest/data/06_18_CN-017_ARH/2020_06_18_20_12_39_AutoCollect'

    main(dir_path)
