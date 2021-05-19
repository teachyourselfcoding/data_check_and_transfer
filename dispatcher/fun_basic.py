# -*- coding: utf-8 -*-
import os
import json
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from archived_ import ui_upload_python2 as UUP

disk_model = {'DATA_FOLDER_PATH':'', 'STATE':''}
#硬盘信息模板, [ 待处理 ] [ 处理中 ] [ 已完成 ] [ 有异常 ] [ 被中断 ] [ 暂停中 ]
disk_list = {}      #已加载硬盘（字典）
disk_priority = []
flg_disk_changed = True
segment_line = []   # absolute directory of mission folder
upload_line = []    # absolute directory of mission folder
false_line = []     # absolute directory of false mission folder
false_reason_line = []      # reasons of false mission folder
disk_hold = {}     # flags showing if a disk is done
mission_info_model = {'硬盘ID':'', '任务ID':'', 'Issue ID':'', '状态':'', '上传进度':'', 'mission_key':''}
# 状态模板： 准备切分 切分中 切分失败 切分超时 准备上传 上传中 上传失败 上传超时 上传成功 已完成 有异常 被中断
mission_info_keys = []
mission_info_memory = {}
reboot_disk_record = {}

def get_disk_id(disk_path):
    if not os.path.exists(disk_path):
        print('path: ' + disk_path + 'does not exist')
        return 'Wrong path'
    all_file = os.listdir(disk_path)
    for item in all_file:
        if item.split('.')[-1] == 'id':
            return item.split('.')[0]
    return 'No .id file found'

def get_target_floder_path(data_path):  # filt wrong folder
    global false_line
    global false_reason_line
    global disk_hold
    target_folder = []
    false_folder = []
    false_reason = []
    temp = UUP.DataCollectionUpload(data_path)
    for folder_name in temp.file_list:
        folder_path = data_path + folder_name
        check_result, check_reason = temp.checkRec(folder_path + '/')
        if not check_result:
            false_folder.append(folder_path)
            false_reason.append(check_reason)
        else:
            try:
                get_mission_key(folder_path)
            except BaseException:
                false_folder.append(folder_path)
                false_reason.append(check_reason)
                continue
            target_folder.append(folder_path)
    del temp

    # edit disk_hold
    id = get_disk_id(data_path.split('data')[0])
    disk_hold[id] = [len(target_folder), len(false_folder)]   # num of correct folders and incorrect ones
    false_line += false_folder
    false_reason_line += false_reason
    return target_folder

def get_task_id(path, json_name = '/data-tag.json'):
    if os.path.exists(path + json_name):
        with open(path + json_name, 'r') as f:
            try:
                json_data = json.load(f)
            except ValueError:
                print(" ==== ", path + json_name,
                      "\033[1;31m is not valuable json bytes \033[0m!\n")
                return 'cannot open json file'
        try:
            task_id = json_data['task_id']
        except BaseException:
            task_id = 'No Task ID'
        return task_id
    else:
        print('WARNING(get_task_id): ' + path + ' has no file named ' + json_name)
        # sig_src.send_error_info('WARNING(get_task_id): ' + path + ' has no file named ' + json_name)
        return 'No .json file'

def get_issue_id(path, json_name = '/data-tag.json'):
    if os.path.exists(path + json_name):
        with open(path + json_name, 'r') as f:
            try:
                json_data = json.load(f)
            except ValueError:
                print(" ==== ", path + json_name,
                      "\033[1;31m is not valuable json bytes \033[0m!\n")
                return 'cannot open json file'
        try:
            issue_id = json_data['issue_id']
        except BaseException:
            issue_id = 'No Issue ID'
        return issue_id
    else:
        print('WARNING(get_issue_id): ' + path + ' has no file named ' + json_name)
        # sig_src.send_error_info('WARNING(get_issue_id): ' + path + ' has no file named ' + json_name)
        return 'No .json file'

def get_mission_key(path, json_name = '/data-tag.json'):
    with open(path + json_name, 'r') as f:
        json_data = json.load(f)
    # mission_key = str(json_data['test_time_start']) + json_data['test_car_id']
    mission_key = get_disk_id(path.split('data')[0]) + path.split('data')[1]
    return mission_key

def add_mission_info(new_added_mission_list):
    global mission_info_keys
    global mission_info_memory
    for folder_path in new_added_mission_list:
        key = get_mission_key(folder_path)
        if key not in mission_info_keys:
            mission_info_keys.append(key)
        mission_info_memory[key] = {'硬盘ID': get_disk_id(folder_path.split('data')[0]),
                                    '任务ID': str(get_task_id(folder_path)),
                                    'Issue ID': str(get_issue_id(folder_path)),
                                    '状态': '准备切分',
                                    '上传进度': '',
                                    'mission_key': key}

def report_mission_error(key, error_info):
    global mission_info_memory
    mission_info_memory[key]['状态'] = error_info
    # report_disk_error(mission_info_memory[key]['硬盘ID'], '有异常')
    sig_src.send_info_sig(key)

def report_disk_error(ID, error_info):
    global disk_list
    disk_list[ID]['STATE'] = error_info
    sig_src.send_disk_sig()

def load_blacklist(file_dir = './dispatcher/history.json'):
    try:
        with open(file_dir, 'r') as f:
            json_data = json.load(f)

        blacklist = json_data['blacklist']
        return blacklist
    except BaseException:
        print("Error: Cannot load blacklist")
        return []

def add_blacklist(key, file_dir = './dispatcher/history.json'):
    global blacklist
    if key not in blacklist:
        blacklist.append(key)
    blacklist_dic = {"blacklist":blacklist}
    json_str = json.dumps(blacklist_dic)
    with open(file_dir, 'w') as json_file:
        json_file.write(json_str)

class signal_source(QObject):
    start_sig = pyqtSignal(object)
    data_path_sig = pyqtSignal(object)
    info_sig = pyqtSignal(object)
    disk_sig = pyqtSignal(object)
    new_upload_sig = pyqtSignal(object)
    completion_sig = pyqtSignal(object)
    error_sig = pyqtSignal(object)
    reboot_sig = pyqtSignal(object)
    def __init__(self):
        super(signal_source,self).__init__()

    def send_start_sig(self,data_path,object):
        self.send_data_path(data_path)
        self.start_sig.emit(object)

    def send_data_path(self,data_path):
        self.data_path_sig.emit(data_path)
        QApplication.processEvents()

    def send_info_sig(self,target_key = None):
        self.info_sig.emit(target_key)

    def send_disk_sig(self):
        self.disk_sig.emit(0)

    def new_upload(self,fold_path):
        self.new_upload_sig.emit(fold_path)

    def new_completion(self,num = 1):
        self.completion_sig.emit(num)
        QApplication.processEvents()

    def send_error_info(self,info):
        self.error_sig.emit(info)
        QApplication.processEvents()

    def send_reboot_sig(self, info = ''):
        self.reboot_sig.emit(info)

sig_src = signal_source()
blacklist = load_blacklist()