import faiss
import os
import pandas as pd
import numpy as np


class FaissIndex:
    def __init__(self, nlist, nprobe):
        self.nlist = nlist
        self.nprobe = nprobe
        self.index = None

    def train_index(self, xb):
        quantizer = faiss.IndexFlatL2(self.d)
        self.index = faiss.IndexIVFFlat(quantizer, self.d, self.nlist)
        self.index.train(xb)
        self.index.add(xb)
        self.index.nprobe = self.nprobe

    def create_index(self, xb):
        if os.path.exists('faiss_index.index'):
            os.remove('faiss_index.index')

        # Init the values of the index
        self.d = xb.shape[1] # Update dimensionality according to the input

        self.train_index(xb)
        faiss.write_index(self.index, 'faiss_index.index')

    def get_index(self):
        self.index = faiss.read_index('faiss_index.index')

    def knn_search(self, xq, k, track_id_list):
        D, I = self.index.search(xq, k)


        results = [(track_id_list[i], D[0][j]) for j, i in enumerate(I[0])]
        results.sort(key=lambda x: x[1])

        return results


def read_song_features(path):
    df = pd.read_csv(path, header=None)

    collection = {row[0]: np.array(row[1:]) for row in df.itertuples(index=False)}
    return collection


def main():
    songs_feature = read_song_features('song_features.csv')
    vectors = np.array(list(songs_feature.values()))
    track_ids = list(songs_feature.keys())
    faiss_index = FaissIndex(nlist=30, nprobe=10)

    if os.path.exists('faiss_index.index'):
        os.remove('faiss_index.index')
        faiss_index.create_index(vectors)
        # faiss_index.get_index()
    else:
        faiss_index.create_index(vectors)


    query_track_id = input('track_id of query: ')

    try:
        query_vector = songs_feature[query_track_id]
    except:
        print('Track not found')
        return

    k = int(input('Top k: '))

    results = faiss_index.knn_search(np.array([query_vector]), k, track_ids)
    print(results)


if __name__ == '__main__':
    main()

