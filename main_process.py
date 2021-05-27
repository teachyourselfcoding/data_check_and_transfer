# coding=utf-8
"""
main_process.py
data evluate, check and upload
zhengyaocheng@sensetime.com
input:FieldTest/$No.
2020-10-23
"""
import os
import sys
import copy
import time
import json
import shutil
import datetime
import fnmatch
import logging
import requests
import traceback
import multiprocessing
import cut_rec_multiprocess
import adas_pipeline

from tools import generate_data_report

from collections import defaultdict, deque
from awscli.clidriver import create_clidriver
from threadpool import ThreadPool, makeRequests
from case_tagging.case_tagging_brake import BrakeCaseTagging
from tools import read_and_write_json
from read_and_write_json import loadTag,saveTag,getTime,getFileSize
from modules_evaluation import generate_evaluation_result, \
    prediction_evaluation_iteration, tprofile_eval
from case_toss.toss_mian_process import TossMain
from case_tagging.tagging_main_process import TaggingMain

datapath = "/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect"


# reload(sys)
# sys.setdefaultencoding('utf8')


# aws transfer tool
AWS_DRIVER = create_clidriver()

# get the date and time
DATE = datetime.datetime.now().strftime('%Y-%m-%d')
upload_recursive = " --profile ad_system_common --recursive --only-show-errors --endpoint-url="
data_month = datetime.datetime.now().strftime('%Y_%m')

# log the transferred file path
def logger(level, str, LOG_FILE='upload_list/fieldtest_upload_list.log'):
    if not os.path.exists(LOG_FILE):
        os.mknod(LOG_FILE)
    try:
        with open(LOG_FILE, 'a') as logFd:
            logFd.write(
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                + ": " + ("Writing " if level else "NOTICE ") + str)
            logFd.write("\n")
    except:
        print ("\033[1;31m [ERROR]\033[0m open log file failed")


class DataCollectionUpload():
    '''
    class to check,evaluation,sgement,upload data
    '''

    def __init__(self, path):
        self.input_data_path = path
        self.file_list = deque()
        self.getAllDataDir()
        self.post = True
        self.backup_tag_list = self.getAllBackUpTag(path)
        self.tag_info = defaultdict(lambda: {})

        self.check_true_file_list = []
        self.check_false_file_list = []
        self.false_check_reasion = []

        self.auto_module_ = loadTag('config/auto_module.json','')
        self.config_ = loadTag('config/data_pipeline_config.json', '')
        self.end_point_30 = self.config_["end_point_30"]
        self.end_point_40 = self.config_["end_point_40"]
        self.end_point_21 = self.config_["end_point_21"]
        self.end_point = self.end_point_21
        self.check_file_name_list = self.config_["check_file"]

        self.headerdata = {"Data-tag-type": "application/json"}
        self.tag_module_list = loadTag(tag_file_name='config/tag_module.json') # special manual tagging, take over, dangerous driving etc
        self.tprofile_thresh = loadTag('config/tprofile_thresh.json', '')
        self.readShellFile('config/download_logs.sh')
        self.pool = ThreadPool(int(multiprocessing.cpu_count() * 0.6))
        self.auto_module_ = loadTag('config/auto_module.json', '')
        self.pred_eval_thresh = loadTag('config/pred_eval_thresh.json','')
        self.case_tagging = TaggingMain(self.pool, self.config_,self.auto_module_,self.tag_module_list)
        self.case_toss = TossMain(self.config_,self.auto_module_,self.pred_eval_thresh)

    def getAllBackUpTag(self, path):
        pattern = "data-tag*"
        format = [".json"]
        return self.getMatchedFilePaths(path, pattern, format, False)

    def readShellFile(self, file_path):
        if not os.path.exists(file_path):
            return
        with open(file_path) as f:
            self.download_logs = f.read()

    def getAllDataDir(self):
        for file in os.listdir(self.input_data_path):
            if self.cullArchiveDir(file):
                continue
            dir_file = os.path.join(self.input_data_path, file)
            if (os.path.isdir(dir_file)):
                h = os.path.split(dir_file)
                self.file_list.append(h[1])
        self.file_list = sorted(self.file_list)


    def cullArchiveDir(self, file):
        '''
        cull the dir which is for data archive
        :param file: file name
        '''
        try:
            archive = file.split('_')[-1]
            if archive in ['ARH', 'slice']:
                return True
        except Exception as e:
            logger(1, str(e), LOG_FILE="upload_list/error.log")
            logging.exception(e)
        return False

    def deterDirProperty(self, dir_path):
        "determine file property according the tag"
        tag_data = loadTag(dir_path)
        tag_list = ["origin_record_tag", "task_id", "test_car_id", "issue_id"]
        if tag_data is None or any(tag not in tag_data for tag in tag_list):
            tag_data = self.matchBackUpTag(dir_path)
            if tag_data is None or tag_data == []:
                tag_data = self.generateTag(dir_path)
        return tag_data

    def matchBackUpTag(self, dir_path):
        try:
            dir_name = os.path.basename(dir_path)
            test_time_list = dir_name.split('_')
            if test_time_list[-1] != "AutoCollect":
                return None
            test_time = [int(test_time_list[i]) for i in range(1, 5)]

            for backup_tag in self.backup_tag_list:
                backup_tag_name = os.path.basename(backup_tag)
                tag_time_str = backup_tag_name.split('(')[1].split(')')[0]
                tag_time = tag_time_str.split('-')

                clock_list = [43200, 1440, 60, 1]
                tag_gap = 0
                for i, clock_time in enumerate(clock_list):
                    add_time = 1
                    tag_gap += (test_time[i] - int(tag_time[i])) * clock_time

                if abs(tag_gap) < 4 and add_time > 0:
                    print(getTime()+"\033[1;32m [INFO]\033[0m", test_time, tag_time)
                    tag_data = loadTag(self.input_data_path, backup_tag)
                    return tag_data
            return None
        except Exception as e:
            print (getTime()+"\033[1;31m [ERROR]\033[0m backup tag not found")

    def generateTag(self, dir_path):
        generated_tag = loadTag("config/default_data-tag.json",'')
        dir_name = os.path.basename(dir_path)
        generated_tag["file_name"] = dir_name
        if len(dir_name) > 10:
            generated_tag["test_date"] = dir_name[0:10]
        saveTag(dir_path, generated_tag)
        return generated_tag

    def main(self, upload=False):
        '''
        main pipeline for collected data check & segment & upload
        :param upload: whether upload
        '''

        start_time = time.time()
        print(getTime()+"\033[1;32m [INFO]\033[0m Starting EVERYTHING")
        self.mainSegment(self.file_list, upload)
        print(getTime() + "\033[1;32m [INFO]\033[0m Finished everything , consuming {:.3f}s".format(
            time.time() - start_time))


    def mainSegment(self, file_list, upload=False):
        '''
        :param dir_name: the dir to be process
        :param upload: whether upload , default as False
        :return: o -> right ; 1-> error
        '''

        dir_path = self.input_data_path
        # dir_path = os.path.join(self.input_data_path, dir_name)

        # check the dir whether right
        check_result, self.false_reason = self.checkRec(dir_path)

        for dir_name in file_list:
            # get the data-tag.json of checked dir
            tag_data = self.deterDirProperty(dir_path)
            if not check_result:
                if 'test_type' in tag_data.keys() and tag_data['test_type'] ==3:
                    pass
                if "issue_id" not in tag_data.keys() or tag_data["issue_id"] == []:
                    tag_data["issue_id"] = ["feature"]
                if tag_data is not None and tag_data["issue_id"] != ["repo_master"] and tag_data["task_id"] != 30000:
                    pass
                else:
                    self.falseDataArchive(dir_path, self.false_reason)
                    return

            if "backup" in tag_data:
                tag_data = tag_data["backup"][0]["data_tag"]
            tag_data["test_date"] = tag_data["test_date"].replace('-', '_')
            if tag_data is None:
                return 1
            if not "global_tag" in tag_data:
                tag_data["global_tag"] = []

            ## generate evluation result with different module
            if tag_data["test_type"] == 1 and self.config_["evaluation"]:
                pool1 = multiprocessing.Pool(processes=12)
                pool1.apply_async(generate_evaluation_result.generateLocalizationEval, args=(dir_path,self.config_,))
                pool1.close()
                pool1.join()
                # try:
                #     generate_evaluation_result.generateTprofileEval(dir_path,self.config_)
                # except Exception as e:
                #     print getTime()+"\033[1;31m [ERROR]\033[0m tprofiling error "
            if "issue_id" not in tag_data.keys() or tag_data["issue_id"] == []:
                tag_data["issue_id"] = ["feature"]
                saveTag(dir_path, tag_data)

            self.tag_info = tag_data
            self.tag_info["localization_result"] = self.getLocalizationResult(dir_path.replace(" ", ""))
            self.tag_info["control_result"] = {}
            self.tag_info["ap_result"] = {}
            self.tag_info["file_name"] = dir_name
            self.tag_info["disk_id"] = self.getDiskId(dir_path)
            self.addEvalTag(dir_path)
            self.tag_info["origin_record_tag"] = self.deDuplication(self.tag_info["origin_record_tag"])
            saveTag(dir_path, self.tag_info)
            self.post = True
            segment, upload = self.judgeIfSegmentAndUpload(self.tag_info,check_result)

        try:
            if self.tag_info["test_type"] == 2 and self.tag_info["issue_id"] == ["AUTODRIVE-6814"]:
                overlap = self.reouteCheckFi(dir_path, self.tag_info["test_car_id"])
                self.tag_info['global_tag'].append(overlap)
                try:
                    self.tag_info = self.getObjectNumber(dir_path,self.tag_info)
                except:
                    pass
                if None in self.tag_info['global_tag']:
                    self.tag_info['global_tag'].remove(None)
                saveTag(dir_path, self.tag_info)

            if segment:
                self.segmentPreprationCollection(dir_name)

            self.mainUpload(dir_path,upload)

        except Exception as e:
            print (traceback.format_exc())
            logger(1, str(e), LOG_FILE="upload_list/error.log")
            print (getTime()+"\033[1;31m [ERROR]\033[0m segment or upload error ")
            return 1
        return 0

    def getDiskId(self,dir_path):
        if  'FieldTest' not in dir_path or 'data' not in dir_path:
            return '000000'
        disk_path = dir_path.split('data')[0]
        disk_id = cut_rec_multiprocess.GetMatchedFilePaths(disk_path,"*",[".id"],False)
        if disk_id ==[]:
            return '000000'
        id = os.path.basename(disk_id[0]).split('.')[0]
        return str(id)

    def getObjectNumber(self,dir_path,tag_info):

        object_count = loadTag(dir_path, 'object_count.json')
        number = 0
        for count in object_count["Object_number"]:
            for a in count:
                number += count[a]
        object_size = number / len(object_count["Object_number"])

        if object_size < 800:
            tag_info['global_tag'].append("fewer_objects")
        elif object_size > 800 and object_size < 1800:
            tag_info['global_tag'].append("normal_objects")
        elif object_size > 1800:
            tag_info['global_tag'].append("many_objects")
        tag_info['global_tag'] = list(set(self.tag_info['global_tag']))
        return tag_info

    def deDuplication(self,list):
        result_list = []
        for record_tag in list:
            record_tag["tag_en"] = record_tag["tag_en"].replace(' ', '_')
            if record_tag not in result_list:
                result_list.append(record_tag)
        return result_list


    def judgeIfSegmentAndUpload(self,data_tag,check_result):

        def judgeifInclude(include_ele, tag_ele):
            if not tag_ele in self.tag_info:
                return False
            if (isinstance(self.tag_info[tag_ele], list)):
                if any(element == include_ele for element in self.tag_info[tag_ele]):
                    return True
            else:
                if self.tag_info[tag_ele] == include_ele:
                    return True
            return False
        segment = False
        upload = True
        if data_tag["test_type"] == 1 and data_tag["issue_id"][0] == "repo_master":
            segment = self.config_["segment_and_upload"]["master_segment"]
            upload = self.config_["segment_and_upload"]["master_upload"]
        elif data_tag["test_type"] == 1 and data_tag["issue_id"][0] != "repo_master":
            if check_result:
                segment = self.config_["segment_and_upload"]["feature_segment"]
            upload = self.config_["segment_and_upload"]["feature_upload"]
        elif data_tag["test_type"] == 2:
            segment = self.config_["segment_and_upload"]["collection_segment"]
            upload = self.config_["segment_and_upload"]["collection_upload"]
        for tag_ele in self.config_["include_segment"]:
            if any(judgeifInclude(include_ele, tag_ele) for include_ele in self.config_["include_segment"][tag_ele]):
                segment = True
        return segment, upload

    def mainUpload(self, dir_path,upload):
        '''
        upload and then archive data
        :param dir_path_without: data path end without /
        '''
        print("checkpoint36")
        print(dir_path)
        tag_info = loadTag(dir_path)
        print(tag_info)
        dir_name = os.path.split(dir_path)[1]
        print(dir_name)
        try:
            self.data_upload(dir_path, tag_info, slice=False,upload = upload)
            archive_path = self.dirArchive(dir_path, tag_info)
            generate_data_report.main(archive_path + '/' + dir_name, True)
            if os.path.exists(dir_path + "_slice/"):
                self.data_upload(dir_path, tag_info, slice=True,upload = upload)
                self.dirArchive(dir_path + "_slice", tag_info)
            return 0
        except Exception as e:
            print (traceback.format_exc())
            logger(1, str(e), LOG_FILE="upload_list/error.log")
            print (getTime()+"\033[1;31m [ERROR]\033[0m upload error ")
            return 1

    def falseDataArchive(self, dir_path, false_reason):
        try:
            #generate_data_report.main(dir_path, False, false_reason)
            self.falseDataUpload(dir_path)
            self.dirArchive(dir_path, tag_info=None, check_result=False)
            return 1
        except Exception as e:
            logger(1, str(e), LOG_FILE="upload_list/error.log")
            print (getTime()+"\033[1;31m [ERROR]\033[0m archive error ")
        return 1

    def addTprofileLabelToCase(self, tprofile_label, tag_data):

        result_case = []
        case_list = tag_data["origin_record_tag"]
        for case in case_list:
            if "end" in case:
                start = case["start"]
                end = case["end"]
            else:
                start = case["start"] - 10000
                end = case["start"] - 5000
            if not "labels" in case:
                case["labels"] = []
            for time, label in tprofile_label.items():
                if int(time) > int(start) and int(time) < int(end):
                    case["labels"].append(label)
            case["labels"] = list(set(case["labels"]))
            result_case.append(case)
        tag_data["origin_record_tag"] = result_case
        return tag_data

    def reouteCheckFi(self, input_path, vehicle_id):
        try:
            rec_parser = os.path.join(self.config_["senseauto_path"],"tools/rec_parser/scripts/offline_data_process.sh")
            output_path = os.path.join(input_path, 'rec_parser')
            config_path = os.path.join(self.config_["senseauto_path"],"system/config/vehicle/", vehicle_id)
            enu_config_path = os.path.join(self.config_["senseauto_path"],"tools/rec_parser/config/sh_enu_origin.txt")
            rec_parse_cmd = "bash {} -i {} -o {} -c {} -e {}".format(
                rec_parser, input_path, output_path, config_path, enu_config_path)
            gps_file = os.path.join(output_path, 'gps.txt')
            os.system(rec_parse_cmd)
            with open(gps_file, 'r') as r:
                lines = r.readlines()
            with open(gps_file, 'w') as fw:
                for l in lines:
                    if "GPS-time" in l:
                        continue
                    items = l.split(',')[1:3]
                    a = items[1]
                    items[1] = items[0].replace("\n", "")
                    items[0] = a.replace("\n", "")
                    items = ''.join(["unknown unknown unknown unknown unknown ", str(items[0]), ', ',
                                     str(items[1]) + ", unknown\n"])
                    fw.write(items)
            os.system(
                "python3 ~/Codes/RouteMeFi-master/routemefi.py --input_path " + gps_file +
                " --db_path ~/Codes/sh_gps/database.txt --save_dir ~/Codes/sh_gps/ --query_merge")
            record_tag = {}
            record_tag["input_dir"] = input_path
            record_tag["tagging_module"] = 0
            self.case_tagging.tag_main(self.tag_info['global_tag'],input_path, [record_tag])
            overlap_json = loadTag(output_path, 'overlap_result.json')
            return 'overlap_' + str(overlap_json["overlapped"])
        except Exception as e:
            print (getTime()+"\033[1;31m [ERROR]\033[0m get ins info error ")

    def checkRec(self, dir_path, slice=False):
        # looks through the following folders: cache, config, cv22, logs, screen_cast, sensor_logs
        #    sensors_record, timing logger, versions
        print(dir_path)
        '''
        :param dir_path: data path end with /
        :param slice: define the checking data is raw data or segment data
        :return: True of False
        '''
        video_result = 0
        check_result = 0
        try:
            check_tag = loadTag(dir_path, 'data-tag.json')
            if check_tag is not None and check_tag["test_car_id"] == "CN-001":
                return True, []
            if check_tag is not None and (check_tag["test_car_id"] == "CN-006" or check_tag["test_car_id"] == "CN-007"):
                check_result+=1
        except Exception as e:
            print (getTime()+"\033[1;31m [ERROR]\033[0m not CN-001 data ")

        self.false_check_reasion = []
        false_reason = []
        if not os.path.exists(dir_path):
            return False, false_reason
        for file_name in self.check_file_name_list:
            check_size = self.check_file_name_list[file_name]
            reult_0_1 = self.judgeFileSizeAndExist(dir_path, file_name, check_size=check_size)
            check_result += reult_0_1
            if reult_0_1 == 0:
                false_reason.append(file_name)
        pattern = "port_*"

        video_files = self.getMatchedFilePaths(dir_path, pattern, formats=[".avi",".h264", "mp4"], recursive=True)

        for video_name in video_files:
            video_reult_0_1 = self.judgeFileSizeAndExist(dir_path='', file_name=video_name, check_size=1)
            video_result += video_reult_0_1
            if video_reult_0_1 == 0:
                false_reason.append(file_name)

        for dir_name in ['cache', 'config', 'logs', 'timing_logger']:
            log_dir_path = os.path.join(dir_path, dir_name)
            if not os.path.exists(log_dir_path):
                false_reason.append("cache")

        if check_result >= 4 and video_result > 0:
            print (getTime()+"\033[1;32m [INFO]\033[0m Dir:", dir_path, "is \033[1;32m correct\033[0m")
            return True, false_reason
        else:
            print (getTime()+"\033[1;31m [ERROR]\033[0m Dir:", dir_path, "is\033[1;31m wrong\033[0m")
            return False, false_reason

    def judgeFileSizeAndExist(self, dir_path, file_name, check_size=0.2):
        "as the function name descripted"
        judge_file = os.path.join(dir_path, file_name)
        if os.path.exists(judge_file) and \
                round(os.path.getsize(judge_file) / float(1024 * 1024), 1) >= check_size:
                    # print("no error, filesize:")
                    # print(os.path.getsize(judge_file))
                    return 1
        else:
            self.false_check_reasion.append(file_name)
            return 0

    def addEvalTag(self, dir_path):
        "add the evaluation result to tag"
        self.local_eval_tag = generate_evaluation_result.getLocalEvalResult(dir_path)
        self.control_eval_tag = generate_evaluation_result.getControlEvalResult(dir_path)
        if self.local_eval_tag is not None:
            for case_tag in self.local_eval_tag:
                self.tag_info["origin_record_tag"].append(case_tag)
        if self.control_eval_tag is not None:
            for case_tag in self.control_eval_tag:
                self.tag_info["origin_record_tag"].append(case_tag)

    def rename_screen_files(self, dir_path):
        "rename screen cast videos"
        screen_files = self.getMatchedFilePaths(dir_path, formats=[".mp4"], recursive=False)
        for id, old_screen_video in enumerate(screen_files):
            new_name = ''.join([dir_path, str(id + 5), '.mp4'])
            os.rename(old_screen_video, new_name)
            print(old_screen_video, '======>', new_name)

    def getMatchedFilePaths(self, dir_path, pattern="*", formats=[".avi"], recursive=False):
        "get all the files in <dir_path> with specified pattern"
        files = []
        data_dir = os.path.normpath(os.path.abspath(dir_path))
        try:
            for f in os.listdir(data_dir):
                current_path = os.path.join(os.path.normpath(data_dir), f)
                if os.path.isdir(current_path) and recursive:
                    files += self.getMatchedFilePaths(current_path, pattern, formats,
                                                      recursive)
                elif fnmatch.fnmatch(f,
                                     pattern) and os.path.splitext(f)[-1] in formats:
                    files.append(current_path)
            return files
        except OSError:
            print("os error")
            return []

    def segmentPreprationCollection(self, dir_name):

        if "origin_record_tag" in self.tag_info and self.tag_info["origin_record_tag"] != []:
            segment_point = self.tag_info["origin_record_tag"]
            # segment points have many sets of data (refer to 24 april data file)
        else:
            return 0
        self.dataSegment(dir_name, segment_point)

    def dataSegment(self, dir_name, segment_point):
        "data segment pipeline"
        segment_list = []
        case_tagging_list = []
        prediction_tagging_list = []
        for record_tag in segment_point: # record_tag is every set
            #dir_path = os.path.join(self.input_data_path, dir_name)
            dir_path = self.input_data_path
            tag_name = record_tag.get("tag_en")  # tag_name = cloudyday etc

            if not tag_name in self.tag_module_list: # special manual tagging, take over, dangerous driving etc
                if "data_type" in record_tag and record_tag["data_type"] == "eval":
                    level_name, log_type, tagging_module = ["EVAL", 0, 1]
                else:
                    level_name, log_type, tagging_module = ["3D-Perception", 0, 1]
                if self.tag_info['test_type'] == 3:
                    level_name, log_type, tagging_module = ["ADAS", 0, 1]
            else:
                level_name = self.tag_module_list[tag_name]["level_name"]
                log_type = self.tag_module_list[tag_name]["log_type"]
                tagging_module = self.tag_module_list[tag_name]["tagging_module"]
            print (getTime()+"\033[1;32m [INFO] \033[0m", level_name, "==>> ", tag_name, "==== module_type:", log_type)

            if "end" in record_tag:
                front_time = 2
                behind_time = (record_tag["end"] - record_tag["start"]) // 1000
            else:
                if not tag_name in self.tag_module_list:
                    front_time = 20
                    behind_time = 10
                else:
                    front_time = self.tag_module_list[tag_name]["front_time"]
                    behind_time = self.tag_module_list[tag_name]["behind_time"]

            if behind_time < 6:
                behind_time = 10

            if "end" in record_tag:
                input_timestamp = (record_tag["start"] + record_tag["end"]) / 2000
            else:
                input_timestamp = record_tag["start"] / 1000

            time_point = record_tag["start"] * 1000
            test_date = self.tag_info["test_date"]
            test_time = str(record_tag["start_format"].replace(":", "_"))
            segment_dir_name = ''.join([test_date, '_', test_time])

            output_path = ''.join([dir_path, '_slice/', level_name, '/', tag_name, '/', segment_dir_name])

            if self.tag_info["issue_id"][0] != "repo_master" and \
                (record_tag['tag_en'] == "take_over" or record_tag['tag_en'] == "Emergency_brake"):
                segment_list.append({"output_dir": output_path,
                                     "time_point": time_point,
                                     "front_duration": front_time,
                                     "behind_duration": behind_time,
                                     "log_type": log_type})
            else:
                segment_list.append({"output_dir": output_path,
                                     "time_point": time_point,
                                     "front_duration": front_time,
                                     "behind_duration": behind_time,
                                     "log_type": log_type})
            if level_name != "EVAL":
                case_tagging_list.append({"input_dir": ''.join([output_path, '/']),
                                          "module_name": tag_name,
                                          "input_timestamp": input_timestamp,
                                          "tagging_module": tagging_module})
            if tag_name == "abnormal_prediction_trajectory":
                prediction_tagging_list.append({"input_dir": ''.join([output_path, '/']),
                                                "module_name": tag_name,
                                                "input_timestamp": input_timestamp})


            if not os.path.exists(output_path):

                os.makedirs(output_path)

            task_id = '' if self.tag_info["issue_id"][0] == "repo_master" else str(self.tag_info["task_id"]) + '/'

            vehicle_id = self.tag_info["test_car_id"].replace("-", "")
            module_tag_data = copy.deepcopy(self.tag_info)
            data_month = self.tag_info["test_date"].rsplit("_", 1)[0]
            dst_path = ''.join([self.getDataCollectionDstLink(self.tag_info, data_month, slice=True),
                                self.tag_info["test_date"],
                                '/', vehicle_id,
                                '/', task_id])
            module_tag_data["data_link"] = ''.join([dst_path, level_name, '/', tag_name, '/', segment_dir_name])
            store_path = ''.join([dir_path, '_slice/', level_name, '/', tag_name, '/', segment_dir_name])
            module_tag_data["origin_record_tag"] = [record_tag]
            if "data_type" in record_tag and record_tag["data_type"] == "eval":
                module_tag_data["data_type"] = record_tag["data_type"]
                module_tag_data["data_type"] = "segment"
                module_tag_data["test_type"] = 9
                self.post = True
            else:
                module_tag_data["data_type"] = "segment"
            module_tag_data["file_name"] = segment_dir_name
            module_tag_data["raw_data_link"] = ''.join(
                [self.getDataCollectionDstLink(self.tag_info, data_month, slice=False),
                 self.tag_info["test_date"],
                 '/', vehicle_id, '/',
                 task_id, dir_name])
            module_tag_data['aws_endpoint'] = self.end_point
            saveTag(store_path, module_tag_data, file_name='data-tag.json')
            self.generateLogDownloadFile(log_type, module_tag_data["raw_data_link"], output_path)

        cut_rec_multiprocess.main(dir_path, segment_list)

        if self.tag_info["test_type"] == 1:
            self.case_tagging.tagMain(self.tag_info["global_tag"],dir_path,case_tagging_list)

    def generateLogDownloadFile(self, log_type, raw_data_link, output_path):
        if not os.path.exists(output_path + "/logs"):
            os.makedirs(output_path + "/logs")
        profile = " --profile ad_system_common "
        log_download_instruction = ''.join(
            ["aws s3 cp", upload_recursive, self.end_point, profile, raw_data_link + '/logs', ' ', "$this_dir/"])
        download_logs = self.download_logs
        download_logs += log_download_instruction
        download_logs += '\n'
        with open(os.path.join(output_path, 'logs/download_logs.sh'), 'w') as f:
            f.write(download_logs)

    def data_upload(self, dir_path, tag_info, slice=False, upload = True):
        'data_upload with aws'
        dir_name = os.path.split(dir_path)[1]
        vehicle_id = tag_info["test_car_id"].replace("-", "")
        data_month = tag_info["test_date"].rsplit("_", 1)[0]

        try:
            feature = False if tag_info["issue_id"] == ["repo_master"] else True
        except Exception as e:
            feature = False
        task_id = str(tag_info["task_id"])+'/' if feature else ''
        if slice:
            upload_path = ''.join([dir_path, "_slice/ "])
            dst_path = ''.join([self.getDataCollectionDstLink(tag_info, data_month, slice=True),
                                tag_info["test_date"], '/',
                                vehicle_id, '/', task_id])
            self.sliceDataCheck(dir_path + '_slice/')
        else:
            upload_path = ''.join([dir_path, '/ '])
            tag_path = ''.join([self.getDataCollectionDstLink(tag_info, data_month, slice=False),
                                tag_info["test_date"], '/',
                                vehicle_id, '/',
                                task_id, dir_name])
            dst_path = ''.join([tag_path, '/'])
            tag_info["data_link"] = tag_path
            tag_info["data_type"] = "raw"
            tag_info['aws_endpoint'] = self.end_point
            if tag_info["test_type"] == 1:
                aa,eval_result = self.getPPEvalResult(tag_path)
                if aa:
                    tag_info["pp_evaluation"] = eval_result
            if tag_info["test_type"] == 3 and self.config_["evaluation"]:
                generate_evaluation_result.generateAdasEval(dir_path, self.config_)
                tag_info["adas_evaluation"] = self.getAdasResult(tag_path)
            try:
                if self.false_reason != []:
                    for false_check in self.false_reason:
                        tag_info["global_tag"].append("no_" + false_check)
                if self.tprfile_resut != []:
                    for tprofile in self.tprfile_resut:
                        tag_info["global_tag"].append(tprofile)
            except Exception as e:
                print ("write global tag error")

            saveTag(dir_path, tag_info, file_name='data-tag.json')

        arg2 = ''.join(["s3 cp ", upload_path, dst_path, upload_recursive + self.end_point])
        # arg_slam =''.join(["s3 cp ", os.path.join(dir_path,'logs/map_update_areas.json '),
        #                   "s3://sz21_data_collection/slam_file/"+data_month+'/'+tag_info["test_date"]+'/'+
        #                    vehicle_id+'/'+task_id+dir_name+'/'+tag_info.get("route")+'/map_update_areas.json',
        #                   " --profile ad_system_common --only-show-errors --endpoint-url=" + self.end_point])
        print (getTime()+"\033[1;32m [INFO] Uploading ...\033[0m ", arg2)
        if upload:
            star_upload_time = time.time()
            file_size = getFileSize(upload_path.replace(' ',''))
            upload_result = AWS_DRIVER.main(arg2.split())
            # AWS_DRIVER.main(arg_slam.split())
            cost_time = time.time()-star_upload_time
            upload_speed = file_size/cost_time
            logger(1, "Uploaded dir:" + upload_path)
            if upload_result == 0:
                print (getTime()+"\033[1;32m [INFO]", dir_name + \
                     "\033[0m", "\033[0m has\033[1;32m uploaded successfully! Speed:\033[0m "+ str(upload_speed) +" MB/s")
            else:
                print (getTime()+"\033[1;32m [INFO]", dir_name + "\033[0m", "\033[0m \033[1;32m upload failed!\033[0m")
        self.TransferPost(tag_info)

    def falseDataUpload(self, dir_path):
        false_data_tag = loadTag(dir_path, 'data_tag.json')
        dir_name = os.path.split(dir_path)[1]
        upload_path = ''.join([dir_path, '/ '])
        dst_path = ''.join([self.config_["upload_path"]["false"], data_month, '/false_data/', dir_name])
        arg2 = ''.join(["s3 cp ", upload_path, dst_path, upload_recursive + self.end_point])
        print(arg2)
        AWS_DRIVER.main(arg2.split())
        if false_data_tag is not None and false_data_tag["issue_id"] != ["repo_master"]:
            false_data_tag["data_link"] = dst_path
            false_data_tag["data_type"] = "raw"
            self.TransferPost(self, false_data_tag)

    def sliceDataCheck(self, dir_path):
        "segmented data check and post"
        data_tag_paths = self.getMatchedFilePaths(dir_path, pattern="data-ta*", formats=[".json"], recursive=True)
        for slice_data_tag_path in data_tag_paths:
            slice_data_path = os.path.split(slice_data_tag_path)[0]
            check_result,false_reason = self.checkRec(slice_data_path, slice=True)
            slice_data_tag = loadTag(slice_data_tag_path,'')
            record_tag = slice_data_tag["origin_record_tag"][0]
            slice_data_tag["origin_record_tag"] = \
                [self.case_toss.mainToss(self.local_eval_tag,os.path.split(slice_data_tag_path)[0],
                                         record_tag,slice_data_tag)]
            saveTag(slice_data_tag_path,slice_data_tag,'')
            if self.tag_info['master'] == False:
                pass
            else:
                if not check_result:
                    saveTag('upload_list/false_segment',slice_data_tag,slice_data_tag["file_name"]+'.json')
                    continue
            if self.tag_info['test_type'] ==3 and not os.path.exists(os.path.split(slice_data_tag_path)[0]+'/cv22'):
                continue
            self.TransferPost(slice_data_tag)

    def getDataCollectionDstLink(self, tag_info, data_month, slice):
        '''
        get the upload path of the dir
        :param tag_info:
        :param data_month:
        :param slice:
        :return:
        '''

        if tag_info["test_type"] == 2:
            if slice:
                return os.path.join(self.config_["upload_path"]["collection"], data_month, "segment_data/")
            else:
                return os.path.join(self.config_["upload_path"]["collection"], data_month, "raw_data/")
        elif tag_info["test_type"] == 3:
            if slice:
                return os.path.join(self.config_["upload_path"]["adas"], data_month, "segment_data/")
            else:
                return os.path.join(self.config_["upload_path"]["adas"], data_month, "raw_data/")
        if tag_info["issue_id"][0] == "repo_master":
            if slice:
                return os.path.join(self.config_["upload_path"]["master"], data_month, "master/segment_data/")
            else:
                return os.path.join(self.config_["upload_path"]["master"], data_month, "master/raw_data/")
        else:
            if slice:
                return os.path.join(self.config_["upload_path"]["feature"], data_month, "feature/segment_data/")
            else:
                return os.path.join(self.config_["upload_path"]["feature"], data_month, "feature/raw_data/")

    def getLocalizationResult(self, dir_path):
        '''get the localization result'''
        localization_result = defaultdict(lambda: {})
        result_file_path = os.path.join(dir_path, 'logs/localization_eval')
        localization_json = loadTag(result_file_path, tag_file_name='evaluation_result.json')
        if localization_json is not None:
            try:
                localization_result["Grade"] = localization_json["Grade"]
                localization_result["Integrity"] = localization_json["Integrity"]
                localization_result["Odometer(km)"] = localization_json["Odometer(km)"]
                localization_result["Setting"] = localization_json["Setting"]
                localization_result["Mileage(km)"] = localization_json.get("Mileage(km)")
                localization_result["Mileage(km)"] = localization_json.get("Mileage(km)")
                localization_result["Stability"] = localization_json.get("Stability")
                localization_result["Tags_Num"] = localization_json.get("Tags_Num")
                if localization_json.get("Odometer(km)") > 1.0 and localization_json.get("Odometer(km)") < 100.0:
                    self.tag_info["test_mileage"] = localization_json.get("Odometer(km)")
            except Exception as e:
                print (getTime()+"\033[1;31m [ERROR]\033[0m get LMR eval info error ")
        if self.tag_info["test_mileage"] < 1.0 or self.tag_info["test_mileage"] > 100.0:
            self.tag_info["test_mileage"] = 18.0
        return localization_result

    def getControlResult(self, dir_path):
        "add the control evaluation result to tag"

        control_result = defaultdict(lambda: {})
        result_file_path = os.path.join(dir_path, 'logs/control_eval')
        control_json = loadTag(result_file_path, tag_file_name='control_eval_results.json')

        if control_json is not None:
            try:
                control_result = control_json["control_result"]
                if 'stop_error' in control_result['control_precision']:
                    control_result['control_precision']['stop_error']['std'] = 0.901
            except Exception as e:
                logger(1, str(e), LOG_FILE="upload_list/error.log")
                print (getTime()+"\033[1;31m [ERROR]\033[0m get control eval info error ")
        return control_result

    def getPredictionResult(self, dir_path):
        "add the control evaluation result to tag"

        ap_result = defaultdict(lambda: {})
        result_file_path = os.path.join(dir_path, 'prediction_evaluation/result')
        ap_json = loadTag(result_file_path, tag_file_name='result.json')

        if ap_json is not None:
            try:
                ap_result["quality"] = ap_json["quality"]
            except Exception as e:
                logger(1, str(e), LOG_FILE="upload_list/error.log")
                print (getTime()+"\033[1;31m [ERROR]\033[0m get ap eval info error ")
                ap_result["quality"] = {}
                ap_result["quality"]['level'] = "bad"
        return ap_result

    def getAdasResult(self,dir_path):
        adas_evaluation = {}
        result_file_path = os.path.join(dir_path,'logs/adas_online_eval/result_overall.json')
        adas_evaluation["result_overall"] =  result_file_path
        return adas_evaluation

    def getPPEvalResult(self,dir_path):
        pp_evaluation = {}
        eval_json = os.path.join(dir_path,'logs/pp_eval/pp_evaluation.json')
        if os.path.exists(eval_json):
            pp_evaluation["result_path"] =  eval_json
            return True, pp_evaluation
        else:
            pp_evaluation["result_path"] = ""
            return False, pp_evaluation

    def TransferPost(self, data_tag):
        "post the data tag to senseFT"
        curl = \
            'https://fieldtest.sensetime.com/task/daemon/update/tag'
        post_result = requests.post(curl, headers=self.headerdata, data=json.dumps(data_tag))
        print (getTime()+"\033[1;32m [INFO]\033[0m ", post_result.text,'\n')
        if post_result.text != u'{"result":"true"}':
            try:
                logger(2, "Uploaded dir:" + data_tag["data_link"], LOG_FILE="upload_list/post_failed_file.log")
                saveTag('upload_list/', data_tag, data_tag["file_name"] + '.json')
            except Exception as e:
                print (getTime()+"\033[1;31m [ERROR]\033[0m save post-failed tag error ")

    def dirArchive(self, dir_path, tag_info, check_result=True):
        "archive the dri which has been uploaded"
        input_data_path, dir_name = os.path.split(dir_path)

        if not check_result:
            try:
                date_id = ''.join(['/False_', dir_name.split('_', -1)[1], '_', dir_name.split('_', -1)[2]])
            except Exception as e:
                date_id = '/False_ARH'
            archive_path = ''.join([input_data_path, date_id, '_ARH'])
            if not os.path.exists(archive_path):
                os.makedirs(archive_path)
            try:
                shutil.move(input_data_path + '/' + dir_name, archive_path)

            except Exception as e:
                print("checkpoint1001")
                print (getTime()+"\033[1;31m [ERROR]\033[0m move dir to ARH failed ")
            return archive_path
        else:
            test_date = tag_info["test_date"].split('_', 1)[1]
            try:
                date_id = ''.join(['/', test_date, '_', tag_info["test_car_id"]])
            except Exception as e:
                date_id = 'True_ARH'
            archive_path = ''.join([input_data_path, date_id, '_ARH'])
            if not os.path.exists(archive_path):
                os.makedirs(archive_path)
            try:
                shutil.move(''.join([input_data_path, '/', dir_name]), archive_path)
            except Exception as e:
                print("checkpoint1002")
                print (getTime()+"\033[1;31m [ERROR]\033[0m move dir to ARH failed ")
            return archive_path


if __name__ == "__main__":

    if len(sys.argv) < 2:
        data_path = datapath
    else:
        data_path = datapath

    if not os.path.exists(data_path):
        pass
        # raise ValueError("========== : {} does NOT exist".format(data_path))
    command = ''.join(['sudo chown -R trajic ', data_path]) # Needs to be edited
    os.system('echo %s | sudo -S %s' % ('Invincible49', 'sudo chown -R trajic "/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect"')) # Needs to be edited
    data_check_class = DataCollectionUpload(data_path)
    data_check_class.main(upload=True)




