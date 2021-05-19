
import os
import time
import json

def loadTag(tag_file_path='', tag_file_name='data-tag.json'):
    '''
    load json file
    :param tag_file_path: input file path
    :param tag_file_name: input file name
    :return: json
    '''
    tag_file = os.path.abspath(os.path.join(tag_file_path, tag_file_name))
    if not os.path.exists(tag_file):
        return None
    with open(tag_file, 'r') as f:
        try:
            tag_data = json.load(f)
            return tag_data
        except ValueError:
            print( " ==== ", tag_file, "\033[1;31m is not valuable json bytes \033[0m!\n")
            return None


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


def getTime():
    return str(time.strftime("%m-%d %H:%M:%S", time.localtime()))

def getFileSize(filePath, size=0):
    for root, dirs, files in os.walk(os.path.abspath(filePath)):
        for f in files:
            size += os.path.getsize(os.path.join(root, f))
    return size/(1024*1024)