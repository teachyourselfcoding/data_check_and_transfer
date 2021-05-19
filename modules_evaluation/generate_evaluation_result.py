# coding=utf-8

import os
import json
import requests
import subprocess, threading
from tools.read_and_write_json import loadTag,saveTag
scripts_path = os.getcwd()


class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):
        def target():
            print ('Thread started')
            self.process = subprocess.Popen(self.cmd, shell=True)
            self.process.communicate()
            print ('Thread finished')

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print ('Terminating process')
            self.process.terminate()
            thread.join()
        print (self.process.returncode)


def generatePredictionEval(dir_path,config_,casetime,input_id):

    eval_script = ''.join(["cd ", config_["senseauto_path"],
                           " && python2 senseauto-prediction/prediction_sdk/evaluation/run_evaluation.py "])
    #output_path = dir_path.split('data')[0]+'data/'
    output_path = os.path.split(dir_path)[0]
    cmd = ''.join([eval_script,  dir_path,' ',output_path,' field_test ',str(casetime),' ',input_id])
    child = subprocess.Popen(cmd,shell=True)
    child.wait()

def generatePathPlanningEval(dir_path,config_):

    eval_script = ''.join(["cd ", config_["senseauto_path"]+'/senseauto-decision-planning/decision_planning_sdk/planning/scripts',
                           " && bash proto/generate_proto.sh "
                           " && python2 parse_planning_evaluation.py "])
    output_path = os.path.join(dir_path,'logs/pp_eval')
    cmd = ''.join([eval_script, ' -s ', dir_path,' -o ',output_path])
    print(cmd)
    child = subprocess.Popen(cmd,shell=True)
    child.wait()


def generateLocalizationEval(dir_path,config_):
    eval_script = ''.join([config_["senseauto_path"],"senseauto-localization/localization_sdk/scripts/local_evaluation/eval_localization.sh "])
    cmd = ''.join([eval_script,  dir_path])
    command = Command(cmd)
    command.run(timeout=300)


def generateControlEval(dir_path,config_):
    python_path = "python3 "
    eval_script = ''.join([config_["senseauto_path"],"senseauto-control/control_sdk/scripts/control_evaluation/src/plot_analysis.py o "])
    cmd = ''.join([python_path, eval_script,  dir_path])
    command = Command(cmd)
    command.run(timeout=300)


# def generateTprofileEval(dir_path,config_):
#     eval_script = ''.join([config_["senseauto_path"],"system/scripts/tprofiler/resolve_everything.bash "])
#     output_path = os.path.join(dir_path,"tprofile_result/")
#     cmd = ''.join([eval_script, dir_path,' ',output_path,' >/dev/null 2>&1'])
#     print "\n\033[1;32m [INFO]\033[0m tprofile processing ...."
#
#     command = Command(cmd)
#     command.run(timeout=900)
#     print "\033[1;32m [INFO]\033[0m tprofile sucessfully\n"

def generateTprofileEval(dir_path,config_):
    print ("\n\033[1;32m [INFO]\033[0m tprofile processing ....")
    tprofile_path = os.path.join(scripts_path,'tprof_eval/tprofile_main_process.py')
    cmd = ''.join([tprofile_path,' ',dir_path,' ',os.path.join(dir_path, 'tprofile_result')])
    command = Command(cmd)
    command.run(timeout=1800)
    print ("\033[1;32m [INFO]\033[0m tprofile sucessfully\n")

def generateAdasEval(dir_path,config_):
    python_path = "python3 "
    eval_script = "system/scripts/auto_evaluation_repo/perception/scripts/adas_eval_bag_pc.py "
    output_path = os.path.join(dir_path,"logs/adas_online_eval/")

    cmd = "cd {} && {} {} --source {} --result {} --config {}  >/dev/null 2>&1".format(
        config_["senseauto_path"],
        python_path,
        eval_script,
        dir_path,
        output_path,
        "fieldtest")
    command=Command(cmd)
    command.run(timeout=300)
    print ("\n\033[1;32m [INFO]\033[0m adas eval  processing ....")


def getLocalEvalResult(dir_name):
    eval_tag_path = os.path.join(dir_name,'logs/localization_eval/')
    local_tag=loadTag(eval_tag_path,'evaluation_result.json')
    if local_tag is None:
        return {}
    eval_tag=local_tag.get("Tags")
    if eval_tag is None or len(eval_tag) < 1:
        return None
    for case_tag in eval_tag:

        if not "labels" in case_tag.keys():
            case_tag["labels"]=[]
        case_tag["labels"].append(case_tag["tag_en"])
        case_tag["data_type"] = "eval"
    return eval_tag

def getControlEvalResult(dir_name):
    eval_tag_path = os.path.join(dir_name,'logs/control_eval/')
    eval_tag = loadTag(eval_tag_path,'control_eval_results.json')
    if eval_tag is None:
        return {}
    eval_tag=eval_tag.get("Tag")
    if len(eval_tag) < 1:
        return None
    for case_tag in eval_tag:
        if not "labels" in case_tag.keys():
            case_tag["labels"]=[]
        case_tag["labels"].append(case_tag["tag_en"])
        case_tag["data_type"] = "eval"
    return eval_tag


def TransferPost(data_tag):
    "post the data tag to senseFT"
    curl = \
        'https://fieldtest.sensetime.com/production_line/upload'
    post_result = requests.post(curl, data=json.dumps(data_tag))
    print ("\n \033[1;32m [INFO]\033[0m ", post_result.text)
    # if post_result.text != u'{"result":"true"}':
    #     logger(2, "Uploaded dir:" + data_tag["data_link"], LOG_FILE="upload_list/post_failed_file.log")


if __name__ =="__main__":
    dir_path='/media/sensetime/FieldTest1/data/2020_05_14_CN-016/2020_05_14_13_47_55_AutoCollect/'
    case_tag=getLocalEvalResult(dir_path)
    print(case_tag)
    saveTag(dir_path,case_tag,'case-eval.json')