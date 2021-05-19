# coding=utf-8
#!/usr/bin/python3

import os
import sys
import json
import time
import fnmatch
import requests

check_file_name_list = {
        "dmppcl.bag.active": {"size":10,"name":"dpcbag"},
        "screen_cast/screen.mp4": {"size":10,"name":"录屏"},
        "sensors_record/canbus.dump.rec": {"size":10,"name":"canbus"},
        "sensors_record/ins.dump.rec": {"size":10,"name":"定位"},
        "sensors_record/top_center_lidar.dump.rec": {"size":10,"name":"雷达"},
        "simulator_scenario/simulator_scenario_log.bin": {"size":10,"name":"仿真"}
    }

def getMatchedFilePaths(dir_path, pattern="*", formats=[".txt"], recursive=False):
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

def checkRec(dir_path):
    '''
    :param dir_path: data path end with /
    :param slice: define the checking data is raw data or segment data
    :return: True of False
    '''

    false_reason = []
    if not os.path.exists(dir_path):
        return False, false_reason
    video_result = 0
    check_result = 0

    for file_name in check_file_name_list:
        check_size = check_file_name_list[file_name]["size"]
        reult_0_1 = judgeFileSizeAndExist(dir_path, file_name, check_size=check_size)
        check_result += reult_0_1
        if reult_0_1 == 0:
            false_reason.append(check_file_name_list[file_name]["name"])
    pattern = "port_*"
    video_files = getMatchedFilePaths(dir_path, pattern, formats=[".avi",".h264"], recursive=False)
    if video_files ==[]:
        false_reason.append("相机")
    for video_name in video_files:
        video_reult_0_1 = judgeFileSizeAndExist(dir_path='', file_name=video_name, check_size=10)
        video_result += video_reult_0_1
        if video_reult_0_1 == 0:
            false_reason.append(file_name)
    if check_result > 5 and video_result > 0:
        return True, false_reason
    else:
        return False, false_reason


def judgeFileSizeAndExist(dir_path, file_name, check_size=0.2):
    "as the function name descripted"

    judge_file = os.path.join(dir_path, file_name)
    if os.path.exists(judge_file) and \
            round(os.path.getsize(judge_file) / float(1024), 1) >= check_size:
        return 1
    else:
        return 0

def TransferPost(data_tag):
    "post the data tag to senseFT"
    headerdata = {"Data-tag-type": "application/json"}
    curl = \
        'http://localhost:8088/api/v1/notice'
    post_result = requests.post(curl, headers=headerdata, data=json.dumps(data_tag))
    print ("\033[1;32m [INFO]\033[0m ", post_result.text,'\n')


def main(data_path):
    post_result = {
        "title": "数据质检",
        "content": "",
        "type": "info",
        "duration": 5
    }
    check_result,check_reason = checkRec(data_path)
    if check_result:
        post_result["type"] = "info"
        post_result["content"] = "数据质检正常"
    else:
        post_result["type"] = "error"
        if check_reason != []:
            for reason in check_reason:
                post_result["content"] += ''.join([reason,"数据异常, ",])
    print(post_result)
    TransferPost(post_result)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        data_path = "/media/sensetime/FieldTest/today"
    else:
        data_path = sys.argv[1]
    if not os.path.exists(data_path):
        raise ValueError("========== : {} does NOT exist".format(data_path))
    time.sleep(10)
    main(data_path)