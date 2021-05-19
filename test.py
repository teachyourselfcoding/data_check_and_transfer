# # # # # # # coding=utf-8
# # # # # # # # log the transferred file path
# # # # # # # import datetime
# # # # # # # import os
# # # # # # #
# # # # # # # def logger(level, str,LOG_FILE = 'upload_list/fieldtest_upload_list.log'):
# # # # # # #
# # # # # # #     if not os.path.exists(LOG_FILE):
# # # # # # #         os.mknod(LOG_FILE)
# # # # # # #     try:
# # # # # # #         logFd = open(LOG_FILE, 'a')
# # # # # # #     except:
# # # # # # #         logFd = open(LOG_FILE, 'a')
# # # # # # #     logFd.write(
# # # # # # #         datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') + ": " + ("Writing " if level else "NOTICE ") + str)
# # # # # # #     logFd.write("\n")
# # # # # # #     logFd.close()
# # # # # # #
# # # # # # # if __name__ == "__main__":
# # # # # # #     try:
# # # # # # #         ir=[]
# # # # # # #         print(ir[0])
# # # # # # #     except Exception as e:
# # # # # # #         logger(1, str(e), LOG_FILE="upload_list/error.log")
# # # # # #
# # # # # #
# # # # # # # from multiprocessing import Pool
# # # # # # # import time
# # # # # # # def test(p):
# # # # # # #        print(p)
# # # # # # #        time.sleep(3)
# # # # # # # if __name__=="__main__":
# # # # # # #     pool = Pool(processes=2)
# # # # # # #     for i  in range(500):
# # # # # # #         '''
# # # # # # #          （1）循环遍历，将500个子进程添加到进程池（相对父进程会阻塞）\n'
# # # # # # #          （2）每次执行2个子进程，等一个子进程执行完后，立马启动新的子进程。（相对父进程不阻塞）\n'
# # # # # # #         '''
# # # # # # #         pool.apply_async(test, args=(i,))   #维持执行的进程总数为10，当一个进程执行完后启动一个新进程.
# # # # # # #     print('test')
# # # # # # #     pool.close()
# # # # # # #     pool.join()
# # # # # # # rec_file='/media/sensetime/FieldTest/data/2020_06_02_20_33_54_AutoCollect/sensors_record/nav.dump.rec'
# # # # # # #
# # # # # # # import struct
# # # # # # #
# # # # # # # rec_fd = open(rec_file, 'rb')
# # # # # # # for i in range(10):
# # # # # # #
# # # # # # #     byte = rec_fd.read(1)
# # # # # # #     k = struct.unpack("B", byte)[0]
# # # # # # #     print(rec_fd)
# # # # # # #     print(byte)
# # # # # # #     print(k)
# # # # # #
# # # # # # #
# # # # # #
# # # # # # import datetime
# # # # # # import json
# # # # # # import os
# # # # # # import queue
# # # # # #
# # # # # # # aa=datetime.datetime.now().strftime('%Y-%m-%d')
# # # # # # # print(aa)
# # # # # # # aa ='/media/sensetime/FieldTest1/data/2020_06_10_17_04_30_AutoCollect_slice/AP/abnormal_prediction_trajectory/2020_06_10_16_33_16'
# # # # # # #
# # # # # # # bb = os.path.split(aa)[0]
# # # # # # # print(bb)
# # # # # #
# # # # # # from multiprocessing import Process, Queue
# # # # # #
# # # # # # def a(upload_queue):
# # # # # #     for i in range(100):
# # # # # #         upload_queue.put(i)
# # # # # #         print("===",i)
# # # # # #
# # # # # # def b(upload_queue):
# # # # # #     while True:
# # # # # #         print(upload_queue.get())
# # # # # #
# # # # # # if __name__ == "__main__":
# # # # # #     upload_queue = Queue()
# # # # # #
# # # # # #     segment_process = Process(target=a, args=(upload_queue,))
# # # # # #
# # # # # #     upload_process = Process(target=b, args=(upload_queue,))
# # # # # #
# # # # # #     segment_process.start()
# # # # # #
# # # # # #
# # # # # #
# # # # # #     upload_process.start()
# # # # # #
# # # # # #     segment_process.join()
# # # # # #
# # # # # #     segment_process.terminate()
# # # # #
# # # # # test_date = '2020_06_03'.split('_',1)[1]
# # # # # print(test_date)
# # # #
# # # # import os
# # # # import datetime
# # # # import logging
# # # #
# # # #
# # # # def logger(level, str, LOG_FILE='upload_list/fieldtest_upload_list.log'):
# # # #     if not os.path.exists(LOG_FILE):
# # # #         os.mknod(LOG_FILE)
# # # #     try:
# # # #         logFd = open(LOG_FILE, 'a')
# # # #     except:
# # # #         logFd = open(LOG_FILE, 'a')
# # # #     logFd.write(
# # # #         datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') + ": " + ("Writing " if level else "NOTICE ") + str)
# # # #     logFd.write("\n")
# # # #     logFd.close()
# # # #
# # # #
# # # # if __name__ == '__main__':
# # # #     a = 1
# # # #     b = 0
# # # #     try:
# # # #         c = a / b
# # # #     except Exception as e:
# # # #         logger(1, str(), LOG_FILE="upload_list/error.log")
# # # #         logging.exception(e)
# # # #         print(str(e))
# # # # import os
# # # # if not os.path.exists('data_report1'):
# # # #     os.makedirs('data_report1')
# # #
# # # # print(not True)
# # #
# # # # import pickle
# # # # import json
# # # # dict1 = {27:'adfg'}
# # # # #print(pickle.dumps(dict1))
# # # #
# # # # import os
# # # # import sys
# # # # import json
# # # # # aws transfer tool
# # # # from awscli.clidriver import create_clidriver
# # # # AWS_DRIVER = create_clidriver()
# # # # import shutil
# # # #
# # # # upload_recursive = " --recursive --endpoint-url="
# # # # end_point_30 = "http://10.5.41.189:9090"
# # # # end_point_40 = "http://10.5.41.234:80"
# # # # end_point = end_point_40
# # # #
# # # # def getAllDataDir(input_data_path):
# # # #     "get all dir in data"
# # # #     file_list=[]
# # # #     for file in os.listdir(input_data_path):
# # # #         if cullArchiveDir(file):
# # # #             continue
# # # #         dir_file = os.path.join(input_data_path, file)
# # # #
# # # #         if (os.path.isdir(dir_file)):
# # # #             h = os.path.split(dir_file)
# # # #             file_list.append(h[1])
# # # #     return file_list
# # # #
# # # # def cullArchiveDir(file):
# # # #     '''
# # # #     cull the dir which is for data archive
# # # #     :param file:
# # # #     :return:
# # # #     '''
# # # #     try:
# # # #         archive = file.split('_', -1)[-1]
# # # #         if archive == 'ARH' or archive == 'slice':
# # # #             return True
# # # #     except Exception as e:
# # # #        print(1)
# # # #     return False
# # # #
# # # # def generateTprofileEval(dir_name):
# # # #     eval_script = "/home/sensetime/ws/repo_pro/senseauto/system/scripts/tprofiler/resolve_everything.bash "
# # # #     cmd = ''.join([eval_script, dir_name,' ',dir_name,'/tprofile_result'])
# # # #     os.system(cmd)
# # # #
# # # # def main(input_path):
# # # #     file_list =  getAllDataDir(input_path)
# # # #
# # # #     for dir_name in file_list:
# # # #         dir_path = input_path+dir_name
# # # #         print(dir_path)
# # # #         generateTprofileEval(dir_path)
# # # #         data_tag = loadTag(dir_path)
# # # #         print(data_tag["backup"][0])
# # # #         data_link =  data_tag["backup"][0]["data_tag"]["data_link"]
# # # #
# # # #         arg2 = ''.join(["s3 cp ", dir_path+'/tprofile_result/ ', data_link+'/tprofile_result/ ', upload_recursive + end_point])
# # # #         print(" ==== ", arg2)
# # # #
# # # #         AWS_DRIVER.main(arg2.split())
# # # #         archive_path = "/media/sensetime/FieldTest1/data/tprofile_ARH"
# # # #         shutil.move(dir_path, archive_path)
# # # #
# # # #
# # # # def loadTag(tag_file_path='', tag_file_name='/data-tag.json'):
# # # #     "read json"
# # # #     if not os.path.exists(tag_file_path + tag_file_name):
# # # #         return {}
# # # #     with open(tag_file_path + tag_file_name, 'r') as f:
# # # #         try:
# # # #             tag_data = json.load(f)
# # # #             return tag_data
# # # #         except ValueError:
# # # #             print(" ==== ", tag_file_path + tag_file_name,
# # # #                   "\033[1;31m is not valuable json bytes \033[0m!\n")
# # # #             return {}
# # # #
# # # #
# # # #
# # # # if __name__ == '__main__':
# # # #
# # # #     main("/media/sensetime/FieldTest1/data/")
# # #
# # # #print('data-tag(08-16-16-39).json'.split('(',-1)[1].split(')',-1)[0])
# # # # print("/media/sensetime/FieldTest1/data/2020_08_17_21_15_05_AutoCollect/".split('/', -1)[-2])
# # # # import os
# # # # import sys
# # # # import json
# # # # from awscli.clidriver import create_clidriver
# # # #
# # # # upload_recursive = " --recursive --endpoint-url="
# # # # end_point_30 = "http://10.5.41.189:9090"
# # # # end_point_40 = "http://10.5.41.234:80"
# # # # end_point = end_point_40
# # # #
# # # # AWS_DRIVER = create_clidriver()
# # # # def getAllDataDir(input_data_path):
# # # #     "get all dir in data"
# # # #     file_list =[]
# # # #     for file in os.listdir(input_data_path):
# # # #         dir_file = os.path.join(input_data_path, file)
# # # #         if os.path.isdir(dir_file):
# # # #             h = os.path.split(dir_file)
# # # #             file_list.append(h[1])
# # # #     return file_list
# # # #
# # # # def loadTag(tag_file_path='', tag_file_name='/data-tag.json'):
# # # #     "read json"
# # # #     if not os.path.exists(tag_file_path + tag_file_name):
# # # #         return {}
# # # #     with open(tag_file_path + tag_file_name, 'r') as f:
# # # #         try:
# # # #             tag_data = json.load(f)
# # # #             return tag_data
# # # #         except ValueError:
# # # #             print(" ==== ", tag_file_path + tag_file_name,
# # # #                   "\033[1;31m is not valuable json bytes \033[0m!\n")
# # # #             return {}
# # # #
# # # #
# # # # def saveTag(tag_file_path, tag_data, file_name='data-tag.json'):
# # # #     "write json"
# # # #     tag_path_name = tag_file_path + file_name
# # # #     if not os.path.exists(tag_path_name):
# # # #         os.mknod(tag_path_name)
# # # #     with open(tag_path_name, 'w') as fw:
# # # #         json.dump(tag_data, fw, indent=4)
# # # #
# # # #
# # # # def CutSimulatorScenario(data_dir, seg_point):
# # # #     '''
# # # #     input:
# # # #         rec_file:str
# # # #         point_list:[{"time_point":121545, "front_duration":15,"behind_duration":5,"output_dir":/path/to/output}]
# # # #     '''
# # # #     try:
# # # #         if os.path.isfile(
# # # #                 "/home/sensetime/ws/repo_pro/senseauto/build/modules/simulator/tools/scenario_log_tools/scenario_log_razor"
# # # #         ):
# # # #             razor = "/home/sensetime/ws/repo_pro/senseauto/build/modules/simulator/tools/scenario_log_tools/scenario_log_razor"
# # # #         elif os.path.isfile(
# # # #
# # # #                 "/tools/simulator_scenario_log_razor/simulator_scenario_log_razor"
# # # #         ):
# # # #             razor = "/tools/simulator_scenario_log_razor/simulator_scenario_log_razor"
# # # #
# # # #         else:
# # # #             print("cannot find the simulator_scenario_log_razor, exit")
# # # #
# # # #         # for seg_point in point_list:
# # # #         time_point=seg_point["time_point"]
# # # #         front_duration=seg_point["front_duration"]
# # # #         behind_duration=seg_point["behind_duration"]
# # # #         output_dir=seg_point["output_dir"]
# # # #         razor_cmd = "{} 1 {} {} {} {} {}".format(
# # # #             razor,
# # # #             data_dir + "/simulator_scenario/simulator_scenario_log.bin", output_dir + "/simulator_scenario",
# # # #             str(int(time_point // 1000000)), str(front_duration), str(behind_duration))
# # # #         print(razor_cmd)
# # # #         os.system(razor_cmd)
# # # #     except Exception as e:
# # # #          print("simulator_log error")
# # # #
# # # #
# # # #
# # # # def main(dir_path):
# # # #     data_tag =  loadTag(dir_path)
# # # #     upload_path  =  data_tag["data_link"]
# # # #     record_tag = data_tag["origin_record_tag"][0]
# # # #     seg_point={}
# # # #     seg_point["time_point"] = record_tag["start"]*1000
# # # #     if "end" in record_tag:
# # # #         seg_point["front_duration"] =  2
# # # #         seg_point["behind_duration"] = (record_tag["end"] - record_tag["start"])/1000
# # # #     else:
# # # #         seg_point["front_duration"] = 25
# # # #         seg_point["behind_duration"] = 15
# # # #     seg_point["output_dir"] = dir_path
# # # #     CutSimulatorScenario(dir_path,seg_point)
# # # #
# # # #     data_upload(dir_path,upload_path,slice=True)
# # # #
# # # #
# # # #
# # # #
# # # #
# # # # def data_upload(dir_path, dst_path, slice=False):
# # # #     'data_upload with aws'
# # # #     # dir_name = os.path.split(dir_path_without)[1]
# # # #     #
# # # #     # vehicle_id = tag_info["test_car_id"].replace("-", "")
# # # #     # data_month = tag_info["test_date"].rsplit("_", 1)[0]
# # # #     # try:
# # # #     #     if tag_info["topic_name"][0] == "repo_master":
# # # #     #         feature = False
# # # #     #     else:
# # # #     #         feature = True
# # # #     # except Exception as e:
# # # #     #     feature = False
# # # #     #
# # # #     # if feature:
# # # #     #     task_id = str(tag_info["task_id"]) + '/'
# # # #     # else:
# # # #     #     task_id = ''
# # # #     #
# # # #     # if slice:
# # # #     #     upload_path = ''.join([dir_path_without, "_slice/ "])
# # # #     #
# # # #     #     dst_path = ''.join([self.getDataCollectionDstLink(tag_info, data_month,slice=True),
# # # #     #                         tag_info["test_date"], '/',
# # # #     #                         vehicle_id, '/', task_id])
# # # #     #
# # # #     #     self.sliceDataCheck(dir_path_without + '_slice/')
# # # #     #
# # # #     # else:
# # # #     #     upload_path = ''.join([dir_path_without, '/ '])
# # # #     #
# # # #     #     tag_path = ''.join([self.getDataCollectionDstLink(tag_info,data_month, slice=False),
# # # #     #                         tag_info["test_date"], '/',
# # # #     #                         vehicle_id, '/',
# # # #     #                         task_id, dir_name])
# # # #     #     dst_path = ''.join([tag_path, '/'])
# # # #     #     tag_info["data_link"] = tag_path
# # # #     #     tag_info["data_type"] = "raw"
# # # #     #     tag_info['aws_endpoint'] = end_point
# # # #     #     self.saveTag(dir_path_without, tag_info, file_name='/data-tag.json')
# # # #
# # # #     arg2 = ''.join(["s3 cp ", dir_path,' ', dst_path,' ', upload_recursive+end_point])
# # # #     print(" ==== ", arg2)
# # # #
# # # #     upload_result = AWS_DRIVER.main(arg2.split())
# # # #     #self.TransferPost(tag_info)
# # # #
# # # #     if upload_result == 0:
# # # #         print  " ---- Dir:\033[1;32m", dir_name + "\033[0m" + dir_name, "\033[0m has\033[1;32m uploaded successfully!\033[0m---\n"
# # # #     else:
# # # #         print " ---- Dir:\033[1;32m", dir_name + "\033[0m" + dir_name, "\033[0m \033[1;32m upload failed!\033[0m---\n"
# # # #
# # # #
# # # #
# # # # if __name__ == "__main__":
# # # #     data_path = "/media/sensetime/FieldTest/data/log_ARH/download.sh"
# # # #     tag_path = "/media/sensetime/FieldTest/data/log_ARH/1.sh"
# # # #     download_path = "/media/sensetime/FieldTest/data/log_ARH/"
# # # #
# # # #     for line in open(data_path, "r"):
# # # #
# # # #
# # # #         dir_name = line.split('/',-1)[-3]
# # # #         print(dir_name)
# # # #         AWS_DRIVER.main(line.split())
# # # #         main(download_path+dir_name)
# # # # import os
# # # # print(os.path.exists('ui'))
# # # # def judgeIdValue(s):
# # # #     try:
# # # #         float(s)
# # # #         if (float(s)>0):
# # # #             return True
# # # #     except ValueError:
# # # #         pass
# # # #
# # # #     try:
# # # #         import unicodedata
# # # #         unicodedata.numeric(s)
# # # #         if (unicodedata.numeric(s)>0):
# # # #             return True
# # # #     except (TypeError, ValueError):
# # # #         pass
# # # #
# # # #     return False
# # # #
# # # # print (judgeIdValue("11"))
# # #
# # # #
# # # # def filterObjectId(object_id_list):
# # # #     max_distribution = 0
# # # #     id_dict = {}
# # # #     filted_list = []
# # # #     for objec_id in object_id_list:
# # # #         if not objec_id in id_dict.keys():
# # # #             id_dict[objec_id] = 0
# # # #         id_dict[objec_id] += 1
# # # #     print(id_dict)
# # # #
# # # #     for object in id_dict:
# # # #         if id_dict[object] > max_distribution:
# # # #             max_distribution = id_dict[object]
# # # #     for object in id_dict:
# # # #         if id_dict[object] == max_distribution:
# # # #             filted_list.append(object)
# # # #     return filted_list
# # # #
# # # #
# # # # print(filterObjectId([122,1222,122,2222,2222,2222,3,4,5,633,633,633]))
# # #
# # # # import time
# # # #
# # # #
# # # # def bjTimeToUnix(bj_time, nsec, input_year_month_day):
# # # #     ts = time.strptime(input_year_month_day + ' ' + bj_time, "%Y-%m-%d %H:%M:%S")
# # # #     print(float(nsec) / 1000.0)
# # # #     return float(time.mktime(ts) + float(nsec) / 1000.0)
# # # #
# # # # print bjTimeToUnix("13:53:47",1000,"2020-08-25")
# # # # print 1597219945.06 < 1597222172.5159123
# # # # import os
# # # # dir_path = "/media/sensetime/FieldTest/data/pp_brake"
# # # # print(dir_path.split('data',-1)[0]+'data/')
# # # #
# # # # print(0*43200)
# # #
# # # # import hashlib
# # # # import base64
# # # #
# # # # fd=open("/home/sensetime/Documents/20200909204558fhhai.png","r")
# # # # fcont=fd.read()
# # # # fmd5=hashlib.md5(fcont)
# # # # print fmd5.hexdigest()#get 32 value
# # # #
# # # #
# # # # image_data = fd.read()
# # # # base64_data = base64.b64encode(image_data)  # base64编码
# # # # print(base64_data)
# # # # print(type(base64_data))
# # # #
# # # # import requests
# # # # import json
# # # # curl = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=8610da8c-ef89-4969-b62e-d7236e956240'
# # # # #
# # # #
# # # #
# # # # def getByte(path):
# # # #     with open(path, 'rb') as f:
# # # #         img_byte = base64.b64encode(f.read())
# # # #     img_str = img_byte.decode('ascii')
# # # #     return img_str
# # # #
# # # #
# # # # img_str = getByte("/home/sensetime/Documents/20200909204558fhhai.png")
# # # #
# # # # data_tag = {
# # # #     "msgtype": "news",
# # # #     "news": {
# # # #        "articles" : [
# # # #            {
# # # #                "title" : "恭喜大总管",
# # # #                "description" : "恭喜大总管",
# # # #                "url" : "fieldtest.sensetime.com",
# # # #                "picurl" : ''
# # # #            }
# # # #         ]
# # # #     }
# # # # }
# # # #
# # # # # data_tag = {
# # # # #     "msgtype": "image",
# # # # #     "image": {
# # # # #         "base64": base64_data,
# # # # #         "md5": fmd5.hexdigest()
# # # # #     }
# # # # # }
# # # # post_result = requests.post(curl, data=json.dumps(data_tag))
# # # # print(post_result)
# # # #
# # # # from wxpy import *
# # # # bot = Bot()
# # # #
# # # # # 机器人账号自身
# # # # myself = bot.self
# # # #
# # # # # 向文件传输助手发送消息
# # # # bot.file_helper.send('Hello from wxpy!')
# # # # a = [1,2,3]
# # # # b = [4, 5,6,1]
# # # # a.extend(b)
# # # # a = list(set(a))
# # # # print(a)
# # # # import copy
# # # # import os
# # # # print(os.path.split(os.path.realpath(__file__))[0])
# # # #
# # # #
# # # # def mergeAdjacentCase(case_list):
# # # #     if len(case_list) < 1:
# # # #         return
# # # #     for i in range(len(case_list) - 1):
# # # #         if i > len(case_list) - 2:
# # # #             break
# # # #         merge, merged_case = checkCaseOverLap(case_list[i], case_list[i + 1])
# # # #         if merge:
# # # #             case_list[i] = merged_case
# # # #             case_list.pop(i + 1)
# # # #             i -= 1
# # # #
# # # #
# # # #
# # # # def checkCaseOverLap(case_a, case_b):
# # # #     if not "start" in case_a.keys():
# # # #         return False, {}
# # # #     if not "start" in case_a.keys():
# # # #         return False, {}
# # # #     if case_b["start"] - case_a["end"] < 10000:
# # # #         merged_case = copy.deepcopy(case_a)
# # # #         merged_case["end"] = case_b["end"]
# # # #         merged_case["end_format"] = case_b["end_format"]
# # # #         merged_case["labels"].extend(case_b["labels"])
# # # #         merged_case["labels"] = list(set(merged_case["labels"]))
# # # #         merged_case["modules"].extend(case_b["modules"])
# # # #         merged_case["modules"] = list(set(merged_case["modules"]))
# # # #         print(merged_case)
# # # #         return True, merged_case
# # # #
# # # # import json
# # # # def loadTag(tag_file_path='', tag_file_name='data-tag.json'):
# # # #     if not os.path.exists(tag_file_path + tag_file_name):
# # # #         return None
# # # #     with open(tag_file_path + tag_file_name, 'r') as f:
# # # #         try:
# # # #             tag_data = json.load(f)
# # # #             return tag_data
# # # #         except ValueError:
# # # #             print(" ==== ", tag_file_path + tag_file_name,
# # # #                   "\033[1;31m is not valuable json bytes \033[0m!\n")
# # # #             return None
# # # #
# # # # if __name__ == '__main__':
# # # #     case_list = loadTag("/home/sensetime/tmp/tprofile_case.json",'')
# # # # #     mergeAdjacentCase(case_list)
# # # # import time
# # # # def bjTimeToUnix( bj_date, bj_time):
# # # #     bj_time = bj_time.split('.', -1)[0]
# # # #
# # # #     print('2020' + bj_date + ' ' + bj_time)
# # # #     ts = time.strptime('2020' + bj_date + ' ' + bj_time, "%Y%m%d %H:%M:%S")
# # # #     return int(time.mktime(ts) * 1000)
# # # #
# # # # print(bjTimeToUnix('0904','12:54:18.345'))
# # #
# # # import os
# # # import json
# # # def loadTag(tag_file_path='', tag_file_name='data-tag.json'):
# # #     "read json"
# # #     if not os.path.exists(tag_file_path + tag_file_name):
# # #         return {}
# # #     with open(tag_file_path + tag_file_name, 'r') as f:
# # #         try:
# # #             tag_data = json.load(f)
# # #             return tag_data
# # #         except ValueError:
# # #             print(" ==== ", tag_file_path + tag_file_name,
# # #                   "\033[1;31m is not valuable json bytes \033[0m!\n")
# # #             return {}
# # #
# # #
# # #
# # # def getAllDataDir(input_data_path):
# # #     "get all dir in data"
# # #     file_list=[]
# # #     for file in os.listdir(input_data_path):
# # #         dir_file = os.path.join(input_data_path, file)
# # #
# # #         if (os.path.isdir(dir_file)):
# # #             h = os.path.split(dir_file)
# # #             file_list.append(h[1])
# # #     return file_list
# # #
# # # def saveTag(tag_file_path, tag_data, file_name='data-tag.json'):
# # #     "write json"
# # #     tag_path_name = tag_file_path + file_name
# # #     if not os.path.exists(tag_path_name):
# # #         os.mknod(tag_path_name)
# # #     with open(tag_path_name, 'w') as fw:
# # #         json.dump(tag_data, fw, indent=4)
# # #
# # # a = loadTag("/home/sensetime/ws/repo_pro/senseauto/system/config/lanelinemap/sh/latest",'/HDMap.json')
# # # saveTag("/home/sensetime/ws/",a,'hdmap.json')
# # # import os
# # # a,b = os.path.split('/home/ubuntu/python_coding/split_func')
# # # print(a,b)
# # #
# # # a = {
# # #   "false_detection": "sense",
# # #   "missed_detection": "sense",
# # #   "false_trffic_light": "PR",
# # #   "detect_position_deviation": "fusion",
# # #   "abnormal_prediction_trajectory": "AP",
# # #   "false_turn_signal": "DPC",
# # #
# # #
# # #   "drive_through_the_red_light": "DPC",
# # #   "Emergency_brake": "DPC",
# # #   "other_unreasonable_driving_behavior": "DPC",
# # #   "take_over": "DPC",
# # #   "no_waiting_area":"LMR",
# # #   "false_lane_line":"LMR"
# # # }
# # # # b= ["false_detection","no_waiting_area","bbb"]
# # # #
# # # # print(any(tag not in a for tag in b))
# # #
# # # # time_list = "2020_10_22_42_33"
# # # # clock_list = [43200,1440,60,1]
# # # #
# # # # a = (test_time[i] - int(tag_time[i])) for i, time in enumerate(clock_list)
# # # # print(a)
# # # # b = [111,333,4,5,5]
# # # #
# # # # c,d,e,f,g = b
# # # # print(c,d,e)
# # # import os
# # # # b = os.path.join('1243',"23423")
# # # # print(b)
# # # # print(os.path.basename(os.path.split('/meda/adsf/ad/adg/adgad/gadg/14.json')[0]))
# # # fea = True
# # # a = 123 if fea else 6
# # # print(a)
# #
# # # import json
# # # import os
# # # import subprocess
# # #
# # #
# # # def getAllDataDir(input_data_path):
# # #     "get all dir in data"
# # #     file_list = []
# # #     for file in os.listdir(input_data_path):
# # #         dir_file = os.path.join(input_data_path, file)
# # #
# # #         if (os.path.isdir(dir_file)):
# # #             h = os.path.split(dir_file)
# # #             file_list.append(h[1])
# # #     return file_list
# # #
# # #
# # # def GetMatchedFilePaths(data_dir,
# # #                         pattern="*",
# # #                         formats=[".h264"],
# # #                         recursive=False):
# # #     files = []
# # #     data_dir = os.path.normpath(os.path.abspath(data_dir))
# # #     import fnmatch
# # #     for f in os.listdir(data_dir):
# # #         current_path = os.path.join(os.path.normpath(data_dir), f)
# # #         if os.path.isdir(current_path) and recursive:
# # #             files += GetMatchedFilePaths(current_path, pattern, formats,
# # #                                          recursive)
# # #         elif fnmatch.fnmatch(f,
# # #                              pattern) and os.path.splitext(f)[-1] in formats:
# # #             files.append(current_path)
# # #     return files
# # #
# # #
# # # def autoModuleDsitrib(input_path):
# # #     print(input_path)
# # #     scripts = "case_tagging/auto_sub_module "
# # #     input_file = os.path.join(input_path, 'screen_cast/case_toss.json')
# # #     output_file = os.path.join(input_path, 'screen_cast/auto_module.json')
# # #     cmd = ''.join([scripts, input_file, ' ', output_file])
# # #     print(cmd)
# # #     child = subprocess.Popen(cmd, shell=True)
# # #     child.wait()
# # #
# # #
# # # def loadTag(tag_file_path='', tag_file_name='data-tag.json'):
# # #     '''
# # #     load json file
# # #     :param tag_file_path: input file path
# # #     :param tag_file_name: input file name
# # #     :return: json
# # #     '''
# # #     tag_file = os.path.abspath(os.path.join(tag_file_path, tag_file_name))
# # #     if not os.path.exists(tag_file):
# # #         return None
# # #     with open(tag_file, 'r') as f:
# # #         try:
# # #             tag_data = json.load(f)
# # #             return tag_data
# # #         except ValueError:
# # #             print " ==== ", tag_file, "\033[1;31m is not valuable json bytes \033[0m!\n"
# # #             return None
# # #
# # #
# # # def saveTag(tag_file_path, tag_data, file_name='data-tag.json'):
# # #     '''
# # #     save json file
# # #     :param tag_file_path: save path
# # #     :param tag_data: to be saved json
# # #     :param file_name: to be savad file name
# # #     '''
# # #     tag_file = os.path.abspath(os.path.join(tag_file_path, file_name))
# # #     if not os.path.exists(tag_file_path):
# # #         os.mkdir(tag_file_path)
# # #     if not os.path.exists(tag_file):
# # #         os.mknod(tag_file)
# # #     with open(tag_file, 'w') as fw:
# # #         json.dump(tag_data, fw, indent=4)
# # #
# # # auto_module_ = {
# # #   "supply_label_contrast":{
# # #     "红灯": "traffic_light_problem",
# # #     "黄灯": "traffic_light_problem",
# # #     "绿灯": "traffic_light_problem",
# # #     "黄闪": "traffic_light_problem",
# # #     "绿闪": "traffic_light_problem",
# # #     "黑灯": "traffic_light_problem",
# # #     "误检": "object_problem",
# # #     "漏检": "object_problem",
# # #     "物体尺寸异常": "object_problem"
# # #   },
# # #   "label_to_number": {
# # #     "红灯": 3,
# # #     "黄灯": 2,
# # #     "绿灯": 1,
# # #     "黄闪": 5,
# # #     "绿闪": 4,
# # #     "黑灯": 6,
# # #     "误检": 0,
# # #     "漏检": 1,
# # #     "物体尺寸异常": 2
# # #   }
# # # }
# # #
# # #
# # # if __name__ == '__main__':
# # #     input_path = '/home/sensetime/Codes/config'
# # #     dir_list = getAllDataDir(input_path)
# # #     tag_list =  GetMatchedFilePaths(input_path,'*',['.json'])
# # #     for tag_file  in tag_list:
# # #         # data_tag =  loadTag(os.path.join(input_path,dir_name))
# # #         # record_tag = data_tag["origin_record_tag"][0]
# # #         #
# # #         # case_toss_file = os.path.join(input_path, dir_name,'screen_cast/case_toss.json')
# # #         case_toss_tag = loadTag(tag_file, '')
# # #         case_toss_tag["Attributes"] = {}
# # #         case_toss_tag["Object_check"] = {}
# # #         case_toss_tag["Attributes"]["object_problem"] = 0
# # #         case_toss_tag["Attributes"]["traffic_light_problem"] = 0
# # #         case_toss_tag["Object_check"]["object_pos"] = 0
# # #         case_toss_tag["Pr_check"] = case_toss_tag["pr_data"]
# # #         # if record_tag['labels'] != []:
# # #         #     for label in record_tag['labels']:
# # #         #         if label in auto_module_["supply_label_contrast"]:
# # #         #             labeled_module = auto_module_["supply_label_contrast"][label]
# # #         #             case_toss_tag["Attributes"][labeled_module] = 1
# # #         #             case_toss_tag["Pr_check"] = case_toss_tag["pr_data"]
# # #         #             if labeled_module == "traffic_light_problem":
# # #         #                 case_toss_tag["Pr_check"]["true_tl_label"] = auto_module_["label_to_number"][label]
# # #         saveTag(tag_file, case_toss_tag, '')
# # #
# # #         #autoModuleDsitrib(os.path.join(input_path,dir_name))
# #
# # # import os
# # # os.system("echo nvidia|sudo fdisk -l")
# # # from tools.read_and_write_json import loadTag,saveTag
# # #
# # # def addWhetherInfo(path):
# # #     case_toss = loadTag(path, 'case_toss.json')
# # #     if case_toss is None:
# # #         return
# # #     whether_tag = 0
# # #     for tag in ["阳光直射",'凌晨']:
# # #         if tag not in ["阳光直射", "阳光背射", "凌晨", "黄昏", "夜晚有路灯", "夜晚无路灯"]:
# # #             continue
# # #         if tag == "阳光直射" or tag == "阳光背射":
# # #             whether_tag = 1
# # #         elif tag == "黄昏":
# # #             whether_tag = 2
# # #         else:
# # #             whether_tag = 3
# # #     case_toss["Global_label"] = {}
# # #     case_toss["Global_label"]["day_time"] = whether_tag
# # #     saveTag(path, case_toss, 'case_toss.json')
# # #
# # # addWhetherInfo("/home/sensetime/tmp/screen_cast")
# # # from awscli.clidriver import create_clidriver
# # # AWS_DRIVER = create_clidriver()
# # # cmd = "s3 rm " \
# # #       "s3://sh40_fieldtest_master/2020_06/master/segment_data/2020_06_29/CN011/EVAL/" \
# # #       "large_longitudial_error/2020_06_29_18_01_45/ --recursive --exclude \'*\' " \
# # #       "--include \'logs/*\' --endpoint-url=http://10.5.41.234:80"
# # # print(cmd)
# # # print(cmd.split())
# # # AWS_DRIVER.main(cmd.split())
# # # line = "1, 4859347589347583"
# # # line = line.strip('\n').strip().split("? ")
# # # print(line)
# # # a = 1234567890
# # # b = 123
# # # c = a+ b*(1e-03)
# # # print(c)
# # # import time
# # #
# # # dt = "2016-05-05 20:28:54"
# # #
# # # #转换成时间数组
# # # timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
# # # #转换成时间戳
# # # timestamp = time.mktime(timeArray)
# # #
# # # print timestamp
# #
# # # coding=utf-8
# #
# # # import os
# # # import sys
# # # import json
# # # import rosbag
# # # sys.path.append("..")
# # # import pandas as pd
# # # from tools.read_and_write_json import loadTag,saveTag
# # # from modules_evaluation.generate_evaluation_result import generatePredictionEval
# # #
# # #
# # #
# # # def main(dir_path, input_time):
# # #     bad_case_path = os.path.join(dir_path,'prediction_evaluation/result')
# # #     pred_bad_case_json = loadTag(bad_case_path,'bad_cases.json')
# # #     if pred_bad_case_json is None:
# # #         return
# # #     case_list = []
# # #
# # #     for case_time in pred_bad_case_json.keys():
# # #         if len(str(case_time)) > 13:
# # #             case_time = case_time[0:13]
# # #         case_time = int(case_time)
# # #         if (input_time - case_time) < 600 and (input_time - case_time) > 0:
# # #             case_list.append(pred_bad_case_json[str(case_time)])
# # #     saveTag(dir_path,case_list,'candidate_case.json')
# # #
# # #
# # # def getDataFromDpcbag(dpc_file, topic_names,record_timestamp):
# # #     print(dpc_file)
# # #     if not os.path.exists(dpc_file):
# # #         print('bag not found')
# # #         return
# # #
# # #     control_error_topic = topic_names[0]
# # #     bag = rosbag.bag.Bag(dpc_file)
# # #     timestamp = []
# # #     vehicle_acc_x = []
# # #     vehicle_acc_y = []
# # #     velocity_x = []
# # #     brake_fdbk = []
# # #     brake_cmd = []
# # #     position_x = []
# # #     position_y = []
# # #
# # #     #print ("\033[1;32m [INFO]\033[0m! parsing dmppcl bag .........\n")
# # #     for topic, msg, t in bag.read_messages(topics=control_error_topic):
# # #         time_sec =  int(msg.header.stamp.to_sec())
# # #
# # #         if time_sec > record_timestamp -4 and time_sec < record_timestamp+1:
# # #             timestamp.append(msg.header.stamp.to_sec())
# # #             vehicle_acc_x.append(msg.vehicle_acc_x)
# # #             vehicle_acc_y.append(msg.vehicle_acc_y)
# # #             velocity_x.append(msg.vehicle_vel_x)
# # #             brake_fdbk.append(msg.vehicle_brake)
# # #             brake_cmd.append(msg.brake_cmd)
# # #             position_x.append(msg.utm_pos_x)
# # #             position_y.append(msg.utm_pos_y)
# # #     bag.close()
# # #
# # #     dict_all = {
# # #         'brake_fdbk': brake_fdbk,
# # #         'vehicle_acc_x': vehicle_acc_x,
# # #         'vehicle_acc_y': vehicle_acc_y,
# # #         'velocity_x': velocity_x,
# # #         'brake_cmd': brake_cmd,
# # #         'position_x': position_x,
# # #         'position_y': position_y,
# # #     }
# # #
# # #     keyname = 'timestamp'
# # #     d = {'index_timestamp': range(0, len(timestamp)), keyname: timestamp}
# # #     df = pd.DataFrame(data=d)
# # #     pandas_all = df
# # #     keylist = list(dict_all.keys())
# # #     for keyname in keylist:
# # #         if keyname == 'timestamp':
# # #             continue
# # #         else:
# # #             d = {keyname: dict_all[keyname]}
# # #             df = pd.DataFrame(data=d)
# # #             pandas_all = pd.concat([pandas_all, df], axis=1)
# # #
# # #     pandas_all_filtered = pandas_all.dropna(axis=1, how='all')
# # #
# # #     # print(pandas_all_filtered)
# # #     return pandas_all_filtered
# # #
# # # def parseBrakeTimestampFromBag(bag_data):
# # #     ego_label={}
# # #     if (bag_data.empty):
# # #         print('empty bag data found')
# # #         return
# # #     max_timestamp = bag_data['timestamp'].loc[bag_data['brake_cmd'].argmax()]
# # #     # ego_car_label = utility.format_time_group(utility.combine_time(
# # #     #     max_timestamp.values, 1))
# # #     index_timestamp = bag_data['index_timestamp'].loc[bag_data['brake_cmd'].argmax()]
# # #     pd_label = bag_data.loc[index_timestamp]
# # #     ego_label['timestamp'] = pd_label['timestamp']
# # #     ego_label['brake_cmd'] = pd_label['brake_cmd']
# # #     ego_label['position_x'] = pd_label['position_x']
# # #     ego_label['position_y'] = pd_label['position_y']
# # #     ego_label['velocity_x'] = pd_label['velocity_x']
# # #     ego_label['vehicle_acc_x'] = pd_label['vehicle_acc_x']
# # #     ego_label['vehicle_acc_y'] = pd_label['vehicle_acc_y']
# # #     #print(ego_label)
# # #     return max_timestamp,ego_label
# # #
# # #
# # #
# # #
# # # def getAllDataDir(input_data_path):
# # #     "get all dir in data"
# # #     file_list=[]
# # #     for file in os.listdir(input_data_path):
# # #         dir_file = os.path.join(input_data_path, file)
# # #
# # #         if (os.path.isdir(dir_file)):
# # #             h = os.path.split(dir_file)
# # #             file_list.append(h[1])
# # #     return file_list
# # #
# # # import fnmatch
# # # def getMatchedFilePaths( dir_path, pattern="*", formats=[".avi"], recursive=False):
# # #     "get all the files in <dir_path> with specified pattern"
# # #     files = []
# # #     data_dir = os.path.normpath(os.path.abspath(dir_path))
# # #     try:
# # #         for f in os.listdir(data_dir):
# # #             current_path = os.path.join(os.path.normpath(data_dir), f)
# # #             if os.path.isdir(current_path) and recursive:
# # #                 files += getMatchedFilePaths(current_path, pattern, formats,
# # #                                                   recursive)
# # #             elif fnmatch.fnmatch(f,
# # #                                  pattern) and os.path.splitext(f)[-1] in formats:
# # #                 files.append(current_path)
# # #         return files
# # #     except OSError:
# # #         print("os error")
# # #         return []
# # #
# # # def checkCase(dir_path):
# # #     canda_tag = loadTag(dir_path,'candidate_case.json')
# # #     obj_tag = loadTag(os.path.join(dir_path,'screen_cast'), 'obstacle.json')
# # #     if obj_tag is None:
# # #         return False
# # #
# # #     obj_list = []
# # #     for obj in obj_tag["id_list"].keys():
# # #         obj_list.append(obj)
# # #     id_list = []
# # #     for obj in canda_tag:
# # #         if obj["id"] ==[]:
# # #             continue
# # #         for id in obj["id"]:
# # #             id_list.append(id)
# # #     id_list = list(set(id_list))
# # #     #print "===== ",obj_list,'\n===== ', id_list,'\n\n'
# # #     # for a in id_list:
# # #     #     if a in obj_tag:
# # #     #         return True
# # #     id_file = getMatchedFilePaths(dir_path,"*",[".id"])
# # #     id = int(os.path.basename(id_file[0]).split('.')[0])
# # #
# # #     if id in id_list:
# # #         print("====== ",id ,id_list)
# # #         return True
# # #
# # #     return False
# # #
# # # import time
# # # def bjToUnix(bj_time):
# # #     timeArray = time.strptime(bj_time, "%Y-%m-%d %H:%M:%S")
# # #     timestamp = time.mktime(timeArray)
# # #     return int(timestamp)
# # #
# # # def judgeIdValue(s):
# # #     try:
# # #         float(s)
# # #         if (float(s)>0):
# # #             return True
# # #     except ValueError:
# # #         pass
# # #
# # #     try:
# # #         import unicodedata
# # #         unicodedata.numeric(s)
# # #         if (unicodedata.numeric(s)>0):
# # #             return True
# # #     except (TypeError, ValueError):
# # #         pass
# # #     return False
# # #
# # # def filterObjectId(object_id_list):
# # #     max_distribution = 0
# # #     id_dict = {}
# # #     filted_list = []
# # #     for objec_id in object_id_list:
# # #         if not objec_id in id_dict.keys():
# # #             id_dict[objec_id] = 0
# # #         id_dict[objec_id] += 1
# # #     print(id_dict)
# # #
# # #     for object in id_dict:
# # #         if id_dict[object] > max_distribution:
# # #             max_distribution = id_dict[object]
# # #     for object in id_dict:
# # #         if id_dict[object] == max_distribution or id_dict[object]>8:
# # #             filted_list.append(object)
# # #     return filted_list
# # #
# # # def filterLogFile(log_list):
# # #     if len(log_list) ==0:
# # #         return ""
# # #     max_file_size = 0
# # #     max_log_file = log_list[0]
# # #     for log_file_path in log_list:
# # #         try:
# # #             log_file_size  = os.path.getsize(log_file_path)
# # #         except Exception as e:
# # #             log_file_size = 0
# # #         if max_file_size == 0 or max_file_size < log_file_size:
# # #             max_file_size = log_file_size
# # #             max_log_file = log_file_path
# # #     return max_log_file
# # #
# # # # def parseDecisionPannningLog(log_name, start_stamp,end_stamp):
# # # #     log_id_list = []
# # # #     list_set = set()
# # # #
# # # #     for line in open(log_name, "r"):
# # # #         time = line[5:13]
# # # #         n_time = line[14:17]
# # # #         if not ":" in time:
# # # #             continue
# # # #         #try:
# # # #         case_time = bjToUnix(time)+int(n_time)*(1e-3)
# # # #         print(case_time, start_stamp, end_stamp)
# # # #         # except:
# # # #         #     continue
# # # #
# # # #         if (case_time > start_stamp and case_time < end_stamp):
# # # #             tag_id_end = line.find(', tag')
# # # #             tag_id_start = line.find('[PP] ')
# # # #             if tag_id_end < 0 or tag_id_start<0:
# # # #                 continue
# # # #
# # # #             obstacle_id = line[tag_id_start+5:tag_id_end]
# # # #             ret = judgeIdValue(obstacle_id)
# # # #             if ret:
# # # #                 log_id_list.append(int(obstacle_id))
# # # #
# # # #     if log_id_list ==[]:
# # # #         return [], []
# # # #     print(log_id_list)
# # # #     list_set.update(log_id_list)
# # # #     print '\n',list_set,'\n'
# # # #
# # # #     obstacle_id_list =  filterObjectId(log_id_list)
# # # #     return obstacle_id_list,log_id_list
# # # def parseDecisionPannningLog(log_name, time_stamp,time_stamp_1,nsec,nsec_1):
# # #     log_id_list = []
# # #     list_set = set()
# # #     print(time_stamp, time_stamp_1, nsec, nsec_1)
# # #     for line in open(log_name, "r"):
# # #         time = line[5:13]
# # #         n_time = line[14:17]
# # #         if not ":" in time:
# # #             continue
# # #         try:
# # #             log_nsec = int(n_time)
# # #         except:
# # #             continue
# # #         if time_stamp != time_stamp_1:
# # #             if (time == time_stamp_1.split(" ",-1)[1] and log_nsec> nsec_1) or \
# # #                     (time == time_stamp.split(" ",-1)[1] and log_nsec < nsec):
# # #
# # #                 tag_id_end = line.find(', tag')
# # #                 tag_id_start = line.find('[PP] ')
# # #                 if tag_id_end < 0 or tag_id_start<0:
# # #                     continue
# # #
# # #                 obstacle_id = line[tag_id_start+5:tag_id_end]
# # #                 ret = judgeIdValue(obstacle_id)
# # #                 if ret:
# # #                     log_id_list.append(int(obstacle_id))
# # #         else:
# # #             if time == time_stamp_1.split(" ", -1)[1] and log_nsec > nsec_1 and log_nsec < nsec:
# # #                 tag_id_end = line.find(', tag')
# # #                 tag_id_start = line.find('[PP] ')
# # #
# # #                 if tag_id_end < 0 or tag_id_start < 0:
# # #                     continue
# # #
# # #                 obstacle_id = line[tag_id_start + 5:tag_id_end]
# # #                 ret = judgeIdValue(obstacle_id)
# # #                 if ret:
# # #                     log_id_list.append(int(obstacle_id))
# # #
# # #     if log_id_list ==[]:
# # #         return [], []
# # #     print(log_id_list)
# # #     list_set.update(log_id_list)
# # #     print '\n',list_set,'\n'
# # #
# # #     obstacle_id_list =  filterObjectId(log_id_list)
# # #     return obstacle_id_list,log_id_list
# # #
# # # def unixToBjclock(unix_time):
# # #     time_array = time.localtime(unix_time)
# # #     now_time_style = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
# # #     return now_time_style
# # #
# # # import math
# # #
# # # if __name__ == '__main__':
# # #     #dir_path = "/media/sensetime/FieldTest1/data/2020_11_20_09_48_10_AutoCollect/"
# # #     topic_names = ['/control/control_error']
# # #     input_path = "/media/sensetime/FieldTest1/data/pred_eval_ARH/"
# # #     dir_list = getAllDataDir(input_path)
# # #     config_ = loadTag('../config/data_pipeline_config.json', '')
# # #     for dir_name in dir_list:
# # #         dir_path = os.path.join(input_path,dir_name)
# # #         dpc_file_path = os.path.join(dir_path,'dmppcl.bag')
# # #         record_tag = loadTag(dir_path,'data-tag.json')
# # #         if record_tag is None:
# # #             continue
# # #         record_timestamp = int(record_tag["origin_record_tag"][0]["start"]) / 1000
# # #         bag_data = getDataFromDpcbag(dpc_file_path, topic_names, record_timestamp)
# # #         brake_timestamp, ego_label = parseBrakeTimestampFromBag(bag_data)
# # #         #print(brake_timestamp*1000)
# # #
# # #
# # #
# # #         # case_stamp = {"case_time":brake_timestamp*1000}
# # #         # saveTag(dir_path,case_stamp, str(brake_timestamp)+'.json')
# # #         # #os.system("bash "+dir_path+'/logs/download_logs.sh')
# # #         # logs_path = os.path.join(dir_path,'logs/')
# # #         # decision_planning_log_file = getMatchedFilePaths(logs_path, 'ros_decision_planning_node.*',[".txt"])
# # #         # brake_timestamp_bj = unixToBjclock(brake_timestamp)
# # #         # brake_timestamp_bj_1 = unixToBjclock(brake_timestamp - 0.5)
# # #         # nsec = math.modf(brake_timestamp )[0] * 1000
# # #         # nsec_1 = math.modf(brake_timestamp-0.5)[0] * 1000
# # #         # if decision_planning_log_file == []:
# # #         #     obstacle_id = [0]
# # #         #     id_list = []
# # #         # else:
# # #         #     log_file = filterLogFile(decision_planning_log_file)
# # #         #     print(log_file)
# # #         #     obstacle_id,id_list = parseDecisionPannningLog(log_file, brake_timestamp_bj,brake_timestamp_bj_1,int(nsec),int(nsec_1))
# # #         # tag = {}
# # #         # tag["obstacle_id"] = obstacle_id
# # #         # tag["id_list"] = {}
# # #         # if id_list != []:
# # #         #     for id in id_list:
# # #         #         if id not in tag["id_list"].keys():
# # #         #             tag["id_list"][id] = 0
# # #         #         tag["id_list"][id] += 1
# # #         # print(tag)
# # #         # saveTag(dir_path + '/screen_cast/', tag, 'obstacle.json')
# # #
# # #
# # #
# # #         # seg_point = {"begin_secs":brake_timestamp-1,
# # #         #              "end_secs":brake_timestamp,
# # #         #              "output_dir":os.path.join(dir_path,'prediction_evaluation')}
# # #         # print(seg_point)
# # #         # CutDpcbag(dpc_file_path,[seg_point])
# # #         # generatePredictionEval(dir_path,config_)
# # #
# # #         #main(dir_path,int(brake_timestamp*1000))
# # #         retult = checkCase(dir_path)
# # #         print(dir_path,": ",retult)
# # #
# #
# #
# # import os
# # import cv2
# # import sys
# # import ast
# # import struct
# # import fnmatch
# # from decimal import Decimal
# # from rospy.rostime import Time
# # from cut_rec_multiprocess import JudgeTheStartAndEndOfVideo
# #
# # def ReadFile(file_path):
# #     data = []
# #     with open(file_path, 'r') as reader:
# #         data = reader.readlines()
# #     return data
# #
# #
# # class TimeReader:
# #     def __init__(self, filename):
# #         self.header_bytes = 0
# #         self.frm_bytes = 0
# #         self.filename = filename
# #         self.f_handle = open(filename, 'rb')
# #         self.read_file_header()
# #
# #     def read_file_header(self):
# #         buf = self.f_handle.read(1)
# #         buf = buf + b'\x00\x00\x00'
# #         self.header_bytes = struct.unpack("i", buf)
# #         buf = self.f_handle.read(1)
# #         buf = self.f_handle.read(2)
# #         buf = buf + b'\x00\x00'
# #         self.frm_bytes = struct.unpack("i", buf)
# #
# #     def read_frm_header(self):
# #         buf = self.f_handle.read(1)
# #         header_bytes = struct.unpack("B", buf)
# #         buf = self.f_handle.read(7)
# #         buf = self.f_handle.read(8)
# #         timestamp, = struct.unpack('Q', buf)
# #         buf = self.f_handle.read(8)
# #         payload_bytes, = struct.unpack('Q', buf)
# #         return timestamp, payload_bytes
# #
# #     def read_frm(self):
# #         timestamp, payload_bytes = self.read_frm_header()
# #         payload = self.f_handle.read(payload_bytes)
# #         return timestamp, payload
# #
# #     def get_time_list(self):
# #         time_list = []
# #         while True:
# #             try:
# #                 t, _ = self.read_frm()
# #                 time_list.append(t)
# #             except:
# #                 break
# #         return time_list
# #
# # def getMatchedFilePaths( dir_path, pattern="*", formats=[".mp4"], recursive=False):
# #     "get all the files in <dir_path> with specified pattern"
# #     files = []
# #     data_dir = os.path.normpath(os.path.abspath(dir_path))
# #     try:
# #         for f in os.listdir(data_dir):
# #             current_path = os.path.join(os.path.normpath(data_dir), f)
# #             if os.path.isdir(current_path) and recursive:
# #                 files += getMatchedFilePaths(current_path, pattern, formats,
# #                                                   recursive)
# #             elif fnmatch.fnmatch(f,
# #                                  pattern) and os.path.splitext(f)[-1] in formats:
# #                 files.append(current_path)
# #         return files
# #     except OSError:
# #         print("os error")
# #         return []
# #
# # def mergeTimeStampFiles(input_path,output_ts_path):
# #     ts_file_list = getMatchedFilePaths(input_path,"*",[".bin"])
# #     ts_file_list = sorted(ts_file_list)
# #     i = 0
# #     with open(output_ts_path,'w') as reuslt:
# #         for ts_file in ts_file_list:
# #             reader = TimeReader(ts_file)
# #             timestamps = reader.get_time_list()
# #             for time in timestamps:
# #                 reuslt.write(str(i)+', '+str(time)+'\n')
# #                 i += 1
# #
# # def JudgeStartAndEndFrame(start_index, end_index,frame_list):
# #     start_msg,end_msg = [],[]
# #     for index,interval in enumerate(frame_list):
# #         if start_index >= interval[0] and start_index <= interval[1]:
# #             start_msg = [index,start_index-interval[0]]
# #         if end_index >= interval[0] and end_index <= interval[1]:
# #             end_msg = [index,end_index-interval[0]]
# #     return start_msg,end_msg
# #
# #
# # def mergeVideo(input_path):
# #     #fourcc = cv2.VideoWriter_fourcc('H', '2', '6', '4')
# #     output_video_path = "/media/sensetime/FieldTest1/123/2020_12_01_A2datacollection_slice/merged.mp4"
# #     output_ts_path = "/media/sensetime/FieldTest1/123/2020_12_01_A2datacollection_slice/merged.txt"
# #     mergeTimeStampFiles(input_path,output_ts_path)
# #     start_index, end_index = JudgeTheStartAndEndOfVideo(output_ts_path,1606812600051032,10,10)
# #
# #
# #     video_list = getMatchedFilePaths(input_path)
# #     video_list = sorted(video_list)
# #     frame_num = 0
# #     frame_list = []
# #     for video_path in video_list:
# #         cap = cv2.VideoCapture(video_path)
# #         old_frame_num = frame_num+1
# #         frame_num += int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
# #         frame_list.append([old_frame_num,frame_num])
# #     start_msg,end_msg = JudgeStartAndEndFrame(start_index, end_index,frame_list)
# #     print(start_index, end_index,start_msg,end_msg)
# #
# #     tmp_path = os.path.join(input_path, video_list[0])
# #     cap = cv2.VideoCapture(tmp_path)
# #     if not cap.isOpened():
# #         print("Cannot open video capture: {}".format(tmp_path))
# #     fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
# #     fourcc = cv2.VideoWriter_fourcc(chr(fourcc & 0xFF),
# #                            chr((fourcc >> 8) & 0xFF),
# #                            chr((fourcc >> 16) & 0xFF),
# #                            chr((fourcc >> 24) & 0xFF))
# #     width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
# #     height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
# #     fps = cap.get(cv2.CAP_PROP_FPS)
# #     writer = cv2.VideoWriter(output_video_path, fourcc, int(fps), (int(width), int(height)))
# #     if not writer.isOpened():
# #         print("Cannot open video writer: {}".format(output_video_path))
# #
# #     cut_video_list = []
# #     for i,video_path in enumerate(video_list):
# #         if i > start_msg[0] and i < end_msg[0]:
# #             cut_video_list.append(video_path)
# #
# #     for i in range(len(cut_video_list)):
# #         if i == 0:
# #             cap_start = cv2.VideoCapture(cut_video_list[i])
# #             cap_start.set(cv2.CAP_PROP_POS_FRAMES, start_msg[1])
# #             frmae_num = cap_start.get(cv2.CAP_PROP_FRAME_COUNT)
# #             counts = start_msg[1]
# #             while counts <= frmae_num:
# #                 flag, frame = cap_start.read()
# #                 counts += 1
# #                 print(counts)
# #                 writer.write(frame)
# #             cap_start.release()
# #         elif i == len(cut_video_list) -1:
# #             cap_end = cv2.VideoCapture(video_list[i])
# #             cap_end.set(cv2.CAP_PROP_POS_FRAMES, end_msg[1])
# #             frame_num = cap_end.get(cv2.CAP_PROP_FRAME_COUNT)
# #             counts = 1
# #             while counts <= end_msg[1] and counts <= frame_num:
# #                 flag, frame = cap_end.read()
# #                 counts += 1
# #                 print(counts)
# #                 writer.write(frame)
# #             cap_end.release()
# #         else:
# #             counts = 1
# #             cap = cv2.VideoCapture(video_list[i])
# #             cap.set(cv2.CAP_PROP_POS_FRAMES, counts)
# #             frame_num = cap.get(cv2.CAP_PROP_FRAME_COUNT)
# #             while counts <=  frame_num:
# #                 flag, frame = cap.read()
# #                 counts += 1
# #                 print(counts)
# #                 writer.write(frame)
# #             cap_end.release()
# #
# #     # for video_path in video_list:
# #     #     print(video_path)
# #     #     cap = cv2.VideoCapture(video_path)
# #     #     frmae_num = cap.get(cv2.CAP_PROP_FRAME_COUNT)
# #     #
# #     #     while(True):
# #     #         ret, frame = cap.read()
# #     #         if ret is False:
# #     #             break
# #     #         #writer.write(frame)
# #
# #     writer.release()
# #     cap.release()
# #
# #
# #
# #
# # if __name__ == '__main__':
# #     mergeVideo("/media/sensetime/FieldTest1/123/2020_12_01_A2datacollection/case2/sunny_day")
# #
# #
# # a = {"aa":1}
# # print(a.get("aa"))
# # a =[1,1]
# # b = [2,2]
# # print(a-b)
#
# # def aaaa():
# #     return 1,2,3,4
# #
# # b,c = aaaa()
# # import time
# # aa =  time.strftime("%m-%d %H:%M:%S", time.localtime())
# # print str(aa)+"\033[1;31m [ERROR]\033[0m tprofiling error "
#
# # def getFileSize(filePath, size=0):
# #     for root, dirs, files in os.walk(filePath):
# #         for f in files:
# #             size += os.path.getsize(os.path.join(root, f))
# #     return size
# # import os
# # # print int(getFileSize("/media/sensetime/FieldTest2/data/2021_01_22_11_41_49_AutoCollect")/float(1024*1024))
# # a=[]
# # for b in a:
# #     print(2222)
# # topic_list = ["/canbus/vehicle_report", "/control/control_debug",
# #               "/decision_planning/decision_debug", "/decision_planning/decision_target",
# #               "/decision_planning/planning_debug", "/decision_planning/trajectory",
# #               "/decision_planning/trajectory_for_prediction", "/localization/navstate_info",
# #               "/node_state", "/perception/camera/traffic_light_sign",
# #               "/perception/fusion/object", "/perception/lidar/object",
# #               "/prediction/objects", "/sensor/gnss",
# #               "/sensor/imu", "/sensor/ins",
# #               "/sensor/lidar/fusion/point_cloud"]
# # from moviepy.editor import *
# # import os
# #
# # L = []
# # for root, dirs, files in os.walk("/media/sensetime/FieldTest1/123/aaa/2020_12_07_15_27_38/cv22/normal/9"):
# #     files.sort()
# #     for file in files:
# #         if os.path.splitext(file)[1] == '.mp4':
# #             filePath = os.path.join(root, file)
# #             video = VideoFileClip(filePath)
# #             L.append(video)
# # print(L)
# # final_clip = concatenate_videoclips(L)
# # final_clip.to_videofile("/media/sensetime/FieldTest1/123/aaa/2020_12_07_15_27_38/cv22/normal/9/target.mp4", fps=30, remove_temp=False)
# #
# # #
# # # import ijson
# # # file_name = '/media/sensetime/FieldTest1/123/2020_11_30_A2datacollection/12.json'
# # # with open(file_name, 'r',) as f:
# # #     parser = ijson.parse(f)
# # #     for prefix, event, value in parser:
# # #         a= prefix.split('.',1)
# # #         # if len(a)> 1:
# # #         #     print a
# # #         print prefix+'==', "===== ",event," ====== ", value,'\n'
# #
# # # a = []
# # # print(a[0])
# import struct
# import copy
#
# class TimeReader:
#     def __init__(self, filename):
#         self.header_bytes = 0
#         self.frm_bytes = 0
#         self.filename = filename
#         self.f_handle = open(filename, 'rb')
#
#     #     self.header_save = 0
#     #     self.frm_save = 0
#     #     self.save_handle = open(filename, 'rb')
#     #     self.read_file_header()
#     #
#     # def read_file_header(self):
#     #     buf = self.f_handle.read(1)
#     #     buf = buf + b'\x00\x00\x00'
#     #     self.header_bytes = struct.unpack("i", buf)
#     #     buf = self.f_handle.read(1)
#     #     buf = self.f_handle.read(2)
#     #     buf = buf + b'\x00\x00'
#     #     self.frm_bytes = struct.unpack("i", buf)
#     #
#     #
#     #
#     #
#     #
#     # def read_frm_header(self,t1,t2):
#     #
#     #     buf = self.f_handle.read(1)
#     #     header_bytes = struct.unpack("B", buf)
#     #     buf = self.f_handle.read(7)
#     #     buf = self.f_handle.read(8)
#     #     timestamp, = struct.unpack('Q', buf)
#     #     buf = self.f_handle.read(8)
#     #     payload_bytes, = struct.unpack('Q', buf)
#     #     payload = self.f_handle.read(payload_bytes)
#     #     line = self.save_handle.readline(24+payload_bytes)
#     #     #print(timestamp)
#     #     if int(timestamp) > t1 and int(timestamp) < t2:
#     #         return True,line
#     #     return False,line
#
#
#     def get_time_list(self,t1,t2):
#
#         with open('/home/sensetime/ws/123.bin','w') as b:
#             buf = self.f_handle.read(1)
#             b.write(buf)
#             buf = buf + b'\x00\x00\x00'
#             self.header_bytes = struct.unpack("i", buf)
#             buf = self.f_handle.read(1)
#             b.write(buf)
#             buf = self.f_handle.read(2)
#             b.write(buf)
#             buf = buf + b'\x00\x00'
#             self.frm_bytes = struct.unpack("i", buf)
#
#             while True:
#                 try:
#                     aa = self.f_handle.read(1)
#                     header_bytes = struct.unpack("B", aa)
#                     bb = self.f_handle.read(7)
#                     cc = self.f_handle.read(8)
#                     timestamp, = struct.unpack('Q', cc)
#                     dd = self.f_handle.read(8)
#                     payload_bytes, = struct.unpack('Q', dd)
#                     payload = self.f_handle.read(payload_bytes)
#                     print(timestamp)
#                     if int(timestamp) > t1 and int(timestamp) < t2:
#                         b.write(aa)
#                         b.write(bb)
#                         b.write(cc)
#                         b.write(dd)
#                         b.write(payload)
#                 except:
#                     break
#
#
#
#
#
# if __name__ == '__main__':
#     aa = TimeReader('/media/sensetime/FieldTest/123/ccc/2020_12_10_20_30_27_AutoCollect/cv22/normal/2/timestamp_20201210194425.bin')
#     aa.get_time_list(1607603438815761911,1607603540883300900)

import numpy as np

print np.array([1,1,1])/np.array([2,3,4])
