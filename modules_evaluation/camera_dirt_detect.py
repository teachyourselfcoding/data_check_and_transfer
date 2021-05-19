import os
import sys

import fnmatch
import logging


def getMatchedFilePaths(dir_path, pattern="*", formats=[".avi"], recursive=False):
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

def cullArchiveDir(file):
    '''
    cull the dir which is for data archive
    :param file:
    :return:
    '''
    try:
        archive = file.split('_', -1)[-1]
        if archive == 'ARH' or archive == 'slice':
            return True
    except Exception as e:
        return False

def getAllDataDir(input_data_path):
    "get all dir in data"
    file_list=[]
    for file in os.listdir(input_data_path):
        if cullArchiveDir(file):
            continue
        dir_file = os.path.join(input_data_path, file)

        if (os.path.isdir(dir_file)):
            h = os.path.split(dir_file)
            file_list.append(h[1])
    return file_list


def camera_dirt_detect(video_files):
    eval_script = "/home/sensetime/ws/dirt_detector "

    if video_files == []:
        return

    cmd = ''.join([eval_script, 'video Tenengrad ', video_files[0], ' /home/sensetime/data/'])
    print(cmd)
    os.system(cmd)


def main(input_data_path):
    file_list=getAllDataDir(input_data_path)
    try:
        for dir_name in file_list:
            dir_path = ''.join([input_data_path, '/', dir_name, '/'])
            pattern = "port_0_camera_*"
            video_files = getMatchedFilePaths(dir_path, pattern, formats=[".avi"], recursive=True)
            camera_dirt_detect(video_files)
    except Exception as e:
        logging.exception(e)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        number = ''
    else:
        data_path = sys.argv[1]
    if not os.path.exists(data_path):
        raise ValueError("========== : {} does NOT exist".format(data_path))

    main(data_path)