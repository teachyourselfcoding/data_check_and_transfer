# coding=utf-8

import os
import sys
import json
import fnmatch
import requests
from read_and_write_json import loadTag,saveTag


def getMatchedFilePaths(dir_path, pattern="*", formats=[".json"], recursive=False):
    files = []
    data_dir = os.path.normpath(os.path.abspath(dir_path))
    #try:
    for f in os.listdir(data_dir):
        current_path = os.path.join(os.path.normpath(data_dir), f)
        if os.path.isdir(current_path) and recursive:
            files += getMatchedFilePaths(current_path, pattern, formats,
                                              recursive)
        elif fnmatch.fnmatch(f,
                             pattern) and os.path.splitext(f)[-1] in formats:
            files.append(current_path)
    return files
    # except OSError:
    #     print("path error")
    #     return []


headerdata = {"Data-tag-type": "application/json"}
def TransferPost(data_tag):
    curl = \
        'https://fieldtest.sensetime.com/task/daemon/update/tag'
    post_result = requests.post(curl, headers=headerdata, data=json.dumps(data_tag))
    print "\n \033[1;32m [INFO]\033[0m ", post_result.text
    print(data_tag["file_name"])
    if post_result.text != u'{"result":"true"}':
        try:
            saveTag('../upload_list/', data_tag, data_tag["file_name"] + '.json')
        except Exception as e:
            print("save upload failed tag failed")
        return False
    else:
        return True


def main(dir_path):
    data_tag_list = getMatchedFilePaths(dir_path,recursive=True)
    print(data_tag_list)
    for data_tag_path in data_tag_list:
        tag_data = loadTag(data_tag_path,'')
        if "backup" in tag_data.keys():
            tag_data =  tag_data["backup"][0]["data_tag"]
        if "test_date" in tag_data.keys():
            tag_data["test_date"] = tag_data["test_date"].replace('-', '_')
        print(data_tag_path)
        #tag_data["issue_id"] = ["AUTODRIVE-6814"]
        # if tag_data["global_tag"] ==[]:
        #     continue
        # for global_tag in tag_data["global_tag"]:
        #     print(global_tag)
        #     if fnmatch.fnmatch(global_tag,"*_rate") or fnmatch.fnmatch(global_tag, "*_fluction") or fnmatch.fnmatch(global_tag, "*_high") or fnmatch.fnmatch(global_tag, "*_fluction"):
        #     #if str(global_tag).endswith('e') or str(global_tag).endswith('h') or str(global_tag).endswith('n'):
        #
        #         tag_data["global_tag"].remove(global_tag)
        # saveTag(data_tag_path,tag_data,'')
        if None in tag_data['global_tag']:
            tag_data['global_tag'].remove(None)
        print (tag_data['global_tag'])
        result = TransferPost(tag_data)
        if result:
            os.remove(data_tag_path)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        number = ''
    else:
        data_path = sys.argv[1]
    if not os.path.exists(data_path):
        raise ValueError("========== : {} does NOT exist".format(data_path))
    main(data_path)




