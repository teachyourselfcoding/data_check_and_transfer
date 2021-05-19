import os
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
            print " ==== ", tag_file, "\033[1;31m is not valuable json bytes \033[0m!\n"
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


def main():
    file_path = "/home/sensetime/ws/semantic_map.json"
    data_tag = loadTag(file_path,"")
    for road_ele in data_tag.keys():
        if data_tag[road_ele] ==[]:
            continue
        id_list = []
        aaa = []
        for element in data_tag[road_ele]:
            id = element["id"]
            if not id in id_list:
                id_list.append(id)
                print("bbbbbbbb")
            else:
                print("aaaaaaaa")


    #saveTag(file_path,data_tag,'')

if __name__ == '__main__':
    main()