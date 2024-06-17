from collections import defaultdict
from sys import getsizeof
from data_processing import process_text
import heapq
import pandas as pd
import os


class Index:
    pass


class SPIMI(Index):
    BUFFER = 65536
    index_number = 0

    def __init__(self, file_path, index_folder):
        self.index = defaultdict(set)
        self.path = index_folder
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.file = file_path
        self.current_index = 0
        self.index_number = SPIMI.index_number
        SPIMI.index_number += 1

    def add(self, term, doc_id):
        if getsizeof(self.index) + getsizeof(term) + getsizeof(doc_id) > self.BUFFER:
            self.save(os.path.join(self.path,
                                   f"index_{self.index_number}_file_{self.current_index}.txt"))
            self.current_index += 1

        self.index[term].add(doc_id)

    def get(self, term):
        return self.index.get(term, {})

    def save(self, path):
        self.index = dict(sorted(self.index.items()))
        with open(path, 'w', encoding="utf-8") as f:
            for term, doc_ids in self.index.items():
                f.write(f"{term}:{doc_ids}\n")
        self.index = defaultdict(set)

    def load(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                term, doc_ids = line.split(":", 1)
                self.index[term.strip()] = eval(doc_ids)

    def build(self):
        # build step
        data = pd.read_csv(self.file)
        data = data[data["language"].isin(["en", "es", "de"])]
        current_id = 0
        for index, row in data.iterrows():
            tokens = process_text(row["lyrics"], row["language"])
            for token in tokens:
                self.add(token, index)
        # merge step
        self.save(os.path.join(self.path,
                                   f"index_{self.index_number}_file_{self.current_index}.txt"))
        self.current_index += 1
        sorted_index = []
        merged_index = defaultdict(set)
        file_names = [os.path.join(self.path, f"index_{self.index_number}_file_{index}.txt")
                      for index in range(self.current_index)]

        readers = [open(file, 'r', encoding="utf-8") for file in file_names]

        while readers:
            for i, reader in enumerate(readers):
                line = reader.readline()
                if not line:
                    readers.pop(i)
                    continue
                term, doc_ids = line.split(":", 1)
                heapq.heappush(sorted_index, IndexEntry(term, doc_ids))
        for entry in sorted_index:
            merged_index[entry.term].add(entry.doc_ids)

        # save merged index and delete blocks
        for reader in readers:
            reader.close()
        for file in file_names:
            os.remove(file)
        with open(os.path.join(self.path, f"merged_index_{self.index_number}.txt"), encoding="utf-8") as f:
            for term, doc_ids in merged_index.items():
                f.write(f"{term}:{doc_ids}\n")


class IndexEntry:
    def __init__(self, term, doc_ids):
        self.term = term
        self.doc_ids = doc_ids

    def __str__(self):
        return f"{self.term}:{self.doc_ids}"

    def __lt__(self, other):
        return self.term < other.term

    def __gt__(self, other):
        return self.term < other.term
