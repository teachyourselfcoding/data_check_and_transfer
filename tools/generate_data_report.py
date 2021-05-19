# coding=utf-8
import os
import datetime
import json
import requests
from collections import defaultdict, deque
from read_and_write_json import loadTag, saveTag


formatted_today = datetime.datetime.now().strftime('%Y_%m_%d')
data_month = datetime.datetime.now().strftime('%Y_%m')

upload_date = datetime.datetime.now().strftime('%Y-%m-%d')
def getTrueList(file_path, check_result=True):
    '''

    :param input_file_list:
    :param check:
    :return:
    '''
    # if not judge_file_data(file_path):
    #     return
    if not os.path.exists('../data_report'):
        os.makedirs('../data_report')
    data_report_tag = loadTag('../data_report/', formatted_today + '.json')
    date = str(formatted_today)
    total_file_size = 0
    total_file_time_length = 0

    if not date in data_report_tag.keys():
        data_report_tag[date] = defaultdict(lambda: {})

    file_name = file_path.split('/', -1)[-1]
    tag_data = loadTag(file_path)
    if tag_data == {}:
        return

    file_size = getFileSize(file_path)
    if 'test_duration' in tag_data.keys():
        file_time_length = tag_data.get('test_duration')
    else:
        file_time_length = 1800
    if not 'true' in data_report_tag[date]:
        data_report_tag[date]['true'] = defaultdict(lambda: {})
    if not file_name in data_report_tag[date]['true']:
        data_report_tag[date]['true'][file_name] = defaultdict(lambda: {})
    data_report_tag[date]['true'][file_name]["upload_date"] = date
    data_report_tag[date]['true'][file_name]["data_type"] = 'raw'
    data_report_tag[date]['true'][file_name]["data_name"] = file_name
    data_report_tag[date]['true'][file_name]["test_car_id"] = tag_data["test_car_id"]
    data_report_tag[date]['true'][file_name]["check_result"] = check_result
    data_report_tag[date]['true'][file_name]["file_size(MB)"] = file_size
    data_report_tag[date]['true'][file_name]["data_link"] = tag_data["data_link"]

    total_file_size += file_size
    total_file_time_length += file_time_length / 60

    print(file_path + '_slice')
    if os.path.exists(file_path + '_slice'):
        slice_file_size = getFileSize(file_path + '_slice')
        slice_file_name = file_name + '_slice'
        if not slice_file_name in data_report_tag[date]['true']:
            data_report_tag[date]['true'][slice_file_name] = defaultdict(lambda: {})
        data_report_tag[date]['true'][slice_file_name]["upload_date"] = date
        data_report_tag[date]['true'][slice_file_name]["data_type"] = 'segment'
        data_report_tag[date]['true'][slice_file_name]["data_name"] = slice_file_name
        data_report_tag[date]['true'][file_name]["test_car_id"] = tag_data["test_car_id"]
        data_report_tag[date]['true'][slice_file_name]["check_result"] = check_result
        data_report_tag[date]['true'][slice_file_name]["file_size(MB)"] = slice_file_size
        data_report_tag[date]['true'][slice_file_name]["data_link"] = tag_data["data_link"].replace('raw',
                                                                                                    'segment') + '_slice'

        total_file_size += slice_file_size

    file_size_str = str(check_result) + "_file_size(MB)"
    if not file_size_str in data_report_tag[date].keys():
        data_report_tag[date][file_size_str] = 0
    data_report_tag[date][file_size_str] += total_file_size

    time_length_str = "Test_length(Min)"
    if not time_length_str in data_report_tag[date].keys():
        data_report_tag[date][time_length_str] = 0
    data_report_tag[date][time_length_str] += total_file_time_length

    print("\033[1;32m [INFO]\033[0m! generate data report successfully\n")
    saveTag('../data_report/', data_report_tag, formatted_today + '.json')


def getFalseList(file_path, check_result=False):
    '''

    :param input_file_list:
    :param check:
    :return:
    '''

    # if not judge_file_data(file_path):
    #     return
    data_report_tag = loadTag('../data_report/', formatted_today + '.json')
    date = str(formatted_today)
    total_file_size = 0
    print('===', date)
    if not date in data_report_tag.keys():
        data_report_tag[date] = defaultdict(lambda: {})

    file_name = file_path.split('/', -1)[-1]

    file_size = getFileSize(file_path)
    if not 'false' in data_report_tag[date]:
        data_report_tag[date]['false'] = defaultdict(lambda: {})
    if not file_name in data_report_tag[date]['false']:
        data_report_tag[date]['false'][file_name] = defaultdict(lambda: {})
    data_report_tag[date]['false'][file_name]["upload_date"] = date
    data_report_tag[date]['false'][file_name]["data_type"] = "raw"
    data_report_tag[date]['false'][file_name]["data_name"] = file_name
    data_report_tag[date]['false'][file_name]["check_result"] = check_result
    data_report_tag[date]['false'][file_name]["file_size(MB)"] = file_size
    data_report_tag[date]['false'][file_name]["data_link"] = ''.join(["s3://sh40_fieldtest_dataset/",data_month,'/false_data/', file_name])

    total_file_size += file_size

    file_size = str(check_result) + "_file_size(MB)"
    if not file_size in data_report_tag[date].keys():
        data_report_tag[date][file_size] = 0
    data_report_tag[date][file_size] += total_file_size

    print("\033[1;32m [INFO]\033[0m! generate data report successfully\n")
    saveTag('../data_report/', data_report_tag, formatted_today + '.json')


def judge_file_data(file_path):
    '''

    :param file_path:
    :return:
    '''

    file_date = get_file_date(file_path)
    if file_date == formatted_today:
        return True
    return False


def getFileSize(filePath, size=0):
    try:
        for root, dirs, files in os.walk(filePath):
            for f in files:
                size += int(round(os.path.getsize(os.path.join(root, f)) / float(1024 * 1024), 0))
        return size
    except Exception as e:
        return 0


def get_file_date(file_path):
    '''

    :param file_path:
    :return:
    '''

    file_name = file_path.split('/', -1)[-1]
    test_date = file_name.split('_', -1)[0] + '_' \
                + file_name.split('_', -1)[1] + '_' \
                + file_name.split('_', -1)[2]
    return test_date

def main(dir_path,check_result = True,false_reason = []):
    data_report = loadTag('config', 'data_report_daily.json')
    if check_result:
        tag_data = loadTag(dir_path,'data-tag.json')
        if tag_data['master']:
            data_report=generateMasterTag(dir_path,tag_data,data_report)
        else:
            data_report=generateFeatureAndCollectionTag(dir_path,tag_data,data_report)
    else:
        data_report=generateFalseDataTag(dir_path,false_reason,data_report)
    TransferPost(data_report)


def generateMasterTag(dir_path,tag_data,data_report):

    data_report['data_link'] = tag_data['data_link']
    data_report['file_name'] = tag_data['file_name']
    data_report['upload_date'] = upload_date
    data_report['file_size'] = getFileSize(dir_path)
    data_report['master'] = tag_data['master']
    if not 'test_duration' in tag_data.keys():
        tag_data['test_duration'] = 2250
    data_report['test_duration'] = tag_data['test_duration']
    data_report['segment_file'] = generateSegmentTag(dir_path,tag_data)
    return data_report


def generateSegmentTag(dir_path,tag_data):
    segment_report = defaultdict(lambda: {})
    segment_report["case_number"] = len(tag_data['origin_record_tag'])
    segment_report["sgement_file_size"] = getFileSize(dir_path+'_slice/')
    for case in tag_data['origin_record_tag']:
        segment_report["case_distribution_count"] ={}
        segment_report["case_distribution_size"] = {}
        if case['tag_en'] not in segment_report["case_distribution_count"].keys():
            segment_report["case_distribution_count"][case['tag_en']] = 0
            segment_report["case_distribution_size"][case['tag_en']] = 0
        segment_report["case_distribution_count"][case['tag_en']] += 1
        segment_report["case_distribution_size"][case['tag_en']] += 400
    return segment_report


def generateFeatureAndCollectionTag(dir_path,tag_data,data_report):

    data_report = loadTag('config', 'data_report_daily.json')
    data_report['data_link'] = tag_data['data_link']
    data_report['upload_date'] = upload_date
    data_report['file_name'] = tag_data['file_name']
    if not 'test_duration' in tag_data.keys():
        tag_data['test_duration'] = 2250
    data_report['test_duration'] = tag_data['test_duration']
    data_report['file_size'] = getFileSize(dir_path)
    data_report['master'] = tag_data['master']
    return data_report



def generateFalseDataTag(dir_path,false_reason,data_report):
    dir_name = dir_path.split('/', -1)[-1]

    data_report['check_result'] = False
    data_report['data_link'] =''.join(["s3://sh40_fieldtest_dataset/",data_month,'/false_data/', dir_name])
    data_report['upload_date'] = upload_date
    data_report['file_name'] = dir_name
    data_report['test_duration'] = 0
    data_report['file_size'] = getFileSize(dir_path)
    data_report['false_reason'] = false_reason
    return data_report


def TransferPost(data_tag):
    "post the data tag to senseFT"
    curl = \
        'https://fieldtest.sensetime.com/production-line/upload'
    post_result = requests.post(curl,  data=json.dumps(data_tag))
    print ("\n \033[1;32m [INFO]\033[0m ", post_result.text)
