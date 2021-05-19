## 数据自动化产线V1.0
### 产品特性
- 硬盘插之即切，切完即传，全程无需人工操作，极致简单；
- 完整的UI显示，所有信息一目了然；
- 支持路测数据全自动切割，上传AWS，本地归档；
- 支持实时显示任务信息，当前完成状态，上传进度与速率，硬盘使用情况；
- 支持数据结构检测，自动发现缺失文件并显示错误信息；

-------------
### 使用方法
在程序目录下执行：

        python3 main.py

弹出UI界面后插上包含待处理数据的硬盘即可。

#### 主要窗口与功能
- ##### 窗口——>“任务详情”

 <div align=center><img width="888" height="278" src="http://gitlab.hk.sensetime.com/zhengyaocheng/data_check_and_transfer/raw/master/pic/detail_frame.png"/></div> 

&emsp; 一次路测/采集所获得的数据的切分、上传被称为一次处理任务。本窗口能够显示当前处理任务的进度与已完成处理任务的信息。显示的信息包括数据所存放的硬盘、数据所属的测试、采集任务的ID、数据所属的测试/采集任务的 **“Issue_ID”** ，各个处理任务所处的状态。如果当前的处理任务处于 **“上传中”** 状态，还会显示上传进度与上传速率。
- ##### 窗口——>“当前操作路径”

 <div align=center><img width="511" height="45" src="http://gitlab.hk.sensetime.com/zhengyaocheng/data_check_and_transfer/raw/master/pic/work_path_frame.png"/></div> 

&emsp; 字面意思，表示当前处理的数据所在的路径。也就是当前处于 **“ [ 处理中 ] ”** 的移动硬盘的 **“/data”** 文件夹。
- ##### 窗口——>“已加载硬盘”

 <div align=center><img width="349" height="98" src="http://gitlab.hk.sensetime.com/zhengyaocheng/data_check_and_transfer/raw/master/pic/ssd_frame.png"/></div> 

&emsp; 显示所有当前已经挂载到本机，并且命名为 **“FieldTest”** 或 **“FieldTest”  + 数字** 的移动硬盘的ID。如果移动硬盘根目录没有表示硬盘ID的 **“.id”** 文件，会显示为 **“Unknown”** 。
- ##### 窗口——>“日志”

 <div align=center><img width="855" height="260" src="http://gitlab.hk.sensetime.com/zhengyaocheng/data_check_and_transfer/raw/master/pic/log_frame.png"/></div> 

&emsp; 显示一些重要信息，方便在出现异常时debug，不是 **“ Error ”** 的可以直接无视...

-------------
#### 重要信息！
- 上传数据时所用的移动硬盘必须命名为 **“ FieldTest ”** 。
- 移动硬盘根目录下必须包含一个 **“.id”** 文件标示硬盘ID，如：**“01234.id”** 。
- 所有需要处理并上传的数据须放在 **/FieldTest/data/** 目录下。
- 严禁拔下状态为 **“ [ 处理中 ] ”** 的硬盘，在V1.0版本中这样的行为会导致程序卡死、进度丢失~~和世界毁灭~~等严重后果。
-------------

### 常见异常与排除方法

- **已上传数据量与总数据量存在差别：** 由于文件夹实际占用磁盘空间与文件夹内不严格等于所有文件数据之和，所以现版本中的上传进度会有些许误差，可以忽略不计。只要“State”栏显示“完成”即代表上传成功。
- **ERROR(get_issue_id)或ERROR(get_task_id)：** 没有找到data-tag.json，检查错误信息中的文件夹地址，如果是采集/测试所得的数据文件夹，说明该文件夹有数据缺失；如果不是数据文件夹（通常不应该出现此类情况），可以忽略不计。
- **“任务详情”窗口出现“Unknown”条目，且“State”栏显示“跳过”：** /data文件夹下存在非原始数据文件夹，忽略即可。


### requirement
python2.7:
    1.rosbag
    2.pandas
    
python3:
    1.numpy
    2.pandas
    3.rospkg
    
### 定制化操作
- 修改config/data_pipeline_config.json -> "senseauto_path" 为你本地编译好的senseauto路径
- 评测，切分，上传功能开关,修改 config/data_pipeline_config.json
-   评测："evaluation"
-   featue 切分："segment_and_upload" -> "feature_segment"
-   featue 上传："segment_and_upload" -> "feature_upload"
- 如果需要指定某辆车或者某个topic进行切分，在"include_segment"对应子目录的list中增加即可
- 



