#!/usr/bin/env python2

import os
import sys
import json
import time
import rosbag
import time as libtime
import datetime
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
sys.path.append("..")

def saveTag(tag_file_path, tag_data, file_name='data-tag.json'):
    '''
    save json file
    :param tag_file_path: save path
    :param tag_data: to be saved json
    :param file_name: to be savad file name
    '''
    tag_file = os.path.abspath(os.path.join(tag_file_path, file_name))
    if not os.path.exists(tag_file_path):
        os.mkdir(tag_file_path)
    if not os.path.exists(tag_file):
        os.mknod(tag_file)
    with open(tag_file, 'w') as fw:
        json.dump(tag_data, fw, indent=4)

def unixToBjclock(unix_time):
    time_array = time.localtime(unix_time)
    now_time_style = time.strftime("%H-%M-%S", time_array)
    return now_time_style


def getDataFromDpcbag(dpc_file,topic_names):
    if not os.path.exists(dpc_file):
        print('bag not found')
        return

    bag = rosbag.bag.Bag(dpc_file)
    ros_msg = {}
    print ("\033[1;32m [INFO]\033[0m! parsing dmppcl bag .........\n")
    for topic, msg, t in bag.read_messages():
        if topic not in ros_msg.keys():
            ros_msg[topic] = {}
            ros_msg[topic]["bj_time"] = []
            ros_msg[topic]["timestamp"] = []
            ros_msg[topic]["seq"] = []
            ros_msg[topic]["frame_diff"] = []
            ros_msg[topic]["frame_hz"] = []

        ros_msg[topic]["timestamp"].append(msg.header.stamp.to_sec())
        ros_msg[topic]["bj_time"].append(unixToBjclock(msg.header.stamp.to_sec()))
        ros_msg[topic]["seq"].append(msg.header.seq)
    bag.close()
    return ros_msg




def getModuleStatis(module_msg):
    ststics = {}
    try:
        ststics["avg_frame_rate"] = (len(module_msg["timestamp"]) -1) / (module_msg["timestamp"][-1] - module_msg["timestamp"][0])
    except:
        ststics["avg_frame_rate"] = 0
    print(ststics["avg_frame_rate"])
    ststics["stddev_frame_rate"] = np.std(module_msg["frame_diff"])
    ststics["min_frame_rate"] =  1/np.max(module_msg["frame_diff"])
    return ststics


def getSensorStatis(module_msg):
    ststics = {}
    try:
        ststics["avg_frame_rate"] = (len(module_msg["timestamp"]) -1) / (module_msg["timestamp"][-1] - module_msg["timestamp"][0])
    except:
        ststics["avg_frame_rate"] = 0
    ststics["stddev_frame_rate"] = np.std(module_msg["frame_diff"])
    ststics["min_frame_rate"] =  1/np.max(module_msg["frame_diff"])
    return ststics

def getUpDownTime(module_msg,up_stream,down_stream,module):
    time_consuming = []

    for j in range(len(module_msg[down_stream]["timestamp"]) - 1):
        for i in range(len(module_msg[up_stream]["timestamp"]) - 1):
            if module_msg[down_stream]["timestamp"][j] > module_msg[up_stream]["timestamp"][i] and \
                    module_msg[down_stream]["timestamp"][j] < module_msg[up_stream]["timestamp"][i + 1]:
                time_consuming.append((module_msg[down_stream]["timestamp"][j] - module_msg[up_stream]["timestamp"][i])*1000-10)
                break
    return time_consuming

def getModuleConsuming(module_msg, updown_stream,module):
    ststics = {}
    time_consuming = []
    up_stream = updown_stream[0]
    down_stream = updown_stream[1]
    if up_stream not in module_msg.keys() or down_stream not in module_msg.keys():
        return ststics
    if len(module_msg[up_stream])<2 or len(module_msg[down_stream])<2:
        return ststics
    time_consuming = getUpDownTime(module_msg,up_stream,down_stream,module)
    ststics["avg_time_consuming"] = np.mean(time_consuming)
    ststics["max_time_consuming"] = np.max(time_consuming)
    ststics["stddev_time_consuming"] = np.std(time_consuming)
    return ststics,time_consuming


def DrawModuleGraph(ros_msg,output_folder,topic_list):

    module_eval = {}
    if not output_folder or not os.path.exists(output_folder):
        print('Output folder not existed: {}'.format(output_folder))
        sys.exit(1)
    for topic,msg in ros_msg.items():
        if not topic in topic_list:
            continue
        ros_msg[topic]["frame_diff"] = np.diff(ros_msg[topic]["timestamp"])
        ros_msg[topic]["frame_hz"] = 1/ros_msg[topic]["frame_diff"]
        if topic == "/localization/navstate_info":
            print(ros_msg[topic]["frame_hz"])

    # consuming_list = {
    #     "DPC": ["/prediction/objects", "/decision_planning/planning_debug"],
    #     "Prediction": ["/perception/fusion/object", "/prediction/objects"],
    #     "Fusion": ["/perception/lidar/object", "/perception/fusion/object"]
    # }
    # for module in consuming_list:
    #     module_eval[module],time_consuming = getModuleConsuming(ros_msg,consuming_list[module],module)
    #     print(module,' avg_time_consuming: ', module_eval[module]["avg_time_consuming"])
    #     print(module,' max_time_consuming: ', module_eval[module]["max_time_consuming"])
    #     print(module,' stddev_time_consuming: ', module_eval[module]["stddev_time_consuming"])

    for module in ros_msg:
        if not module in topic_list:
            continue
        diff_scatter = go.Scattergl(x=ros_msg[module]["bj_time"][1:],
                                    y=np.array(ros_msg[module]["frame_diff"])*1000,
                                    mode='lines',
                                    name='frame_diff')
        hz_scatters = go.Scattergl(x=ros_msg[module]["bj_time"][1:],
                                   y=ros_msg[module]["frame_hz"],
                                   mode='lines',
                                   name='frame_hz')

        fig = make_subplots(rows=2, cols=1,
                            x_title='Frames',
                            subplot_titles=[str(module) + ' frames diff',
                                            str(module) + ' frames'])

        fig.add_trace(diff_scatter,row=1,col=1)
        fig.add_trace(hz_scatters,row=2,col=1)
        fig.update_xaxes(title_text='Timestamp',
                         title={'standoff': 0, 'font': {'size': 10}})
        fig.update_yaxes(title_text='Elapsed(ms)')
        fig.update_layout(
            title={
                'text': 'Thread-free Timeline',
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
            },
            legend={
                'orientation': 'h',
                'yanchor': 'top',
                'y': -0.1,
                'x': 0,
            },
            margin={
                'autoexpand': True,
            },
            autosize=True,
            showlegend=True,
            hovermode='y unified'
        )

        print('write {}'.format(module))
        fig.write_html(os.path.join(output_folder, 'module{}.{}-to-{}.html'.format(
                                    str(module).replace('/','_'),
                                    ros_msg[module]["bj_time"][0],
                                    ros_msg[module]["bj_time"][-1])))

        if module not in module_eval:
            module_eval[module] = getModuleStatis(ros_msg[module])
            print(' avg_frame_rate: ', module_eval[module]["avg_frame_rate"])
            print(' min_frame_rate: ', module_eval[module]["min_frame_rate"])
            print(' stddev_frame_rate: ', module_eval[module]["stddev_frame_rate"])
    return module_eval

def DrawSensorGraph(ros_msg,output_folder,sensor_topics):
    module_eval = {}
    if not output_folder or not os.path.exists(output_folder):
        print('Output folder not existed: {}'.format(output_folder))
        sys.exit(1)
    for topic, msg in ros_msg.items():
        if not topic in sensor_topics:
            continue
        ros_msg[topic]["frame_diff"] = np.diff(ros_msg[topic]["timestamp"])
        ros_msg[topic]["frame_hz"] = 1 / ros_msg[topic]["frame_diff"]
    for module in ros_msg:
        if not module in sensor_topics:
            continue
        diff_scatter = go.Scattergl(x=ros_msg[module]["bj_time"][1:],
                                    y=np.array(ros_msg[module]["frame_diff"])*1000,
                                    mode='lines',
                                    name='frame_diff')
        hz_scatters = go.Scattergl(x=ros_msg[module]["bj_time"][1:],
                                   y=ros_msg[module]["frame_hz"],
                                   mode='lines',
                                   name='frame_hz')

        fig = make_subplots(rows=2, cols=1,
                            x_title='Frames',
                            subplot_titles=[str(module) + ' frames diff',
                                            str(module) + ' frames'])

        fig.add_trace(diff_scatter,row=1,col=1)
        fig.add_trace(hz_scatters,row=2,col=1)
        fig.update_xaxes(title_text='Timestamp',
                         title={'standoff': 0, 'font': {'size': 10}})
        fig.update_yaxes(title_text='Elapsed(ms)')
        fig.update_layout(
            title={
                'text': 'Thread-free Timeline',
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
            },
            legend={
                'orientation': 'h',
                'yanchor': 'top',
                'y': -0.1,
                'x': 0,
            },
            margin={
                'autoexpand': True,
            },
            autosize=True,
            showlegend=True,
            hovermode='y unified'
        )

        print('write {}'.format(module))
        fig.write_html(os.path.join(output_folder, 'module{}.{}-{}.html'.format(
                                    str(module).replace('/','_'),
                                    ros_msg[module]["bj_time"][0],
                                    ros_msg[module]["bj_time"][-1])))

        if module not in module_eval:
            module_eval[module] = getSensorStatis(ros_msg[module])
            print(' avg_frame_rate: ', module_eval[module]["avg_frame_rate"])
            print(' min_frame_rate: ', module_eval[module]["min_frame_rate"])
            print(' stddev_frame_rate: ', module_eval[module]["stddev_frame_rate"])
    return module_eval

def moduleMain(input_file,output_folder):

    topic_list = ["/canbus/vehicle_report","/control/control_debug",
                  "/decision_planning/decision_debug","/decision_planning/decision_target",
                  "/decision_planning/planning_debug","/decision_planning/trajectory",
                  "/decision_planning/trajectory_for_prediction","/localization/navstate_info",
                  "/node_state","/perception/camera/traffic_light_sign",
                  "/perception/fusion/object","/perception/lidar/object",
                  "/prediction/objects","/sensor/gnss",
                  "/sensor/imu","/sensor/ins",
                  "/sensor/lidar/fusion/point_cloud"]

    sensor_topics = ["/canbus/vehicle_report","/sensor/lidar/fusion/point_cloud",
                    "/sensor/gnss","/sensor/imu","/sensor/ins",]
    module_topics = ["/control/control_debug", "/decision_planning/decision_debug",
                    "/decision_planning/decision_target", "/decision_planning/planning_debug",
                    "/decision_planning/trajectory", "/decision_planning/trajectory_for_prediction",
                    "/localization/navstate_info", "/node_state","/perception/camera/traffic_light_sign",
                    "/perception/fusion/object","/perception/lidar/object", "/prediction/objects"]
    ros_msg = getDataFromDpcbag(input_file, topic_list)
    module_eval = DrawModuleGraph(ros_msg, output_folder, module_topics)
    sensor_eval = DrawSensorGraph(ros_msg, output_folder, sensor_topics)
    result_json = {"module_eval":module_eval,
                   "sensor_eval":sensor_eval}
    saveTag(output_folder,result_json,'module_result.json')


if __name__ == '__main__':
    moduleMain(sys.argv[1],sys.argv[2])