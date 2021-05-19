import numpy as np
import geojson
import json
import utils


def convert_to_geojson(points, save_path, offset=[0.0, 0.0], dist_threshold=20):
    # points: utm

    # apply offset
    points = utils.apply_offset(points, offset[0], offset[1])

    # extract lines
    lines = []
    for p in points:
        if len(lines) == 0:
            lines.append([p])
            continue

        line = lines[-1]
        last_point = line[-1]
        dist = utils.dis_from_xypair(last_point, p)
        if dist <= dist_threshold:
            line.append(p)
            lines[-1] = line
        else:
            lines.append([p])

    # convert to geojson
    feat_list = []
    for line in lines:
        ds_line = utils.downsample_points(line, dist_thresh=dist_threshold)
        ds_line = utils.downsample_by_dist(ds_line, dist_thresh=dist_threshold * 0.2)
        ds_line = utils.utm_to_lnglat(ds_line)
        line = geojson.LineString(ds_line)
        feat = geojson.Feature(geometry=line)
        feat_list.append(feat)

    # write json file
    feat_coll = geojson.FeatureCollection(feat_list)
    with open(save_path, 'w') as file:
        json.dump(feat_coll, file, indent=4)
        # print('<TO_GEOJSON>: save geojson to ===> ', save_path)

