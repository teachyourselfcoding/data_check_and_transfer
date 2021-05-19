# coding=utf-8
"""
Call_Info_Fram.py
functions for UI display
by Zong Shihao
zongshihao@sensetime.com
"""

import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from Info_Fram import *
from archived_.ui_upload_python2 import DataCollectionUpload
# from ui_field_test import DataCollectionUpload
from ui_slot import sig_src, get_disk_id, record, SSD_dic
import psutil
import time
from datetime import datetime

work_disk_path = None

class Info_Window(QMainWindow,Ui_Info_Form):
    head_labels = ['Disk ID','Task ID','Issue_ID', 'State','Progress']
    log_labels = ['Time','Information']
    def __init__(self):
        super(Info_Window,self).__init__()
        self.setupUi(self)
        self.all_done = False
        # Detail_table config:
        self.Detail_table.setColumnCount(len(self.head_labels))
        self.Detail_table.setRowCount(1)
        for i in range(self.Detail_table.columnCount()):
            self.Detail_table.setColumnWidth(i,170)
        self.Detail_table.setHorizontalHeaderLabels(self.head_labels)
        # Log_table config:
        self.Log_table.setColumnCount(len(self.log_labels))
        self.Log_table.setRowCount(1)
        self.Log_table.setRowHeight(0,50)
        self.Log_table.setColumnWidth(1,730)
        self.Log_table.setHorizontalHeaderLabels(self.log_labels)

    def run(self):
        # self.detect_disk()
        data_check_class = DataCollectionUpload(str(self.SSD_browser.toPlainText()))
        self.upload_thread = Upload_Thread(data_check_class)
        self.upload_thread.start()


    def update_info(self,dic):
        if dic['State'] == '上传失败':
            self.reset('上传失败')
            return
        if dic['Completed'] == False:
            if dic['State'] == '上传成功':
                self.progress_thread.terminate()
                dic['Progress'] = ''
            for i in range(self.Detail_table.columnCount()):
                item = QTableWidgetItem(dic[self.head_labels[i]])
                item.setTextAlignment(Qt.AlignCenter)
                self.Detail_table.setItem(self.Detail_table.rowCount()-1,i,item)
        else:
            global work_disk_path
            work_disk_path = None
        # self.all_done = dic['Completed']
        # if self.all_done:
        #     global work_disk_path
        #     work_disk_path = None
        QApplication.processEvents()

    def update_disk_info(self):
        SSD_info = ''
        if len(list(SSD_dic.keys())) > 0:
            for item in list(SSD_dic.keys()):
                SSD_info += item + '  |  ' + SSD_dic[item]['state'] + '\n'
        else:
            SSD_info = 'No FieldTest detected \n'
        self.SSD_loaded_browser.setText(SSD_info)
        QApplication.processEvents()

    def get_progress(self, fold_path):
        data_size = 0.0
        ignore_path = "logs"
        for root, dirs, files in os.walk(fold_path):
            dirs[:] = [d for d in dirs if d != ignore_path];
            data_size += sum([os.path.getsize(os.path.join(root, file)) for file in files])
        data_size = round(data_size / 1000 / 1000 / 1000, 3)
        self.progress_thread = Progress_Thread(data_size)
        self.progress_thread.start()

    def add_row(self, num = 1):
        record['Progress'] = ''
        self.Detail_table.setRowCount(self.Detail_table.rowCount() + num)
        self.Detail_table.scrollToBottom()
        QApplication.processEvents()

    def disk_detect_start(self):
        self.disk_thread = Disk_Detect_Thread()
        self.disk_thread.start()

    def add_error_log(self,info):
        time_now = datetime.now()
        item_0 = QTableWidgetItem(time_now.strftime('%H:%M:%S'))
        item_0.setTextAlignment(Qt.AlignCenter)
        self.Log_table.setItem(self.Log_table.rowCount() - 1, 0, item_0)

        item_1 = QTableWidgetItem(info)
        item_1.setTextAlignment(Qt.AlignLeft)
        item_1.setTextAlignment(Qt.AlignVCenter)
        self.Log_table.setItem(self.Log_table.rowCount() - 1, 1, item_1)

        self.Log_table.setRowCount(self.Log_table.rowCount() + 1)
        self.Log_table.setRowHeight(self.Log_table.rowCount() - 1, 50)
        self.Log_table.scrollToBottom()
        QApplication.processEvents()

    def reset(self,info):
        self.upload_thread.terminate()
        self.progress_thread.terminate()
        self.disk_thread.terminate()
        record['State'] = info + '!!!'
        record['Progress'] = ''
        global work_disk_path
        work_disk_path = None
        print(record)
        sig_src.send_info(record)
        sig_src.send_data_path('')
        QApplication.processEvents()
        time.sleep(1)
        self.disk_detect_start()
        sig_src.send_error_info('程序已重启！请检查异常硬盘连接状态')

class Upload_Thread(QtCore.QThread):
    flg_all_done = False
    def __init__(self,data_check_class):
        super(Upload_Thread, self).__init__()
        self.data_check_class = data_check_class

    def __del__(self):
        self.wait()

    def run(self):
        try:
            self.data_check_class.main()
        except OSError:
            sig_src.send_reset_sig('硬盘意外弹出')

class Progress_Thread(QtCore.QThread):
    def __init__(self,data_size):
        super(Progress_Thread, self).__init__()
        self.data_size = data_size
        self.pre_bytes_sent = 0
        self.bytes_sent = 0
        self.upload_done = False

    def __del__(self):
        self.wait()

    def run(self):
        try:
            start_bytes_sent = psutil.net_io_counters().bytes_sent
            self.bytes_sent = start_bytes_sent
            time_step = 1
            time.sleep(time_step)
            while True:
                if self.upload_done:
                    record['Progress'] = str(self.data_size) + 'GB/' + str(self.data_size) + 'GB'
                    sig_src.send_info(record)
                    QApplication.processEvents()
                    break
                self.pre_bytes_sent = self.bytes_sent
                self.bytes_sent = psutil.net_io_counters().bytes_sent
                progress = round((self.bytes_sent - start_bytes_sent) / 1024.0 / 1024 / 1024, 3)
                speed = round((self.bytes_sent - self.pre_bytes_sent)/time_step /1024.0 / 1024, 3)
                record['Progress'] = str(progress) + 'GB/' + str(self.data_size) + 'GB'
                record['Progress'] += '  ' + str(speed) + ' MB/s'
                sig_src.send_info(record)
                time.sleep(time_step)
            self.terminate()
        except OSError:
            sig_src.send_reset_sig('硬盘意外弹出')

class Disk_Detect_Thread(QtCore.QThread):
    def __init__(self,):
        super(Disk_Detect_Thread, self).__init__()

    def __del__(self):
        self.wait()

    def run(self):
        while True:
            global work_disk_path
            if work_disk_path != None and list(SSD_dic.keys()) == []:
                sig_src.send_reset_sig('硬盘意外弹出哦')
            try:
                text = os.popen('df -h').readlines()
                delete_list = list(SSD_dic.keys())
                for line in text:
                    if 'FieldTest' in line:
                        disk_path = line.split(' ')[-1].replace('\n', '')
                        data_path = disk_path + '/data/'
                        ID = get_disk_id(disk_path)

                        if ID in delete_list:
                            delete_list.remove(ID)
                        else:
                            SSD_dic[ID] = {'data_path': data_path, 'state': '[ 待处理 ]'}
                        SSD_dic[ID]['data_path'] = data_path

                        global work_disk_path
                        if work_disk_path == None and SSD_dic[ID]['state'] == '[ 待处理 ]':
                            work_disk_path = disk_path
                            sig_src.send_start_sig(data_path,self)

                        if work_disk_path == None:
                            work_disk_id = None
                        else:
                            work_disk_id = get_disk_id(work_disk_path)

                        if ID == work_disk_id:
                            if SSD_dic[ID]['state'] == '[ 待处理 ]':
                                SSD_dic[ID]['state'] = '[ 处理中 ]'
                        else:
                            if ID in list(SSD_dic.keys()):
                                if SSD_dic[ID]['state'] == '[ 处理中 ]':
                                    SSD_dic[ID]['state'] = '[ 已完成 ]'
                            else:
                                SSD_dic[ID]['state'] = '[ 待处理 ]'
                for item in delete_list:
                    SSD_dic.pop(item)
                sig_src.send_disk_sig()
                time.sleep(1)
            except OSError:
                sig_src.send_reset_sig('硬盘意外弹出')


