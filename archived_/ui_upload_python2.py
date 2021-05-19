# coding=utf-8
"""
data_check.py
check the data format before upload
by Zheng Yaocheng
zhengyaocheng@sensetime.com
input:FieldTest/$No.
output:the dir to transfer
"""

import copy
import datetime
import fnmatch
import json
import logging
import multiprocessing
import os
import shutil
import sys
from collections import defaultdict, deque


import requests
from awscli.clidriver import create_clidriver
from threadpool import ThreadPool, makeRequests

import cut_rec_multiprocess
import generate_data_report
from modules_evaluation import generate_evaluation_result,prediction_evaluation_iteration,tprofile_eval
from brake_case_tagging import BrakeCaseTagging


# aws transfer tool
AWS_DRIVER = create_clidriver()

CHECK_CONFIG = 'data_check.json'

# get the date and time
DATE = datetime.datetime.now().strftime('%Y-%m-%d')
upload_recursive = " --recursive --endpoint-url="
end_point_30 = "http://10.5.41.189:9090"
end_point_40 = "http://10.5.41.234:80"
end_point = end_point_40

data_month = datetime.datetime.now().strftime('%Y_%m')


# log the transferred file path
def logger(level, str, LOG_FILE='upload_list/fieldtest_upload_list.log'):
    if not os.path.exists(LOG_FILE):
        os.mknod(LOG_FILE)
    try:
        logFd = open(LOG_FILE, 'a')
    except:
        logFd = open(LOG_FILE, 'a')
    logFd.write(
        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') + ": " + ("Writing " if level else "NOTICE ") + str)
    logFd.write("\n")
    logFd.close()


class DataCollectionUpload():
    '''
    class to check,evaluation,sgement,upload data
    '''

    def __init__(self, path):
        self.input_data_path = path
        self.file_list = deque()
        self.backup_tag_list = self.getMatchedFilePaths(path,"data-tag*", formats=[".json"], recursive=False)
        self.tag_info = defaultdict(lambda: {})
        self.getAllDataDir()
        self.tag_file_name = '/data-tag.json'
        self.headerdata = {"Data-tag-type": "application/json"}
        self.check_file_name_list = self.loadTag(tag_file_name='../config/data_check.json')
        self.tag_module_list = self.loadTag(tag_file_name='../config/tag_module.json')
        self.post = True
        self.pool = ThreadPool(int(multiprocessing.cpu_count() * 0.6))
        self.check_true_file_list = []
        self.check_false_file_list = []
        self.false_check_reasion=[]
        self.case_tagging =  BrakeCaseTagging()
        self.tprofile_thresh = self.loadTag('../config/tprofile_thresh.json', '')
        self.readShellFile('../config/download_logs.sh')

    def loadTag(self, tag_file_path='', tag_file_name='data-tag.json'):
        "read json"
        if not os.path.exists(tag_file_path + tag_file_name):
            return None
        with open(tag_file_path + tag_file_name, 'r') as f:
            try:
                tag_data = json.load(f)
                return tag_data
            except ValueError:
                print(" ==== ", tag_file_path + tag_file_name,
                      "\033[1;31m is not valuable json bytes \033[0m!\n")
                return None

    def saveTag(self, tag_file_path, tag_data, file_name='data-tag.json'):
        "write json"
        tag_path_name = tag_file_path + file_name
        print(tag_path_name)
        if not os.path.exists(tag_file_path):
            os.mkdir(tag_file_path)
        if not os.path.exists(tag_path_name):
            os.mknod(tag_path_name)
        with open(tag_path_name, 'w') as fw:
            json.dump(tag_data, fw, indent=4)

    def readShellFile(self,file_path):
        if os.path.exists(file_path):
            with open(file_path) as f:
                self.download_logs = f.read()


    def getAllDataDir(self):
        "get all dir in data"
        for file in os.listdir(self.input_data_path):
            if self.cullArchiveDir(file):
                continue
            dir_file = os.path.join(self.input_data_path, file)

            if (os.path.isdir(dir_file)):
                h = os.path.split(dir_file)
                self.file_list.append(h[1])

    def cullArchiveDir(self, file):
        '''
        cull the dir which is for data archive
        :param file:
        :return:
        '''
        try:
            archive = file.split('_', -1)[-1]
            if archive == 'ARH' or archive == 'slice':
                return True
        except Exception as e:
            logger(1, str(e), LOG_FILE="../upload_list/error.log")
            logging.exception(e)
        return False

    def deterDirProperty(self, dir_path):
        "determine file property according the tag"
        tag_data = self.loadTag(dir_path)
        get_match_tag = False
        if tag_data is None:
            get_match_tag = True
        elif not "origin_record_tag" in tag_data.keys() \
            or not "task_id" in tag_data.keys() \
            or not "test_car_id" in tag_data.keys() \
            or not "issue_id" in tag_data.keys():
            get_match_tag = True
        if get_match_tag:
            tag_data = self.matchBackUpTag(dir_path)
            if tag_data is None or tag_data ==[]:
                tag_data = self.generateTag(dir_path)
            return tag_data
        else:
            return tag_data

    def matchBackUpTag(self,dir_path):
        try:
            dir_name = dir_path.split('/', -1)[-2]
            test_time_list = dir_name.split('_',-1)
            if test_time_list[-1] != "AutoCollect":
                return None
            test_time = [int(test_time_list[1]),
                         int(test_time_list[2]),
                         int(test_time_list[3]),
                         int(test_time_list[4])]
            for backup_tag in self.backup_tag_list:
                backup_tag_name  = os.path.basename(backup_tag)
                tag_time_str= backup_tag_name.split('(',-1)[1].split(')',-1)[0]
                tag_time = tag_time_str.split('-',-1)
                print(test_time,tag_time)
                tag_gap = (test_time[0]-int(tag_time[0]))*43200\
                        +(test_time[1]-int(tag_time[1]))*1440\
                        +(test_time[2] - int(tag_time[2])) * 60\
                        +(test_time[3] - int(tag_time[3]))
                print(tag_gap)
                if abs(tag_gap) < 4:
                    tag_data = self.loadTag(self.input_data_path,backup_tag_name)
                    print(backup_tag_name)
                    return tag_data
            return None
        except Exception as e:
            print("backup tag not found")


    def generateTag(self, dir_path):
        generate_tag = defaultdict(lambda: {})
        dir_name = dir_path.split("/")[-2]
        generate_tag["assignee"] = "dingjinchao"
        generate_tag["city"] = "shanghai"
        generate_tag["data_type"] = "raw"
        generate_tag["route"] = "o2l"
        generate_tag["master"] = False
        generate_tag["file_name"] = dir_name
        generate_tag["frequency"] = 1
        generate_tag["origin_record_tag"] = []
        generate_tag["task_id"] = 30000
        generate_tag["test_type"] = 1
        generate_tag["test_date"] = dir_name[0:10]
        generate_tag["test_duration"] = 2610
        generate_tag["topic_name"] = ["feature"]
        generate_tag["test_car_id"] = "CN-100"
        self.saveTag(dir_path, generate_tag)
        return generate_tag

    def main(self, upload=False):
        '''
        main pipeline for collected data check & segment & upload
        :param upload: whether upload
        :return: None
        '''

        for dir_name in self.file_list:
            self.mainSegment(dir_name, upload)

    def mainSegment(self, dir_name, upload=False):
        '''
        :param dir_name: the dir to be process
        :param upload: whether upload , default as False
        :return: o -> right ; 1-> error
        '''
        dir_path = ''.join([self.input_data_path, '/', dir_name, '/'])
        dir_path_without = ''.join([self.input_data_path, '/', dir_name])

        # check the dir whether right
        check_result,false_reason = self.checkRec(dir_path)
        # get the data-tag.json of checked dir
        tag_data = self.deterDirProperty(dir_path)
        if not check_result:
            if tag_data is not None and tag_data["topic_name"]!= ["repo_master"] and tag_data["task_id"] !=30000:
                pass
            else:
                self.falseDataArchive(dir_path_without,false_reason)
                return

        if "backup" in tag_data.keys():
            tag_data =  tag_data["backup"][0]["data_tag"]
        tag_data["test_date"] = tag_data["test_date"].replace('-', '_')
        if tag_data is None:
            return 1

        print(false_reason)
        if not  "global_tag" in tag_data.keys():
            tag_data["global_tag"] =[]
        if false_reason  != []:
            for false_check in false_reason:
                tag_data["global_tag"].append("no_"+false_check)

        print(tag_data["test_date"])
        # generate evluation result with different module
        if tag_data["test_type"] == 1:
            pool1 = multiprocessing.Pool(processes=3)
            #pool1.apply_async(generate_evaluation_result.generatePredictionEval, args=(dir_path,))
            pool1.apply_async(generate_evaluation_result.generateLocalizationEval, args=(dir_path,))
            pool1.apply_async(generate_evaluation_result.generateControlEval, args=(dir_path,))
            pool1.close()
            pool1.join()
            generate_evaluation_result.generateTprofileEval(dir_path)
            tprofile_label,tprfile_resut,tprofile_case =tprofile_eval.main(dir_path)
            if tprfile_resut != []:
                for tprofile in tprfile_resut:
                    tag_data["global_tag"].append(tprofile)
            tag_data = self.addTprofileLabelToCase(tprofile_label,tag_data)

        if tag_data["topic_name"] == []:
            tag_data["topic_name"].append("feature")
            self.saveTag(dir_path, tag_data)

        self.tag_info = tag_data
        self.tag_info["localization_result"] = self.getLocalizationResult(dir_path.replace(" ", ""))
        self.tag_info["control_result"] = self.getControlResult(dir_path.replace(" ", ""))
        self.tag_info["ap_result"] = self.getPredictionResult(dir_path.replace(" ", ""))
        self.tag_info["file_name"] = dir_name
        self.addEvalTag(dir_path)
        self.saveTag(dir_path, self.tag_info)

        if self.tag_info["test_type"] == 1 and self.tag_info["topic_name"][0] == "repo_master":
            try:
                self.post = True
                self.segmentPreprationCollection(dir_name)
                if upload:
                    self.mainUpload(dir_path_without)
            except Exception as e:
                logger(1, str(e), LOG_FILE="../upload_list/error.log")
                logging.exception(e)
                return 1

        if self.tag_info["test_type"] == 1 and self.tag_info["topic_name"][0] != "repo_master":  # 路测feature
            try:

                self.post = True
                if self.tag_info["topic_name"] == ["AUTODRIVE-6695_aggregator_online_test"] or self.tag_info["test_car_id"] == "BUS-001":
                    self.segmentPreprationCollection(dir_name)
                if upload:
                    self.mainUpload(dir_path_without)
            except Exception as e:
                logger(1, str(e), LOG_FILE="../upload_list/error.log")
                logging.exception(e)
                return 1


        if self.tag_info["test_type"] == 2:  # 路测feature
            try:
                self.post = True
                self.reouteCheckFi(dir_path, self.tag_info["test_car_id"])
                self.segmentPreprationCollection(dir_name)
                if upload:
                    self.mainUpload(dir_path_without)
            except Exception as e:
                logger(1, str(e), LOG_FILE="../upload_list/error.log")
                logging.exception(e)
                return 1
        return 0

    def mainUpload(self, dir_path_without):
        '''
        upload and then archive data
        :param dir_path_without: data path end without /
        '''

        tag_info = self.loadTag(dir_path_without + '/')
        dir_name = os.path.split(dir_path_without)[1]
        try:
            self.data_upload(dir_path_without, tag_info, slice=False)
            archive_path = self.dirArchive(dir_path_without, tag_info)
            self.check_true_file_list.append(archive_path + '/' + dir_name)
            if os.path.exists(dir_path_without + "_slice/"):
                self.data_upload(dir_path_without, tag_info, slice=True)
                self.dirArchive(dir_path_without + "_slice", tag_info)
            generate_data_report.getTrueList(archive_path + '/' + dir_name, True)
            generate_data_report.main(archive_path + '/' + dir_name, True)
            return 0
        except Exception as e:
            logger(1, str(e), LOG_FILE="../upload_list/error.log")
            logging.exception(e)
            return 1

    def falseDataArchive(self, dir_path_without,false_reason):
        try:
            generate_data_report.getFalseList(dir_path_without, False)
            generate_data_report.main(dir_path_without, False, false_reason)
            self.falseDataUpload(dir_path_without)
            self.dirArchive(dir_path_without, tag_info=None, check_result=False)
            return 1
        except Exception as e:
            logger(1, str(e), LOG_FILE="../upload_list/error.log")
            logging.exception(e)
        return 1

    def addTprofileLabelToCase(self,tprofile_label, tag_data):

        result_case = []
        case_list = tag_data["origin_record_tag"]
        for case in case_list:
            if "end" in case.keys():
                start = case["start"]
                end = case["end"]
            else:
                start = case["start"] - 10000
                end = case["start"] - 5000
            if not "labels" in case.keys():
                case["labels"] = []
            for time,label in tprofile_label.items():
                if int(time) > int(start) and int(time) < int(end):
                    case["labels"].append(label)
            case["labels"] = list(set(case["labels"]))
            result_case.append(case)
        tag_data["origin_record_tag"] = result_case
        return tag_data

    def reouteCheckFi(self,input_path,vehicle_id):
        try:
            rec_parser = "~/ws/repo_pro/senseauto/tools/rec_parser/scripts/offline_data_process.sh "
            output_path = input_path+'rec_parser'
            config_path = " ~/ws/repo_pro/senseauto/system/config/vehicle/"+vehicle_id
            enu_config_path = "~/ws/repo_pro/senseauto/tools/rec_parser/config/sh_enu_origin.txt"
            os.system("bash "+rec_parser+' -i '+input_path+' -o '+output_path+ ' -c ' +config_path+' -e '+enu_config_path)
            with open(output_path+'/gps.txt', 'r') as r:
                lines = r.readlines()
            with open(output_path+'/gps.txt', 'w') as fw:
                for l in lines:
                    if not "GPS-time" in l:
                        items = l.split(',')
                        items = items[1:3]
                        a = items[1]
                        items[1] = items[0].replace("\n", "")
                        items[0] = a.replace("\n", "")
                        items = "unknown unknown unknown unknown unknown " + str(items[0])+', ' +str(items[1])+", unknown\n"
                        fw.write(items)
            os.system("python3 ~/Codes/RouteMeFi-master/routemefi.py --input_path "+output_path+'/gps.txt '+ "--db_path ~/Codes/sh_gps/database.txt --save_dir ~/Codes/sh_gps/output_gps --query_merge")
        except Exception as e:
            print("get routing error")

    def changeGPSTxt(self,gps_txt):
        with open(gps_txt, 'w') as file:
            lines = file.readlines()
            for line in lines:
                # wgs84(lon, lat, height)
                items = line.split(',')
                items = items[1:3]
                #items = [float(x[:-1]) for x in items]
                a=items[1]
                items[1]=items[0]
                items[0]=a
                items = "unknown unknown unknown unknown unknown " + items +", unknown"
                file.write(items)

    def checkRec(self, dir_path, slice=False):
        '''
        :param dir_path: data path end with /
        :param slice: define the checking data is raw data or segment data
        :return: True of False
        '''
        try:
            check_tag = self.loadTag(dir_path,'data-tag.json')
            if check_tag is not None and check_tag["test_car_id"] == "CN-001":
                return True,[]
        except Exception as e:
            print("Not CN-001 data")

        self.false_check_reasion = []
        false_reason = []
        if not os.path.exists(dir_path):
            return False,false_reason
        video_result = 0
        check_result = 0
        for file_name in self.check_file_name_list:
            check_size = self.check_file_name_list[file_name]
            reult_0_1 = self.judgeFileSizeAndExist(dir_path, file_name, check_size=check_size)
            check_result += reult_0_1
            if reult_0_1 == 0:
                false_reason.append(file_name)
        pattern = "port_*"
        video_files = self.getMatchedFilePaths(dir_path, pattern, formats=[".avi"], recursive=True)

        for video_name in video_files:
            video_reult_0_1 = self.judgeFileSizeAndExist(dir_path='', file_name=video_name, check_size=5)
            video_result += video_reult_0_1
            if video_reult_0_1 == 0:
                false_reason.append(file_name)
        dpc_result_0_1 = self.judgeFileSizeAndExist(dir_path, "dmppcl.bag", check_size=10)
        check_result += dpc_result_0_1
        if dpc_result_0_1 == 0:
            false_reason.append(file_name)

        if not os.path.exists(dir_path+'/cache'):
            false_reason.append("cache")
        if not os.path.exists(dir_path+'/config'):
            false_reason.append("config")
        if not os.path.exists(dir_path+'/logs'):
            false_reason.append("logs")
        if not os.path.exists(dir_path+'/timing_logger'):
            false_reason.append("timing_logger")
        if check_result > 3 and video_result > 0:
            print " ---- Dir:", dir_path, "is \033[1;32m correct\033[0m!\n"
            return True,false_reason
        else:
            print " ---- Dir:", dir_path, "is\033[1;31m wrong\033[0m!\n"
            return False,false_reason

    def judgeFileSizeAndExist(self, dir_path, file_name, check_size=1):
        "as the function name descripted"

        file_path = ''.join([dir_path, file_name])
        if os.path.exists(file_path) and \
                round(os.path.getsize(file_path) / float(1024 * 1024), 0) >= check_size:
            return 1
        else:
            self.false_check_reasion.append(file_name)
            print " ---- Error, the file:", file_name, "on dir", dir_path, "is\033[1;31m wrong\033[0m!\n"
            return 0

    def addEvalTag(self, dir_path):
        "add the evaluation result to tag"
        local_eval_tag = generate_evaluation_result.getLocalEvalResult(dir_path)
        control_eval_tag = generate_evaluation_result.getControlEvalResult(dir_path)
        if local_eval_tag is not None:
            for case_tag in local_eval_tag:
                self.tag_info["origin_record_tag"].append(case_tag)
        if control_eval_tag is not None:
            for case_tag in control_eval_tag:
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
        "prepration for segment"

        if "origin_record_tag" in self.tag_info and self.tag_info["origin_record_tag"] != []:
            segment_point = self.tag_info["origin_record_tag"]
        else:
            return 0

        self.dataSegment(dir_name, segment_point)

    def dataSegment(self, dir_name, segment_point):
        "data segment pipeline"

        segment_list = []
        case_finder_list = []
        case_tagging_list = []
        prediction_tagging_list = []
        for record_tag in segment_point:
            dir_path = ''.join([self.input_data_path, '/', dir_name])
            input_path = ''.join([dir_path, '/'])

            module_name = record_tag.get("tag_en")

            "data segment pipeline"
            if module_name in self.tag_module_list.keys():
                level_name = self.tag_module_list[module_name]
            else:
                level_name = "DPC"

            if "data_type" in record_tag.keys() and record_tag["data_type"] == "eval":
                level_name = "EVAL"

            if level_name == "DPC":
                log_type = 1
            else:
                log_type = 0
            print "\033[1;32m ===>>  \033[0m", level_name, "==>> ", module_name, "==== module_type:", log_type, '\n'

            if not "end" in record_tag.keys():
                if level_name == "DPC":
                    front_time = 15
                    behind_time = 25
                else:
                    front_time = 20
                    behind_time = 10
            else:
                front_time = 2
                behind_time = (record_tag["end"] - record_tag["start"]) // 1000
            if behind_time < 6:
                behind_time =10

            time_point = record_tag["start"] * 1000
            test_date = self.tag_info["test_date"]
            test_time = str(record_tag["start_format"].replace(":", "_"))
            segment_dir_name = ''.join([test_date, '_', test_time])
            output_path = ''.join([dir_path, '_slice/', level_name, '/', module_name, '/', segment_dir_name])

            segment_list.append({"output_dir": output_path,
                                 "time_point": time_point,
                                 "front_duration": front_time,
                                 "behind_duration": behind_time,
                                 "log_type": log_type})

            if "end" in record_tag.keys():
                input_timestamp = (record_tag["start"] + record_tag["end"]) / 2000
            else:
                input_timestamp = record_tag["start"] / 1000

            if module_name == "false_brake" or module_name == "Emergency_brake" or module_name == "sharp_slowdown":

                tagging_module = 2
            elif  module_name == "take_over":
                tagging_module = 3
            else:
                tagging_module = 1

            case_tagging_list.append({"input_dir": ''.join([output_path, '/']),
                                      "module_name": module_name,
                                      "input_timestamp": input_timestamp,
                                      "tagging_module":tagging_module})

            if module_name == "abnormal_prediction_trajectory":
                prediction_tagging_list.append({"input_dir": ''.join([output_path, '/']),
                                                "module_name": module_name,
                                                "input_timestamp": input_timestamp})

            if not os.path.exists(output_path):
                os.makedirs(output_path)

            if self.tag_info["topic_name"][0] == "repo_master":
                task_id = ''
            else:
                task_id = str(self.tag_info["task_id"]) + '/'

            vehicle_id = self.tag_info["test_car_id"].replace("-", "")
            module_tag_data = copy.deepcopy(self.tag_info)
            data_month = self.tag_info["test_date"].rsplit("_",1)[0]
            dst_path = ''.join([self.getDataCollectionDstLink(self.tag_info,data_month, slice=True),
                                self.tag_info["test_date"],
                                '/', vehicle_id,
                                '/', task_id])
            module_tag_data["data_link"] = ''.join([dst_path, level_name, '/', module_name, '/', segment_dir_name])
            store_path = ''.join([dir_path, '_slice/', level_name, '/', module_name, '/', segment_dir_name])
            module_tag_data["origin_record_tag"] = [record_tag]
            if "data_type" in record_tag.keys() and record_tag["data_type"] == "eval":
                module_tag_data["data_type"] = record_tag["data_type"]
                self.post = True
            else:
                module_tag_data["data_type"] = "segment"
            module_tag_data["file_name"] = segment_dir_name
            module_tag_data["raw_data_link"] = ''.join([self.getDataCollectionDstLink(self.tag_info, data_month,slice=False),
                                                        self.tag_info["test_date"],
                                                        '/', vehicle_id, '/',
                                                        task_id, dir_name])
            module_tag_data['aws_endpoint'] = end_point
            self.saveTag(store_path, module_tag_data, file_name='/data-tag.json')
            self.generateLogDownloadFile(log_type,module_tag_data["raw_data_link"],output_path)

        cut_rec_multiprocess.main(input_path, segment_list)
        if self.tag_info["topic_name"][0] == "repo_master":
            self.preCaseTagging(dir_path, case_tagging_list)
            self.prePredictionEval(dir_path,prediction_tagging_list)

    def generateLogDownloadFile(self,log_type,raw_data_link,output_path):
        if not os.path.exists(output_path + "/logs"):
            os.makedirs(output_path + "/logs")
        if log_type ==0:
            if not os.path.exists(output_path + "/logs/tmp.txt"):
                os.mknod(output_path + "/logs/tmp.txt")
        else:
            profile = " --profile ad_system_common "
            log_download_instruction = ''.join(["aws s3 cp",upload_recursive,end_point_40,profile,raw_data_link+'/logs',' ',"$this_dir/"])
            download_logs = self.download_logs
            download_logs+=log_download_instruction
            download_logs += '\n'
            with open(output_path+'/logs/download_logs.sh', 'w') as f:
                f.write(download_logs)


    def preCaseFinder(self, dir_path, case_finder_list):
        "multi process to process case finder"

        print "\033[1;32m [INFO]\033[0m! case finder ing .........\n"
        input_list = []
        for record_tag in case_finder_list:
            input_list.append(([dir_path, record_tag], None))

        try:
            requests = makeRequests(self.caseFinder, input_list)
            [self.pool.putRequest(req) for req in requests]
            self.pool.wait()
        except Exception as e:
            return
        print "\033[1;32m [INFO]\033[0m! case finder successfully\n"


    def caseFinder(self, dir_path, record_tag):
        "case finder function"

        case_finder = "/home/sensetime/ws/repo_pro/senseauto/build/modules/simulator/tools/scenario_log_tools/case_finder"
        case_output_path = record_tag["input_dir"]+'screen_cast/'
        if not os.path.exists(case_output_path):
            os.makedirs(case_output_path)
        simulator_path = ''.join([record_tag["input_dir"], 'simulator_scenario/0/logger.bin'])
        input_timestamp = record_tag["input_timestamp"]
        case_finder_cmd = "{} {} {} 2 {} {} {}".format(
            case_finder,
            simulator_path,
            case_output_path + 'case_finder.json',
            str(input_timestamp),
            str(15),
            str(5))
        os.system(case_finder_cmd)
        self.renameCaseTaggingTag(case_output_path)

    def renameCaseTaggingTag(self, case_output_path):
        "as the function name"

        case_finder = self.loadTag(case_output_path, 'case_finder.json')
        if case_finder == [] or case_finder is None:
            case_finder = {}
            self.saveTag(case_output_path, case_finder, 'case_finder.json')
            return
        if "obstacle_id" in case_finder[0] and case_finder[0]["obstacle_id"] == [""]:
            case_finder[0]["obstacle_id"] =[]
        if "obstacle_id" in case_finder[0] and case_finder[0]["obstacle_id"] == ["0"]:
            case_finder[0]["obstacle_id"] = []
        if "ego_tags" in case_finder[0]:
            case_finder[0]["ego_tags"] = self.refineTag(case_finder[0]["ego_tags"])
        if "obstacle_vehicle_tags" in case_finder[0]:
            case_finder[0]["obstacle_vehicle_tags"] = self.refineTag(case_finder[0]["obstacle_vehicle_tags"])
        if "obstacle_vru_tags" in case_finder[0]:
            case_finder[0]["obstacle_vru_tags"] = self.refineTag(case_finder[0]["obstacle_vru_tags"])
        self.saveTag(case_output_path, case_finder[0], 'case_finder.json')


    def preCaseTagging(self, dir_path, case_tagging_list):
        print "\033[1;32m [INFO]\033[0m! case tagging ing .........\n"
        input_list = []
        for record_tag in case_tagging_list:
            input_list.append(([dir_path, record_tag], None))

        try:
            requests = makeRequests(self.caseTagging, input_list)
            [self.pool.putRequest(req) for req in requests]
            self.pool.wait()
        except Exception as e:
            return
        print "\033[1;32m [INFO]\033[0m! case tagging successfully\n"


    def caseTagging(self, dir_path, record_tag):
        "case finder function"
        self.case_tagging.main(dir_path, record_tag)
        case_output_path=record_tag["input_dir"]+'/screen_cast/'

        self.renameCaseTaggingTag(case_output_path)


    def prePredictionEval(self,dir_path,prediction_tagging_list):
        print "\033[1;32m [INFO]\033[0m! prediction tagging ing .........\n"
        eval_bad_result = self.loadTag(dir_path,'/prediction_evaluation/result/bad_cases.json')
        input_list = []
        for record_tag in prediction_tagging_list:
            input_list.append(([dir_path ,eval_bad_result,record_tag], None))
        try:
            requests = makeRequests(prediction_evaluation_iteration.main, input_list)
            [self.pool.putRequest(req) for req in requests]
            self.pool.wait()
        except Exception as e:
            return
        print "\033[1;32m [INFO]\033[0m! prediction tagging successfully\n"


    def refineTag(self, case_list):
        "fix the output of case finder tag"

        for i in range(len(case_list)):
            case_list[i] = case_list[i].split(":")[-1]
        return case_list

    def data_upload(self, dir_path_without, tag_info, slice=False):
        'data_upload with aws'
        dir_name = os.path.split(dir_path_without)[1]

        vehicle_id = tag_info["test_car_id"].replace("-", "")
        data_month = tag_info["test_date"].rsplit("_", 1)[0]
        try:
            if tag_info["topic_name"][0] == "repo_master":
                feature = False
            else:
                feature = True
        except Exception as e:
            feature = False

        if feature:
            task_id = str(tag_info["task_id"]) + '/'
        else:
            task_id = ''

        if slice:
            upload_path = ''.join([dir_path_without, "_slice/ "])

            dst_path = ''.join([self.getDataCollectionDstLink(tag_info, data_month,slice=True),
                                tag_info["test_date"], '/',
                                vehicle_id, '/', task_id])

            self.sliceDataCheck(dir_path_without + '_slice/')

        else:
            upload_path = ''.join([dir_path_without, '/ '])

            tag_path = ''.join([self.getDataCollectionDstLink(tag_info,data_month, slice=False),
                                tag_info["test_date"], '/',
                                vehicle_id, '/',
                                task_id, dir_name])
            dst_path = ''.join([tag_path, '/'])
            tag_info["data_link"] = tag_path
            tag_info["data_type"] = "raw"
            tag_info['aws_endpoint'] = end_point
            self.saveTag(dir_path_without, tag_info, file_name='/data-tag.json')

        arg2 = ''.join(["s3 cp ", upload_path, dst_path, upload_recursive+end_point])
        print(" ==== ", arg2)

        upload_result = AWS_DRIVER.main(arg2.split())
        logger(1, "Uploaded dir:" + upload_path)

        self.TransferPost(tag_info)

        if upload_result == 0:
            print  " ---- Dir:\033[1;32m", dir_name + "\033[0m" + dir_name, "\033[0m has\033[1;32m uploaded successfully!\033[0m---\n"
        else:
            print " ---- Dir:\033[1;32m", dir_name + "\033[0m" + dir_name, "\033[0m \033[1;32m upload failed!\033[0m---\n"

    def falseDataUpload(self, dir_path_without):
        false_data_tag = self.loadTag(dir_path_without,'/data_tag.json')

        dir_name = os.path.split(dir_path_without)[1]
        upload_path = ''.join([dir_path_without, '/ '])
        dst_path = ''.join(["s3://sh40_fieldtest_dataset/",data_month,'/false_data/', dir_name])
        arg2 = ''.join(["s3 cp ", upload_path, dst_path, upload_recursive+end_point])
        AWS_DRIVER.main(arg2.split())
        if false_data_tag is not None and false_data_tag["topic_name"] != ["repo_master"]:
            false_data_tag["data_link"] = dst_path
            false_data_tag["data_type"] = "raw"
            self.TransferPost(self, false_data_tag)

    def sliceDataCheck(self, dir_path):
        "segmented data check and post"

        data_tag_paths = self.getMatchedFilePaths(dir_path, pattern="data-ta*", formats=[".json"], recursive=True)

        for slice_data_tag_path in data_tag_paths:
            slice_data_path = os.path.split(slice_data_tag_path)[0]
            check_result,false_reason = self.checkRec(slice_data_path + '/', slice=True)
            name = os.path.basename(os.path.split(slice_data_tag_path)[0])
            slice_data_tag = self.loadTag(slice_data_tag_path, name+'.json')
            if not check_result:
                self.saveTag('../upload_list/false_segment', slice_data_tag, '')
                continue
            self.TransferPost(slice_data_tag)  # post data tag to senseFT

    def getDataCollectionDstLink(self, tag_info, data_month,slice):
        "get the upload path of the dir "

        if tag_info["test_type"] == 2:
            if slice:
                return "s3://sh40_data_collection/"+data_month+"/segment_data/"
            else:
                return "s3://sh40_data_collection/"+data_month+"/raw_data/"
        if tag_info["topic_name"][0] == "repo_master":
            if slice:
                return "s3://sh40_fieldtest_master/"+data_month+"/master/segment_data/"
            else:
                return "s3://sh40_fieldtest_master/"+data_month+"/master/raw_data/"
        else:
            if slice:
                return "s3://sh40_fieldtest_feature/"+data_month+"/feature/segment_data/"
            else:
                return "s3://sh40_fieldtest_feature/"+data_month+"/feature/raw_data/"

    def getLocalizationResult(self, dir_path):
        "get the localization result"
        localization_result = defaultdict(lambda: {})
        result_file_path = ''.join([dir_path, '/logs/localization_eval/'])
        localization_json = self.loadTag(result_file_path, tag_file_name='evaluation_result.json')
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
                print("localization key is not here")
        if self.tag_info["test_mileage"] < 1.0 or self.tag_info["test_mileage"] > 100.0:
            self.tag_info["test_mileage"] = 18.0
        return localization_result

    def getControlResult(self, dir_path):
        "add the control evaluation result to tag"

        control_result = defaultdict(lambda: {})
        result_file_path = ''.join([dir_path, '/logs/control_eval/'])
        control_json = self.loadTag(result_file_path, tag_file_name='control_eval_results.json')

        if control_json is not None:
            try:
                control_result = control_json["control_result"]
                if 'stop_error' in control_result['control_precision'].keys():
                    control_result['control_precision']['stop_error']['std'] = 0.901
            except Exception as e:
                logger(1, str(e), LOG_FILE="../upload_list/error.log")
                print("control key is not here")
        return control_result

    def getPredictionResult(self, dir_path):
        "add the control evaluation result to tag"

        ap_result = defaultdict(lambda: {})
        result_file_path = ''.join([dir_path, '/prediction_evaluation/result/'])
        ap_json = self.loadTag(result_file_path, tag_file_name='result.json')

        if ap_json is not None:
            try:
                ap_result["quality"] = ap_json["quality"]
            except Exception as e:
                logger(1, str(e), LOG_FILE="../upload_list/error.log")
                print("ap key is not here")
                ap_result["quality"] = {}
                ap_result["quality"]['level'] = "bad"
        return ap_result


    def TransferPost(self, data_tag):
        "post the data tag to senseFT"
        curl = \
            'https://fieldtest.sensetime.com/task/daemon/update/tag'
        post_result = requests.post(curl, headers=self.headerdata, data=json.dumps(data_tag))
        print "\n \033[1;32m [INFO]\033[0m ", post_result.text
        if post_result.text != u'{"result":"true"}':
            try:
                logger(2, "Uploaded dir:" + data_tag["data_link"], LOG_FILE="../upload_list/post_failed_file.log")
                self.saveTag('../upload_list/', data_tag, data_tag["file_name"] + '.json')
            except Exception as e:
                print("save upload failed tag failed")

    def dirArchive(self, dir_path_without, tag_info, check_result=True):
        "archive the dri which has been uploaded"
        dir_name = os.path.split(dir_path_without)[1]
        input_data_path = os.path.split(dir_path_without)[0]

        if not check_result:
            try:
                date_id = ''.join(['/False_', dir_name.split('_', -1)[1], '_', dir_name.split('_', -1)[2]])
            except Exception as e:
                date_id = '/False_ARH'
            archive_path = input_data_path + date_id + '_ARH'
            print(archive_path)
            if not os.path.exists(archive_path):
                os.makedirs(archive_path)
            try:
                shutil.move(input_data_path + '/' + dir_name, archive_path)
            except Exception as e:
                print("move failed")
            return archive_path
        else:
            test_date = tag_info["test_date"].split('_', 1)[1]
            try:
                date_id = ''.join(['/', test_date, '_', tag_info["test_car_id"]])
            except Exception as e:
                date_id = 'True_ARH'
            archive_path = input_data_path + date_id + '_ARH'
            if not os.path.exists(archive_path):
                os.makedirs(archive_path)
            try:
                shutil.move(input_data_path + '/' + dir_name, archive_path)
            except Exception as e:
                print("move failed")
            return archive_path

if __name__ == "__main__":

    if len(sys.argv) < 2:
        number = ''
    else:
        data_path = sys.argv[1]
    if not os.path.exists(data_path):
        raise ValueError("========== : {} does NOT exist".format(data_path))
    data_check_class = DataCollectionUpload(data_path)
    data_check_class.main(upload=True)