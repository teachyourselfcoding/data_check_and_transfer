# coding=utf-8

import os
import sys
import json
import datetime
import fnmatch
from log_summarizer_local import logSummarizer


def downloadLog(download_path,http_log_path):
    cmd = ''.join(['wget -P ',download_path,' ',http_log_path])
    print(cmd)
    os.system(cmd)



def getMonth():
    month = datetime.datetime.now().strftime('%Y-%m')
    return month

def generateResultJson(download_path,vehicle_path,vehicle_id):
    print(download_path)
    if not os.path.exists(download_path):
        return
    json_save_path = os.path.join(download_path,'2021-01.json')
    start_day = '2021-01-01'
    end_day = '2021-01-31'
    print(json_save_path)
    logSummarizer(start_day, end_day,vehicle_path+'/',vehicle_id,json_save_path)


def wgetLog(log_path):
    vehicle_list = ['003','009','010','011','012','013','014','016','017']

    for id in vehicle_list:
        vehicle_id = "CN-"+id
        download_path = os.path.join(log_path,vehicle_id,"novatel")
        http_log_path = "https://fieldtest.sensetime.com/download/sensor-check/"+vehicle_id+"/2021-01.log"
        downloadLog(download_path,http_log_path)
        vehicle_path = os.path.join(log_path,vehicle_id)
        generateResultJson(download_path,vehicle_path,vehicle_id)



def loadTag(tag_file_path='', tag_file_name='data-tag.json'):
    '''
    load json file
    :param tag_file_path: input file path
    :param tag_file_name: input file name
    :return: json
    '''
    tag_file = os.path.abspath(os.path.join(tag_file_path, tag_file_name))
    if not os.path.exists(tag_file):
        return None
    with open(tag_file, 'r') as f:
        try:
            tag_data = json.load(f)
            return tag_data
        except ValueError:
            print " ==== ", tag_file, "\033[1;31m is not valuable json bytes \033[0m!\n"
            return None

def GetMatchedFilePaths(data_dir,
                        pattern="*",
                        formats=[".h264"],
                        recursive=False):
    files = []
    data_dir = os.path.normpath(os.path.abspath(data_dir))
    import fnmatch
    for f in os.listdir(data_dir):
        current_path = os.path.join(os.path.normpath(data_dir), f)
        if os.path.isdir(current_path) and recursive:
            files += GetMatchedFilePaths(current_path, pattern, formats,
                                         recursive)
        elif fnmatch.fnmatch(f,
                             pattern) and os.path.splitext(f)[-1] in formats:
            files.append(current_path)
    return files

def generateSummary(path):
    vehicle_list = ['003', '009', '010', '011', '012', '013', '014', '016', '017']
    times = 0
    for id in vehicle_list:
        vehicle_id = "CN-" + id
        download_path = os.path.join(path, vehicle_id, "novatel")
        json_files = GetMatchedFilePaths(download_path,"*",[".json"],True)
        if json_files == []:
            continue
        json_tag = loadTag(json_files[0],'')
        times+=len(json_tag["details"][vehicle_id]["novatel"])
    print(times)



def main():
    log_path = "/home/sensetime/ws/.sensor_check_summary/"
    wgetLog(log_path)
    generateSummary(log_path)




if __name__ == '__main__':
    main()