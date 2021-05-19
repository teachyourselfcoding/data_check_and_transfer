# coding=UTF-8
import sys
import os
import numpy as np
import json

output = {}
details = {}

def load_log(log_folder_path, sensor_type, date_start, date_end, result):
    # check files
    folder_path = log_folder_path + sensor_type + "/"
    file_names = get_log_file_names(date_start, date_end)
    if file_names == -1:
        return

    # variable declare
    time_key = None
    check_times = 0
    positive_times = 0
    parser_enable = False
    positive_flg = False
    error_count = 0

    result[sensor_type] = {}
    for name in file_names:
        log_path = folder_path + name
        if os.path.exists(log_path) and os.access(log_path, os.R_OK):
            with open(log_path, "r") as f:
                lines = f.readlines()
                for line in lines:
                    line = line[:-1]
                    # data analysis
                    if "----" in line:
                        time_key = line.split("[")[1].split("]")[0].replace(" ","_")
                        if time_key.split("_")[0] < date_end and time_key.split("_")[0] > date_start:
                            result[sensor_type][str(time_key)] = []
                            check_times += 1
                            positive_flg = False
                            parser_enable = True
                            continue
                        else:
                            parser_enable = False
                            continue
                    if "--error--" in line and parser_enable:
                        error_count += 1
                        result[sensor_type][str(time_key)].append(line.replace(" ","_",1))
                        if positive_flg == False:
                            positive_times += 1
                            positive_flg = True
                        continue
                    if "--warning--" in line and parser_enable:
                        result[sensor_type][str(time_key)].append(line.replace(" ","_",1))
                        continue
                    if "--ok--" in line and parser_enable:
                        result[sensor_type][str(time_key)].append(line.replace(" ","_",1))
                        continue
        else:
            print("Cannot find or open log file: "+log_path+", skip.")
            continue
    return [check_times, positive_times, error_count]

def get_log_file_names(date_start, date_end):
    # date check
    if int(date_start[:4])<2000 or int(date_end[:4])<2000:
        print("Do you think we have autodrive data that year？")
    if int(date_start[5:7])<1 or int(date_start[5:7])>12 or int(date_end[5:7])<1 or int(date_end[5:7])>12:
        print("Do you mean the date on some extraterrestrial plants?")
        return -1

    # get names
    if date_start[0:7] == date_end[0:7]:
        file_names = [date_end[0:7] + ".log"]
    else:
        year_list = [year for year in np.arange(int(date_start[:4]),int(date_end[:4])+1)]
        if len(year_list) == 1:
            month_list = [("0"+str(mon))[-2:] for mon in np.arange(int(date_start[5:7]),int(date_end[5:7])+1)]
            file_names = [date_start[:5]+mon+".log" for mon in month_list]
        else:
            month_list = [("0" + str(mon))[-2:] for mon in np.arange(int(date_start[5:7]), 13)]
            file_names = [date_start[:5] + mon + ".log" for mon in month_list]
            for year in year_list[1:-1]:
                file_names += [str(year)+"-"+("0" + str(mon))[-2:]+".log" for mon in np.arange(1,13)]
            month_list = [("0" + str(mon))[-2:] for mon in np.arange(1,int(date_end[5:7])+1)]
            file_names += [date_end[:5] + mon + ".log" for mon in month_list]
    return file_names

def save_json(data,file_name):
    with open(file_name, "w") as f:
        json.dump(data, f)
    print(file_name+".json has been saved successfully.")


def logSummarizer(date_start,date_end,log_folder_path,hostname,output_file_name):
    output["date_start"] = date_start
    output["date_end"] = date_end
    output["over_view"] = {"check_times":{}, "positive_times":{}, "error_count":{}}
    output["details"] = {hostname:{}}
    ##
    # sensor_name = sensor_type
    for sensor_type in ["lidar", "camera", "novatel", "radar"]:
        [check_times, positive_times, error_count] = load_log(log_folder_path, sensor_type, date_start, date_end,
                                                              output["details"][hostname])
        output["over_view"]["check_times"][sensor_type] = check_times
        output["over_view"]["positive_times"][sensor_type] = positive_times
        output["over_view"]["error_count"][sensor_type] = error_count

    save_json(output, output_file_name)

# if __name__ == "__main__":
#     # read val
#     # date_start = sys.argv[1]
#     # date_end = sys.argv[2]
#     # log_folder_path = sys.argv[3]
#     # hostname = sys.argv[4]
#     # output_file_name =  sys.argv[5]
#     # # initiate
#     main()
