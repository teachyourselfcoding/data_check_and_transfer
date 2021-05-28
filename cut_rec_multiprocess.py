# coding=utf-8
import os
import time

import cv2
import ast
import sys
import copy
import struct
import rosbag
import shutil
import argparse
import multiprocessing

import execnet

from decimal import Decimal
from rospy.rostime import Time

import adas_pipeline
from adas_pipeline import TimeReader
from tools.read_and_write_json import loadTag, saveTag, getTime

get_path = os.path.join


def GetMatchedFilePaths(data_dir,
                        pattern="*",
                        formats=[".h264"],
                        recursive=False):
    files = []
    data_dir = os.path.normpath(os.path.abspath(data_dir))

    import fnmatch

    for f in os.listdir(data_dir):
        current_path = get_path(os.path.normpath(data_dir), f)
        if os.path.isdir(current_path) and recursive:
            files += GetMatchedFilePaths(current_path, pattern, formats,
                                         recursive)
        elif fnmatch.fnmatch(f,
                             pattern) and os.path.splitext(f)[-1] in formats:
            files.append(current_path)
    return files


def ReadFile(file_path):
    data = []
    with open(file_path, 'r') as reader:
        data = reader.readlines()
    return data


def GetArguments():
    parser = argparse.ArgumentParser(description='')

    parser.add_argument("-d",
                        type=str,
                        dest="directory",
                        default="",
                        help="data directory")

    parser.add_argument("-l",
                        type=list,
                        dest="segment_list",
                        default="",
                        help="[{output_dir,time_point,front_duration,behind_duration,log_type}]")

    args = vars(parser.parse_args())
    return args


def CutBin(timestamp_bin_file, bin_list, point_list):
    if bin_list == []:
        return
    new_bin = TimeReader(str(timestamp_bin_file))
    timestamp_file = new_bin.get_all_list()

    for seg_point in bin_list:
        output_dir = seg_point["output_dir"]
        start_index = seg_point["start_index"]
        end_index = seg_point["end_index"]
        output_timestamp_file = output_dir + "/sliced.bin"

        file = open(output_timestamp_file, "wb")
        file.write(struct.pack('I', 0))

        for timestamp in timestamp_file:
            # print(timestamp.timestamp)
            if start_index <= timestamp.index <= end_index:

                file.write(struct.pack('B', timestamp.header_bytes[0]))

                file.write(timestamp.unknown_buf)

                file.write(struct.pack('Q', timestamp.timestamp))

                file.write(struct.pack('Q', timestamp.payload_bytes))

                file.write(timestamp.payload)



def CutTimestamp(timestamp_file, point_list):
    if point_list == []:
        return

    for seg_point in point_list:
        output_dir = seg_point["output_dir"]
        start_index = seg_point["start_index"]
        end_index = seg_point["end_index"]
        output_timestamp_file = output_dir + "/" + os.path.basename(timestamp_file)
        timestamp_lines = ReadFile(timestamp_file)
        with open(output_timestamp_file, "w") as fout:
            for i in range(len(timestamp_lines)):
                if i >= start_index and i <= end_index:
                    fout.write(timestamp_lines[i])


def CutVideos(video_path, point_list):
    '''
    input:
        video_path:str
        point_list:[{"start_index":121545, "end_index":1245454,"output_dir":/path/to/output}]
    '''

    if point_list == []:
        return
    # read video
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Cannot open video capture: {}".format(video_path))
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print("code: {}, width: {}, height: {}, fps: {}".format(
        fourcc, width, height, fps))

    for seg_point in point_list:
        output_dir = seg_point["output_dir"]
        start_index = seg_point["start_index"]
        end_index = seg_point["end_index"]
        output_video_path = output_dir + "/" + os.path.basename(video_path)
        writer = cv2.VideoWriter(output_video_path, fourcc, int(fps), (int(width), int(height)))
        if not writer.isOpened():
            print("Cannot open video writer: {}".format(output_video_path))
        counts = start_index

        try:
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_index)
            while counts <= end_index:
                flag, frame = cap.read()
                counts += 1
                writer.write(frame)
        except:
            print(getTime() + "\033[1;31m [ERROR]\033[0m cut video failed ")
            return 0
    writer.release()
    cap.release()


def CutVideoWithMpeg(video_path, point_list):
    if point_list == []:
        return
    for seg_point in point_list:
        output_dir = seg_point["output_dir"]
        start_time = seg_point["start_time"]
        end_time = seg_point["end_time"]
        output_video_path = output_dir + "/" + os.path.basename(video_path)
        if os.path.exists(output_video_path):
            os.remove(output_video_path)
        cmd = 'ffmpeg -avoid_negative_ts 1 -accurate_seek -i ' + video_path + ' -ss ' + str(start_time) + \
              ' -c copy -to ' + str(end_time) + ' ' + output_video_path + ' >/dev/null 2>&1'
        print(cmd)
        os.system(cmd)


def CutBasler(screen_files, screen_txts, segment_list):
    start_time = time.time()
    print(getTime() + "\033[1;32m [INFO]\033[0m Cutting Basler Video .........\n")

    point_list = []

    for i in range(len(screen_txts)):
        screen_file = screen_files[i]
        screen_txt = screen_txts[i]
        # judge the start and end
        for seg_point in segment_list:
            time_point = seg_point["time_point"]
            front_duration = seg_point["front_duration"] + 5
            behind_duration = seg_point["behind_duration"]
            output_dir = seg_point["output_dir"]
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)

            start_index, end_index, start_time, end_time = JudgeTheStartAndEndOfBasler(
                screen_txt, time_point, front_duration, behind_duration)
            if start_index == 0 or end_index == 0:
                continue

            point_list.append({"start_index": start_index,
                               "end_index": end_index,
                               "start_time": start_time.to_sec(),
                               "end_time": end_time.to_sec(),
                               "output_dir": output_dir})

        try:
            # cut videos
            CutVideos(screen_file, point_list)
            # cut timestamp
            CutTimestamp(screen_txt, point_list)
        except Exception as e:
            print (getTime()+"\033[1;31m [ERROR]\033[0m Error while cutting Basler video ")

    print(getTime() + "\033[1;32m [INFO]\033[0m Finished cutting " + str(
        len(screen_files)) + " Basler Videos, consuming {:.3f}s".format(time.time() - start_time))

def CutScreenCast(screen_files, screen_txts, segment_list):

    print(getTime() + "\033[1;32m [INFO]\033[0m Cutting Screencast Video .........\n")
    start_time = time.time()
    point_list = []

    for i in range(len(screen_txts)):
        screen_file = screen_files[i]
        screen_txt = screen_txts[i]
        # judge the start and end
        for seg_point in segment_list:
            time_point = seg_point["time_point"]
            front_duration = seg_point["front_duration"] + 5
            behind_duration = seg_point["behind_duration"]
            output_dir = seg_point["output_dir"] + '/screen_cast'

            if not os.path.exists(output_dir):
                os.mkdir(output_dir)

            start_index, end_index, start_time, end_time = JudgeTheStartAndEndOfScreencast(
                screen_txt, time_point, front_duration, behind_duration)
            if start_index == 0 or end_index == 0:
                continue

            point_list.append({"start_index": start_index,
                               "end_index": end_index,
                               "start_time": start_time.to_sec(),
                               "end_time": end_time.to_sec(),
                               "output_dir": output_dir})

        try:
            # cut videos
            print(getTime() + "\033[1;32m [INFO]\033[0m Cutting Screencast Video .........\n")
            CutVideos(screen_file, point_list)
            # cut timestamp
            CutTimestamp(screen_txt, point_list)

        except Exception as e:
            print (getTime()+"\033[1;31m [ERROR]\033[0m While cutting screencast video ")
    print(getTime() + "\033[1;32m [INFO]\033[0m Finished cutting " + str(
        len(screen_files)) + " Screencast Videos, consuming {:.3f}s".format(time.time() - start_time))


def JudgeTheStartAndEndOfBasler(timestamp_file, time_point, front_duration,
                                behind_duration):
    start_point = time_point - front_duration * 1000000
    end_point = time_point + behind_duration * 1000000
    suggested_start = Time(int(start_point / 1000000), start_point % 1000000 * 1000)
    suggested_end = Time(int(end_point / 1000000), end_point % 1000000 * 1000)
    suggested_point = Time(int(time_point / 1000000), time_point % 1000000 * 1000)

    timestamps_lines = ReadFile(timestamp_file)
    timestamps = []
    for i in range(len(timestamps_lines)):
        line = timestamps_lines[i]
        line = line.strip('\n').strip().split(", ")
        if len(line) < 2:
            continue
        frame = ast.literal_eval(line[0])
        sec = int(Decimal(line[1][:10]))
        nsec = int(Decimal(line[1][10:] + "0" * (9 - len(line[1][10:]))))
        timestamps.append((i, Time(sec, nsec)))
    if len(timestamps) <= 0:
        sys.exit(1)
    stamp_start = timestamps[0][1]
    stamp_end = timestamps[len(timestamps) - 1][1]

    if stamp_start > suggested_point or stamp_end < suggested_point:
        print("video time_point={} is not in [{}, {}]".format(
            time_point, stamp_start, stamp_end))
        return (0, 0, 0, 0)
    start = max(stamp_start, suggested_start)
    end = min(stamp_end, suggested_end)

    start_index = 0
    end_index = 0
    for i in range(len(timestamps)):
        if timestamps[i][1] < start:
            start_index = i
        if timestamps[i][1] < end:
            end_index = i
    return start_index, end_index, start - stamp_start, end - stamp_start


def JudgeTheStartAndEndOfScreencast(timestamp_file, time_point, front_duration,
                                    behind_duration):
    start_point = time_point - front_duration * 1000000
    end_point = time_point + behind_duration * 1000000
    suggested_start = Time(int(start_point / 1000000), start_point % 1000000 * 1000)
    suggested_end = Time(int(end_point / 1000000), end_point % 1000000 * 1000)
    suggested_point = Time(int(time_point / 1000000), time_point % 1000000 * 1000)

    timestamps_lines = ReadFile(timestamp_file)
    timestamps = []
    for i in range(len(timestamps_lines)):
        line = timestamps_lines[i]
        line = line.strip('\n').strip().split(", ")
        if len(line) < 2:
            continue
        frame = ast.literal_eval(line[0])
        sec = int(Decimal(line[1][:10]))
        nsec = int(Decimal(line[1][10:] + "0" * (9 - len(line[1][10:]))))
        timestamps.append((i, Time(sec, nsec)))
    if len(timestamps) <= 0:
        sys.exit(1)
    stamp_start = timestamps[0][1]
    stamp_end = timestamps[len(timestamps) - 1][1]

    if stamp_start > suggested_point or stamp_end < suggested_point:
        print("video time_point={} is not in [{}, {}]".format(
            time_point, stamp_start, stamp_end))
        return (0, 0, 0, 0)
    start = max(stamp_start, suggested_start)
    end = min(stamp_end, suggested_end)

    start_index = 0
    end_index = 0
    for i in range(len(timestamps)):
        if timestamps[i][1] < start:
            start_index = i
        if timestamps[i][1] < end:
            end_index = i
    return start_index, end_index, start - stamp_start, end - stamp_start


# timestamp_file is a list!
def JudgeTheStartAndEndOfVideo(timestamp_file, time_point, front_duration,
                               behind_duration):

    start_point = time_point - front_duration * 1000000
    end_point = time_point + behind_duration * 1000000
    suggested_start = Time(int(start_point / 1000000), start_point % 1000000 * 1000)
    suggested_end = Time(int(end_point / 1000000), end_point % 1000000 * 1000)
    suggested_point = Time(int(time_point / 1000000), time_point % 1000000 * 1000)

    # timestamps_lines = ReadFile(timestamp_file)
    timestamps_lines = timestamp_file
    timestamps = []

    for i in range(len(timestamps_lines)):
        line = str(timestamps_lines[i])
        line = line.strip('\n').strip().split(", ")
        # if len(line) < 2:
        #     # print(line)
        #     continue
        # frame = ast.literal_eval(line[0])
        # sec = int(Decimal(line[1][:10]))
        # nsec = int(Decimal(line[1][10:] + "0" * (9 - len(line[1][10:]))))
        sec = int(Decimal(line[0][:10]))
        nsec = int(Decimal(line[0][10:] + "0" * (9 - len(line[0][10:]))))
        timestamps.append((i, Time(sec, nsec)))

    if len(timestamps) <= 0:
        sys.exit(1)
    stamp_start = timestamps[0][1]
    stamp_end = timestamps[len(timestamps) - 1][1]


    if stamp_start > suggested_point or stamp_end < suggested_point:
        print("video time_point={} is not in [{}, {}]".format(
            time_point, stamp_start, stamp_end))
        return (0, 0, 0, 0)
    start = max(stamp_start, suggested_start)
    end = min(stamp_end, suggested_end)

    start_index = 0
    end_index = 0

    for i in range(len(timestamps)):
        if timestamps[i][1] < start:
            start_index = i
        if timestamps[i][1] < end:
            end_index = i

    return start_index, end_index, start - stamp_start, end - stamp_start


def RecReadEntry(f, current_fd_pointer):
    entry = {}
    byte = f.read(1)
    if not byte:
        return False, entry
    entry["topic_id"] = struct.unpack("B", byte)[0]
    byte = f.read(8)

    entry["time_ns"] = struct.unpack("Q", byte)[0]
    byte = f.read(4)
    entry["cap_len"] = struct.unpack("I", byte)[0]
    # byte = f.read(entry["cap_len"])
    f.seek(entry["cap_len"], 1)  # ignore the data len
    entry["current_fd_pointer"] = current_fd_pointer + 1 + 8 + 4 + entry[
        "cap_len"]
    return True, entry


def JudgeTheStartAndEndOfRec(rec_file, segment_list):

    start_end_index_list = []
    rec_fd = open(rec_file, 'rb')

    RecReadHeader(rec_fd)
    header_len = rec_fd.tell()
    current_fd_pointer = header_len

    data_segments = []
    while True:
        segment_begin = current_fd_pointer
        res, data = RecReadEntry(rec_fd, current_fd_pointer)
        if not res:
            break
        current_fd_pointer = data["current_fd_pointer"]
        if current_fd_pointer <= 0:
            sys.exit(1)
        segment_end = current_fd_pointer - 1
        data_segments.append((data["time_ns"], segment_begin, segment_end))

    if len(data_segments) <= 0:
        print("rec segments size is 0, exit")
        return [0, 0]

    stamp_start = data_segments[0][0]
    stamp_end = data_segments[len(data_segments) - 1][0]


    for seg_point in segment_list:

        time_point = seg_point["time_point"]
        front_duration = seg_point["front_duration"]
        behind_duration = seg_point["behind_duration"]

        start_point = time_point - front_duration * 1000000
        end_point = time_point + behind_duration * 1000000
        suggested_start = start_point * 1000
        suggested_end = end_point * 1000
        suggested_point = time_point * 1000

        if stamp_start > suggested_point or stamp_end < suggested_point:
            print("rec time_point={} is not in [{}, {}]".format(
                time_point, stamp_start, stamp_end))
            start_end_index_list.append([0, 0])
            continue
        start = max(stamp_start, suggested_start)
        end = min(stamp_end, suggested_end)

        start_index = 0
        end_index = 0
        for i in range(len(data_segments)):
            if data_segments[i][0] < start:
                start_index = i
            if data_segments[i][0] < end:
                end_index = i
        start_end_index_list.append([data_segments[start_index][1], data_segments[end_index][2]])
    return start_end_index_list


def CutRec(rec_file, point_list):

    '''
    input:
        rec_file:str
        point_list:[{"start_index":121545, "end_index":1245454,"output_dir":/path/to/output}]
    '''
    if point_list == []:
        print("point list in None")
        return
    rec_fd = open(rec_file, 'rb')

    for seg_point in point_list:
        output_dir = seg_point["output_dir"]
        start_index = seg_point["start_index"]
        end_index = seg_point["end_index"]
        sensor_output_dir = output_dir + "/sensors_record/"

        if not os.path.isdir(sensor_output_dir):
            os.mkdir(sensor_output_dir)

        rec_fd.seek(0, 0)
        RecReadHeader(rec_fd)
        header_len = rec_fd.tell()

        output_rec_file = sensor_output_dir + os.path.basename(rec_file)
        output_size = end_index - start_index + 1
        left_size = output_size
        with open(output_rec_file, "wb") as out_fd:
            # write header
            rec_fd.seek(0, 0)
            header_data = rec_fd.read(header_len)
            out_fd.write(header_data)

            rec_fd.seek(start_index, 0)
            # write data segments
            while left_size > 0:
                if left_size > 1024:
                    chunk_size = 1024
                else:
                    chunk_size = left_size
                chunk = rec_fd.read(chunk_size)
                out_fd.write(chunk)
                left_size = left_size - chunk_size


def CutRecs(rec_files, segment_list):

    start_time = time.time()
    print(getTime() + "\033[1;32m [INFO]\033[0m Cuting rec files......")
    for rec_file in rec_files:
        point_list = []
        print('\n.................', rec_file)
        sd_index_list = JudgeTheStartAndEndOfRec(rec_file, segment_list)
        if sd_index_list == [0, 0] or len(sd_index_list) != len(segment_list):
            continue
        for i in range(len(segment_list)):
            seg_point = segment_list[i]
            output_dir = seg_point["output_dir"]
            start_index = sd_index_list[i][0]
            end_index = sd_index_list[i][1]
            if start_index == 0 or end_index == 0:
                continue
            point_list.append({"start_index": start_index, "end_index": end_index, "output_dir": output_dir})

        CutRec(rec_file, point_list)
    print(getTime() + "\033[1;32m [INFO]\033[0m Finished cutting " + str(
        len(rec_files)) + " .Rec files, consuming {:.3f}s".format(time.time() - start_time))


def RecReadHeader(f):
    header = {}
    byte = f.read(1)
    header["magic_number"] = int.from_bytes(byte, "big", signed=False)

    byte = f.read(1)
    header["topic_number"] = int.from_bytes(byte, "big", signed=False)
    header["topics"] = []
    header["id2topic"] = {}

    for i in range(header["topic_number"]):
        cur_topic = {}
        byte = f.read(1)
        cur_topic["topic_id"] = int.from_bytes(byte, "little", signed=False)
        byte = f.read(4)
        cur_topic["topic_max_length"] = int.from_bytes(byte, "little", signed=False)
        byte = f.read(1)
        cur_topic["topic_len"] = int.from_bytes(byte, "little", signed=False)
        byte = f.read(cur_topic["topic_len"])

        cur_topic["topic_data"] = "".join(
            byte.decode('ascii'))
        header["topics"].append(cur_topic)
        header["id2topic"][cur_topic["topic_id"]] = cur_topic["topic_data"]

    byte = f.read(4)

    header["extra_len"] = int.from_bytes(byte, "little", signed=False)

    header["extra_data"] = ''
    if header["extra_len"] > 0:
        byte = f.read(header["extra_len"])
        header["extra_data"] = cur_topic["topic_data"] = "".join(
            byte.decode('ascii'))


def CutDpcbag(dpc_file, point_list):

    def expr_eval(expr):
        def eval_fn(topic, m, t):
            return eval(expr)

        return eval_fn

    inbag = rosbag.bag.Bag(dpc_file)
    dpc_name = os.path.basename(dpc_file)

    output_list = []
    for seg_point in point_list:
        begin_secs = seg_point["begin_secs"]
        end_secs = seg_point["end_secs"]
        output_dir = os.path.join(seg_point["output_dir"], dpc_name)
        filter_expr = []
        filter_expr.extend(["t.to_sec() > {}".format(begin_secs)])
        filter_expr.extend(["t.to_sec() < {}".format(end_secs)])
        filter_expr = " and ".join(filter_expr)
        print(filter_expr)

        rosbag.rosbag_main.filter_cmd([dpc_file, output_dir, filter_expr])

        outbag = rosbag.bag.Bag(output_dir, 'w')
        filter_fn = expr_eval(filter_expr)
        meter = rosbag.rosbag_main.ProgressMeter(output_dir, inbag._uncompressed_size)
        output_list.append([outbag, filter_fn, meter, output_dir])
    total_bytes = 0
    for topic, raw_msg, t in inbag.read_messages(raw=True):
        # try:
        msg_type, serialized_bytes, md5sum, pos, pytype = raw_msg
        msg = pytype()
        msg.deserialize(serialized_bytes)
        for i in range(len(output_list)):
            if output_list[i][1](topic, msg, t):
                output_list[i][0].write(topic, msg, t)
            total_bytes += len(serialized_bytes)
            output_list[i][2].step(total_bytes)
        # except Exception as e:
        #     print getTime()+"\033[1;31m [ERROR]\033[0m cut dpc bag failed "

    inbag.close()
    for i in range(len(output_list)):
        output_list[i][0].close()


def CutDpcs(dpc_files, segment_list):
    start_time = time.time()
    print(getTime() + "\033[1;32m [INFO]\033[0m Cuting dpc bag......")
    point_list = []

    for i in range(len(dpc_files)):
        dpc_file = dpc_files[i]

        # judge the start and end
        for seg_point in segment_list:
            time_point = seg_point["time_point"]
            front_duration = seg_point["front_duration"]
            behind_duration = seg_point["behind_duration"]
            output_dir = seg_point["output_dir"]

            begin_secs = time_point / 1000000 - front_duration
            end_secs = time_point / 1000000 + behind_duration
            point_list.append({"begin_secs": begin_secs, "end_secs": end_secs, "output_dir": output_dir})
        CutDpcbag(dpc_file, point_list)

    print(getTime() + "\033[1;32m [INFO]\033[0m Completed cutting of Dpc files\n")
    print(getTime() + "\033[1;32m [INFO]\033[0m Finished cutting " + str(
        len(dpc_files)) + " Basler Videos, consuming {:.3f}s".format(time.time() - start_time))

def CutHmiFile(hmi_file, segment_list):
    for seg_point in segment_list:
        time_point = seg_point["time_point"]
        front_duration = seg_point["front_duration"]
        behind_duration = seg_point["behind_duration"]
        output_dir = os.path.join(seg_point["output_dir"], 'hmi')
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        output_file = os.path.join(output_dir, os.path.basename(hmi_file))

        begin_nsecs = time_point - front_duration * 1000000
        end_nsecs = time_point + behind_duration * 1000000

        cmd = ''.join(
            ["cat ", hmi_file, " | awk '$1 >='$((", str(begin_nsecs), "))' && $1 <='$((", str(end_nsecs), "))'' > ",
             output_file])
        print(cmd)
        os.system(cmd)


def CopyConfigCacheAndLogs(data_dir, segment_list):
    print(getTime() + "\033[1;32m [INFO]\033[0m copying config and log .........\n")
    for seg_point in segment_list:
        output_dir_path = seg_point["output_dir"]
        log_dir_list = ["cache", "config", "versions", "simulator_scenario"]
        for log_dir in log_dir_list:
            try:
                log_dir_path = os.path.join(output_dir_path, log_dir)
                if os.path.isdir(log_dir_path):
                    shutil.rmtree(log_dir_path)
                if os.path.exists(os.path.join(data_dir, log_dir)):
                    shutil.copytree(os.path.join(data_dir, log_dir), log_dir_path)
            except Exception as e:
                print(getTime() + "\033[1;31m [ERROR]\033[0m copy cache or config failed ")

        cv22_path = os.path.join(data_dir, 'cv22')
        cv22_output_path = os.path.join(output_dir_path, 'cv22')
        cv22_copy_list = ["canlog", "config"]
        for cv22_dir in cv22_copy_list:
            try:
                cv22_dir_path = os.path.join(cv22_output_path, cv22_dir)
                if os.path.isdir(cv22_dir_path):
                    shutil.rmtree(cv22_dir_path)
                if os.path.exists(os.path.join(cv22_path, cv22_dir)):
                    shutil.copytree(os.path.join(cv22_path, cv22_dir), cv22_dir_path)
            except Exception as e:
                print(getTime() + "\033[1;31m [ERROR]\033[0m copy cv22 failed ")

    print(getTime() + "\033[1;32m [INFO]\033[0m Completed copying of config cache and log\n")
    # CutSimulatorScenario(data_dir, segment_list)


def CutSimulatorScenario(data_dir, point_list):
    '''
    input:
        rec_file:str
        point_list:[{"time_point":121545, "front_duration":15,"behind_duration":5,"output_dir":/path/to/output}]
    '''
    config_ = loadTag('config/data_pipeline_config.json', '')
    try:
        if os.path.isfile(os.path.join(config_["senseauto_path"],
                                       "senseauto-simulation/node/build/module/simulator/tools/scenario_log_tools/scenario_log_razor")):
            razor = os.path.join(config_["senseauto_path"],
                                 "senseauto-simulation/node/build/module/simulator/tools/scenario_log_tools/scenario_log_razor")
        elif os.path.isfile(os.path.join(config_["senseauto_path"],
                                         "senseauto-simulation/node/module/simulator/tools/scenario_log_tools/scenario_log_razor")):
            razor = os.path.join(config_["senseauto_path"],
                                 "senseauto-simulation/node/module/simulator/tools/scenario_log_tools/scenario_log_razor")
        else:

            print("cannot find the simulator_scenario_log_razor, exit")
        for seg_point in point_list:
            time_point = seg_point["time_point"]
            front_duration = seg_point["front_duration"]
            behind_duration = seg_point["behind_duration"]
            output_dir = seg_point["output_dir"]
            simulator_file = os.path.join(data_dir, 'simulator_scenario/simulator_scenario_log.bin')
            outout_dir_path = os.path.join(output_dir, 'simulator_scenario')
            razor_cmd = "{} 1 {} {} {} {} {}".format(
                razor,
                simulator_file, outout_dir_path,
                str(int(time_point // 1000000)), str(front_duration + 15), str(behind_duration + 20))

            print(razor_cmd)
            os.system(razor_cmd)

    except Exception as e:
        print(getTime() + "\033[1;31m [ERROR]\033[0m cut simulator.bin failed ")


def main(data_dir, segment_list):

    pattern = "port_*"
    screen_files = []
    screen_txts = []

    basler_video_file = GetMatchedFilePaths(data_dir,
                                            "port_0*",
                                            [".avi"],
                                            True)
    basler_txt_file = GetMatchedFilePaths(data_dir,
                                          "port_0*",
                                          [".txt"],
                                          True)

    video_files = GetMatchedFilePaths(data_dir,
                                      pattern,
                                      formats=[".avi", ".h264", "mp4"],
                                      recursive=False)

    timestamp_files = GetMatchedFilePaths(data_dir,
                                          # 2021_05_07_20_22_12_AutoCollect/port_0_camera_0_2021_5_7_19_36_1.txt
                                          pattern, [".txt"],
                                          recursive=False)
    hmi_files = GetMatchedFilePaths(data_dir,
                                    "@*", [".hmi"],
                                    recursive=False)

    screen_cast_path = os.path.join(data_dir, 'screen_cast')

    rec_files_ori = GetMatchedFilePaths(os.path.join(data_dir, 'sensors_record'),
                                        formats=[".rec"],
                                        recursive=False)
    if os.path.exists(screen_cast_path):

        screen_files = GetMatchedFilePaths(screen_cast_path,
                                           formats=[".mp4"],
                                           recursive=False)

        screen_txts = GetMatchedFilePaths(screen_cast_path,
                                          formats=[".txt"],
                                          recursive=False)
    dpc_files = GetMatchedFilePaths(data_dir,
                                    formats=[".bag"],
                                    recursive=False)

    for video_file in video_files:
        print(
            " ---------- {}".format(video_file))  # 2021_05_07_20_22_12_AutoCollect/port_0_camera_0_2021_5_7_19_36_1.avi

    for hmi_file in hmi_files:
        print(" ---------- {}".format(hmi_file))  # did not find hmi file

    for timestamp_file in timestamp_files:
        print(" ---------- {}".format(timestamp_file))

    rec_files = copy.deepcopy(rec_files_ori)

    for rec_file in rec_files_ori:
        print(" ---------- {}".format(rec_file))
        try:
            if os.path.exists(rec_file) and os.path.getsize(rec_file) == 0:
                os.remove(rec_file)
                rec_files.remove(rec_file)
        except:
            print(getTime() + "\033[1;31m [ERROR]\033[0m move 0-size rec failed ")

    for dpc_file in dpc_files:
        print(" ---------- {}".format(dpc_file))

    # Cutting of Recs files
    pool1 = multiprocessing.Pool(processes=12)
    pool1.apply_async(CutRecs, args=(rec_files, segment_list))
    pool1.close()
    pool1.join()

    # Cutting of Recs files
    pool2 = multiprocessing.Pool(processes=12)
    pool2.apply_async(CutDpcs, args=(dpc_files, segment_list))
    pool2.close()
    pool2.join()

    # CopyConfigCacheAndLogs(data_dir, segment_list)
    pool3 = multiprocessing.Pool(processes=12)
    pool3.apply_async(CopyConfigCacheAndLogs, args=(data_dir, segment_list))
    pool3.close()
    pool3.join()

    if len(basler_video_file) > 0 and len(basler_txt_file) > 0:
        CutBasler(basler_video_file, basler_txt_file, segment_list)

    pool = multiprocessing.Pool(processes=12)
    if len(screen_files) > 0 and len(screen_txts) > 0:
        pool.apply_async(CutScreenCast, args=(screen_files, screen_txts, segment_list))
    pool.close()
    pool.join()

    pool = multiprocessing.Pool(processes=12)

    if len(hmi_files) > 0 and os.path.exists(hmi_files[0]):
        print(getTime() + "\033[1;32m [INFO]\033[0m Cutting HMI Video .........\n")
        pool.apply_async(CutHmiFile, args=(hmi_files[0], segment_list))
    pool.close()
    pool.join()

    adas_pipeline.adasMainProcess(data_dir, segment_list)



if __name__ == "__main__":
    # args = GetArguments()
    dpc_file = "/media/sensetime/FieldTest/data/12_ARH/2020_10_30_14_23_42_AutoCollect/dmppcl.bag"
    output_dir = "/media/sensetime/FieldTest/data/12_ARH/2020_10_30_14_23_42_AutoCollect/cache/"
    point_list = []
    file = '/home/trajic/PycharmProjects/pythonProject4/timestamp_20210507213152.bin'
    new_bin = TimeReader(file)
    bin_files = new_bin.get_time_list()

    begin_secs = 1604037382
    end_secs = 1604037422
    point_list.append({"begin_secs": begin_secs, "end_secs": end_secs, "output_dir": output_dir})
    timestamp_file = "/media/sensetime/FieldTest1/data/2020_11_20_15_21_53_AutoCollect/screen_cast/2020-11-20-14-50-51.txt"
    time_point = 1605855623000000
    front_duration = 14
    behind_duration = 5
