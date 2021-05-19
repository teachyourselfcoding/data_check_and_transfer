import numpy as np
from pyproj import Proj


utm_zone = '51'
_myProj = Proj('+proj=utm +zone={}, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs'.format(utm_zone))


def lnglat_to_utm(points):
    pts = np.array(points)
    x, y = _myProj(pts[:, 0], pts[:, 1])

    return list(zip(x, y))


def utm_to_lnglat(points):
    pts = np.array(points)
    lng, lat = _myProj(pts[:, 0], pts[:, 1], inverse=True)

    return list(zip(lng, lat))


def _dirvec_from_xypair(a, b):
    d = np.array((b[0] - a[0], b[1] - a[1]))
    return d / (np.linalg.norm(d) + 1e-19)


def dis_from_xypair(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def record_runtime(func, tag='query'):
    def ret_func(args):
        import time
        start_time = time.time()
        rets = func(args)
        end_time = time.time()
        print('{} runtime: {:.4f} s.'.format(tag, end_time - start_time))
        return rets
    return ret_func


def downsample_by_dist(points, dist_thresh=1.0):
    # NOTE: require ordered point sequence
    pts = points.copy()
    ret = [pts[0]]
    for p in pts[1:]:
        d = dis_from_xypair(ret[-1], p)
        if d > dist_thresh:
            ret += [p]

    return ret


def downsample_points(points, cos_thresh=1e-4, dist_thresh=10):
    # NOTE: require ordered point sequence
    pts = points.copy()
    if len(pts) == 1: return pts
    ret = [pts[0], pts[1]]
    for p in pts[2:-1]:
        d = dis_from_xypair(ret[-1], p)
        if d > dist_thresh:
            ret += [p]
            continue

        dv = _dirvec_from_xypair(ret[-2], ret[-1])
        newd = _dirvec_from_xypair(ret[-1], p)
        if dv.dot(newd) < 1 - cos_thresh:
            ret += [p]
        else:
            ret[-1] = p

    if len(points) > 2:
        ret += [pts[-1]]

    return ret


def unclutter(coords, min_dist=1.0):
    # NOTE: require ordered point sequence
    ret = [coords[0]]

    for p in coords[1:-1]:
        if dis_from_xypair(ret[-1], p) < min_dist:
            continue
        ret += [p]

    ret += [coords[-1]]

    return ret


def apply_offset(coords, offset_utm_x=0, offset_utm_y=0):
    ret = []
    for p in coords:
        newp = (p[0] + offset_utm_x, p[1] + offset_utm_y)
        ret += [newp]

    return ret

    
