# -*- coding: utf-8 -*-
from dispatcher.fun_thread_manage import *
import time


class Main_Window(QMainWindow,Ui_MainWindow):
    head_labels = ['硬盘ID', '任务ID', 'Issue ID', '状态', '上传进度']
    error_labels = ['时间', '详情']
    def __init__(self):
        super(Main_Window, self).__init__()
        self.setupUi(self)
        #   tableView_mission_info config
        self.tableWidget_mission_info.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget_mission_info.setColumnCount(len(self.head_labels))
        self.tableWidget_mission_info.setRowCount(1)
        for i in range(self.tableWidget_mission_info.columnCount()):
            self.tableWidget_mission_info.setColumnWidth(i, 170)
        self.tableWidget_mission_info.setHorizontalHeaderLabels(self.head_labels)
        #   tableWidget_error_info config
        self.tableWidget_error_info.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget_error_info.setColumnCount(len(self.error_labels))
        self.tableWidget_error_info.setHorizontalHeaderLabels(self.error_labels)
        self.tableWidget_error_info.setColumnWidth(0, 170)
        self.tableWidget_error_info.setColumnWidth(1, 680)
        self.tableWidget_error_info.setRowCount(1)

    def update_disk_info(self):
        disk_info = []
        if len(disk_list.keys()) > 0:
            for item in disk_priority:
                disk_info.append(item + '  |  ' + disk_list[item]['STATE'])
        else:
            disk_info.append('No FieldTest detected')
        slm = QStringListModel()
        slm.setStringList(disk_info)
        self.listView_disk_list.setModel(slm)
        QApplication.processEvents()

    def update_mission_info(self, target_key = None):
        self.tableWidget_mission_info.setRowCount(len(mission_info_keys) + 1)
        if target_key == None:
            # self.tableWidget_mission_info.setRowCount(len(mission_info_keys) + 1)
            row = 0
            for key in mission_info_keys:
                for i in range(self.tableWidget_mission_info.columnCount()):
                    item = QTableWidgetItem(mission_info_memory[key][self.head_labels[i]])
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget_mission_info.setItem(row, i, item)
                row += 1
            self.tableWidget_mission_info.scrollToBottom()
            QApplication.processEvents()
        else:
            row = mission_info_keys.index(target_key)
            for i in range(self.tableWidget_mission_info.columnCount()):
                item = QTableWidgetItem(mission_info_memory[target_key][self.head_labels[i]])
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_mission_info.setItem(row, i, item)
            self.tableWidget_mission_info.scrollToBottom()
            QApplication.processEvents()

    def update_error_info(self, info):
        row = self.tableWidget_error_info.rowCount()
        item = QTableWidgetItem(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        self.tableWidget_error_info.setItem(row - 1, 0, item)
        item = QTableWidgetItem(info)
        self.tableWidget_error_info.setItem(row - 1, 1, item)
        row += 1
        self.tableWidget_error_info.setRowCount(row)
        self.tableWidget_error_info.scrollToBottom()
        QApplication.processEvents()

def signal_init(main_window):
    sig_src.disk_sig.connect(main_window.update_disk_info)
    sig_src.info_sig.connect(main_window.update_mission_info)
    sig_src.reboot_sig.connect(reboot_threads)
    sig_src.error_sig.connect(main_window.update_error_info)

def threads_run():
    disk_thread.start()
    segment_thread.start()
    upload_thread.start()
    watch_dog_thread.start()

def reboot_threads(info):
    global reboot_disk_record
    # record numbers of reboot signals sent by every disk
    if len(disk_priority) > 0:
        if disk_priority[0] in reboot_disk_record.keys():
            reboot_disk_record[disk_priority[0]] += 1
        else:
            reboot_disk_record[disk_priority[0]] = 1
    try:
        segment_thread.terminate()
        upload_thread.terminate()
        watch_dog_thread.terminate()
        disk_thread.terminate()
        progress_thread.terminate()
    except BaseException:
        print("终止不存在的线程")
    sig_src.send_error_info(info + ', 线程已重启！')
    QApplication.processEvents()
    time.sleep(1)
    threads_run()
    print(info + ', 线程已重启！')
    print("segment_line")
    print(segment_line)
    print("upload_line")
    print(upload_line)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = Main_Window()
    main_window.show()

    signal_init(main_window)
    threads_run()

    sys.exit(app.exec_())