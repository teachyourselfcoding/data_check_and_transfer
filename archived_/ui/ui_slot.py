# coding=utf-8
"""
ui_solt.py
functions and objects imported in ui_field_test.py.
this file gets mission state and emits signals for slots of UI objects

by Zong Shihao
zongshihao@sensetime.com
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
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication
import time
import psutil

record = {'Disk ID':'', 'Task ID':'', 'State':'', 'Progress':'','Completed':False, 'Issue_ID':''}
SSD_dic = {}

class signal_source(QObject):
    start_sig = pyqtSignal(object)
    data_path_sig = pyqtSignal(object)
    info_sig = pyqtSignal(object)
    disk_sig = pyqtSignal(object)
    new_upload_sig = pyqtSignal(object)
    completion_sig = pyqtSignal(object)
    error_sig = pyqtSignal(object)
    reset_sig = pyqtSignal(object)
    def __init__(self):
        super(signal_source,self).__init__()

    def send_start_sig(self,data_path,object):
        self.send_data_path(data_path)
        self.start_sig.emit(object)

    def send_data_path(self,data_path):
        self.data_path_sig.emit(data_path)
        QApplication.processEvents()

    def send_info(self,dic):
        self.info_sig.emit(dic)

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

    def send_reset_sig(self,info):
        self.reset_sig.emit(info)

sig_src = signal_source()

def get_disk_id(path):
    if not os.path.exists(path):
        sig_src.send_error_info('path: ' + path + 'does not exist')
    all_file = os.listdir(path)
    for item in all_file:
        if item.split('.')[-1] == 'id':
            return item.split('.')[0]
    return 'Unknown'

def get_task_id(path, json_name = '/data-tag.json'):
    if os.path.exists(path + json_name):
        with open(path + json_name, 'r') as f:
            try:
                json_data = json.load(f)
            except ValueError:
                print(" ==== ", path + json_name,
                      "\033[1;31m is not valuable json bytes \033[0m!\n")
                return 'No .json file'
        task_id = json_data['task_id']
        return task_id
    else:
        print('WARNING(get_task_id): ' + path + ' has no file named ' + json_name)
        sig_src.send_error_info('WARNING(get_task_id): ' + path + ' has no file named ' + json_name)
        return 'Wrong PATH'

def get_issue_id(path, json_name = '/data-tag.json'):
    if os.path.exists(path + json_name):
        with open(path + json_name, 'r') as f:
            try:
                json_data = json.load(f)
            except ValueError:
                print(" ==== ", path + json_name,
                      "\033[1;31m is not valuable json bytes \033[0m!\n")
                return 'No .json file'
        task_id = json_data['issue_id']
        return task_id
    else:
        print('WARNING(get_issue_id): ' + path + ' has no file named ' + json_name)
        sig_src.send_error_info('WARNING(get_issue_id): ' + path + ' has no file named ' + json_name)
        return 'Wrong PATH'

def mission_prep(input_data_path,dir_name):
    record['Disk ID'] = get_disk_id(input_data_path.split('data')[0])
    record['Task ID'] = str(get_task_id(input_data_path + dir_name))
    record['Issue_ID'] = str(get_issue_id(input_data_path + dir_name))
    record['State'] = '读取数据'
    record['Completed'] = False
    if record['Task ID'] == 'Wrong PATH':
        record['State'] = '跳过'
        sig_src.send_info(record)
        return False
    # sig_src.new_upload(input_data_path + dir_name)
    sig_src.send_info(record)
    return True

def mission_error(error_info = None):
    misson_complete(0)
    if error_info:
        sig_src.send_error_info(error_info)

def misson_complete(num = 1):
    record['State'] = '完成'
    sig_src.send_info(record)
    sig_src.new_completion(num)
    time.sleep(1)

def disk_complete():
    record['Completed'] = True
    sig_src.send_info(record)

def update_state(data = ''):
    record['State'] = data
    sig_src.send_info(record)