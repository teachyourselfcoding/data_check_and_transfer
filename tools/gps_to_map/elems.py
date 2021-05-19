import numpy as np
from scipy.spatial import cKDTree as KDTree 
from to_geojson import convert_to_geojson
from utils import dis_from_xypair, downsample_by_dist, record_runtime


class PointSet:
    def __init__(self, points, ds_dist=None, self_check=False, dist_check=None):
        # points: utm
        self.points = points
        self.ds_dist = ds_dist
        self.self_check = self_check
        self.dist_check = dist_check
        self.kdtree = None
        
        if ds_dist:
            self._downsample(ds_dist)
            if self_check:
                self._self_check(dist_check)


    @staticmethod
    def _get_dirvec(idx, tar_points):
        idx_pre = idx - 1
        idx_nxt = (idx + 1) % len(tar_points)
        dist_pre = dis_from_xypair(tar_points[idx], tar_points[idx_pre])
        dist_nxt = dis_from_xypair(tar_points[idx], tar_points[idx_nxt])
        neb_points = [tar_points[idx_pre], tar_points[idx]] if dist_pre < dist_nxt else [tar_points[idx], tar_points[idx_nxt]]
        neb_points = np.array(neb_points)
        dirvec = neb_points[1, ...] - neb_points[0, ...]

        return np.array(dirvec)


    @staticmethod
    def _get_nearest(po, px, py):
        x, y = po
        x1, y1 = px
        x2, y2 = py

        oaab = (x1-x) * (x2-x1) + (y1-y) * (y2-y1)
        obab = (x2-x) * (x2-x1) + (y2-y) * (y2-y1)
        if oaab * obab > 0:
            return min(dis_from_xypair(po, px), dis_from_xypair(po, py))

        A = y1 - y2
        B = x2 - x1
        C = y1 * (x1 - x2) - x1 * (y1 - y2)
        k = np.sqrt(A*A + B*B)

        return np.abs(A*x + B*y + C) / k


    @staticmethod
    def _do_interp(coords, interval=1.0):
        ret = []
        for i in range(len(coords) - 1):
            p, q = np.array(coords[i]), np.array(coords[i + 1])
            n = int(np.linalg.norm(q - p) / interval)

            xs = np.linspace(p[0], q[0], n, endpoint=False)
            ys = np.linspace(p[1], q[1], n, endpoint=False)
            samples = zip(xs, ys)

            ret.extend(samples)

        ret.append(coords[-1])
        return ret


    def _downsample(self, dist_threshold):
        pts_pre = len(self.points)
        self.points = downsample_by_dist(self.points, dist_thresh=dist_threshold)
        pts_now = len(self.points)
        print('   -- downsample points {} => {}, downsample rate: {:.2f}%.'.format(pts_pre, pts_now, pts_now / pts_pre * 100))


    def _self_check(self, dist_threshold):
        pts_pre = len(self.points)

        # step-1: self check with a smaller threshold
        ds_points = self.points
        ret_points = ds_points[:3]
        from tqdm import tqdm
        for nidx in tqdm(range(3, len(ds_points))):
            p = ds_points[nidx]

            kdtree = KDTree(ret_points)
            # dist, qidx = kdtree.query(p, k=2)
            # dist = self._get_nearest(p, ret_points[qidx[0]], ret_points[qidx[1]])
            # qidx = qidx[0]
            
            dist, qidx = kdtree.query(p)
            if dist >= dist_threshold:
                ret_points.append(p)
            else:
                dirvec_check = self._get_dirvec(nidx, ds_points)
                dirvec_query = self._get_dirvec(qidx, ret_points)

                cos_angle = dirvec_check @ dirvec_query
                if cos_angle < 0:
                    ret_points.append(p)
        
        '''
        # step-2: self check with large threshold and interp
        tmp_points = ret_points
        ret_points = tmp_points[:3]
        us_points = self._do_interp(ret_points)
        for nidx in tqdm(range(3, len(tmp_points))):
            p = tmp_points[nidx]

            us_kdtree = KDTree(us_points)
            # dist, qidx = us_kdtree.query(p, k=2)
            # dist = self._get_nearest(p, us_points[qidx[0]], us_points[qidx[1]])
            # qidx = qidx[0]
            
            dist, qidx = us_kdtree.query(p)
            if dist >= dist_threshold:
                us_points = us_points[:-1] + self._do_interp([ret_points[-1], p])
                ret_points.append(p)
            else:
                dirvec_check = self._get_dirvec(nidx, tmp_points)
                dirvec_query = self._get_dirvec(qidx, us_points)

                cos_angle = dirvec_check @ dirvec_query
                if cos_angle < 0:
                    us_points = us_points[:-1] + self._do_interp([ret_points[-1], p])
                    ret_points.append(p)
        '''
        
        self.points = ret_points
        pts_now = len(self.points)
        print('   -- self check: {} => {}. self overlapped {:.2f}%.'.format(pts_pre, pts_now, (1 - pts_now / pts_pre) * 100))

    
    def apply_offset(self, offset_utm_x=0.0, offset_utm_y=0.0):
        # TODO: record offsets and support recovering
        coords = self.points
        ret = []
        for p in coords:
            newp = (p[0] + offset_utm_x, p[1] + offset_utm_y)
            ret += [newp]
        self.points = ret
        return self


    def build_kdtree(self):
        self.kdtree = KDTree(self.points)
        print('   ====>> build kdtree with {} points.'.format(self.kdtree.data.__len__()))
        return self

    
    def merge_points(self, points, dist_threshold, merge_overlap=0.9, debug=False):
        if self.kdtree is None:
            self.build_kdtree()

        if isinstance(points, PointSet):
            points = points.points
        
        query_func = record_runtime(self.kdtree.query) if debug else self.kdtree.query
        dists, _ = query_func(points)
        new_points = np.array(points)
        new_points = new_points[dists >= dist_threshold, :]
        
        overlap = 1 - new_points.shape[0] / len(points)
        print('   ====>> overplapped: {:.2f}%.'.format(overlap * 100))
        if overlap < merge_overlap:
            self.points += list(new_points)
            print('   ====>> merged into database.')
            self.build_kdtree()
        
        return overlap, overlap < merge_overlap


    def to_geojson(self, save_path):
        convert_to_geojson(self.points, save_path)
        return self

