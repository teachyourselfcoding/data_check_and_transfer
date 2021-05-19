from utils import lnglat_to_utm, utm_to_lnglat
from elems import PointSet
import numpy as np
import argparse
import os
import time


parser = argparse.ArgumentParser(description='mefi')
parser.add_argument('--input_path', type=str, default=None)
parser.add_argument('--input_dir', type=str, default=None)
parser.add_argument('--save_dir', type=str, default=None)
parser.add_argument('--db_path', type=str, default=None)

parser.add_argument('--query_overlap', action='store_true', default=True)
parser.add_argument('--query_merge', action='store_true', default=False)
# TODO: not support yet
parser.add_argument('--query_pose', action='store_true', default=False)

# TODO: offset not supported yet
parser.add_argument('--offset_x', type=str, default=0.0)
parser.add_argument('--offset_y', type=str, default=0.0)

parser.add_argument('--dist_ds', type=float, default=3.0, help='distance threshold for downsampling.')
parser.add_argument('--dist_merge', type=float, default=3.0, help='distance threshold for merging.')
parser.add_argument('--self_check', action='store_true', default=False, help='whether do self-checking when reading txt data.')
parser.add_argument('--merge_thres', type=float, default=0.5, help='overlap threshold for merging 0.0 ~ 1.0.')

args = parser.parse_args()


dist_ds = args.dist_ds
dist_check = args.dist_ds
do_self_check = args.self_check
dist_merge = args.dist_merge
merge_thres = args.merge_thres

# TODO: not support yet
offset_x = 0.0
offset_y = 0.0


def read_lidar_data(txt_path, ds_dist=None, self_check=False, dist_check=None):
    print('\n>> >> read data from file', txt_path)
    with open(txt_path, 'r') as file:
        lines = file.readlines()
        datas = []
        # for line in lines:
        #     # wgs84(lon, lat, height)
        #     items = line.split(',')
        #     print(items)
        #     items = items[1:3]
        #     print(items)
        #     items = [float(x[:-1]) for x in items]
        #     a=items[1]
        #     items[1]=items[0]
        #     items[0]=a
        #     print(items)
        #     datas.append(items)
        for line in lines:
            # wgs84(lon, lat, height)
            items = line.split(' ')
            items = items[5:7]
            items = [float(x[:-1]) for x in items]
            datas.append(items)

    utms = lnglat_to_utm(datas)
    return PointSet(utms, ds_dist, self_check, dist_check)

import json
def saveTag(tag_file_path, tag_data, file_name='data-tag.json'):
    '''
    save json file
    :param tag_file_path: save path
    :param tag_data: to be saved json
    :param file_name: to be savad file name
    '''
    tag_file = os.path.abspath(os.path.join(tag_file_path, file_name))
    if not os.path.exists(tag_file_path):
        os.mkdir(tag_file_path)
    if not os.path.exists(tag_file):
        os.mknod(tag_file)
    with open(tag_file, 'w') as fw:
        json.dump(tag_data, fw, indent=4)



if __name__ == '__main__':
    if args.query_merge or args.query_overlap:
        assert args.input_dir is not None or args.input_path, 'input path or dir is required.'

        database = None
        if args.db_path is not None:
            # assume that db is downsampled
            database = read_lidar_data(args.db_path)

        if args.input_dir is not None:
            frames_path = os.listdir(args.input_dir)
            frames_path = [os.path.join(args.input_dir, x) for x in frames_path]

        elif args.input_path is not None:
            frames_path = [args.input_path]
        else:
            raise NotImplementedError

        merge_result = []
        for path in frames_path:
            frame = read_lidar_data(path, dist_ds, do_self_check, dist_check)
            if database is None:
                database = frame
                print('build databaset with the first data.')
                merge_result.append([0.0, True])
            else:
                op, me = database.merge_points(frame, dist_merge, -1 if not args.query_merge else merge_thres)
                merge_result.append([op, me])

        # log
        print('\n\n')
        for idx, merge in enumerate(merge_result):
            try:
                save_path  = os.path.split(args.input_path)[0]
                save_tag = {"overlapped":merge[0] * 100}
                saveTag(save_path,save_tag,'overlap_result.json')
            except Exception as e:
                print('save overlap error')

            print('{}: overlapped {:.2f}%.{}'.format(frames_path[idx], merge[0] * 100, ' merged into database.' if merge[1] else ''))

        if args.save_dir:
            tag = time.time()
            save_path = os.path.join(args.save_dir, 'database.txt')
            with open(save_path, 'w') as f:
                lng_lats = utm_to_lnglat(database.points)
                for p in lng_lats:
                    datas = ['unknown'] * 5 + [str(p[0]) + ',', str(p[1]) + ',', 'unkonwn']
                    f.writelines(' '.join(datas) + '\n')
            print('\nsave merged database to:', save_path)

            save_path = os.path.join(args.save_dir, 'database.geojson')
            database.to_geojson(save_path)
            print('save geojson to:', save_path)

