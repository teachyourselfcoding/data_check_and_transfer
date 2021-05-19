# coding=utf-8

import os
import subprocess
from read_and_write_json import loadTag,saveTag


endpoint_url = ' --endpoint-url=http://10.5.41.234:80 --page-size 100000 '
counts_1 = 0


def getTagInfo(cmd):
    download_cmd = cmd.replace(' /media/sensetime','/data-tag.json /media/sensetime')
    download_cmd = download_cmd.replace(' --recursive','data-tag.json')
    if len(download_cmd.split(' ')) < 4:
        return
    #os.system(download_cmd)
    tag_path = download_cmd.split(' ')[7].replace('\n','')
    print(tag_path)
    return rmAwsFile(tag_path)

def rmAwsFile(tag_path):
    tag_info = loadTag(tag_path,'')
    if tag_info is None:
        print('tag info is error')
        return
    if "backup" in tag_info:
        tag_info = tag_info["backup"][0]["data_tag"]
    print(tag_info['data_link'])
    if 'issue_id' in tag_info.keys() and tag_info['issue_id'] != []:
        for issus_id in tag_info['issue_id']:
            if issus_id in ['AutoDrive-7496','AutoDrive-7424','AutoDrive-6974','AutoDrive-6509']:
                print('++++++++++++++++++++++++ get can not rm file')
                return
    if tag_info['topic_name'] == ['repo_master']:
        print('++++++++++++++++++++++++ get can not rm file')
        return
    data_link = tag_info['data_link']
    print  '\n\n ================== ',data_link,'\n'
    rm_cmd = ''.join(['aws s3 rm ',data_link,' --recursive ',endpoint_url])
    print(rm_cmd)
    global counts_1
    counts_1 += 1
    print(counts_1)
    os.system(rm_cmd)
    os.system(rm_cmd)


def main():
    sh_file = '/media/sensetime/FieldTest/rm/download.sh'
    with open(sh_file,'r') as f:
        lines = f.readlines()
        for cmd in lines:
            tag_info = getTagInfo(cmd)


if __name__ == '__main__':
    main()
