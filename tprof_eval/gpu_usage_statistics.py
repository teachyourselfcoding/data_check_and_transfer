#!/usr/bin/env python3

import os
import sys
import json
import time as libtime
import datetime
import numpy as np
import plotly.graph_objects as go

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

def gpuMain(input_file,output_folder):
    result = {"Memory_usage":{},
              "GPU_usage":{}}

    if not os.path.exists(input_file):
        print('Can\'t not find input file: {}'.format(input_file))
        sys.exit(1)

    if output_folder is None:
        output_folder = os.path.dirname(input_file)

    with open(input_file) as fin:
        next(fin)
        time = {}
        date = {}
        total = {}
        memory_user = {}
        gpu_user = {}

        gpucore = set()
        def Parse(data):
            try:
                _time, _,_name, _, _, _, _, _temp, _perct_gpu, _perct_mem, _total, _free, _used = data.split(", ")
            except Exception as e:
                print('Invalid data: {}'.format(e))
                return None
            else:
                return _time, _,_name, _, _, _, _, _temp, _perct_gpu, _perct_mem, \
                       int(_total.split(' ')[0]), int(_free.split(' ')[0]), int(_used.split(' ')[0])
        for data in fin:
            data = Parse(data)
            if data is None:
                continue
            _time, _,_name, _, _, _, _, _temp, _perct_gpu, _perct_mem, _total, _free, _used = data

            gpucore.add(_name)
            if _name not in total.keys():
                total[_name] = []
            total[_name].append(_total)
            if _name not in time.keys():
                time[_name] = []
            time[_name].append(_time)
            if _name not in memory_user.keys():
                memory_user[_name] = []
            memory_user[_name].append(_used)
            if _name not in gpu_user.keys():
                gpu_user[_name] = []
            gpu_user[_name].append(int(_perct_gpu.split(' ')[0]))



        for core in gpucore:
            _total = np.array(total[core])
            _memory_user = np.array(memory_user[core]) / _total
            _gpu_user = np.array(gpu_user[core])
            result["Memory_usage"][core] = np.mean(_memory_user)
            result["GPU_usage"][core] = np.mean(_gpu_user)
            fig = go.Figure()
            fig.add_bar(x=time[core], y=_gpu_user, name='user')
            fig.update_layout(barmode='stack', bargap=0, title={'text' : core})
            print('write {}'.format(core), np.mean(_gpu_user),np.std(_gpu_user))
            fig.write_html(os.path.join(output_folder, 'gpu_usage.{}.html'.format(str(core).replace(':','-'))))
    saveTag(output_folder,result,'gpu_result.json')


if __name__ == '__main__':
    gpuMain(sys.argv[1],sys.argv[2])

