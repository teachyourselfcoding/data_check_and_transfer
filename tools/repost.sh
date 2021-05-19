#!/bin/sh
# refine the orders your wanna execute at fixed time
cd ~/ws/repo_pro/senseauto/
bash system/scripts/repo/sync.sh
repo download-topic AUTODRIVE-6564_reset_eval_prediction
cd ~/Codes/data_check_and_transfer/tools/
python repost_tag.py ../upload_list/