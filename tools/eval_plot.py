# coding=utf-8
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from read_and_write_json import loadTag,saveTag



def getAllDataDir(input_data_path):
    file_list = []
    for file in os.listdir(input_data_path):
        dir_file = os.path.join(input_data_path, file)
        if (os.path.isdir(dir_file)):
            h = os.path.split(dir_file)
            file_list.append(h[1])
    return file_list

def plotMap(plot_dict):
    fig = plt.figure()
    #ax1 = fig.add_axes([0.1, 0.45, 0.8, 0.5])

    for tag_en in plot_dict:
        if tag_en == "longitudinal_jump":
            y_label = [8, 8]
            color = "r"
            linestyle = "-"
            linewidth = 4.0
        elif tag_en == "lateral_jump":
            y_label = [7, 7]
            color = "y"
            linestyle = "-"
            linewidth = 4.0
        elif tag_en == "heading_jump":
            y_label = [6, 6]
            color = "g"
            linestyle = "-"
            linewidth = 4.0
        elif tag_en == "large_longitudinal_error":
            y_label = [5, 5]
            color = "c"
            linestyle = "-"
            linewidth = 4.0
        elif tag_en == "large_lateral_error":
            y_label = [4, 4]
            color = "b"
            linestyle = "-"
            linewidth = 4.0
        elif tag_en == "large_heading_error":
            y_label = [3, 3]
            color = "r"
            linestyle = "-"
            linewidth = 4.0

        for line in plot_dict[tag_en]:

            x_label = line
            plt.plot(x_label, y_label, color=color, linestyle=linestyle, marker="o", linewidth=linewidth)
    plt.ylim(0, 10)
    return plt

def judgeIfOverLap(x1,y1,x2,y2):
    minx =  min(x1,x2)
    maxy = max(y1,y2)
    if (maxy - minx) <  (y1-x1 + y2-x2):
        return True
    return False


def main():
    input_path = '/media/sensetime/FieldTest/data/local_eval/true_label'
    file_list = getAllDataDir(input_path)

    for file_name in file_list:
        eval_file_path = os.path.join(input_path, file_name, 'localization_eval')
        tag_file_path = os.path.join(input_path, file_name)
        eval_info = loadTag(eval_file_path, 'evaluation_result.json')
        tag_info = loadTag(tag_file_path, '12.json')

        for tag in tag_info["tags"]:
            print(file_name)
            save_dict = {}
            start = int(str(int(tag["start"]*1000))[0:11]) - 25
            if "end" in tag:
                end = int(str(int(tag["end"]*1000))[0:11]) + 25
            else:
                end = start + 50
            for eval in eval_info["Tags"]:
                eval_start = int(str(int(eval["start"]*1000))[0:11])
                eval_end = int(str(int(eval["end"]*1000))[0:11])
                if not judgeIfOverLap(start,end,eval_start,eval_end):
                    continue

                if eval["tag_en"] == "longitudinal_jump":
                    if not eval["tag_en"] in save_dict:
                        save_dict[eval["tag_en"]] = eval["max_longitudinal_jump(m/s)"]
                    else:
                        if save_dict[eval["tag_en"]] < eval["max_longitudinal_jump(m/s)"]:
                            save_dict[eval["tag_en"]] = eval["max_longitudinal_jump(m/s)"]
                elif eval["tag_en"] == "lateral_jump":
                    if not eval["tag_en"] in save_dict:
                        save_dict[eval["tag_en"]] = eval["max_lateral_jump(m/s)"]
                    else:
                        if save_dict[eval["tag_en"]] < eval["max_lateral_jump(m/s)"]:
                            save_dict[eval["tag_en"]] = eval["max_lateral_jump(m/s)"]
                elif eval["tag_en"] == "heading_jump":
                    if not eval["tag_en"] in save_dict:
                        save_dict[eval["tag_en"]] = eval["max_heading_jump(deg/s)"]
                    else:
                        if save_dict[eval["tag_en"]] < eval["max_heading_jump(deg/s)"]:
                            save_dict[eval["tag_en"]] = eval["max_heading_jump(deg/s)"]
                elif eval["tag_en"] == "large_longitudinal_error":
                    if not eval["tag_en"] in save_dict:
                        save_dict[eval["tag_en"]] = eval["max_longitudinal_error(m)"]
                    else:
                        if save_dict[eval["tag_en"]] < eval["max_longitudinal_error(m)"]:
                            save_dict[eval["tag_en"]] = eval["max_longitudinal_error(m)"]
                elif eval["tag_en"] == "large_lateral_error":
                    if not eval["tag_en"] in save_dict:
                        save_dict[eval["tag_en"]] = eval["max_lateral_error(m)"]
                    else:
                        if save_dict[eval["tag_en"]] < eval["max_lateral_error(m)"]:
                            save_dict[eval["tag_en"]] = eval["max_lateral_error(m)"]
                elif eval["tag_en"] == "large_heading_error":
                    error_num = "max_heading_error(m)"
                    for key in eval.keys():
                        if key.split('(')[0] == "max_heading_error":
                            error_num =  key
                    if not eval["tag_en"] in save_dict:

                            save_dict[eval["tag_en"]] = eval[error_num]
                    else:
                        if save_dict[eval["tag_en"]] < eval[error_num]:
                            save_dict[eval["tag_en"]] = eval[error_num]
            saveTag(tag_file_path,save_dict,tag["start_format"].replace(':',"_")+'.json')

        plot_dict = {
            "longitudinal_jump": [],
            "lateral_jump": [],
            "heading_jump": [],
            "large_longitudinal_error": [],
            "large_lateral_error": [],
            "large_heading_error": [],
            "large_time_gap":[]
        }
        tag_file_path  = os.path.join(input_path,file_name,'localization_eval')
        eval_tag = loadTag(tag_file_path,'evaluation_result.json')
        if eval_tag is None:
            continue
        for tag in eval_tag["Tags"]:
            print(file_name)
            print(tag)
            st = int(str(int(tag["start"]*1000))[0:11]) - 1599000000
            ed = int(str(int(tag["end"]*1000))[0:11]) - 1599000000
            plot_dict[tag["tag_en"]].append([st,ed])
        plt = plotMap(plot_dict)
        plt.savefig(tag_file_path+"/tag_file.png", dpi=120)



if __name__ == '__main__':
    main()