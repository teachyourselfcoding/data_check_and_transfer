# coding=utf-8

import os
import sys
import json
import fnmatch
import requests
from tools.read_and_write_json import loadTag,saveTag

from awscli.clidriver import create_clidriver
AWS_DRIVER = create_clidriver()

upload_recursive = " --recursive --endpoint-url="
end_point_30 = "http://10.5.41.189:9090"
end_point_40 = "http://10.5.41.234:80"
end_point = end_point_40

def data_upload(dir_path_without, tag_info, slice=False):
    'data_upload with aws'
    dir_name = os.path.split(dir_path_without)[1]

    vehicle_id = tag_info["test_car_id"].replace("-", "")
    data_month = tag_info["test_date"].rsplit("_", 1)[0]
    try:
        if tag_info["topic_name"][0] == "repo_master":
            feature = False
        else:
            feature = True
    except Exception as e:
        feature = False

    if feature:
        task_id = str(tag_info["task_id"]) + '/'
    else:
        task_id = ''

    if slice:
        upload_path = ''.join([dir_path_without, "_slice/ "])

        dst_path = ''.join([getDataCollectionDstLink(tag_info, data_month,slice=True),
                            tag_info["test_date"], '/',
                            vehicle_id, '/', task_id])

    else:
        upload_path = ''.join([dir_path_without, '/ '])

        tag_path = ''.join([getDataCollectionDstLink(tag_info, data_month, slice=False),
                            tag_info["test_date"], '/',
                            vehicle_id, '/',
                            task_id, dir_name])
        dst_path = ''.join([tag_path, '/'])
    arg2 = ''.join(["s3 cp ", upload_path, dst_path, upload_recursive+end_point])
    print(" ==== ", arg2)

    upload_result = AWS_DRIVER.main(arg2.split())

    if upload_result == 0:
        print(" ---- Dir:\033[1;32m", dir_name + "\033[0m" + dir_name, "\033[0m has\033[1;32m uploaded successfully!\033[0m---\n")
    else:
        print(" ---- Dir:\033[1;32m", dir_name + "\033[0m" + dir_name, "\033[0m \033[1;32m upload failed!\033[0m---\n")

def getDataCollectionDstLink(tag_info, data_month,slice):
    "get the upload path of the dir "

    if tag_info["test_type"] == 2:
        if slice:
            return "s3://sh40_data_collection/"+data_month+"/segment_data/"
        else:
            return "s3://sh40_data_collection/"+data_month+"/raw_data/"
    if tag_info["topic_name"][0] == "repo_master":
        if slice:
            return "s3://sh40_fieldtest_master/"+data_month+"/master/segment_data/"
        else:
            return "s3://sh40_fieldtest_master/"+data_month+"/master/raw_data/"
    else:
        if slice:
            return "s3://sh40_fieldtest_feature/"+data_month+"/feature/segment_data/"
        else:
            return "s3://sh40_fieldtest_feature/"+data_month+"/feature/raw_data/"


def getAllDataDir(input_data_path):
    "get all dir in data"
    file_list = []
    for file in os.listdir(input_data_path):
        if cullArchiveDir(file):
            continue
        dir_file = os.path.join(input_data_path, file)

        if (os.path.isdir(dir_file)):
            h = os.path.split(dir_file)
            file_list.append(h[1])
    return file_list


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



def mainUpload(dir_path_without):
    '''
    upload and then archive data
    :param dir_path_without: data path end without /
    '''

    tag_info = loadTag(dir_path_without + '/')
    dir_name = os.path.split(dir_path_without)[1]
    data_upload(dir_path_without, tag_info, slice=False)
    if os.path.exists(dir_path_without + "_slice/"):
        data_upload(dir_path_without, tag_info, slice=True)



def main(input_path):

    dir_path_list = getAllDataDir(input_path)
    print(dir_path_list)
    for dir_path in dir_path_list:
        mainUpload(input_path+'/'+dir_path)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        number = ''
    else:
        data_path = sys.argv[1]
    if not os.path.exists(data_path):
        raise ValueError("========== : {} does NOT exist".format(data_path))
    main(data_path)
