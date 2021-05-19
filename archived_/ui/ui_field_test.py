# coding=utf-8
"""
data_check.py
check the data format before upload
by Zheng Yaocheng
zhengyaocheng@sensetime.com
input:FieldTest/$No.
output:the dir to transfer
"""

import os
import sys
import json
from collections import defaultdict, deque
import datetime
import shutil
from awscli.clidriver import create_clidriver
import subprocess
import fnmatch
import copy
import requests
import ui_slot as ui

driver = create_clidriver()

FILE_NAME_LIST_REC = {'canbus.dump.rec': 4,
                      'top_center_lidar.dump.rec': 50,
                      "ins.dump.rec": 4}
DATE = datetime.datetime.now().strftime('%Y-%m-%d')

def logger(level, str):
    LOG_FILE = 'upload_list/fieldtest_upload_list.log'
    if not os.path.exists(LOG_FILE):
        os.mknod(LOG_FILE)
    try:
        logFd = open(LOG_FILE, 'a')
    except:
        logFd = open(LOG_FILE, 'a')
    logFd.write(
        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        + ": " + ("Writing " if level else "NOTICE ") + str
    )
    logFd.write("\n")
    logFd.close()


class DataCollectionUpload():
    def __init__(self, path):
        self.input_data_path = path
        self.file_list = deque()
        self.tag_info = defaultdict(lambda: {})
        self.getAllDataDir()
        self.tag_file_name = '/data-tag.json'
        self.level_statistics = defaultdict(lambda: 0)
        self.headerdata = {"Data-tag-type": "application/json"}


    def loadTag(self, tag_file_path, tag_file_name='/data-tag.json'):
        "read json"
        if os.path.exists(tag_file_path + tag_file_name):
            with open(tag_file_path + tag_file_name, 'r') as f:
                try:
                    tag_data = json.load(f)
                    return tag_data
                except ValueError:
                    print(" ==== ", tag_file_path + tag_file_name,
                          "\033[1;31m is not valuable json bytes \033[0m!\n")
                    return None


    def saveTag(self, tag_file_path, tag_data, file_name):
        "write json"
        tag_path_name=tag_file_path + file_name
        if not os.path.exists(tag_path_name):
            os.mknod(tag_path_name)
        with open(tag_path_name, 'w') as fw:
            json.dump(tag_data, fw)


    def getAllDataDir(self):
        "get all dir in data"
        for file in os.listdir(self.input_data_path):
            dir_file = os.path.join(self.input_data_path, file)
            if (os.path.isdir(dir_file)):
                h = os.path.split(dir_file)
                self.file_list.append(h[1])


    def deterDirProperty(self, dir_path):
        "determine file property according the tag"
        tag_data = self.loadTag(dir_path)
        if tag_data is not None and "origin_record_tag" in tag_data.keys():
            if self.checkRec(dir_path):
                return tag_data


    def main(self):
        "main pipeline for collected data check & segment & upload"
        for dir_name in self.file_list:
            if not ui.mission_prep(self.input_data_path,dir_name):      ###
                continue                                                ###
            dir_path = ''.join([self.input_data_path,'/',dir_name])
            tag_data = self.deterDirProperty(dir_path)
            if tag_data is None:
                print(" ======= tag is None in ", dir_name)
                ui.mission_error(''.join([" ======= tag is None in ", dir_name]))  ###
                continue
            if tag_data is not None and tag_data["test_type"] == 1 and \
                    tag_data["topic_name"][0] == "repo_master":    # 路测master
                self.tag_info = tag_data

                self.segmentPreprationCollection(dir_name)
                self.data_upload(dir_name, slice=False)
                self.dirArchive(dir_name)
                if os.path.exists(dir_path + "_slice/"):
                    self.data_upload(dir_name, slice=True)
                    self.dirArchive(dir_name+"_slice/")

            if tag_data["test_type"] == 1 and tag_data["topic_name"][0] != "repo_master":   # 路测feature
                self.tag_info = tag_data
                #self.segmentPreprationCollection(dir_name)
                self.data_upload(dir_name, slice=False,feature=True)
                self.dirArchive(dir_name)
                if os.path.exists(dir_path + "_slice/"):
                    self.data_upload(dir_name, slice=True,feature=True)
                    self.dirArchive(dir_name+"_slice/")
            ui.misson_complete()  ###
        ui.disk_complete()  ###


    def checkRec(self, dir_path):
        "judge the file size and existence with type of REC"

        "check rec files in <sensors_record>"
        for file_name in FILE_NAME_LIST_REC:
            rec_file = ''.join([dir_path,"/sensors_record/",file_name])
            if os.path.exists(rec_file) and round(os.path.getsize(rec_file) / float(1024 * 1024), 0) > \
                    FILE_NAME_LIST_REC[file_name]:
                result = 1
            else:
                result = 0
                print(" ---- Error, the file: ",rec_file," on dir", dir_path, " is wrong!")
                ui.sig_src.send_error_info(''.join([" ---- Error, the file: ", rec_file, " on dir",
                                                    dir_path, " is wrong!"]))  #
                break

        "check dpc_bag"
        dpc_file = ''.join([dir_path,"/dmppcl.bag"])
        if os.path.exists(dpc_file) and round(os.path.getsize(dpc_file) / float(1024 * 1024), 0) > 100:
            result += 1
        else:
            result = 0
            print(" ---- Error, the file: dmppcl.bag on dir", dir_path, " is wrong!")
            ui.sig_src.send_error_info(''.join([" ---- Error, the file: dmppcl.bag on dir",
                                                dir_path, " is wrong!"]))  #

        self.rename_screen_files(dir_path)

        "check video files"
        pattern = "port_0_camera_*"
        video_files = self.getMatchedFilePaths(dir_path, pattern, formats=[".avi"], recursive=True)
        if video_files and result > 1:
            for video_name in video_files:
                if round(os.path.getsize(video_name) / float(1024 * 1024), 0) > 50:
                    result += 1
                else:
                    print(" ---- Error, the file", video_name, " on dir", dir_path, " is wrong!")
                    ui.sig_src.send_error_info(''.join([" ---- Error, the file", video_name, " on dir",
                                                        dir_path, " is wrong!"]))  #
                    os.remove(video_name)
                    os.remove(video_name.replace('avi', 'txt'))


        elif not video_files:
            result = 0
            print(" ---- Error, the file: *.avi on dir", dir_path, " is wrong!")
            ui.sig_src.send_error_info(''.join([" ---- Error, the file: *.avi on dir", dir_path, " is wrong!"]))

        print(result)
        if result > 2:
            print(" ---- Dir:", dir_path, " is \033[1;32m correct\033[0m!\n")
            ui.sig_src.send_error_info(''.join([" ---- Dir:", dir_path, " is correct"]))
            return True
        else:
            print(" ---- Dir:", dir_path, " is\033[1;31m wrong\033[0m!\n")
            ui.sig_src.send_error_info(''.join([" ---- Dir:", dir_path, " is wrong"]))
            return False


    def rename_screen_files(self,dir_path):
        "rename screen cast videos"
        screen_files = self.getMatchedFilePaths(dir_path, formats=[".mp4"], recursive=False)
        for id, old_screen_video in enumerate(screen_files):
            new_name=''.join([dir_path,'/',str(id+5 ),'.mp4'])
            os.rename(old_screen_video,new_name)
            print(old_screen_video,'======>',new_name)


    def getMatchedFilePaths(self, dir_path, pattern="*", formats=[".avi"], recursive=False):
        "get all the files in <dir_path> with specified pattern"
        files = []
        data_dir = os.path.normpath(os.path.abspath(dir_path))
        for f in os.listdir(data_dir):
            current_path = os.path.join(os.path.normpath(data_dir), f)
            if os.path.isdir(current_path) and recursive:
                files += self.getMatchedFilePaths(current_path, pattern, formats,
                                                  recursive)
            elif fnmatch.fnmatch(f,
                                 pattern) and os.path.splitext(f)[-1] in formats:
                files.append(current_path)
        return files


    def segmentPreprationCollection(self, dir_name):
        "prepration for segment"
        ui.update_state('切分...')  ###
        if "origin_record_tag" in self.tag_info and self.tag_info["origin_record_tag"] != []:
            segment_point = self.tag_info["origin_record_tag"]
        else:
            return 0

        for module in segment_point:
            name = module.get("tag_en")
            if not "end" in module.keys():
                self.dataSegment(name, dir_name, record_tag=module)
            else:
                self.dataSegment(name, dir_name, record_tag=module, sequence=True)


    def dataSegment(self, module_name, dir_name, record_tag, sequence=False, log_type=0):
        "dta segment pipeline"
        dir_path = ''.join([self.input_data_path, '/', dir_name])
        input_path = dir_path + '/'

        if module_name == "false_detection" or module_name =="false_traffic_light":
            level_name = "sense"
            log_type = 0
        else:
            level_name = "DPC"
            log_type = 1
        print("----------------------", level_name, "==>>", module_name)
        print(" ==== ", module_name, ", ==== module_type:", log_type)

        if sequence:
            front_time = 2
            behind_time = str((record_tag["end"] - record_tag["start"]) // 1000)
        else:
            front_time = 15
            behind_time = 5

        time_point = str(record_tag["start"] * 1000)
        segment_dir_name=str(record_tag["start_format"].replace(":","_"))
        output_path = ''.join([dir_path,'_slice/',level_name,'/',module_name,'/',segment_dir_name])

        subprocess.call(
            [
                'python2', './rec_video_scenario_cutter_fieldtest.py',
                '-d', input_path,
                '-o', output_path,
                '-t', time_point,
                '-f', str(front_time),
                '-b', str(behind_time),
                '-m', str(log_type)
            ]
        )

        # save tag for sgemented file
        if self.tag_info["topic_name"][0] == "repo_master":
            task_id=''
        else:
            task_id=str(self.tag_info["task_id"])+'/'


        vehicle_id=self.tag_info["test_car_id"].replace("-", "")

        module_tag_data = copy.deepcopy(self.tag_info)
        dst_path = ''.join([self.getDataCollectionDstLink(slice=True),
                            self.tag_info["test_date"],
                            '/',vehicle_id,
                            '/',task_id])
        module_tag_data["data_link"] = ''.join([dst_path,level_name,'/',module_name,'/',segment_dir_name,'/'])
        store_path = ''.join([dir_path,'_slice/',level_name,'/',module_name,'/',segment_dir_name])
        module_tag_data["origin_record_tag"] = [record_tag]
        module_tag_data["data_type"] = "segment"
        module_tag_data["file_name"] = segment_dir_name
        module_tag_data["raw_data_link"] = ''.join([self.getDataCollectionDstLink(slice=False),
                                                    self.tag_info["test_date"],
                                                    '/',vehicle_id,'/',
                                                    task_id , dir_name])
        self.saveTag(store_path, module_tag_data, file_name='/data-tag.json')

        self.TransferPost(module_tag_data)   #post data tag to senseFT


    def data_upload(self, dir_name, slice=False,feature=False):
        'data_upload with aws'
        end_point = " --recursive --endpoint-url=http://10.5.41.189:9090"
        vehicle_id = self.tag_info["test_car_id"].replace("-", "")
        if feature:
            task_id = str(self.tag_info["task_id"])+'/'
        else:
            task_id = ''


        if slice:
            upload_path = ''.join([self.input_data_path,'/',dir_name,"_slice/ "])
            dst_path = ''.join([self.getDataCollectionDstLink(slice=True),
                                self.tag_info["test_date"],'/',
                                vehicle_id,'/',task_id])
            ui.sig_src.new_upload(self.input_data_path + dir_name + "_slice")  #
        else:
            upload_path = ''.join([self.input_data_path,'/',dir_name,'/ '])

            tag_path = ''.join([self.getDataCollectionDstLink(slice=False),
                                self.tag_info["test_date"], '/',
                                vehicle_id, '/',
                                task_id, dir_name])
            dst_path=''.join([tag_path,'/'])
            self.tag_info["data_link"] = tag_path
            self.tag_info["data_type"] = "raw"
            self.tag_info["localization_result"] = self.getLocalizationResult(upload_path.replace(" ", ""))
            self.saveTag(self.input_data_path + '/' + dir_name, self.tag_info, file_name='/data-tag.json')
            ui.sig_src.new_upload(self.input_data_path + dir_name)  #

        self.TransferPost(self.tag_info)
        arg2 = ''.join(["s3 cp ",upload_path,dst_path,end_point])
        print(" ==== ", arg2)
        ui.update_state('上传中')  ###
        # ui.sig_src.new_upload(self.input_data_path + dir_name)  ###
        upload_result = driver.main(arg2.split())
        logger(1, "Uploaded dir:" + upload_path)
        if upload_result == 0:
            print(" ---- Dir:\033[1;32m", dir_name + "\033[0m" + dir_name,
                  "\033[0m has\033[1;32m uploaded successfully!\033[0m---\n")
            ui.update_state('上传成功')  ###
        else:
            print(" ---- Dir:\033[1;32m", dir_name + "\033[0m" + dir_name,
                  "\033[0m \033[1;32m upload failed!\033[0m---\n")
            ui.update_state('上传失败')  ###


    def getDataCollectionDstLink(self, slice):
        if self.tag_info["topic_name"][0] == "repo_master":
            if slice:
                return "s3://Field_Test_Data/master/segment_data/"
            else:
                return "s3://Field_Test_Data/master/raw_data/"
        else:
            if slice:
                return "s3://Field_Test_Data/feature/segment_data/"
            else:
                return "s3://Field_Test_Data/feature/raw_data/"


    def getLocalizationResult(self, dir_path):
        "get the localization result"
        localization_result = defaultdict(lambda: {})
        result_file_path = ''.join([dir_path , '/logs/localization_eval/'])
        localization_json = self.loadTag(result_file_path, tag_file_name='evaluation_result.json')

        if localization_json is not None:
            localization_result["Grade"] = localization_json["Grade"]
            localization_result["Integrity"] = localization_json["Integrity"]
        return localization_result


    def TransferPost(self, data_tag):
        curl = 'https://fieldtest.sensetime.com/task/daemon/update/tag'
        post_result = requests.post(curl, headers=self.headerdata, data=json.dumps(data_tag))
        print("--$$$$$$--", post_result.text)


    def dirArchive(self, dir_name):
        "archive the dri which has been uploaded"
        date_id=''.join(['/',self.tag_info["test_date"],'_',self.tag_info["test_car_id"]])
        archive_path = self.input_data_path + date_id
        if not os.path.exists(archive_path):
            os.makedirs(archive_path)
        shutil.move(self.input_data_path + '/' + dir_name, archive_path)
        ui.update_state('归档完成')


if __name__ == "__main__":

    if len(sys.argv) < 2:
        number = ''
    else:
        number = sys.argv[1]
    data_path = '/media/zhengyaocheng/FieldTest' + str(number) + '/data/'
    if not os.path.exists(data_path):
        raise ValueError("========== Prediction: {} does NOT exist".format(data_path))
    data_check_class = DataCollectionUpload(data_path)
    data_check_class.main()
