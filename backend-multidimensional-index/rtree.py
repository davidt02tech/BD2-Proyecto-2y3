import os
from rtree import index
from numpy import ndarray

RTREE_DAT_FILE = "rtree_index.dat"

class RTree:
    def __init__(self, points: ndarray):
        self.p = index.Property()
        self.rtree_index = index.Index('rtree_index', properties=self.p, interleaved=False)
        self.dimension = points.shape[1]

        if (len(self.rtree_index) == 0):
            for track_id in points:
                feature_vector = points[track_id]
                rtree_index.insert(id(track_id), tuple(feature_vector)*2, obj=(feature_vector, track_id))
    
    def knn_search(self, query_point: ndarray, k: int):
        knn_results = list(self.rtree_index.nearest(tuple(query_point) * 2, num_results=k, objects=True))
        
        results = [(result.object[1], result.object[0].tolist()) for result in knn_results]
        return results
