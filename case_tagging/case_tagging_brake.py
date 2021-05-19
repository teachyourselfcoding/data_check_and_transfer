# coding=utf-8

import os
import sys
import rosbag
import rospy
import pandas as pd
from datetime import datetime
import time
import fnmatch
import json
import math
sys.path.append("..")
from tools.read_and_write_json import loadTag,saveTag




class BrakeCaseTagging():
    def __init__(self,config_):
        self.case_finder_path = os.path.join(config_["senseauto_path"],
            'senseauto-simulation/node/build/module/simulator/tools/scenario_log_tools/case_finder')

    def getDataFromDpcbag(self,dpc_file, topic_names,record_timestamp):
        print(dpc_file)
        if not os.path.exists(dpc_file):
            print('bag not found')
            return

        control_error_topic = topic_names[0]
        bag = rosbag.bag.Bag(dpc_file)
        timestamp = []
        vehicle_acc_x = []
        vehicle_acc_y = []
        velocity_x = []
        brake_fdbk = []
        brake_cmd = []
        position_x = []
        position_y = []

        #print ("\033[1;32m [INFO]\033[0m! parsing dmppcl bag .........\n")
        for topic, msg, t in bag.read_messages(topics=control_error_topic):
            time_sec =  int(msg.header.stamp.to_sec())

            if time_sec > record_timestamp -4 and time_sec < record_timestamp+1:
                timestamp.append(msg.header.stamp.to_sec())
                vehicle_acc_x.append(msg.vehicle_acc_x)
                vehicle_acc_y.append(msg.vehicle_acc_y)
                velocity_x.append(msg.vehicle_vel_x)
                brake_fdbk.append(msg.vehicle_brake)
                brake_cmd.append(msg.brake_cmd)
                position_x.append(msg.utm_pos_x)
                position_y.append(msg.utm_pos_y)
        bag.close()

        dict_all = {
            'brake_fdbk': brake_fdbk,
            'vehicle_acc_x': vehicle_acc_x,
            'vehicle_acc_y': vehicle_acc_y,
            'velocity_x': velocity_x,
            'brake_cmd': brake_cmd,
            'position_x': position_x,
            'position_y': position_y,
        }

        keyname = 'timestamp'
        d = {'index_timestamp': range(0, len(timestamp)), keyname: timestamp}
        df = pd.DataFrame(data=d)
        pandas_all = df
        keylist = list(dict_all.keys())
        for keyname in keylist:
            if keyname == 'timestamp':
                continue
            else:
                d = {keyname: dict_all[keyname]}
                df = pd.DataFrame(data=d)
                pandas_all = pd.concat([pandas_all, df], axis=1)

        pandas_all_filtered = pandas_all.dropna(axis=1, how='all')

        # print(pandas_all_filtered)
        return pandas_all_filtered

    def parseBrakeTimestampFromBag(self,bag_data):
        ego_label={}
        if (bag_data.empty):
            print('empty bag data found')
            return
        max_timestamp = bag_data['timestamp'].loc[bag_data['brake_cmd'].argmax()]
        # ego_car_label = utility.format_time_group(utility.combine_time(
        #     max_timestamp.values, 1))
        index_timestamp = bag_data['index_timestamp'].loc[bag_data['brake_cmd'].argmax()]
        pd_label = bag_data.loc[index_timestamp]
        ego_label['timestamp'] = pd_label['timestamp']
        ego_label['brake_cmd'] = pd_label['brake_cmd']
        ego_label['position_x'] = pd_label['position_x']
        ego_label['position_y'] = pd_label['position_y']
        ego_label['velocity_x'] = pd_label['velocity_x']
        ego_label['vehicle_acc_x'] = pd_label['vehicle_acc_x']
        ego_label['vehicle_acc_y'] = pd_label['vehicle_acc_y']
        #print(ego_label)
        return max_timestamp,ego_label


    def unixToBjclock(self,unix_time):
        time_array = time.localtime(unix_time)
        now_time_style = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        return now_time_style


    def parseDecisionPannningLog(self,log_name, time_stamp,time_stamp_1,nsec,nsec_1):
        log_id_list = []
        list_set = set()

        for line in open(log_name, "r"):
            time = line[5:13]
            n_time = line[14:17]
            if not ":" in time:
                continue
            try:
                log_nsec = int(n_time)
            except:
                continue

            if time_stamp != time_stamp_1:
                if (time == time_stamp_1 and log_nsec > nsec_1) or \
                        (time == time_stamp and log_nsec < nsec):

                    tag_id_end = line.find(', tag')
                    tag_id_start = line.find('[PP] ')
                    if tag_id_end < 0 or tag_id_start < 0:
                        continue

                    obstacle_id = line[tag_id_start + 5:tag_id_end]
                    ret = self.judgeIdValue(obstacle_id)
                    if ret:
                        log_id_list.append(int(obstacle_id))
            else:
                if time == time_stamp_1 and log_nsec > nsec_1 and log_nsec < nsec:
                    tag_id_end = line.find(', tag')
                    tag_id_start = line.find('[PP] ')

                    if tag_id_end < 0 or tag_id_start < 0:
                        continue

                    obstacle_id = line[tag_id_start + 5:tag_id_end]
                    ret = self.judgeIdValue(obstacle_id)
                    if ret:
                        log_id_list.append(int(obstacle_id))

        if log_id_list ==[]:
            return [], []
        print(log_id_list)
        list_set.update(log_id_list)
        print('\n',list_set,'\n')

        obstacle_id_list =  self.filterObjectId(log_id_list)
        return obstacle_id_list,log_id_list

    def filterObjectId(self,object_id_list):
        max_distribution = 0
        id_dict = {}
        filted_list = []
        for objec_id in object_id_list:
            if not objec_id in id_dict.keys():
                id_dict[objec_id] = 0
            id_dict[objec_id] += 1
        print(id_dict)

        for object in id_dict:
            if id_dict[object] > max_distribution:
                max_distribution = id_dict[object]
        for object in id_dict:
            if id_dict[object] == max_distribution or id_dict[object]>8:
                filted_list.append(object)
        return filted_list

    def judgeIdValue(self,s):
        try:
            float(s)
            if (float(s)>0):
                return True
        except ValueError:
            pass

        try:
            import unicodedata
            unicodedata.numeric(s)
            if (unicodedata.numeric(s)>0):
                return True
        except (TypeError, ValueError):
            pass

        return False


    def parseFusionLog(self,log_name, obstacle_id, time_stamp):
        for line in open(log_name, "r"):
            time = line[5:13]
            if time != time_stamp:
                continue
            global_tag = line.find('Global')
            if global_tag < 0:
                continue

            tag_str_number = line.find(' ' + str(obstacle_id) + ' ')

            if tag_str_number > 0:
                label = line[tag_str_number + 1:]
                label_dict = self.obejctStrToDict(label)
                return label_dict

    def obejctStrToDict(self,str_label):

        label_dict = {}
        label_list = str_label.split(' ', -1)
        #print(label_list)

        label_dict['object_id'] = label_list[0]
        label_dict['object_class'] = label_list[1]
        label_dict['object_box_length'] = label_list[4]
        label_dict['object_box_width'] = label_list[5]
        label_dict['object_box_height'] = label_list[6]
        label_dict['object_position_mean_x'] = label_list[7]
        label_dict['object_position_mean_y'] = label_list[8]
        label_dict['object_velocity_x'] = label_list[9]
        label_dict['object_velocity_y'] = label_list[10]
        label_dict['object_acceleration_x'] = label_list[11]
        label_dict['object_acceleration_y'] = label_list[12]
        label_dict['object_confidence'] = label_list[14]
        return label_dict

    def getMatchedFilePaths(self,dir_path, pattern="*", formats=[".txt"], recursive=False):
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


    def case_finder(self,input_path,output_path,module_id = 2,object_id=0,input_timestamp=123,input_nsec=123,before_secs=5,after_seconds=1):
        case_finder_cmd = "{} {} {} {} {} {} {} {} {}".format(
            self.case_finder_path,
            input_path,
            os.path.join(output_path, 'case_finder.json'),
            str(module_id),
            str(object_id),
            str(input_timestamp),
            str(input_nsec),
            str(before_secs),
            str(after_seconds))
        print(case_finder_cmd,'\n')
        os.system(case_finder_cmd)

    def filterLogFile(self,log_list):
        if len(log_list) ==0:
            return ""
        max_file_size = 0
        max_log_file = log_list[0]
        for log_file_path in log_list:
            try:
                log_file_size  = os.path.getsize(log_file_path)
            except Exception as e:
                log_file_size = 0
            if max_file_size == 0 or max_file_size < log_file_size:
                max_file_size = log_file_size
                max_log_file = log_file_path
        return max_log_file

    def brake_main(self,raw_dir_path, record_tag):

        dir_path = record_tag["input_dir"]
        tagging_module = record_tag["tagging_module"]

        tag_save_path = ''.join([dir_path,'screen_cast/'])
        dpc_file_path = ''.join([dir_path,'dmppcl.bag'])
        bin_path = ''.join([dir_path,'simulator_scenario/0/logger.bin'])
        print(record_tag)


        if tagging_module == 3:
            self.case_finder(bin_path, tag_save_path, 3)
            tag = loadTag(tag_save_path,'case_finder.json')

        elif tagging_module == 0:
            bin_path = ''.join([dir_path,'/simulator_scenario/simulator_scenario_log.bin'])
            self.case_finder(bin_path, dir_path, 0)

        elif tagging_module ==2:

            topic_names = ['/control/control_error']
            tag_info = loadTag(dir_path)
            record_timestamp = int(tag_info["origin_record_tag"][0]["start"])/1000
            print(record_timestamp)
            bag_data = self.getDataFromDpcbag(dpc_file_path, topic_names,record_timestamp)
            brake_timestamp,ego_label = self.parseBrakeTimestampFromBag(bag_data)
            brake_timestamp_bj = self.unixToBjclock(brake_timestamp)
            brake_timestamp_bj_1 = self.unixToBjclock(brake_timestamp - 0.5)
            nsec = math.modf(brake_timestamp )[0] * 1000
            nsec_1 = math.modf(brake_timestamp-0.5)[0] * 1000
            print ('brake case timestamp: ',brake_timestamp, brake_timestamp_bj)
            id_json_path = ''.join([record_tag["input_dir"],'screen_cast/obstacle.json'])

            self.case_finder(bin_path,tag_save_path,2,id_json_path,int(brake_timestamp),int(nsec),5,1)
        else:
            self.case_finder(bin_path, tag_save_path, 1, 0, int(record_tag["input_timestamp"]), int(000), 5, 1)


def getAllDataDir(input_data_path):
    "get all dir in data"
    file_list=[]
    for file in os.listdir(input_data_path):
        dir_file = os.path.join(input_data_path, file)

        if (os.path.isdir(dir_file)):
            h = os.path.split(dir_file)
            file_list.append(h[1])
    return file_list

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


def calculatePrecision(dir_path,file_list):

    true_tagging = 0
    false_tagging= 0
    for brake_dir_name in file_list:
        case_tagging_path = dir_path+brake_dir_name+'/screen_cast/'
        id_file_path = GetMatchedFilePaths(case_tagging_path,"*",".id",False)
        print(brake_dir_name,id_file_path)
        id_file_name = os.path.basename(id_file_path[0])
        true_id = int(id_file_name.split('.',-1)[0])
        tagging_json = loadTag(case_tagging_path,'case_finder.json')
        tagging_id = int(tagging_json[0]["obstacle_id"][0])

        if true_id == tagging_id:
            true_tagging +=1
        else:
            false_tagging +=1
            print(brake_dir_name)

    print ("\n====tagging precision====: ",float(true_tagging)/float(true_tagging+false_tagging),'\n')


from threadpool import ThreadPool, makeRequests
import multiprocessing

if __name__ == '__main__':
    config_ = loadTag("../config/data_pipeline_config.json",'')
    case_tagging =  BrakeCaseTagging(config_)
    pool = ThreadPool(int(multiprocessing.cpu_count() * 0.4))
    dir_path =  "/media/sensetime/FieldTest/data/12_ARH/2020_10_30_14_23_42_AutoCollect_slice/DPC/Emergency_brake/"
    file_list = getAllDataDir(dir_path)
    input_list = []
    #calculatePrecision(dir_path, file_list)
    for brake_dir_name in file_list:
        print(brake_dir_name)
        #print(brake_dir_path)
        record_tag  ={}
        record_tag["input_dir"] = dir_path+brake_dir_name+'/'
        record_tag["tagging_module"] = 2
        if not os.path.exists(dir_path+brake_dir_name+'/screen_cast'):
            os.makedirs(dir_path+brake_dir_name+'/screen_cast')

        input_list.append(([dir_path, record_tag], None))
    requests = makeRequests(case_tagging.main, input_list)
    [pool.putRequest(req) for req in requests]
    pool.wait()




