import os
import cv2
import time
import logging
import shutil
import struct
import subprocess
from timebin_reader import TimeReader
from datetime import datetime
import multiprocessing
import cut_rec_multiprocess
from tools.read_and_write_json import loadTag,saveTag,getTime

segment_list = []

class Timestamp:
    def __init__(self, index, header_bytes, unknown_buf, timestamp, payload_bytes, payload):
        self.index = index
        self.header_bytes = header_bytes
        self.unknown_buf = unknown_buf
        self.timestamp = timestamp
        self.payload_bytes = payload_bytes
        self.payload = payload

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
    def read_frm_header_new(self):
        buf = self.f_handle.read(1)
        # header_bytes = buf
        header_bytes = struct.unpack("B", buf)
        buf = self.f_handle.read(7)
        unknown_buf = buf
        buf = self.f_handle.read(8)
        # timestamp = buf
        timestamp, = struct.unpack('Q', buf)
        buf = self.f_handle.read(8)
        # payload_bytes = buf
        payload_bytes, = struct.unpack('Q', buf)
        # header_bytes = self.f_handle.read(24)
        return header_bytes, unknown_buf, timestamp, payload_bytes

    def read_frm(self):
        timestamp, payload_bytes = self.read_frm_header()
        payload = self.f_handle.read(payload_bytes)
        return timestamp, payload

    def read_frm_new(self):
        header_bytes, unknown_buf, timestamp, payload_bytes = self.read_frm_header_new()
        payload = self.f_handle.read(payload_bytes)
        return header_bytes, unknown_buf, timestamp, payload_bytes, payload

    def get_all_list(self):
        time_list = []
        index = 1
        while True:
            try:
                header_bytes, unknown_buf, time_stamp, payload_bytes, payload = self.read_frm_new()
                new_timestamp = Timestamp(index, header_bytes, unknown_buf, time_stamp, payload_bytes, payload)
                time_list.append(new_timestamp)
                index = index + 1
            except Exception as e:
                # logging.exception(e)
                break
        return time_list

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


def bjTimeToUnix(input_time):

    timeArray = time.strptime(input_time, "%Y%m%d%H%M%S")
    timestamp = time.mktime(timeArray)
    return int(timestamp)

def refineSegmentList(video_list,time_bin_list,segment_list):
    print("checkpoint14")
    print(segment_list)
    time_list = []
    timestamp_list =[]
    print("checkpoint14.1.1")
    print(time_bin_list)
    for i,bin_file in enumerate(time_bin_list):
        print("checkpoint15")
        print(bin_file)
        reader = TimeReader(bin_file)
        timestamps = reader.get_time_list()
        timestamp_list.append(timestamps)
        time_list.append([timestamps[0],timestamps[-1]])

    print("checkpoint14.1")
    print(segment_list)
    for i,segment_point in enumerate(segment_list):
        print("checkpoint16")
        segment_list[i]['remove'] = False
        segment_video_list = []
        segment_list[i]['ofront_duration'] = segment_list[i]['front_duration']
        segment_list[i]['obehind_duration'] = segment_list[i]['behind_duration']
        start_time = (segment_point['time_point'] - segment_point['front_duration'] *1000000)*1000
        end_time = (segment_point['time_point'] + segment_point['behind_duration'] *1000000)*1000
        segment_list[i]['start_video'], segment_list[i]['end_video'] = -1, -1
        for j,time_stamp in enumerate(timestamp_list):
            if start_time > time_stamp[0] and start_time < time_stamp[-1]:
                segment_list[i]['start_video'] = j
                segment_list[i]['start_cut'] = start_time - time_stamp[0]
                segment_list[i]['front_duration'] = (segment_point['time_point']*1000 - time_stamp[0]) / 1e9
            if end_time > time_stamp[0] and end_time < time_stamp[-1]:
                segment_list[i]['end_video'] = j
                segment_list[i]['end_cut'] = end_time - time_stamp[0]
                segment_list[i]['behind_duration'] = (time_stamp[-1] - segment_point['time_point'] * 1000) / 1e9

        for h in range(len(video_list)):
            if h >= segment_list[i]['start_video'] and h <= segment_list[i]['end_video']:
                segment_video_list.append(video_list[h])
                print("checkpoint2.3")
        if segment_video_list == [] or segment_list[i]['start_video'] == -1 or segment_list[i]['end_video'] ==-1:
            segment_list[i]['remove'] = True
        else:
            if len(segment_video_list) > 1:
                first_video_bj = os.path.basename(segment_video_list[0]).split('_')[2]
                first_video_unix = bjTimeToUnix(bjtime)
                for l in range(1, len(segment_video_list)):
                    print(l)
                    bjtime = os.path.basename(segment_video_list[l]).split('_')[2]
                    unixtime = bjTimeToUnix(bjtime)
                    if abs(unixtime - first_video_unix) < 120:
                        first_video_unix = unixtime
                    else:
                        print("checkpoint2.4")
                        print(unixtime - first_video_unix)
                        segment_list[i]['remove'] = True
                        break
    result_list = []
    for segment in segment_list:
        print(segment)
        if segment['remove'] == False:
            result_list.append(segment)
    print("checkpoint14.2")
    print(segment_list)
    print(result_list)
    return result_list


def mergeVideo(merge_video,output_dir,output_name = 'NOR_stream0_merged.mp4'):
    file_name = os.path.join(output_dir,'file.txt')
    output_file = os.path.join(output_dir,output_name)
    with open(file_name,'w') as f:
        for video in merge_video:
            f.write("file '"+video+"'"+'\n')
    cmd = 'ffmpeg -safe 0 -f concat -i '+file_name+' -c copy '+output_file+' >/dev/null 2>&1'
    print(cmd)
    process = subprocess.Popen(cmd, shell=True)
    process.communicate()

def mergeTimeTxt(time_bin_path,output_path):
    time_bin_file_list = cut_rec_multiprocess.GetMatchedFilePaths(time_bin_path,"*",[".bin"])
    output_bin_file = os.path.join(output_path,'timestamp.txt')
    if not os.path.exists(output_bin_file):
        os.mknod(output_bin_file)
    if time_bin_file_list == []:
        print(getTime()+"\033[1;31m [ERROR]\033[0m not get any time.bin file")
        return 0
    ts_file_list = sorted(time_bin_file_list)
    i = 0
    # with open(output_bin_file, 'w') as reuslt:
    #     for ts_file in ts_file_list:
    #         print(ts_file)
    #         if os.path.getsize(ts_file) == 0:
    #             continue
    #         reader = TimeReader(ts_file)
    #         timestamps = reader.get_time_list()
    #         for time in timestamps:
    #             reuslt.write(str(i) + ', ' + str(time) + '\n')
    #             i += 1

def moveAdasVideosAndBin(adas_path, video_list, segment_list):
    print("checkpoint7")
    print(segment_list)
    # video_tmp_path = 'cv22/normal'
    for i,segment_point in enumerate(segment_list):
        if os.path.isdir(os.path.join(adas_path,'canlog')):
            try:
                shutil.copytree(os.path.join(adas_path,'canlog'), os.path.join(segment_point["output_dir"],'cv22/canlog'))
                # Moves canlog file from unsliced to sliced folder
            except:
                pass

        output_dir = os.path.join(segment_point["output_dir"], 'video_tmp_path')
        # if not os.path.exists(output_dir):
        #     os.makedirs(output_dir)
        if 'start_video' not in list(segment_point.keys()) or 'end_video' not in list(segment_point.keys()):
            print("Segment point error")
            continue

        merge_video = []
        # for i in range(len(video_list)):
        #     file_name = os.path.basename(video_list[i])
        #     if i >= segment_point['start_video'] and i <= segment_point['end_video']:
        #         merge_video.append(os.path.join(output_dir, file_name))
        #         shutil.copyfile(video_list[i], os.path.join(output_dir, file_name))
        #         shutil.copyfile(video_list[i].replace('.mp4', '.mp4.time.bin'),
        #                        os.path.join(output_dir, file_name.replace('.mp4', '.mp4.time.bin')))
        # merge_path = os.path.join(segment_point["output_dir"],'cv22/merged_video')
        splited_path = os.path.join(segment_point["output_dir"],'cv22/splited_video')

        # cutVideo(merge_video,splited_path,segment_point)
        cutTimetxt(output_dir, splited_path,segment_point)
        # calib_path = os.path.join(segment_point["output_dir"], 'cv22/calib')
        # if os.path.exists(calib_path):
        #     shutil.rmtree(calib_path)
        # shutil.copytree('config/calib', calib_path)

# def cutVideo(merge_video,splited_path,segment_point):
#     tmp_path = os.path.join(splited_path,'tmp_path')
#     if os.path.exists(splited_path):
#         shutil.rmtree(splited_path)
#     os.makedirs(splited_path)
#     if not os.path.exists(tmp_path):
#         os.makedirs(tmp_path)
#
#     start = segment_point['start_cut'] / 1e9
#     end = segment_point['end_cut'] / 1e9
#     if len(merge_video) == 0:
#         return
#     elif len(merge_video) == 1:
#         cmd = 'ffmpeg -i '+merge_video[0]+' -ss '+str(start)+' -c copy -to '+str(end)+' '\
#               +os.path.join(splited_path,'splited_video.mp4')+' >/dev/null 2>&1'
#         os.system(cmd)
#     else:
#         cmd1 = 'ffmpeg -i ' + merge_video[0] + ' -ss ' + str(start) + ' -c copy ' \
#                + os.path.join(tmp_path,'start.mp4')+' >/dev/null 2>&1'
#         cmd2 = 'ffmpeg -i ' + merge_video[1] + ' -c copy -to ' + str(end) + ' ' \
#                + os.path.join(tmp_path,'end.mp4')+' >/dev/null 2>&1'
#         os.system(cmd1)
#         os.system(cmd2)
#         merge_video[0] = os.path.join(tmp_path,'start.mp4')
#         merge_video[-1] = os.path.join(tmp_path,'end.mp4')
#         mergeVideo(merge_video,splited_path,'splited_video.mp4')
#         shutil.rmtree(tmp_path)
#     pass

def cutTimetxt(merge_video,splited_path,segment_point):
    start_time = (segment_point['time_point'] - segment_point['ofront_duration'] *1000000)*1000
    end_time = (segment_point['time_point'] + segment_point['obehind_duration'] * 1000000) * 1000
    time_bin_file_list = cut_rec_multiprocess.GetMatchedFilePaths(merge_video, "*", [".bin"])
    output_bin_file = os.path.join(splited_path, 'splited_timestamp.txt')
    if not os.path.exists(output_bin_file):
        os.mknod(output_bin_file)
    if time_bin_file_list == []:
        print(getTime()+"\033[1;31m [ERROR]\033[0m not get any time.bin file")
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
                if int(time) > int(start_time) and int(time) < int(end_time):
                    reuslt.write(str(i) + ', ' + str(time) + '\n')
                    i += 1

# def cutDpcs(rosbag_file,segment_list):
#     if rosbag_file == []:
#         return
#     print("printing rosbag_file checkpoint18")
#     print(rosbag_file)
#     print("checkpoint16")
#     cut_rec_multiprocess.CutDpcs(rosbag_file, segment_list)


def judgeFileSizeAndExist(judge_file, check_size=0, upsize=200000):
    "as the function name descripted"
    print("checkpoint4.1")
    if os.path.exists(judge_file) and \
        os.path.getsize(judge_file) / float(1024 * 1024) >= 0 and \
        round(os.path.getsize(judge_file) / float(1024 * 1024), 1) < upsize:
        print("checkpoint4.2")
        return True
    else:
        print(getTime()+"\033[1;31m [ERROR]\033[0m file:", judge_file, " is\033[1;31m wrong\033[0m\n")
        print("checkpoint4.3")
        return False

def refineVideoAndTime(video_list,tmp_time_list):
    time_bin_list = []
    result_video_list = []
    print("checkpoint19.2")
    print(tmp_time_list)
    print(video_list)
    for video_file in video_list:
        print("checkpoint19.3")
        print(video_file)
        time_bin_file = video_file.replace('.mp4', '.mp4.time.bin')
        print("checkpoint19.4")
        print(time_bin_file)
        # if time_bin_file in tmp_time_list:
        #     print("checkpoint19.5")
        # else:
        #     print("checkpoint19.5.1")
        # if judgeFileSizeAndExist(video_file,25,30):
        #     print("checkpoint19.6")
        # else:
        #     print("checkpoint19.6.1")
        # if os.path.getsize(time_bin_file) != 0:
        #     print("checkpoint19.7")
        # else:
        #     print("checkpoint19.7.1")
        #     print(time_bin_file)
        if time_bin_file in tmp_time_list and \
            judgeFileSizeAndExist(video_file,25,30) and \
            os.path.getsize(time_bin_file) != 0:
            print("checkpoint19.8")
            print(time_bin_file)
            print(video_file)
            time_bin_list.append(time_bin_file)
            result_video_list.append(video_file)
    print("checkpoint19.6")
    return result_video_list,time_bin_list

def JudgeStartAndEndFrame(start_index, end_index,frame_list):
    start_msg,end_msg = [],[]
    for index,interval in enumerate(frame_list):
        print(index,interval)
        if start_index >= interval[0] and start_index <= interval[1]:
            start_msg = [index,start_index-interval[0]]
        if end_index >= interval[0] and end_index <= interval[1]:
            end_msg = [index,end_index-interval[0]]
    print("Judge start and end frame")
    print(start_index, end_index)
    print(start_msg, end_msg)
    return start_msg,end_msg

def cutAdasVideosMultiprocess(video_list, point_list):
    frame_num = 0
    frame_list = []
    print(video_list)
    print("checkpoint200")
    print(point_list)
    for video_path in video_list:
        cap = cv2.VideoCapture(video_path)
        old_frame_num = frame_num + 1

        frame_num += int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_list.append([old_frame_num, frame_num])
    cap = cv2.VideoCapture(video_list[0])
    if not cap.isOpened():
        print(("Cannot open video capture: {}".format(video_list[0])))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    pool = multiprocessing.Pool(processes=12)
    for i, seg_point in enumerate(point_list):
        pool.apply_async(newmultiprocess, args=(video_list, seg_point, fourcc, fps, width, height, frame_list))
    pool.close()
    pool.join()
    cap.release()

def newmultiprocess(video_list, seg_point, fourcc, fps, width, height, frame_list,):

        output_dir = seg_point["output_dir"]
        output_dir = ''.join([output_dir,".mp4"])
        # output_dir = ''.join([output_dir, ".avi"])
        # start_index = seg_point["start_index"]
        start_index = seg_point["start_index"]//2
        print(start_index)
        # end_index = seg_point["end_index"]
        end_index = seg_point["end_index"]//2
        print(end_index)
        writer = cv2.VideoWriter(output_dir, fourcc, int(fps), (int(width), int(height)))
        if not writer.isOpened():
            print(("Cannot open video writer: {}".format(output_dir)))
        print("\033[1;32m checkpoint200.1\033[0m ")
        print(start_index,end_index,frame_list)

        start_msg, end_msg = JudgeStartAndEndFrame(start_index, end_index, frame_list)
        print("\033[1;32m checkpoint200.2\033[0m ")
        print(start_msg,end_msg)
        cut_video_list = []

        for i, video_path in enumerate(video_list):
            print(i, video_path)
            if i >= start_msg[0] and i <= end_msg[0]:
                cut_video_list.append(video_path)
        print((cut_video_list,start_msg, end_msg))
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

def cutAdasVideos(video_list, point_list):

    frame_num = 0
    frame_list = []
    print("checkpoint200")
    print(point_list)

    for video_path in video_list:
        cap = cv2.VideoCapture(video_path)
        old_frame_num = frame_num + 1

        frame_num += int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_list.append([old_frame_num, frame_num])
    cap = cv2.VideoCapture(video_list[0])
    if not cap.isOpened():
        print(("Cannot open video capture: {}".format(video_list[0])))
    # fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    # fourcc = cv2.VideoWriter_fourcc(chr(fourcc & 0xFF),
    #                                 chr((fourcc >> 8) & 0xFF),
    #                                 chr((fourcc >> 16) & 0xFF),
    #                                 chr((fourcc >> 24) & 0xFF))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # fourcc = cv2.VideoWriter_fourcc(*'X264')

    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(("code: width: {}, height: {}, fps: {}".format(
        width, height, fps)))
    for i,seg_point in enumerate(point_list):
        print("testing1")
        print(i, seg_point)
        output_dir = seg_point["output_dir"]
        output_dir = ''.join([output_dir,".mp4"])
        # output_dir = ''.join([output_dir, ".avi"])
        # start_index = seg_point["start_index"]
        start_index = seg_point["start_index"]//2
        print(start_index)
        # end_index = seg_point["end_index"]
        end_index = seg_point["end_index"]//2
        print(end_index)
        writer = cv2.VideoWriter(output_dir, fourcc, int(fps), (int(width), int(height)))
        if not writer.isOpened():
            print(("Cannot open video writer: {}".format(output_dir)))
        print("\033[1;32m checkpoint200.1\033[0m ")
        print(start_index,end_index,frame_list)

        start_msg, end_msg = JudgeStartAndEndFrame(start_index, end_index, frame_list)
        print("\033[1;32m checkpoint200.2\033[0m ")
        print(start_msg,end_msg)
        cut_video_list = []

        for i, video_path in enumerate(video_list):
            print(i, video_path)
            if i >= start_msg[0] and i <= end_msg[0]:
                cut_video_list.append(video_path)
        print((cut_video_list,start_msg, end_msg))
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

# def CutTimestamp(point_list, segment_list, timestamp_bin_file):
#
#     f = open('/home/trajic/Desktop/data/myfile.txt', 'w')
#     count = 0
#     for timestamp in timestamp_bin_file:
#         line = "".join([str(count), ", ", timestamp])
#         count = count +1
#         f.write(line)
#     f.close()
#



def cutVideoAndTxt(video_list, segment_list, timestamp_bin_file):
    print("test1")
    print(segment_list)
    print(getTime()+"\033[1;32m [INFO]\033[0m  Cutting video files......")
    start_time = time.time()

    new_bin = TimeReader(str(timestamp_bin_file))
    timestamp_file = new_bin.get_time_list()

    point_list = []
    timestamp_list = []
    timebin_list = []
    video_tmp_path = 'cv22/Sliced_ADAS'

    for seg_point in segment_list:
        print("checkpoint1.0.1")
        print(seg_point)
        time_point = seg_point["time_point"]
        front_duration = seg_point["front_duration"]
        behind_duration = seg_point["behind_duration"]
        output_dir = seg_point["output_dir"]
        print("\033[1;32m checkpoint1.1.\033[0m ")
        print((time_point, front_duration, behind_duration))

        start_index, end_index,b,c = cut_rec_multiprocess.JudgeTheStartAndEndOfVideo(
            timestamp_file, time_point, front_duration, behind_duration)
        print("\033[1;32m checkpoint1.1.3\033[0m ")
        print(start_index, end_index, b, c)

        output_video_path = os.path.join(output_dir, video_tmp_path, "Sliced_ADAS.mp4")
        print("checkpoint1.1")
        if not os.path.exists(os.path.join(output_dir, video_tmp_path)):
            os.makedirs(os.path.join(output_dir, video_tmp_path))
        print(output_video_path)

        point_list.append({"start_index": start_index, "end_index": end_index, "output_dir": output_video_path})
        # timestamp_list.append({"start_index": start_index,
        #                        "end_index": end_index,
        #                        "output_dir": os.path.join(output_dir, video_tmp_path)})

        timebin_list.append({"start_index": start_index - front_duration * 60,
                             "end_index": end_index + behind_duration * 60,
                             "output_dir": os.path.join(output_dir, video_tmp_path)})
    print("\033[1;32m checkpoint1.1.4\033[0m ")
    print(point_list)
    print(timebin_list)

    # shutil.copyfile(timestamp_file,os.path.join(merged_path,"NOR_stream0.txt"))
    print("\033[1;32m checkpoint1.1.5\033[0m ")
    print(video_list, point_list)
    # cutAdasVideos(video_list, point_list)
    cutAdasVideosMultiprocess(video_list, point_list)
    cut_rec_multiprocess.CutBin(timestamp_bin_file, timebin_list, point_list)

    print(getTime()+"\033[1;32m [INFO]\033[0m Cuting video files completly, consuming {:.3f}s".format(time.time()-start_time))

def adasMainProcess(dir_path,segment_list):
    print("checkpoint20")
    print(dir_path)
    print(segment_list)
    adas_path = os.path.join(dir_path, 'cv22')
    print(adas_path)
    if not os.path.exists(adas_path):
        print(" Found no adas path")
        return []

    video_list_1 = cut_rec_multiprocess.GetMatchedFilePaths(adas_path, "Amba_stream1*", [".mp4"], True)
    video_list_1 = sorted(video_list_1)
    print("checkpoint2.1")
    print(video_list_1)


    print("checkpoint19.1")
    print(segment_list)
    # segment_list = refineSegmentList(video_list_1, time_bin_list, segment_list)
    print("checkpoint4")
    print(segment_list)

    timestamp_bin_filepath = cut_rec_multiprocess.GetMatchedFilePaths(adas_path, "timestamp*", [".bin"], True)
    print("checkpoint6.1")
    print(timestamp_bin_filepath)
    cutVideoAndTxt(video_list_1, segment_list, timestamp_bin_filepath[0])
    # moveAdasVideosAndBin(adas_path, video_list_1, segment_list)

    return segment_list

if __name__ == "__main__":
    dir_path = '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect'
    point_list = [{'start_index': 2234, 'end_index': 87673, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/night_without_lamp/2021_05_07_19_37_02/cv22/Sliced_ADAS/Sliced_ADAS.mp4'}, {'start_index': 1328, 'end_index': 3128, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/sunnyday/2021_05_07_19_37_05/cv22/Sliced_ADAS/Sliced_ADAS.mp4'}, {'start_index': 2879, 'end_index': 87239, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/highway/2021_05_07_19_37_13/cv22/Sliced_ADAS/Sliced_ADAS.mp4'}, {'start_index': 3092, 'end_index': 77191, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/Straight_road/2021_05_07_19_37_17/cv22/Sliced_ADAS/Sliced_ADAS.mp4'}, {'start_index': 77312, 'end_index': 81152, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/The_crossroads/2021_05_07_19_57_54/cv22/Sliced_ADAS/Sliced_ADAS.mp4'}, {'start_index': 86141, 'end_index': 87941, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/city/2021_05_07_20_00_39/cv22/Sliced_ADAS/Sliced_ADAS.mp4'}, {'start_index': 86862, 'end_index': 88662, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/night_with_lamp/2021_05_07_20_00_51/cv22/Sliced_ADAS/Sliced_ADAS.mp4'}, {'start_index': 98402, 'end_index': 101042, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/The_crossroads/2021_05_07_20_03_45/cv22/Sliced_ADAS/Sliced_ADAS.mp4'}, {'start_index': 101133, 'end_index': 101673, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/uphill/2021_05_07_20_04_31/cv22/Sliced_ADAS/Sliced_ADAS.mp4'}, {'start_index': 101885, 'end_index': 102665, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/downhill/2021_05_07_20_04_43/cv22/Sliced_ADAS/Sliced_ADAS.mp4'}, {'start_index': 105787, 'end_index': 108187, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/The_crossroads/2021_05_07_20_05_48/cv22/Sliced_ADAS/Sliced_ADAS.mp4'}, {'start_index': 120062, 'end_index': 123782, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/The_crossroads/2021_05_07_20_09_46/cv22/Sliced_ADAS/Sliced_ADAS.mp4'}, {'start_index': 129520, 'end_index': 130300, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/The_crossroads/2021_05_07_20_12_24/cv22/Sliced_ADAS/Sliced_ADAS.mp4'}, {'start_index': 159016, 'end_index': 161836, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/The_crossroads/2021_05_07_20_20_36/cv22/Sliced_ADAS/Sliced_ADAS.mp4'}]
    time_bin_list = [{'start_index': 1620387422891880, 'end_index': 1620387422977320, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/night_without_lamp/2021_05_07_19_37_02/cv22/Sliced_ADAS'}, {'start_index': 1620387425790800, 'end_index': 1620387425792600, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/sunnyday/2021_05_07_19_37_05/cv22/Sliced_ADAS'}, {'start_index': 1620387433651880, 'end_index': 1620387433736240, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/highway/2021_05_07_19_37_13/cv22/Sliced_ADAS'}, {'start_index': 1620387437192880, 'end_index': 1620387437266980, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/Straight_road/2021_05_07_19_37_17/cv22/Sliced_ADAS'}, {'start_index': 1620388674200880, 'end_index': 1620388674204720, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/The_crossroads/2021_05_07_19_57_54/cv22/Sliced_ADAS'}, {'start_index': 1620388839360800, 'end_index': 1620388839362600, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/city/2021_05_07_20_00_39/cv22/Sliced_ADAS'}, {'start_index': 1620388851381800, 'end_index': 1620388851383600, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/night_with_lamp/2021_05_07_20_00_51/cv22/Sliced_ADAS'}, {'start_index': 1620389025716880, 'end_index': 1620389025719520, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/The_crossroads/2021_05_07_20_03_45/cv22/Sliced_ADAS'}, {'start_index': 1620389071234880, 'end_index': 1620389071235420, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/uphill/2021_05_07_20_04_31/cv22/Sliced_ADAS'}, {'start_index': 1620389083754880, 'end_index': 1620389083755660, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/downhill/2021_05_07_20_04_43/cv22/Sliced_ADAS'}, {'start_index': 1620389148793880, 'end_index': 1620389148796280, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/The_crossroads/2021_05_07_20_05_48/cv22/Sliced_ADAS'}, {'start_index': 1620389386986880, 'end_index': 1620389386990600, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/The_crossroads/2021_05_07_20_09_46/cv22/Sliced_ADAS'}, {'start_index': 1620389544608880, 'end_index': 1620389544609660, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/The_crossroads/2021_05_07_20_12_24/cv22/Sliced_ADAS'}, {'start_index': 1620390036212880, 'end_index': 1620390036215700, 'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/The_crossroads/2021_05_07_20_20_36/cv22/Sliced_ADAS'}]
    segment_list = [{'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/night_without_lamp/2021_05_07_19_37_02', 'time_point': 1620387422892000, 'front_duration': 2, 'behind_duration': 1422, 'log_type': 0}, {'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/sunnyday/2021_05_07_19_37_05', 'time_point': 1620387425792000, 'front_duration': 20, 'behind_duration': 10, 'log_type': 0}, {'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/highway/2021_05_07_19_37_13', 'time_point': 1620387433652000, 'front_duration': 2, 'behind_duration': 1404, 'log_type': 0}, {'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/Straight_road/2021_05_07_19_37_17', 'time_point': 1620387437193000, 'front_duration': 2, 'behind_duration': 1233, 'log_type': 0}, {'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/The_crossroads/2021_05_07_19_57_54', 'time_point': 1620388674201000, 'front_duration': 2, 'behind_duration': 62, 'log_type': 0}, {'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/city/2021_05_07_20_00_39', 'time_point': 1620388839362000, 'front_duration': 20, 'behind_duration': 10, 'log_type': 0}, {'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/night_with_lamp/2021_05_07_20_00_51', 'time_point': 1620388851383000, 'front_duration': 20, 'behind_duration': 10, 'log_type': 0}, {'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/The_crossroads/2021_05_07_20_03_45', 'time_point': 1620389025717000, 'front_duration': 2, 'behind_duration': 42, 'log_type': 0}, {'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/uphill/2021_05_07_20_04_31', 'time_point': 1620389071235000, 'front_duration': 2, 'behind_duration': 7, 'log_type': 0}, {'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/downhill/2021_05_07_20_04_43', 'time_point': 1620389083755000, 'front_duration': 2, 'behind_duration': 11, 'log_type': 0}, {'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/The_crossroads/2021_05_07_20_05_48', 'time_point': 1620389148794000, 'front_duration': 2, 'behind_duration': 38, 'log_type': 0}, {'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/The_crossroads/2021_05_07_20_09_46', 'time_point': 1620389386987000, 'front_duration': 2, 'behind_duration': 60, 'log_type': 0}, {'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/The_crossroads/2021_05_07_20_12_24', 'time_point': 1620389544609000, 'front_duration': 2, 'behind_duration': 11, 'log_type': 0}, {'output_dir': '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect_slice/ADAS/The_crossroads/2021_05_07_20_20_36', 'time_point': 1620390036213000, 'front_duration': 2, 'behind_duration': 45, 'log_type': 0}]
    video_list_2 = ['/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect/cv22/normal/Amba_stream0_20210507193623_1_70.mp4', '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect/cv22/video/mp4-0/1/Amba_stream0_20210507194124_1_71.mp4', '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect/cv22/video/mp4-0/1/Amba_stream0_20210507194623_1_72.mp4', '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect/cv22/video/mp4-0/1/Amba_stream0_20210507195124_1_73.mp4', '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect/cv22/video/mp4-0/1/Amba_stream0_20210507195623_1_74.mp4', '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect/cv22/video/mp4-0/1/Amba_stream0_20210507200124_1_75.mp4', '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect/cv22/video/mp4-0/1/Amba_stream0_20210507200624_1_76.mp4', '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect/cv22/video/mp4-0/1/Amba_stream0_20210507201124_1_77.mp4', '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect/cv22/video/mp4-0/1/Amba_stream0_20210507201624_1_78.mp4', '/home/trajic/Desktop/data/2021_05_07_20_22_12_AutoCollect/cv22/video/mp4-0/1/Amba_stream0_20210507202124_1_79.mp4']
    # merged_path = '/home/trajic/Desktop/data/2021_05_07_22_02_10_AutoCollect/cv22/merged_file'
    adasMainProcess(dir_path, segment_list)
    print("testing adas_pipeline")
# adasMainProcess('/home/SENSETIME/caixinyu1/Desktop/data/2021_05_07_22_02_10_AutoCollect', segment_list)
