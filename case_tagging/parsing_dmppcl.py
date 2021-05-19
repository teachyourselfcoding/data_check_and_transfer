# coding=utf-8

import os
import sys
import rosbag
import rospy
import pandas as pd
from datetime import datetime
import time
import fnmatch



def getDataFromDpcbag(dpc_file,topic_names):
    if not os.path.exists(dpc_file):
        print('bag not found')
        return

    control_error_topic = topic_names[0]
    bag = rosbag.bag.Bag(dpc_file)
    timestamp = []
    lon_acc = []
    velocity=[]
    brake_fdbk =[]
    brake_cmd = []
    position_x=[]
    position_y=[]
    print ("\033[1;32m [INFO]\033[0m! parsing dmppcl bag .........\n")
    for topic, msg, t in bag.read_messages(topics=control_error_topic):

        timestamp.append(msg.header.stamp.to_sec())
        lon_acc.append(msg.vehicle_acc_x)
        velocity.append(msg.vehicle_vel_x)
        brake_fdbk.append(msg.vehicle_brake)
        brake_cmd.append(msg.brake_cmd)
        position_x.append(msg.utm_pos_x)
        position_y.append(msg.utm_pos_y)

    bag.close()


    dict_all = {
        'brake_fdbk': brake_fdbk,
        'lon_acc': lon_acc,
        'velocity': velocity,
        'brake_cmd': brake_cmd,
        'position_x':position_x,
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

    #print(pandas_all_filtered)
    return pandas_all_filtered


def parseBag(bag_data):
    #bag_data_tmp=bag_data[(bag_data['timestamp']>label_timestamp -10) & (bag_data['timestamp']<label_timestamp)]
    max_timestamp=brakeAnalysis(bag_data)

    return max_timestamp



def brakeAnalysis(bag_data):
    if (bag_data.empty):
        print('empty bag data found')
        return

    max_timestamp= bag_data['timestamp'].loc[bag_data['brake_cmd'].argmax()]


    return max_timestamp



def unixToBjclock(unix_time):
    time_array=time.localtime(unix_time)
    now_time_style=time.strftime('%H:%M:%S',time_array)

    return now_time_style


def parseDPLog(log_name,time_stamp):
    log_id = []
    for line in open(log_name, "r"):
        time = line[5:13]
        if time != time_stamp:
            continue
        tag_str_number=line.find(', tag')

        if tag_str_number < 0:
            continue


        obstacle_id = line[tag_str_number-3:tag_str_number]
        log_id.append(obstacle_id)
    print(log_id)
    return max(log_id,key=log_id.count)

def parseFusionLog(log_name,obstacle_id,time_stamp):
    for line in open(log_name, "r"):
        time = line[5:13]
        if time != time_stamp:
            continue
        global_tag = line.find('Global')
        if global_tag < 0:
            continue

        tag_str_number = line.find(' '+str(obstacle_id)+' ')

        if tag_str_number > 0:
            label = line[tag_str_number+1:]
            label_dict = strToDict(label)
            return label_dict


def strToDict(str_label):

    label_dict={}
    label_list=str_label.split(' ',-1)
    print(label_list)

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







def getMatchedFilePaths(dir_path, pattern="*", formats=[".txt"], recursive=False):
    "get all the files in <dir_path> with specified pattern"
    files = []
    data_dir = os.path.normpath(os.path.abspath(dir_path))
    try:
        for f in os.listdir(data_dir):
            current_path = os.path.join(os.path.normpath(data_dir), f)
            if os.path.isdir(current_path) and recursive:
                files += getMatchedFilePaths(current_path, pattern, formats,
                                                  recursive)
            elif fnmatch.fnmatch(f,
                                 pattern) and os.path.splitext(f)[-1] in formats:
                files.append(current_path)
        return files
    except OSError:
        print("os error")
        return []



def main():
    dpc_file='/media/sensetime/FieldTest/data/07_14_CN-008_ARH/2020_07_14_22_30_29_AutoCollect_slice/DPC/false_brake/2020_07_14_22_24_22/dmppcl.bag'
    topic_names = ['/control/control_error']

    bag_data = getDataFromDpcbag(dpc_file, topic_names)
    brake_timestamp = parseBag(bag_data)
    brake_timestamp_bj = unixToBjclock(brake_timestamp)
    # print(brake_timestamp)
    # print(brake_timestamp_bj)

    log_path='/media/sensetime/FieldTest/data/07_14_CN-008_ARH/2020_07_14_22_30_29_AutoCollect_slice/DPC/false_brake/2020_07_14_22_24_22/logs/'
    decision_planning_log_file = getMatchedFilePaths(log_path,'ros_decision_planning_node.*')

    obstacle_id = parseDPLog(decision_planning_log_file[0],brake_timestamp_bj)
    print(obstacle_id)

    fusion_background_log_file = getMatchedFilePaths(log_path+'background_log/','ros_sensor_fusion_node_background.*')

    obstacle_label = parseFusionLog(fusion_background_log_file[0],obstacle_id,brake_timestamp_bj)
    print(obstacle_label)













if __name__ == '__main__':
    main()