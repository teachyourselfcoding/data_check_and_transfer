# coding=utf-8

import os
import subprocess
from read_and_write_json import loadTag,saveTag


ls_cmd = "aws s3 ls --endpoint-url=http://10.5.41.189:9090 "
download_cmd = "aws s3 cp --endpoint-url=http://10.5.41.189:9090 "
rm_cmd = "aws s3 rm --recursive --exclude \'*\' " \
         "--include \'logs/*\' --endpoint-url=http://10.5.41.189:9090 "
input_bucket = "s3://Field_Test_Data/master/segment_data/2020_03_"

with open('../config/download_logs.sh') as f:
    download_aws = f.read()

def getFileList(input_path):
    ls_command =  ''.join([ls_cmd,input_path])
    #output =  subprocess.Popen(ls_command.split(),stdout=subprocess.PIPE,shell=True).communicate()
    output =  os.popen(ls_command)
    text = output.read()
    output.close()
    return text

upload_recursive = " --recursive --only-show-errors --endpoint-url="
def rmLogs(input_path):
    # file_list = getFileList(input_path+'logs/')
    # print(len(file_list.split()))
    # if len(file_list.split()) < 10:
    #     return
    rm_command =  ''.join([rm_cmd,input_path])
    print(rm_command)
    os.system(rm_command)
    generateLogDownloadFile(input_path)




def generateLogDownloadFile(input_path):
    tag_path = ''.join([input_path, 'data-tag.json'])
    file_name = input_path.split('/',-1)[-2]
    download_path = ''.join(["/media/sensetime/FieldTest1/data/logs_ARH/",file_name,'/data-tag.json'])
    download_command = ''.join([download_cmd,tag_path,' ',download_path])
    os.system(download_command)
    tag=loadTag(download_path,'')
    if tag is None:
        return
    raw_data_link = tag["raw_data_link"]
    output_path =  ''.join(["/media/sensetime/FieldTest1/data/logs_ARH/",file_name])
    if not os.path.exists(output_path + "/logs"):
        os.makedirs(output_path + "/logs")
    profile = " --profile ad_system_common "
    log_download_instruction = ''.join(
        ["aws s3 cp", upload_recursive, "http://10.5.41.189:9090", profile, raw_data_link + '/logs', ' ', "$this_dir/"])
    download_logs = download_aws
    download_logs += log_download_instruction
    download_logs += '\n'
    with open(os.path.join(output_path, 'logs/download_logs.sh'), 'w') as f:
        f.write(download_logs)
    file_path = ''.join(["/media/sensetime/FieldTest1/data/logs_ARH/",file_name])
    upload_command = ''.join([download_cmd,file_path+'/logs/',' ',input_path+'logs/',' --recursive'])
    os.system(upload_command)


def main(input_path):
    file_list = getFileList(input_path)
    for file_name in file_list.split():
        if '/' in file_name:

            recursive_path = ''.join([input_path, file_name])
            if file_name == "logs/":
                print(input_path)
                rmLogs(input_path)
            else:
                main(recursive_path)





if __name__ == '__main__':
    list = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25',
            '26','27','28','29','30']
    for data in list:
        input = input_bucket+data+'/'
        print(input)
        main(input)

