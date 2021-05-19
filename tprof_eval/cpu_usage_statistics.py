#!/usr/bin/env python3

import os
import sys
import json
import time as libtime
import datetime
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

def cpuMain(input_file,output_folder):
    result={}

    if not os.path.exists(input_file):
        print('Can\'t not find input file: {}'.format(input_file))
        sys.exit(1)

    if output_folder is None:
        output_folder = os.path.dirname(input_file)
    # module_tprofile = eval_sensor_output.ModuleTprofile(output_folder,'cpu_tprofile_case.json')

    with open(input_file) as fin:
        time = {}
        date = {}
        total = {}
        user = {}
        system = {}
        io_wait = {}
        steal = {}
        idle = {}
        cpucore = set()
        def Parse(data):
            try:
                _date, _time, _, _, name, t_user, t_nice, t_system, t_idle, t_io_wait, \
                t_irq, t_soft_irq, t_steal, t_guest, t_guest_nice = data.split()
            except Exception as e:
                print('Invalid data: {}'.format(e))
                return None
            else:
                return _date, _time, _, _, name, int(t_user), int(t_nice), int(t_system), \
                       int(t_idle), int(t_io_wait), int(t_irq),int(t_soft_irq), int(t_steal), int(t_guest), int(t_guest_nice)
        for data in fin:
            data = Parse(data)
            if data is None:
                continue
            _date, _time, _, _,name, t_user, t_nice, t_system, t_idle, t_io_wait, t_irq, t_soft_irq, t_steal, t_guest, t_guest_nice = data
            _cpucore = name
            _user = t_user + t_nice
            _system = t_system + t_irq + t_soft_irq
            _total = _user + _system + t_idle + t_io_wait + t_steal
            _io_wait = t_io_wait
            _steal = t_steal
            _idle = t_idle

            cpucore.add(_cpucore)
            if _cpucore not in total.keys():
                total[_cpucore] = []
            total[_cpucore].append(_total)
            if _cpucore not in time.keys():
                time[_cpucore] = []
            time[_cpucore].append(_time)
            if _cpucore not in date.keys():
                date[_cpucore] =[]
            date[_cpucore].append(_date)
            if _cpucore not in user.keys():
                user[_cpucore] = []
            user[_cpucore].append(_user)
            if _cpucore not in system.keys():
                system[_cpucore] = []
            system[_cpucore].append(_system)
            if _cpucore not in io_wait.keys():
                io_wait[_cpucore] = []
            io_wait[_cpucore].append(_io_wait)
            if _cpucore not in steal.keys():
                steal[_cpucore] = []
            steal[_cpucore].append(_steal)
            if _cpucore not in idle.keys():
                idle[_cpucore] = []
            idle[_cpucore].append(_idle)

        for core in cpucore:
            total[core] = list(np.diff(total[core]))
            user[core] = list(np.diff(user[core]))
            system[core] = list(np.diff(system[core]))
            io_wait[core] = list(np.diff(io_wait[core]))
            steal[core] = list(np.diff(steal[core]))
            idle[core] = list(np.diff(idle[core]))


            _total = np.array(total[core])
            _user = np.array(user[core]) / _total
            _system = np.array(system[core]) / _total
            _io_wait = np.array(io_wait[core]) / _total
            _steal = np.array(steal[core]) / _total
            _idle = np.array(idle[core]) / _total
            fig = go.Figure()
            fig.add_bar(x=time[core], y=_user, name='user')
            fig.add_bar(x=time[core], y=_system, name='system')
            fig.add_bar(x=time[core], y=_io_wait, name='io_wait')
            fig.add_bar(x=time[core], y=_steal, name='steal')
            fig.add_bar(x=time[core], y=_idle, name='idle')
            result[core] = np.mean(_user)
            fig.update_layout(barmode='stack', bargap=0, title={'text': core})
            print('write {}'.format(core))
            fig.write_html(os.path.join(output_folder, 'cpu_usage.{}.html'.format(core)))
    saveTag(output_folder, result, 'cpu_result.json')

if __name__ == '__main__':
    cpuMain(sys.argv[1],sys.argv[2])
