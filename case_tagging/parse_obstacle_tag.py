# -*- coding: utf-8 -*-

import os
import rosbag
import debug_info_pb2


def getDataFromDpcbag(dpc_file,topic_names,timestamp):
    if not os.path.exists(dpc_file):
        print('bag not found')
        return
    control_error_topic = topic_names[0]
    bag = rosbag.bag.Bag(dpc_file)
    pp_tag = []
    data = debug_info_pb2.TimeTagMapProto()
    print ("\033[1;32m [INFO]\033[0m! parsing dmppcl bag .........\n")
    for topic, msg, t in bag.read_messages(topics=control_error_topic):
        if int(str(msg.predict_timestamp)[0:13]) > timestamp - 600 \
            and int(str(msg.predict_timestamp)[0:13]) < timestamp:
            pp_tag.append(msg.obstacle_tag_binary.data)
    bag.close()
    return pp_tag


def parseProtoTag(bag_file,timestamp):
    # pp_tag = getDataFromDpcbag(bag_file, ["/planning/debug"],timestamp)
    # data = debug_info_pb2.TimeTagMapProto()
    # id_list = []
    # for obstacle_tag in pp_tag:
    #     data.ParseFromString(obstacle_tag)
    #     if  data.id_seq == []:
    #         continue
    #     for id in data.id_seq:
    #         if id > 0:
    #             id_list.append(id)
    return [111,222]



if __name__ == '__main__':
    bag_file = '/media/sensetime/FieldTest1/data/data_check/03_09_CN-013_ARH/03_09_CN-013_ARH/2021_03_09_15_57_08_AutoCollect_slice/DPC/Emergency_brake/2021_03_09_15_08_14/dmppcl.bag'
    parseProtoTag(bag_file,1615273694000)
