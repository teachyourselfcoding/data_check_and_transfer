# coding=utf-8

import os
import json
import sys
import fnmatch
from tools.read_and_write_json import loadTag,saveTag




def getMatchedFilePaths(dir_path, pattern="*", formats=[".json"], recursive=False):
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

def parsingJsonForModuleTimeConsuming(tprofile_json,function_name):
    module_time_consuming = {}
    tprofile_tag =  loadTag(tprofile_json,tag_file_name = '')
    function_time_list  = tprofile_tag["tprofile_result"]
    call_number = 0
    for function_time in function_time_list:
        if function_time[0] == function_name:
            if call_number ==0 or call_number < function_time[3]:
                call_number = function_time[3]
                module_time_consuming["mean"] =  function_time[1]
                module_time_consuming["stddev"] = function_time[2]
            else:
                pass
    return module_time_consuming


def parsingJsonFoSensorTimeConsuming(tprofile_json,function_name):
    tprofile_tag = loadTag(tprofile_json, tag_file_name='')
    return tprofile_tag[function_name]

def moduleParsing(dir_path,time_consuming_json,tprofile_thresh,TPROFILE_RESULT):

    tprofile_result_path = ''.join([dir_path, 'tprofile_result/'])
    pattern = "ros_*"
    modules_json = getMatchedFilePaths(tprofile_result_path, pattern, [".json"])

    for tprofile_json in modules_json:
        if "lidar_detection" in tprofile_json:
            module_name = "lidar_detection"
            function_name_for_time_consuming = "ros_ad::LidarDetectionWrapper::onPointCloud2"
        elif "decision_planning" in tprofile_json:
            module_name = "decision_planning"
            function_name_for_time_consuming = "ros_ad::DecisionPlanningWrapper::onTimer"
        elif "prediction" in tprofile_json:
            module_name = "prediction"
            function_name_for_time_consuming = "ros_ad::PredictionWrapper::ProcessPredictionTask"
        elif "sensor_fusion" in tprofile_json:
            module_name = "sensor_fusion"
            function_name_for_time_consuming = "ros_ad::SensorFusionWrapper::onTimer"
        else:
            continue
        module_time_consuming = parsingJsonForModuleTimeConsuming(tprofile_json, function_name_for_time_consuming)
        time_consuming_json[module_name] = module_time_consuming
        time_thresh = tprofile_thresh["modules"][module_name]["time_thresh"]
        stddev_thresh = tprofile_thresh["modules"][module_name]["stddev_thresh"]

        if time_consuming_json[module_name]["mean"] < time_thresh:
            time_consuming_json[module_name]["result"] = True
        else:
            time_consuming_json[module_name]["result"] = False
            TPROFILE_RESULT.append(module_name+"_time_consuming_high")
        if stddev_thresh != 0.0 and time_consuming_json[module_name]["stddev"] > stddev_thresh:
            TPROFILE_RESULT.append(module_name+"_time_consuming_fluction")

    return time_consuming_json

def sensorParsing(dir_path,time_consuming_json,tprofile_thresh,TPROFILE_RESULT):
    tprofile_result_path = ''.join([dir_path, 'tprofile_result/'])
    pattern = "sensor_*"
    sensor_json_list = getMatchedFilePaths(tprofile_result_path, pattern, [".json"])

    for sensor_json in sensor_json_list:
        if "camera_eval" in sensor_json:
            module_name = "camera"
            sensor_eval_function = "CAMERA_FRAME_FREQ"
        elif "radar_eval" in sensor_json:
            module_name = "radar"
            sensor_eval_function = "CAN_FRAME_FREQ"
        elif "canbus_eval" in sensor_json:
            module_name = "canbus"
            sensor_eval_function = "CAN_FRAME_FREQ"
        elif "ins_eval" in sensor_json:
            module_name = "ins"
            sensor_eval_function = "INS_FRAME_FREQ"
        elif "lidar_eval" in sensor_json:
            module_name = "lidar"
            sensor_eval_function = "LIDAR_FRAME_FREQ"
        else:
            continue
        sensor_time_consuming = parsingJsonFoSensorTimeConsuming(sensor_json, sensor_eval_function)
        time_consuming_json[module_name] ={}
        frame_thresh = tprofile_thresh["sensors"][module_name]["frame_thresh"]
        stddev_thresh = tprofile_thresh["sensors"][module_name]["stddev_thresh"]
        if len(sensor_time_consuming)>4:
            time_consuming_json[module_name]["mean"] = sensor_time_consuming[0]
            time_consuming_json[module_name]["min"] = sensor_time_consuming[1]
            time_consuming_json[module_name]["median"] = sensor_time_consuming[2]
            time_consuming_json[module_name]["max"] = sensor_time_consuming[3]
            time_consuming_json[module_name]["std"] = sensor_time_consuming[4]
            if time_consuming_json[module_name]["mean"] > frame_thresh:
                time_consuming_json[module_name]["result"] =  True
            else:
                time_consuming_json[module_name]["result"] = False
                TPROFILE_RESULT.append(module_name+"_low_frame_rate")
            if stddev_thresh !=0.0 and time_consuming_json[module_name]["std"] > stddev_thresh:
                TPROFILE_RESULT.append(module_name+"_frame_rate_fluction")
    return time_consuming_json


def main(tprofile_thresh,dir_path):
    TPROFILE_RESULT = []
    try:
        time_consuming_json = {}
        time_consuming_json=moduleParsing(dir_path, time_consuming_json,tprofile_thresh,TPROFILE_RESULT)
        time_consuming_json=sensorParsing(dir_path, time_consuming_json,tprofile_thresh,TPROFILE_RESULT)

        saveTag(dir_path+'screen_cast/',time_consuming_json,'module_time_consuing.json')
    except Exception as e:
        print("tprofile_eval error")
    print(TPROFILE_RESULT)
    return TPROFILE_RESULT


def getAllDataDir(input_data_path):
    "get all dir in data"
    file_list = []
    for file in os.listdir(input_data_path):
        dir_file = os.path.join(input_data_path, file)

        if (os.path.isdir(dir_file)):
            h = os.path.split(dir_file)
            file_list.append(h[1])
    return file_list

if __name__ == '__main__':

    dir_path = "/media/sensetime/FieldTest/data/tprofile/"
    file_list = getAllDataDir(dir_path)
    tprofile_thresh  = loadTag('../config/tprofile_thresh.json', '')
    for file_path in file_list:
        print(file_path)
        main(tprofile_thresh,dir_path+file_path+'/')


