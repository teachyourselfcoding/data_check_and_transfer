#!/usr/bin/env python3


import os
import sys
import copy
import json
import time
import numpy as np
import plotly.graph_objects as go
from anytree import LevelOrderGroupIter


class ModuleTprofile():
    def __init__(self,output_path,output_file = 'module_tprofile_case.json'):
        self.file_path = os.path.split(os.path.realpath(__file__))[0]
        self.config =  self.loadTag(self.file_path,'/module_thresh.json')
        self.output_path = output_path+'/'
        self.output_file = output_file
        self.case_list = self.loadTag(self.output_path,self.output_file)
        self.tprofile_result = self.loadTag(self.output_path,'/tprofile_result.json',{})


    def loadTag(self, tag_file_path='', tag_file_name='data-tag.json',default_return = []):
        if not os.path.exists(tag_file_path + tag_file_name):
            return default_return
        with open(tag_file_path + tag_file_name, 'r') as f:
            try:
                tag_data = json.load(f)
                return tag_data
            except ValueError:
                print(" ==== ", tag_file_path + tag_file_name,
                      "\033[1;31m is not valuable json bytes \033[0m!\n")
                return default_return

    def saveTag(self,tag_file_path, tag_data, file_name='data-tag.json'):
        tag_path_name = tag_file_path + file_name
        with open(tag_path_name, 'w') as fw:
            json.dump(tag_data, fw, indent=4)


    def moduleConsumingDetect(self,scatter):
        if scatter is None:
            return
        if scatter['name'] in self.config["modules"].keys():
            module_name = self.config["modules"][scatter['name']]["module"]
            module_thresh = self.config["modules"][scatter['name']]["time_thresh"]
            abnormal_times = self.config["modules"][scatter['name']]["abnormal_times"]
            label = module_name+'_time_consuming_expection'
            tag = module_name+"耗时异常"
            abnormal_number = 0
            for i in range(len(scatter['y'])):
                time_consuming = scatter['y'][i]
                if time_consuming > module_thresh:
                    if abnormal_number ==0:
                        start_time = int(str(scatter['x'][i])[0:13])
                    label_time = int(str(scatter['x'][i])[0:13])
                    self.tprofile_result[label_time] = label
                    abnormal_number +=1
                elif time_consuming < module_thresh and abnormal_number > 0:
                    if abnormal_number > abnormal_times:
                        self.addCase(module_name,label,tag,start_time,scatter['x'][i])
                        abnormal_number =0
                    if abnormal_number > 1:
                        abnormal_number -= 1

    def addCase(self,module,label,tag,start_time,end_time):
        case = {}
        case["modules"] = []
        case["labels"] = []
        case["modules"].append(module)
        case["labels"].append(label)
        case["tag"] = tag
        case["data_type"] = "eval"
        case["tag_en"] = label
        case["start"] =  int(str(start_time)[0:13])
        case["end"] = int(str(end_time )[0:13])
        if case["end"] - case["start"] < 10000:
            case["end"] += 10000
        case["start_format"] = self.unixToBjclock(case["start"]/1000)
        case["end_format"] = self.unixToBjclock(case["end"] / 1000)
        case["lat"] = 31.586201938389177
        case["lng"] = 120.43301214971125
        self.case_list.append(case)


    def unixToBjclock(self,unix_time):
        time_array=time.localtime(unix_time)
        now_time_style=time.strftime('%H:%M:%S',time_array)
        return now_time_style

    def Filter(self,node):
        return node.average_elapsed_time != -1 and node.called_times > 10

    def StripNameSpace(self,demangled_name):
        # Remove namspace
        pattern = r'.*::(\w+[<>])'
        import re
        return re.sub(pattern, r'\1', demangled_name)

    def moduleTproDetect(self,root_tree):
        self._root_tree = root_tree
        for level, group in enumerate(LevelOrderGroupIter(self._root_tree)):
            for node in group:
                enter_timepoints = np.array(node.enter_timepoint)
                elapsed_times = np.array(node.elapsed_time)
                if not len(elapsed_times) or not len(enter_timepoints):
                    continue
                if len(elapsed_times) != len(enter_timepoints):
                    continue
                if len(elapsed_times) != len(enter_timepoints):
                    continue
                abbrev = self.StripNameSpace(node.name) if len(node.name) > 32 else node.name
                if len(node.name) > 64 or node.name == '??':
                    continue
                if not len(enter_timepoints) or not len(elapsed_times):
                    print('Skip node: {} {} {}'.format(node.name, len(enter_timepoints), len(elapsed_times)))
                    continue
                if not self.Filter(node):
                    continue
                if elapsed_times.size < 2:
                    continue
                scatter = go.Scattergl(
                    y=elapsed_times,
                    x=enter_timepoints,
                    mode='lines',
                    name=abbrev,
                    text=abbrev,
                )
                self.moduleConsumingDetect(scatter)
        self.mergeAdjacentCase()
        self.saveTag(self.output_path, self.case_list, self.output_file)
        self.saveTag(self.output_path, self.tprofile_result, '/tprofile_result.json')

    def mergeAdjacentCase(self):
        if len(self.case_list) < 1:
            return
        for i in range(len(self.case_list)-1):
            if i > len(self.case_list) - 2:
                break
            merge,merged_case = self.checkCaseOverLap(self.case_list[i],self.case_list[i+1])
            if merge:
                self.case_list[i] = merged_case
                self.case_list.pop(i+1)
                i -= 1

    def checkCaseOverLap(self,case_a,case_b):
        if not "start" in case_a.keys():
            return False,{}
        if not "start" in case_a.keys():
            return False,{}
        if case_b["start"] - case_a["end"] < 10000:
            merged_case = copy.deepcopy(case_a)
            merged_case["end"]  = case_b["end"]
            merged_case["end_format"] = case_b["end_format"]
            merged_case["labels"].extend(case_b["labels"])
            merged_case["labels"] = list(set(merged_case["labels"]))
            merged_case["modules"].extend(case_b["modules"])
            merged_case["modules"] = list(set(merged_case["modules"]))
            return True, merged_case
        return False,{}

    def canbusDelayDetect(self,timestamps, req_ns, res_ns):
        timestamps_ns = np.array(timestamps)
        req_ns = np.array(req_ns)[:, 1]
        res_ns = np.array(res_ns)[:, 1]

        parse_ms = (timestamps_ns - res_ns) / 1e6
        transport_ms = (timestamps_ns - req_ns) / 1e6
        parse_delay_thresh  = self.config["sensors"]["canbus"]["parse_delay_thresh"]
        transport_delay_thresh = self.config["sensors"]["canbus"]["transport_delay_thresh"]
        abnormal_times = self.config["sensors"]["canbus"]["abnormal_times"]
        label = "canbus_parse_delay_expection"
        tag = "延迟过高"
        abnormal_number = 0
        for i in range(len(parse_ms)):
            parse_delay = parse_ms[i]
            transport_delay = transport_ms[i]
            if parse_delay > parse_delay_thresh or \
                    transport_delay > transport_delay_thresh:
                if abnormal_number ==0:
                    start_time = timestamps_ns[i]
                label_time = int(str(timestamps_ns[i])[0:13])
                self.tprofile_result[label_time] = label
                abnormal_number +=1
            else:
                if abnormal_number > abnormal_times:
                    self.addCase("System",label,tag, start_time, timestamps_ns[i])
                    abnormal_number = 0
                if abnormal_number > 0:
                    abnormal_number -= 1
        self.mergeAdjacentCase()
        self.saveTag(self.output_path, self.case_list, self.output_file)
        self.saveTag(self.output_path, self.tprofile_result, '/tprofile_result.json')

    def cameraDelayDetect(self, timestamps, parsedone_ns,  cost_ns):
        timestamps_ns = np.array(timestamps)
        camera_parsecost_us = np.array(cost_ns)[:, 1] / 1e3

        parse_cost_thresh  = self.config["sensors"]["camera"]["parse_cost_thresh"]
        abnormal_times = self.config["sensors"]["camera"]["abnormal_times"]
        label = "camera_parse_delay_expection"
        tag = "相机延迟过高"
        abnormal_number = 0
        for i in range(len(camera_parsecost_us)):
            parse_delay = camera_parsecost_us[i]
            if parse_delay > parse_cost_thresh:
                if abnormal_number ==0:
                    start_time = timestamps_ns[i]
                label_time = int(str(timestamps_ns[i])[0:13])
                self.tprofile_result[label_time] = label
                abnormal_number +=1
            else:
                if abnormal_number > abnormal_times:
                    self.addCase("System", label,tag, start_time, timestamps_ns[i])
                    abnormal_number = 0
                if abnormal_number > 0:
                    abnormal_number -= 1
        self.mergeAdjacentCase()
        self.saveTag(self.output_path, self.case_list, self.output_file)
        self.saveTag(self.output_path, self.tprofile_result, '/tprofile_result.json')

    def lidarDelayDetect(self, timestamps, lidar_package_infos):
        timestamps_ns = np.array(timestamps)

        lidar_parsedone_s = [info[0] / 1e9 for info in lidar_package_infos]  # From Nsec to sec
        lidar_parsedone_gaps = np.diff(lidar_parsedone_s)
        label = "lidar_parse_delay_expection"
        tag = "雷达延迟过高"
        delay_thresh  = self.config["sensors"]["lidar"]["delay_thresh"]
        abnormal_times = self.config["sensors"]["lidar"]["abnormal_times"]
        abnormal_number = 0
        for i in range(len(lidar_parsedone_gaps)):
            parse_delay = lidar_parsedone_gaps[i]
            if parse_delay > delay_thresh:
                if abnormal_number == 0:
                    start_time = timestamps_ns[i]
                label_time = int(str(timestamps_ns[i])[0:13])
                self.tprofile_result[label_time] = label
                abnormal_number += 1
            else:
                if abnormal_number > abnormal_times:
                    self.addCase("System",label,tag, start_time, timestamps_ns[i])
                    abnormal_number = 0
                if abnormal_number > 0:
                    abnormal_number -= 1
        self.mergeAdjacentCase()
        self.saveTag(self.output_path, self.case_list, self.output_file)
        self.saveTag(self.output_path, self.tprofile_result, '/tprofile_result.json')

    def cpuUsageDetect(self,use_core,date_core,time_core,core):
        if len(use_core) > len(time_core):
            return
        use_thresh = self.config["cpu"]["use_thresh"]
        abnormal_times = self.config["cpu"]["abnormal_times"]
        label = str(core)+"_usage_expection"
        tag = "cpu占用过高"
        abnormal_number = 0

        for i in range(len(use_core)):
            cpu_use =  use_core[i]
            if cpu_use > use_thresh:
                if abnormal_number == 0:
                    start_date =date_core[i]
                    start_time = time_core[i]
                label_time = int(str(self.bjTimeToUnix(date_core[i],time_core[i]))[0:13])
                self.tprofile_result[label_time] = label
                abnormal_number += 1
            else:
                if abnormal_number > abnormal_times:
                    start_time = self.bjTimeToUnix(start_date,start_time)
                    end_time = self.bjTimeToUnix(date_core[i],time_core[i])
                    self.addCase("System", label, tag, start_time, end_time)
                    abnormal_number = 0
                if abnormal_number > 0:
                    abnormal_number -= 1
        self.mergeAdjacentCase()
        self.saveTag(self.output_path, self.case_list, self.output_file)
        self.saveTag(self.output_path, self.tprofile_result, '/tprofile_result.json')

    def bjTimeToUnix(self,bj_date,bj_time):
        bj_time = bj_time.split('.', -1)[0]
        ts = time.strptime('2020' + bj_date + ' ' + bj_time, "%Y%m%d %H:%M:%S")
        return int(time.mktime(ts) * 1000)