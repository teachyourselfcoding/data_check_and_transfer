# coding=utf-8

import os
import sys
import datetime
import requests


def transferLog(log_path):
    url="http://localhost:8088/api/v1/upload/sensor-check?path=" + log_path
    post_result = requests.get(url)

def getMonth():
    month = datetime.datetime.now().strftime('%Y-%m')
    print(datetime.datetime.now().strftime('%Y-%m-%d')+' post log')
    return month

def main():
    file_name = getMonth()+".log"
    log_path = "/home/sensetime/ws/.sensor_check_log/novatel/"+file_name
    transferLog(log_path)

if __name__ == '__main__':
    main()