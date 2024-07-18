import os
from rtree import index
from numpy import ndarray

RTREE_DAT_FILE = "rtree_index.dat"

class RTree:
    def __init__(self, points):
        self.p = index.Property()
        self.p.dimension = 91
        self.rtree_index = index.Index('rtree_index', properties=self.p, interleaved=True)

        if (len(self.rtree_index) == 0):
            for key, feature_vector in points.items():
                #print(key)
                #print(feature_vector)
                #bbox = tuple(map(tuple, feature_vector))
                bbox = tuple(map(float, feature_vector)) + tuple(map(float, feature_vector))
                print(bbox)
                self.rtree_index.insert(id(key), bbox, obj=(bbox, key))
    
    def knn_search(self, query_point: ndarray, k: int):
        knn_results = list(self.rtree_index.nearest(query_point, num_results=k, objects=True))
        
        results = [(result.object[1], result.object[0].tolist()) for result in knn_results]
        return results