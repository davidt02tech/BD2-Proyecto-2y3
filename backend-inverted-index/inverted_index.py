from collections import defaultdict
from sys import getsizeof
from .data_processing import process_text
import heapq
import pandas as pd
import os

class Index:
    pass

class SPIMI(Index):
    BUFFER = 4096
    index_number = 0

    def __init__(self, file_path, index_folder):
        self.index = defaultdict(list)
        self.path = index_folder
        self.file = file_path
        self.current_index = 0
        self.index_number = SPIMI.index_number
        SPIMI.index_number += 1

    def add(self, term, doc_id):
        if getsizeof(self.index) + getsizeof(term) + getsizeof(doc_id) > self.BUFFER:
            self.save(os.path.join(self.path,
                                   f"index_{self.index_number}_file_{self.current_index}.txt"))
            self.current_index += 1

        self.index[term].append(doc_id)

    def get(self, term):
        return self.index.get(term, [])

    def save(self, path):
        self.index = sorted(self.index.items())
        with open(path, 'w') as f:
            for term, doc_ids in self.index.items():
                f.write(f"{term}:{doc_ids}\n")
        self.index = defaultdict(list)

    def load(self, path):
        with open(path, 'r') as f:
            for line in f:
                term, doc_ids = line.split(":", 1)
                self.index[term.strip()] = eval(doc_ids)

    def build():
        #build step
        data = pd.read_csv(self.file)
        data = data[data["language"].isin(["en", "es", "de"])]
        current_id = 0
        for index, row in data.iterrows():
            tokens = process_text(row["lyrics"], row["language"])
            for token in tokens:
                self.add(token, index)
        #merge step
        sorted_index=[]
        file_names = [f"index_{self.index_number}_file_{index}.txt" for index in range(self.current_index)]

        readers = [open(file, 'r') for file in file_names]
        for reader in readers:
            line = reader.readline()
            if line:
                term, doc_ids = line.split(":", 1)
                heapq.heappush(sorted_index, IndexEntry(term, eval(docs_ids)))


        
class IndexEntry:
    def __init__(self, term, doc_ids):
        self.term = term
        self.doc_ids=doc_ids

    def __str__(self):
        return f"{self.term}:{self.doc_ids}"

    def __lt__(self, other):
        return self.term < other.term

    def __gt__(self, other):
        return self.term < other.term
        
            

