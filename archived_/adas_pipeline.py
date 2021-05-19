# coding=utf-8

import os
import cv2
import time
import logging
import shutil
import struct
import multiprocessing
from tools.read_and_write_json import loadTag,saveTag
from moviepy.editor import concatenate_videoclips,VideoFileClip
from cut_rec_multiprocess \
    import GetMatchedFilePaths,JudgeTheStartAndEndOfVideo,CutTimestamp,CutDpcs



class TimeReader:
    def __init__(self, filename):
        self.header_bytes = 0
        self.frm_bytes = 0
        self.filename = filename
        self.f_handle = open(filename, 'rb')
        self.read_file_header()

    def read_file_header(self):
        buf = self.f_handle.read(1)
        buf = buf + b'\x00\x00\x00'
        self.header_bytes = struct.unpack("i", buf)
        buf = self.f_handle.read(1)
        buf = self.f_handle.read(2)
        buf = buf + b'\x00\x00'
        self.frm_bytes = struct.unpack("i", buf)

    def read_frm_header(self):
        buf = self.f_handle.read(1)
        header_bytes = struct.unpack("B", buf)
        buf = self.f_handle.read(7)
        buf = self.f_handle.read(8)
        timestamp, = struct.unpack('Q', buf)
        buf = self.f_handle.read(8)
        payload_bytes, = struct.unpack('Q', buf)
        return timestamp, payload_bytes

    def read_frm(self):
        timestamp, payload_bytes = self.read_frm_header()
        payload = self.f_handle.read(payload_bytes)
        return timestamp, payload

    def get_time_list(self):
        time_list = []
        while True:
            try:
                t, _ = self.read_frm()
                time_list.append(t)
            except Exception as e:
                #logging.exception(e)
                break
        return time_list


class BinCutment:
    def __init__(self, filename):
        self.header_bytes = 0
        self.frm_bytes = 0
        self.filename = filename
        self.f_handle = open(filename, 'rb')

    def cut_bin_with_time(self,output_bin,t1,t2):
        print(output_bin)
        with open(output_bin,'w') as b:
            buf = self.f_handle.read(1)
            b.write(buf)
            buf = buf + b'\x00\x00\x00'
            self.header_bytes = struct.unpack("i", buf)
            buf = self.f_handle.read(1)
            b.write(buf)
            buf = self.f_handle.read(2)
            b.write(buf)
            buf = buf + b'\x00\x00'
            self.frm_bytes = struct.unpack("i", buf)

            while True:
                try:
                    aa = self.f_handle.read(1)
                    header_bytes = struct.unpack("B", aa)
                    bb = self.f_handle.read(7)
                    cc = self.f_handle.read(8)
                    timestamp, = struct.unpack('Q', cc)
                    dd = self.f_handle.read(8)
                    payload_bytes, = struct.unpack('Q', dd)
                    payload = self.f_handle.read(payload_bytes)

                    if int(timestamp) > t1 and int(timestamp) < t2:
                        b.write(aa)
                        b.write(bb)
                        b.write(cc)
                        b.write(dd)
                        b.write(payload)
                except:
                    break


def mergeTimeTxt(time_bin_path,output_path):
    time_bin_file_list = GetMatchedFilePaths(time_bin_path,"*",[".bin"])
    output_bin_file = os.path.join(output_path,'timestamp.txt')
    if not os.path.exists(output_bin_file):
        os.mknod(output_bin_file)
    if time_bin_file_list == []:
        print "\033[1;31m [ERROR]\033[0m not get any time.bin file"
        return 0
    ts_file_list = sorted(time_bin_file_list)
    i = 0
    with open(output_bin_file, 'w') as reuslt:
        for ts_file in ts_file_list:
            print(ts_file)
            if os.path.getsize(ts_file) == 0:
                continue
            reader = TimeReader(ts_file)
            timestamps = reader.get_time_list()
            for time in timestamps:
                reuslt.write(str(i) + ', ' + str(time) + '\n')
                i += 1

def mergeTimeBin(time_bin_path, output_path):
    time_bin_file_list = GetMatchedFilePaths(time_bin_path,"*",[".bin"])
    output_bin_file = os.path.join(output_path, 'timestamp.bin')
    if len(time_bin_file_list) ==1:
        shutil.copyfile(time_bin_file_list[0], output_bin_file)
        return True
    if len(time_bin_file_list) ==0:
        return False
    with open(output_bin_file, 'w') as reuslt:
        with open(time_bin_file_list[0],'rb') as aa:
            reuslt.write(aa.read(1))
            reuslt.write(aa.read(1))
            reuslt.write(aa.read(2))
            reuslt.write(aa.read())
        for i in range(1,len(time_bin_file_list)):
            with open(time_bin_file_list[i],'rb') as bb:
                bb.read(1)
                bb.read(1)
                bb.read(2)
                reuslt.write(bb.read())
    return True

def bjTimeToUnix(input_time):

    timeArray = time.strptime(input_time, "%Y%m%d%H%M%S")
    timestamp = time.mktime(timeArray)
    return int(timestamp)

def mergeVideos(video_list,merged_path):
    print "\033[1;32m [INFO]\033[0m  merging video files......"
    start_time = time.time()
    last_bjtime = os.path.basename(video_list[0]).split('_')[2]
    last_unixtime = bjTimeToUnix(last_bjtime)
    merge_video_list = []
    tmp_list = []
    for i in range(1,len(video_list)):
        bjtime = os.path.basename(video_list[i]).split('_')[2]
        unixtime = bjTimeToUnix(bjtime)
        tmp_list.append(video_list[i])
        if abs(unixtime - last_unixtime) < 120:
            last_unixtime = unixtime
        else:
            merge_video_list.append(tmp_list)
            tmp_list = []
            last_unixtime = unixtime
        if i == len(video_list)-1:
            merge_video_list.append(tmp_list)
    for i,merge_video in enumerate(merge_video_list):
        if merge_video ==[]:
            continue
        cap = cv2.VideoCapture(video_list[0])
        if not cap.isOpened():
            print("Cannot open video capture: {}".format(video_list[0]))
        fps = cap.get(cv2.CAP_PROP_FPS)

        FileClip_list = []
        for video in merge_video:
            FileClip_list.append(VideoFileClip(video))
        final_clip = concatenate_videoclips(FileClip_list)
        final_clip.to_videofile(merged_path+'/merge_video_'+str(i)+'.mp4', int(fps/3),threads =3, remove_temp=True)
    print "\033[1;32m [INFO]\033[0m  merging video files completly, consuming {:.3f}s".format(time.time()-start_time)

def JudgeStartAndEndFrame(start_index, end_index,frame_list):
    start_msg,end_msg = [],[]
    for index,interval in enumerate(frame_list):
        if start_index >= interval[0] and start_index <= interval[1]:
            start_msg = [index,start_index-interval[0]]
        if end_index >= interval[0] and end_index <= interval[1]:
            end_msg = [index,end_index-interval[0]]
    return start_msg,end_msg

def cutAdasVideos(video_list, point_list):
    frame_num = 0
    frame_list = []
    for video_path in video_list:
        cap = cv2.VideoCapture(video_path)
        old_frame_num = frame_num + 1

        frame_num += int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_list.append([old_frame_num, frame_num])
    cap = cv2.VideoCapture(video_list[0])
    if not cap.isOpened():
        print("Cannot open video capture: {}".format(video_list[0]))
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    fourcc = cv2.VideoWriter_fourcc(chr(fourcc & 0xFF),
                                    chr((fourcc >> 8) & 0xFF),
                                    chr((fourcc >> 16) & 0xFF),
                                    chr((fourcc >> 24) & 0xFF))
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print("code: width: {}, height: {}, fps: {}".format(
        width, height, fps))
    for i,seg_point in enumerate(point_list):
        output_dir = seg_point["output_dir"]
        start_index = seg_point["start_index"]
        end_index = seg_point["end_index"]

        writer = cv2.VideoWriter(output_dir, fourcc, int(fps), (int(width), int(height)))
        if not writer.isOpened():
            print("Cannot open video writer: {}".format(output_dir))
        start_msg, end_msg = JudgeStartAndEndFrame(start_index, end_index, frame_list)
        cut_video_list = []

        for i, video_path in enumerate(video_list):
            if i >= start_msg[0] and i <= end_msg[0]:
                cut_video_list.append(video_path)
        print(cut_video_list,start_msg, end_msg)
        if len(cut_video_list) < 2:
            cap_start = cv2.VideoCapture(cut_video_list[0])
            cap_start.set(cv2.CAP_PROP_POS_FRAMES, start_msg[1])
            frmae_num = cap_start.get(cv2.CAP_PROP_FRAME_COUNT)
            counts = start_msg[1]
            while counts <= frmae_num and counts <= end_msg[1]:
                flag, frame = cap_start.read()
                counts += 1
                writer.write(frame)
            cap_start.release()
        else:
            for j in range(len(cut_video_list)):
                if j == 0:
                    cap_start = cv2.VideoCapture(cut_video_list[j])
                    cap_start.set(cv2.CAP_PROP_POS_FRAMES, start_msg[1])
                    frmae_num = cap_start.get(cv2.CAP_PROP_FRAME_COUNT)
                    counts = start_msg[1]
                    while counts <= frmae_num:
                        flag, frame = cap_start.read()
                        counts += 1
                        writer.write(frame)
                    cap_start.release()
                elif j == len(cut_video_list) - 1 and j != 0:
                    cap_end = cv2.VideoCapture(cut_video_list[j])
                    cap_end.set(cv2.CAP_PROP_POS_FRAMES, 1)
                    frame_num = cap_end.get(cv2.CAP_PROP_FRAME_COUNT)
                    counts = 1
                    while counts <= end_msg[1] and counts <= frame_num:
                        flag, frame = cap_end.read()
                        counts += 1
                        writer.write(frame)
                    cap_end.release()
                else:
                    counts = 1
                    cap = cv2.VideoCapture(cut_video_list[j])
                    cap.set(cv2.CAP_PROP_POS_FRAMES, counts)
                    frame_num = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                    while counts <= frame_num:
                        flag, frame = cap.read()
                        counts += 1
                        writer.write(frame)
                    cap.release()
        writer.release()
    cap.release()


def cutVideoAndTxt(video_list,segment_list,merged_path):
    print "\033[1;32m [INFO]\033[0m  Cuting video files......"
    start_time = time.time()
    timestamp_file = os.path.join(merged_path,'timestamp.txt')
    point_list = []
    timestamp_list = []
    timebin_list = []
    video_tmp_path = 'cv22/normal'
    bin_file = os.path.join(merged_path,'timestamp.bin')
    for seg_point in segment_list:
        time_point = seg_point["time_point"]
        front_duration = seg_point["front_duration"]
        behind_duration = seg_point["behind_duration"]
        output_dir = seg_point["output_dir"]
        start_index, end_index,b,c = JudgeTheStartAndEndOfVideo(
            timestamp_file, time_point, front_duration, behind_duration)
        if start_index == 0 and end_index == 0:
            continue
        output_video_path = os.path.join(output_dir, video_tmp_path, "NOR_stream0.mp4")
        if not os.path.exists(os.path.join(output_dir, video_tmp_path)):
            os.makedirs(os.path.join(output_dir, video_tmp_path))
        point_list.append({"start_index": start_index, "end_index": end_index, "output_dir": os.path.join(output_dir, video_tmp_path)})
        timestamp_list.append({"start_index": start_index,
                               "end_index": end_index,
                               "output_dir": os.path.join(output_dir, video_tmp_path)})
        timebin_list.append({"start_index": time_point - front_duration*1000000,
                               "end_index": time_point + behind_duration*1000000,
                               "output_dir": os.path.join(output_dir, video_tmp_path)})
    # cutAdasVideos(video_list, point_list)
    # CutTimestamp(timestamp_file, timestamp_list)
    # CutTimeBin(bin_file,timebin_list)
    return moveAdasVideosAndBin(video_list, point_list,segment_list)
    print "\033[1;32m [INFO]\033[0m Cuting video files completly, consuming {:.3f}s".format(time.time()-start_time)

def moveAdasVideosAndBin(video_list, point_list,segment_list):
    frame_num = 0
    frame_list = []
    for video_path in video_list:
        cap = cv2.VideoCapture(video_path)
        old_frame_num = frame_num + 1

        frame_num += int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_list.append([old_frame_num, frame_num])
    for i,seg_point in enumerate(point_list):
        output_dir = seg_point["output_dir"]
        start_index = seg_point["start_index"]
        end_index = seg_point["end_index"]
        start_msg, end_msg = JudgeStartAndEndFrame(start_index, end_index, frame_list)
        cut_video_list = []
        for j, video_path in enumerate(video_list):
            if j >= start_msg[0] and j <= end_msg[0]:
                cut_video_list.append(video_path)
        for video_path in cut_video_list:
            file_name = os.path.basename(video_path)
            print(video_path,output_dir,file_name)
            shutil.copyfile(video_path,os.path.join(output_dir,file_name))
            print(video_path, output_dir, file_name)
            shutil.copyfile(video_path.replace('.mp4','.mp4.time.bin'), os.path.join(output_dir, file_name.replace('.mp4','.mp4.time.bin')))
        start_time = start_msg[1]*33333
        end_time = (1800-end_msg[1]) * 33333
        print(segment_list[i]['front_duration'], segment_list[i]['behind_duration'],start_msg[1],end_msg[1])
        segment_list[i]['front_duration'] = float(segment_list[i]['front_duration']) + start_msg[1]*0.033333
        segment_list[i]['behind_duration'] = float(segment_list[i]['behind_duration']) + (1800-end_msg[1]) * 0.033333
        print(segment_list[i]['front_duration'] ,segment_list[i]['behind_duration'])


    return segment_list


def CutTimeBin(bin_file,timebin_list):
    if not os.path.exists(bin_file) or timebin_list ==[]:
        return
    for seg_point in timebin_list:
        print(11111)
        output_dir=seg_point["output_dir"]
        start_time=seg_point["start_index"]
        end_time = seg_point["end_index"]
        output_bin_file = output_dir + "/" + os.path.basename(bin_file)
        bin_cut = BinCutment(bin_file)
        bin_cut.cut_bin_with_time(output_bin_file,start_time*1000,end_time*1000)

def cutDpcs(rosbag_file,segment_list):
    if rosbag_file == []:
        return
    print rosbag_file
    # for i in range(len(segment_list)):
    #     segment_list[i]["output_dir"] = os.path.join(segment_list[i]["output_dir"],'cv22')
    print("checkpoint10010")
    CutDpcs(rosbag_file,segment_list)

def processRosbag(rosjson_file,segment_list):
    start_time = time.time()
    if not os.path.exists(rosjson_file):
        print "\033[1;31m [ERROR]\033[0m get rosjson file error"
        return 0
    ros_file_name = os.path.basename(rosjson_file).split('.')[0]+'.bag'
    output_ros_file = os.path.join(os.path.split(rosjson_file)[0],ros_file_name)
    json_to_ros_cmd = ''.join(['cd ~/Codes/catkin_ws ',
                               '&& rosrun custom_msg_topic adverties_message.py ',
                               rosjson_file,' ',
                               output_ros_file])
    os.system(json_to_ros_cmd)
    for i in range(len(segment_list)):
        segment_list[i]["output_dir"] = os.path.join(segment_list[i]["output_dir"],'cv22')
    print("checkpoint1009")
    CutDpcs([output_ros_file],segment_list)
    print "\033[1;32m [INFO]\033[0m process dpcs consuming {:.3f}s".format(time.time() - start_time)


def judgeFileSizeAndExist(judge_file, check_size=0.2,upsize = 200000,false_check_reason=[],false_list = []):
    "as the function name descripted"
    if os.path.exists(judge_file) and \
            round(os.path.getsize(judge_file) / float(1024 * 1024), 1) >= check_size and \
            round(os.path.getsize(judge_file) / float(1024 * 1024), 1) < upsize:
            return false_check_reason,false_list
    else:
        #false_check_reason.append(os.path.basename(judge_file))
        false_list.append(judge_file)
        print "\033[1;31m [ERROR]\033[0m file:", judge_file, " is\033[1;31m wrong\033[0m\n"

        return false_check_reason,false_list


def checkAdasFile(video_list,rosjson_file):
    false_check_reason,false_video_list,false_rosjosn_list =[],[],[]
    if video_list == []:
        false_check_reason.append("videos")
    if rosjson_file == []:
        false_check_reason.append("rosjson")

    for video_path in video_list:
        false_check_reason,false_video_list =judgeFileSizeAndExist(video_path,25,30,false_check_reason,false_video_list)
    for rosjson_path in rosjson_file:
        false_check_reason,false_rosjosn_list = judgeFileSizeAndExist(rosjson_path, 5,0,false_check_reason,false_rosjosn_list)
    return false_check_reason,false_video_list,false_rosjosn_list


def adasMainProcess(dir_path,segment_list):
    adas_path = os.path.join(dir_path,'cv22')
    if not os.path.exists(adas_path):
        return []
    time_bin_path = os.path.join(adas_path,'normal/2')
    merged_path = os.path.join(adas_path,'merged_file')

    if not os.path.exists(merged_path):
        os.mkdir(merged_path)
    if not os.path.exists(time_bin_path):
        print "\033[1;31m [ERROR]\033[0m get time.bin file error"
        return []
    mergeTimeTxt(time_bin_path,merged_path)
    #mergeTimeBin(time_bin_path, merged_path)
    video_list = GetMatchedFilePaths(adas_path+'/normal/',"NOR_stream0*",[".mp4"],True)
    rosjson_file = GetMatchedFilePaths(adas_path, "frm*", [".json"], True)
    rosbag_file = GetMatchedFilePaths(dir_path, "a*", [".bag"], True)
    false_check_reason,false_video_list,false_rosjosn_list = checkAdasFile(video_list,rosjson_file)
    if false_video_list  != []:
        for false_video in false_video_list:
            video_list.pop(false_video)
    video_list = sorted(video_list)
    return_list = cutVideoAndTxt(video_list, segment_list, merged_path)

    cutDpcs(rosbag_file, return_list)
    # pool1 = multiprocessing.Pool(processes=4)
    # pool1.apply_async(mergeVideos, args=(video_list, merged_path,))
    # pool1.apply_async(cutVideoAndTxt, args=(video_list, segment_list,merged_path,))
    # #pool1.apply_async(processRosbag, args=(rosjson_file[0], segment_list,))
    # pool1.apply_async(cutDpcs,args=(rosbag_file, segment_list,))
    # pool1.close()
    # pool1.join()
    return false_check_reason



    # mergeVideos(video_list,merged_path)
    # cutVideoAndTxt(video_list,segment_list,merged_path)
    # processRosbag(rosjson_file[0],segment_list)



if __name__ == '__main__':
    #adasMainProcess('/media/sensetime/FieldTest/123/ccc/2020_12_10_20_30_27_AutoCollect', [{'log_type': 0, 'behind_duration': 69, 'output_dir': u'/media/sensetime/FieldTest/123/ccc/2020_12_10_20_30_27_AutoCollect_slice/ADAS/The_crossroads/2020_12_10_19_50_03', 'time_point': 1607601003448000, 'front_duration': 2}, {'log_type': 0, 'behind_duration': 62, 'output_dir': u'/media/sensetime/FieldTest/123/ccc/2020_12_10_20_30_27_AutoCollect_slice/ADAS/t-junction/2020_12_10_19_52_13', 'time_point': 1607601133780000, 'front_duration': 2}, {'log_type': 0, 'behind_duration': 10, 'output_dir': u'/media/sensetime/FieldTest/123/ccc/2020_12_10_20_30_27_AutoCollect_slice/ADAS/downhill/2020_12_10_19_53_27', 'time_point': 1607601207367000, 'front_duration': 2}, {'log_type': 0, 'behind_duration': 106, 'output_dir': u'/media/sensetime/FieldTest/123/ccc/2020_12_10_20_30_27_AutoCollect_slice/ADAS/The_crossroads/2020_12_10_19_53_52', 'time_point': 1607601232712000, 'front_duration': 2}])
    #mergeTimeTxt('/media/sensetime/FieldTest/123/ccc/12_10_CN-008_ARH/2020_12_10_20_30_27_AutoCollect/cv22/normal/10/111/merged/112/','/media/sensetime/FieldTest/123/ccc/12_10_CN-008_ARH/2020_12_10_20_30_27_AutoCollect/cv22/normal/10/111/merged/112/')
    #mergeTimeBin('/media/sensetime/FieldTest/123/ccc/12_10_CN-008_ARH/2020_12_10_20_30_27_AutoCollect/cv22/normal/10/111/merged/112/','/media/sensetime/FieldTest/123/ccc/12_10_CN-008_ARH/2020_12_10_20_30_27_AutoCollect/cv22/normal/10/111/merged/112/')
    adasMainProcess('/media/sensetime/FieldTest/123/ccc/2020_12_10_20_30_27_AutoCollect', [{'log_type': 0, 'behind_duration': 69, 'output_dir': u'/media/sensetime/FieldTest/123/ccc/2020_12_10_20_30_27_AutoCollect_slice/ADAS/The_crossroads/2020_12_10_19_50_03', 'time_point': 1607601003448000, 'front_duration': 2}, {'log_type': 0, 'behind_duration': 62, 'output_dir': u'/media/sensetime/FieldTest/123/ccc/2020_12_10_20_30_27_AutoCollect_slice/ADAS/t-junction/2020_12_10_19_52_13', 'time_point': 1607601133780000, 'front_duration': 2}, {'log_type': 0, 'behind_duration': 10, 'output_dir': u'/media/sensetime/FieldTest/123/ccc/2020_12_10_20_30_27_AutoCollect_slice/ADAS/downhill/2020_12_10_19_53_27', 'time_point': 1607601207367000, 'front_duration': 2}, {'log_type': 0, 'behind_duration': 106, 'output_dir': u'/media/sensetime/FieldTest/123/ccc/2020_12_10_20_30_27_AutoCollect_slice/ADAS/The_crossroads/2020_12_10_19_53_52', 'time_point': 1607601232712000, 'front_duration': 2}])
