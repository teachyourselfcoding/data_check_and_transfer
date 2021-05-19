import os
import sys
import json
from awscli.clidriver import create_clidriver
from brake_case_tagging import BrakeCaseTagging
from tools.read_and_write_json import loadTag,saveTag

upload_recursive = " --recursive --endpoint-url="
end_point_30 = "http://10.5.41.189:9090"
end_point_40 = "http://10.5.41.234:80"
end_point = end_point_40
case_tagging =  BrakeCaseTagging()

AWS_DRIVER = create_clidriver()
def getAllDataDir(input_data_path):
    "get all dir in data"
    file_list =[]
    for file in os.listdir(input_data_path):
        dir_file = os.path.join(input_data_path, file)
        if os.path.isdir(dir_file):
            h = os.path.split(dir_file)
            file_list.append(h[1])
    return file_list


def CutSimulatorScenario(data_dir, seg_point):
    '''
    input:
        rec_file:str
        point_list:[{"time_point":121545, "front_duration":15,"behind_duration":5,"output_dir":/path/to/output}]
    '''
    try:
        if os.path.isfile(
                "/home/sensetime/ws/repo_pro/senseauto/build/modules/simulator/tools/scenario_log_tools/scenario_log_razor"
        ):
            razor = "/home/sensetime/ws/repo_pro/senseauto/build/modules/simulator/tools/scenario_log_tools/scenario_log_razor"
        elif os.path.isfile(

                "/tools/simulator_scenario_log_razor/simulator_scenario_log_razor"
        ):
            razor = "/tools/simulator_scenario_log_razor/simulator_scenario_log_razor"

        else:
            print("cannot find the simulator_scenario_log_razor, exit")

        # for seg_point in point_list:
        time_point=seg_point["time_point"]
        front_duration=seg_point["front_duration"]
        behind_duration=seg_point["behind_duration"]
        output_dir=seg_point["output_dir"]
        razor_cmd = "{} 1 {} {} {} {} {}".format(
            razor,
            data_dir + "/simulator_scenario/simulator_scenario_log.bin", output_dir + "/simulator_scenario",
            str(int(time_point // 1000000)), str(front_duration), str(behind_duration))
        print(razor_cmd)
        os.system(razor_cmd)
    except Exception as e:
         print("simulator_log error")



def main(dir_path):
    data_tag =  loadTag(dir_path)

    upload_path  =  data_tag["data_link"]
    record_tag = data_tag["origin_record_tag"][0]
    seg_point={}
    seg_point["time_point"] = record_tag["start"]*1000
    if "end" in record_tag:
        seg_point["front_duration"] =  2
        seg_point["behind_duration"] = (record_tag["end"] - record_tag["start"])/1000
    else:
        seg_point["front_duration"] = 25
        seg_point["behind_duration"] = 15
    seg_point["output_dir"] = dir_path
    #CutSimulatorScenario(dir_path,seg_point)
    if "end" in record_tag.keys():
        input_timestamp = (record_tag["start"] + record_tag["end"]) / 2000
    else:
        input_timestamp = record_tag["start"] / 1000

    module_name = record_tag["tag_en"]
    if module_name == "false_brake" or module_name == "Emergency_brake" or module_name == "sharp_slowdown":

        tagging_module = 2
    elif module_name == "take_over":
        tagging_module = 3
    else:
        tagging_module = 1

    tagging_tag = {"input_dir": dir_path+'/',
                  "module_name": record_tag["tag_en"],
                  "input_timestamp": input_timestamp,
                  "tagging_module":tagging_module}
    try:
        os.makedirs(dir_path+'/screen_cast')
    except Exception as e:
        print(111)
    case_tagging.main(download_path,tagging_tag)

    renameCaseTaggingTag(dir_path+'/screen_cast/')
    data_upload(dir_path,upload_path,slice=True)


def renameCaseTaggingTag(case_output_path):
    "as the function name"
    case_finder = loadTag(case_output_path, 'case_finder.json')
    try:
        if case_finder == [] or case_finder is None:
            case_finder = {}
            saveTag(case_output_path, case_finder, 'case_finder.json')
            return
        if "obstacle_id" in case_finder[0] and case_finder[0]["obstacle_id"] == [""]:
            case_finder[0]["obstacle_id"] = []
        if "obstacle_id" in case_finder[0] and case_finder[0]["obstacle_id"] == ["0"]:
            case_finder[0]["obstacle_id"] = []
        if "ego_tags" in case_finder[0]:
            case_finder[0]["ego_tags"] = refineTag(case_finder[0]["ego_tags"])
        if "obstacle_vehicle_tags" in case_finder[0]:
            case_finder[0]["obstacle_vehicle_tags"] = refineTag(case_finder[0]["obstacle_vehicle_tags"])
        if "obstacle_vru_tags" in case_finder[0]:
            case_finder[0]["obstacle_vru_tags"] = refineTag(case_finder[0]["obstacle_vru_tags"])
        saveTag(case_output_path, case_finder[0], 'case_finder.json')
    except Exception as e:
        print("222")


def refineTag(case_list):
    "fix the output of case finder tag"
    for i in range(len(case_list)):
        case_list[i] = case_list[i].split(":")[-1]
    return case_list



def data_upload(dir_path, dst_path, slice=False):
    'data_upload with aws'
    # dir_name = os.path.split(dir_path_without)[1]
    #
    # vehicle_id = tag_info["test_car_id"].replace("-", "")
    # data_month = tag_info["test_date"].rsplit("_", 1)[0]
    # try:
    #     if tag_info["topic_name"][0] == "repo_master":
    #         feature = False
    #     else:
    #         feature = True
    # except Exception as e:
    #     feature = False
    #
    # if feature:
    #     task_id = str(tag_info["task_id"]) + '/'
    # else:
    #     task_id = ''
    #
    # if slice:
    #     upload_path = ''.join([dir_path_without, "_slice/ "])
    #
    #     dst_path = ''.join([self.getDataCollectionDstLink(tag_info, data_month,slice=True),
    #                         tag_info["test_date"], '/',
    #                         vehicle_id, '/', task_id])
    #
    #     self.sliceDataCheck(dir_path_without + '_slice/')
    #
    # else:
    #     upload_path = ''.join([dir_path_without, '/ '])
    #
    #     tag_path = ''.join([self.getDataCollectionDstLink(tag_info,data_month, slice=False),
    #                         tag_info["test_date"], '/',
    #                         vehicle_id, '/',
    #                         task_id, dir_name])
    #     dst_path = ''.join([tag_path, '/'])
    #     tag_info["data_link"] = tag_path
    #     tag_info["data_type"] = "raw"
    #     tag_info['aws_endpoint'] = end_point
    #     self.saveTag(dir_path_without, tag_info, file_name='/data-tag.json')

    arg2 = ''.join(["s3 cp ", dir_path,'/screen_cast/ ', dst_path,'/screen_cast/ ', upload_recursive+end_point])
    print(" ==== ", arg2)

    upload_result = AWS_DRIVER.main(arg2.split())
    #self.TransferPost(tag_info)

    if upload_result == 0:
        print  " ---- Dir:\033[1;32m", dir_name + "\033[0m" + dir_name, "\033[0m has\033[1;32m uploaded successfully!\033[0m---\n"
    else:
        print " ---- Dir:\033[1;32m", dir_name + "\033[0m" + dir_name, "\033[0m \033[1;32m upload failed!\033[0m---\n"

def getAllDataDir(input_data_path):
    "get all dir in data"
    file_list=[]
    for file in os.listdir(input_data_path):
        dir_file = os.path.join(input_data_path, file)

        if (os.path.isdir(dir_file)):
            h = os.path.split(dir_file)
            file_list.append(h[1])
    return file_list

download_path = "/media/sensetime/FieldTest/data/case_finder_ARH/"
if __name__ == "__main__":
    data_path = "/media/sensetime/FieldTest/add_bin/download.sh"
    tag_path = "/media/sensetime/FieldTest/data/aa_ARH"

    dir_list = getAllDataDir(download_path)

    #for line in open(data_path, "r"):
    for dir_name in dir_list:


        #dir_name = line.split('/',-1)[-3]
        print(dir_name)
        #AWS_DRIVER.main(line.split())

        main(download_path+dir_name)