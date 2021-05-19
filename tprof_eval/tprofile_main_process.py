#!/usr/bin/env python3

import os
import sys
import fnmatch
sys.path.append("..")
from cpu_usage_statistics import cpuMain
from gpu_usage_statistics import gpuMain
from module_usage_statistics import moduleMain
script_path=os.getcwd()
cpu_script = os.path.join(script_path,'tprof_eval/cpu_usage_statistics.py')
gpu_script = os.path.join(script_path,'tprof_eval/gpu_usage_statistics.py')
ros_script = os.path.join(script_path,'tprof_eval/module_usage_statistics.py')


def getMatchedFilePaths(dir_path, pattern="*", formats=[".json"], recursive=False):
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

def tproMain(input_dir,output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    cpu_usage_files = getMatchedFilePaths(input_dir,"cpu*",['.log'])
    gpu_usage_files = getMatchedFilePaths(input_dir,"nvidia*",['.log'])
    module_tpro_file = os.path.join(input_dir,'dmppcl.bag')
    if len(cpu_usage_files) > 0 and os.path.exists(cpu_usage_files[0]):
        cmd = ''.join([cpu_script,' ',cpu_usage_files[0],' ',output_dir])
        os.system(cmd)
    if len(gpu_usage_files) > 0 and os.path.exists(gpu_usage_files[0]):
        cmd = ''.join([gpu_script, ' ', gpu_usage_files[0], ' ', output_dir])
        os.system(cmd)
    if os.path.exists(module_tpro_file):
        cmd = ''.join([ros_script, ' ', module_tpro_file, ' ', output_dir])
        os.system(cmd)

if __name__ == '__main__':
    tproMain(sys.argv[1],sys.argv[2])
