# -*- coding: utf-8 -*-
import sys
from fun_basic import *
import time
import psutil

sys.path.append('..')
from archived_ import ui_upload_python2 as UUP


class Disk_Detect_Thread(QThread):
    def __init__(self,):
        super(Disk_Detect_Thread, self).__init__()

    def __del__(self):
        self.wait()

    def production_line_manage(self):
        global segment_line
        global upload_line
        global blacklist

        max_working_disk_count = 2
        working_disk_count = 0
        waiting_disk_count = 0
        for disk in disk_list.values():
            if disk['STATE'] == '[ 处理中 ]':
                working_disk_count += 1
            if disk['STATE'] == '[ 待处理 ]':
                waiting_disk_count += 1
        if working_disk_count > max_working_disk_count:
            print("Error: working_disk_count overflow")
            sig_src.send_error_info("Error: working_disk_count overflow")

        # clear disappeared folders from production line
        idx = 0
        while idx < len(segment_line):
            if not os.path.exists(segment_line[idx]):
                del segment_line[idx]
            else:
                idx += 1
        idx = 0
        while idx < len(upload_line):
            if not os.path.exists(upload_line[idx]):
                del upload_line[idx]
            else:
                idx += 1

        # add new tasks to production line
        while working_disk_count < max_working_disk_count and waiting_disk_count > 0:
            id = disk_priority[working_disk_count]
            new_added_mission = get_target_floder_path(disk_list[id]['DATA_FOLDER_PATH'])
            # kick out missions whose keys are in the blacklist
            idx = 0
            while idx < len(new_added_mission):
                key = get_mission_key(new_added_mission[idx])
                if key in blacklist:
                    new_added_mission.remove(new_added_mission[idx])
                else:
                    idx += 1
            # add new mission to segment line
            segment_line += new_added_mission
            add_mission_info(new_added_mission)
            sig_src.send_info_sig()
            disk_list[id]['STATE'] = '[ 处理中 ]'
            working_disk_count += 1
            waiting_disk_count -= 1

    def run(self):
        global flg_disk_changed
        global segment_line

        while True:
            try:
                text = os.popen('df -h').readlines()
                delete_list = list(disk_list.keys())
                for line in text:
                    if 'FieldTest' in line:
                        disk_path = line.split(' ')[-1].replace('\n', '')
                        data_path = disk_path + '/data/'
                        ID = get_disk_id(disk_path)

                        if ID in delete_list:
                            delete_list.remove(ID)
                            if disk_list[ID]['DATA_FOLDER_PATH'] != data_path:
                                disk_list[ID]['DATA_FOLDER_PATH'] = data_path
                                flg_disk_changed = True
                        else:   # new disk loaded
                            disk_list[ID] = {'DATA_FOLDER_PATH': data_path, 'STATE': '[ 待处理 ]'}
                            if ID in reboot_disk_record.keys() and reboot_disk_record[ID] > 10:
                                disk_list[ID]['STATE'] = '[ 有异常 ]'
                            # insert disk id into disk_priority
                            if len(disk_priority) == 0 \
                                    or (disk_list[disk_priority[-1]]['STATE'] == '[ 待处理 ]' \
                                    or disk_list[disk_priority[-1]]['STATE'] == '[ 处理中 ]'):
                                disk_priority.append(ID)
                            else:
                                idx = 0
                                while disk_list[disk_priority[idx]]['STATE'] == '[ 待处理 ]' \
                                        or disk_list[disk_priority[idx]]['STATE'] == '[ 处理中 ]':
                                    idx += 1
                                    if idx == len(disk_priority) - 1:
                                        break
                                disk_priority.insert(idx, ID)
                            flg_disk_changed = True

                # delete data of removed disks from disk_list
                for item in delete_list:
                    # when a disk was removed accidentally
                    if disk_list[item]['STATE'] == '[ 处理中 ]':
                        # report error info
                        for key in mission_info_keys:
                            if mission_info_memory[key]['硬盘ID'] == item and mission_info_memory[key]["状态"] != "已完成":
                                report_mission_error(key, '被中断')
                                # delete mission in production line

                        # reboot programe
                        print('硬盘意外弹出')
                        sig_src.send_reboot_sig('硬盘意外弹出')

                    disk_list.pop(item)
                    disk_priority.remove(item)
                    try:
                        del disk_hold[item]
                    except BaseException:
                        pass
                    flg_disk_changed = True

                if len(disk_priority) != len(disk_list.keys()):
                    print("Error: disk_priority length")
                    sig_src.send_error_info("Error: disk_priority length")

                if flg_disk_changed:
                    self.production_line_manage()
                    sig_src.send_disk_sig()
                    flg_disk_changed = False
                time.sleep(1)
                watch_dog_thread.feed_dog("disk")
            except OSError as e:
                sig_src.send_error_info('Disk_Detect_Thread: ' + str(e))
                print('硬盘意外弹出')
                self.production_line_manage()
                # break #
            # except BaseException:

class Segment_Thread(QtCore.QThread):
    def __init__(self):
        super(Segment_Thread, self).__init__()
        self.data_process = None

    def __del__(self):
        self.wait()

    def switch_path(self,data_input_path):
        del self.data_process
        self.data_process = UUP.DataCollectionUpload(data_input_path)

    def run(self):
        print('Segment_Thread started   ')
        global segment_line
        global mission_info_keys
        global mission_info_memory
        while True:
            time.sleep(0.1)
            try:
                dog_food = ''
                if len(segment_line) > 0:
                    if not os.path.exists(segment_line[0]):
                        del segment_line[0]
                        continue
                    dog_food = segment_line[0]
                    data_path = segment_line[0].split('data')[0] + 'data/'
                    folder_name = segment_line[0].split('data/')[1]

                    if self.data_process == None or data_path != self.data_process.input_data_path:
                        self.switch_path(data_path)

                    key = get_mission_key(data_path + folder_name)
                    mission_info_memory[key]['状态'] = '切分中'
                    sig_src.send_info_sig(key)

                    segment_result = self.data_process.mainSegment(folder_name)
                    if segment_result == 0:
                        print(folder_name + ' is segmented')
                        mission_info_memory[key]['状态'] = '准备上传'
                        sig_src.send_info_sig(key)
                        upload_line.append(segment_line[0])
                    else:
                        print(folder_name + ' segment failed, error code: ' + str(segment_result))
                        report_mission_error(key, '切分失败')
                    del segment_line[0]
                watch_dog_thread.feed_dog("segment", dog_food)
            except OSError:
                print('OSError of Segment_Thread')
            except BaseException:
                print('BaseException of Segment_Thread')
                continue

class Upload_Thread(QtCore.QThread):
    def __init__(self):
        super(Upload_Thread, self).__init__()
        self.data_process = None

    def __del__(self):
        self.wait()

    # def switch_path(self,data_input_path):
    #     del self.data_process
    #     self.data_process = UUP.DataCollectionUpload(data_input_path)

    def check_data_path(self, data_input_path):
        if self.data_process == None or data_input_path != self.data_process.input_data_path:
            del self.data_process
            self.data_process = UUP.DataCollectionUpload(data_input_path)

    def run(self):
        print('Upload_Thread started   ')
        global upload_line
        global false_line
        global disk_hold
        global flg_disk_changed
        while True:
            time.sleep(0.1)
            try:
                dog_food = ''
                if len(upload_line) > 0:
                    if not os.path.exists(upload_line[0]):
                        del upload_line[0]
                        continue
                    dog_food = upload_line[0]
                    data_path = upload_line[0].split('data')[0] + 'data/'
                    folder_name = upload_line[0].split('data/')[1]

                    # if self.data_process == None or data_path != self.data_process.input_data_path:
                    #     self.switch_path(data_path)
                    self.check_data_path(data_path)

                    key = get_mission_key(data_path + folder_name)
                    mission_info_memory[key]['状态'] = '上传中'
                    progress_thread.set_key(key)
                    progress_thread.start()
                    sig_src.send_info_sig(key)

                    upload_result = self.data_process.mainUpload(upload_line[0])
                    progress_thread.upload_done = True
                    if upload_result == 0:
                        print(folder_name + ' is uploaded')
                        mission_info_memory[key]['状态'] = '上传成功'
                        mission_info_memory[key]['状态'] = '已完成'
                    else:
                        print(folder_name + ' uploading failed')
                        report_mission_error(key, '上传失败')
                        # Considering that all situation may cause uploading failure have been considered,
                        # it is not necessary to use blacklist here.

                    '''
                    # excute when a disk is complished
                    if get_disk_id(upload_line[0].split('data')[0]) != disk_priority[0]:
                        print('Disk ' + disk_priority[0] + 'is completed')
                        disk_list[disk_priority[0]]['STATE'] = '[ 已完成 ]'
                        disk_priority.append(disk_priority[0])
                        del disk_priority[0]
                        flg_disk_changed = True
                    '''
                    id = get_disk_id(upload_line[0].split('data')[0])
                    disk_hold[id][0] -= 1

                    del upload_line[0]
                    sig_src.send_info_sig(key)

                else:
                    try:
                        '''
                        # when the last disk is done
                        if len(segment_line) == 0 and len(disk_list.keys()) > 0 and disk_list[disk_priority[0]]['STATE'] == '[ 处理中 ]':
                            print('Disk ' + disk_priority[0] + ' is completed')
                            disk_list[disk_priority[0]]['STATE'] = '[ 已完成 ]'
                            disk_priority.append(disk_priority[0])
                            del disk_priority[0]
                            print('All disks are completed')
                            flg_disk_changed = True
                        '''

                        # when false_line is not empty
                        if len(false_line) > 0:
                            dog_food = false_line[0]
                            data_path = false_line[0].split('data')[0] + 'data/'
                            self.check_data_path(data_path)
                            self.data_process.falseDataArchive(false_line[0], false_reason_line[0])

                            id = get_disk_id(false_line[0].split('data')[0])
                            disk_hold[id][1] -= 1

                            del false_line[0]
                            del false_reason_line[0]

                    except IndexError as e:
                        print('IndexError of Upload_Thread: ' + str(e))
                    except BaseException:
                        continue

                # when a disk is done
                try:
                    disk_done_flg = disk_hold[disk_priority[0]] == [0,0]
                except BaseException:
                    disk_done_flg = False
                if disk_done_flg:
                    print('Disk ' + disk_priority[0] + ' is completed')
                    disk_list[disk_priority[0]]['STATE'] = '[ 已完成 ]'
                    disk_priority.append(disk_priority[0])
                    del disk_hold[disk_priority[0]]
                    del disk_priority[0]
                    flg_disk_changed = True
                watch_dog_thread.feed_dog("upload", dog_food)
            except OSError:
                print('OSError of Upload_Thread')
            # except BaseException:
            #     print('BaseException of Upload_Thread')
            #     continue

class Progress_Thread(QtCore.QThread):
    def __init__(self):
        super(Progress_Thread, self).__init__()
        self.key = None
        self.upload_done = True
        self.pre_bytes_sent = 0
        self.bytes_sent = 0

    def __del__(self):
        self.wait()

    def set_key(self,key):
        self.key = key
        fold_path = upload_line[0]
        if get_mission_key(fold_path) != key:
            print('Error: Progress_Thread.key does not correspond upload_line\n')
            sig_src.send_error_info('Error: Progress_Thread.key does not correspond upload_line')
        self.data_size = 0.0
        ignore_path = "logs"
        for root, dirs, files in os.walk(fold_path):
            dirs[:] = [d for d in dirs if d != ignore_path];
            self.data_size += sum([os.path.getsize(os.path.join(root, file)) for file in files])
        if os.path.exists(fold_path + "_slice"):
            for root, dirs, files in os.walk(fold_path + "_slice"):
                dirs[:] = [d for d in dirs if d != ignore_path];
                self.data_size += sum([os.path.getsize(os.path.join(root, file)) for file in files])
        self.data_size = round(self.data_size / 1000 / 1000 / 1000, 3)
        self.upload_done = False

    def run(self):
        try:
            start_bytes_sent = psutil.net_io_counters().bytes_sent
            self.bytes_sent = start_bytes_sent
            time_step = 1
            # time.sleep(time_step)
            while True:
                if self.upload_done:
                    mission_info_memory[self.key]['上传进度'] = '完成于' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    sig_src.send_info_sig(self.key)
                    break
                self.pre_bytes_sent = self.bytes_sent
                self.bytes_sent = psutil.net_io_counters().bytes_sent
                progress = round((self.bytes_sent - start_bytes_sent) / 1024.0 / 1024 / 1024, 3)
                speed = round((self.bytes_sent - self.pre_bytes_sent)/time_step /1024.0 / 1024, 3)
                mission_info_memory[self.key]['上传进度'] = str(progress) + 'GB/' + str(self.data_size) + 'GB'
                mission_info_memory[self.key]['上传进度'] += '  ' + str(speed) + ' MB/s'
                sig_src.send_info_sig(self.key)
                time.sleep(time_step)
            watch_dog_thread.feed_dog("progress")
        except OSError:
            # sig_src.send_reset_sig('硬盘意外弹出')
            print('OSError of Progress_Thread')
            sig_src.send_error_info('OSError of Progress_Thread')

class Watch_Dog_Thread(QtCore.QThread):
    def __init__(self):
        super(Watch_Dog_Thread, self).__init__()
        self.reset()

    def __del__(self):
        self.wait()

    def reset(self):
        # time out threshold (seconds)
        self.time_th_disk = 15.0
        self.time_th_segment = 180 * 60.0
        self.time_th_upload = 120*60.0
        self.time_th_progress = 5.0
        # timer ticks
        self.timer_disk = time.time()
        self.timer_segment = time.time()
        self.timer_upload = time.time()
        self.timer_progress = time.time()
        # dog food
        self.food_disk = ''
        self.food_segment = ''
        self.food_upload = ''

    def feed_dog(self,thread, msg = ''):
        if thread == "disk":
            self.timer_disk = time.time()
            return 0

        if thread == "segment":
            if self.food_segment == msg and msg != '':
                print("Segment_Thread is in an endless loop")
                sig_src.send_error_info('切分线程卡死/陷入死循环')
                self.timer_segment -= self.time_th_segment
                return 2
            self.timer_segment = time.time()
            self.food_segment = msg
            return 0

        if thread == "upload":
            if self.food_upload == msg and msg != '':
                print("Upload_Thread is in an endless loop")
                sig_src.send_error_info("上传线程卡死/陷入死循环")
                self.timer_upload -= self.time_th_upload
                return 3
            self.timer_upload = time.time()
            self.food_upload = msg
            return 0

        if thread == "progress":
            self.timer_progress = time.time()
            return 0

        print("Error: feed wrong food, dog is angry")
        sig_src.send_error_info("Error: 狗粮错误, 看门狗很生气, 后果很严重！")
        return 1

    def run(self):
        self.reset()
        flg_no_food = False
        while True:
            time.sleep(0.1)
            time_tick = time.time()
            if time_tick - self.timer_disk > self.time_th_disk:
                print("Disk_Detect_Thread time out")
                sig_src.send_error_info("Disk_Detect_Thread 线程超时")
                flg_no_food = True

            if time_tick - self.timer_segment > self.time_th_segment:
                print("Segment_Thread time out")
                if len(segment_line) > 0:
                    key = get_mission_key(segment_line[0])
                    report_mission_error(key, '切分超时')
                    sig_src.send_error_info(segment_line[0] + '切分超时')
                    add_blacklist(key)
                    # flg_no_food = True
                else:
                    sig_src.send_error_info('segment_line为空, 切分线程超时')
                flg_no_food = True

            if time_tick - self.timer_upload > self.time_th_upload:
                print("Upload_Thread time out")
                if len(upload_line) > 0:
                    key = get_mission_key(upload_line[0])
                    report_mission_error(key, '上传超时')
                    sig_src.send_error_info(upload_line[0] + '上传超时')
                    add_blacklist(key)
                    # flg_no_food = True
                else:
                    sig_src.send_error_info('upload_line为空, 上传线程超时')
                flg_no_food = True

            # if time_tick - self.timer_progress > self.time_th_progress:
            #     print("Progress_Thread time out")
            #     flg_no_food = True

            if flg_no_food:
                sig_src.send_reboot_sig('看门狗触发重启')
                self.reset()
                flg_no_food = False

segment_thread = Segment_Thread()
upload_thread = Upload_Thread()
disk_thread = Disk_Detect_Thread()
progress_thread = Progress_Thread()
watch_dog_thread = Watch_Dog_Thread()