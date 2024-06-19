from collections import defaultdict
from data_processing import process_text
import heapq
import pandas as pd
import os

def make_tuple(string):
    first, second = string.split(',', 1)
    first = first[1:]
    second = second[:-1]
    return first, int(second)


class Index:
    pass

class Bucket:
    BUCKET_SIZE = 4096
    id = 0
    def __init__(self, folder_path, postings=defaultdict(int), next_bucket=None):
        self.id = Bucket.id
        self.path = folder_path
        Bucket.id += 1
        self.postings = postings
        self.next_bucket = next_bucket
        self.first_bucket = self.id
        self.size = 0

    def serialize(self):
        return f"({dict.__repr__(self.postings)}, {self.next_bucket})"

    def get_path(self):
        return os.path.join(self.path, self.get_pointer())

    def get_pointer(self):
        return f"bucket_{self.first_bucket}.txt"

    def add_to_postings(self, doc_id):
        if doc_id not in self.postings.keys() and len(self.postings) + 1 > Bucket.BUCKET_SIZE:
            self.save_bucket()
            self.id = Bucket.id + 1
            Bucket.id += 1
            self.postings = defaultdict(int)
            self.next_bucket = None
        self.postings[doc_id] += 1
        self.size += 1

    def save_bucket(self):
        self.next_bucket = Bucket.id + 1
        with open(self.get_path(), "w") as f:
            f.write(self.serialize())

class IndexEntry:
    def __init__(self, term, bucket_pointer):
        self.term = term
        self.bucket_pointer = doc_ids

    def __str__(self):
        return f"{self.term}:{self.bucket_pointer}"

    def __lt__(self, other):
        return self.term < other.term

    def __gt__(self, other):
        return self.term < other.term



class SPIMI(Index):
    BLOCK_SIZE = 4096  # n of entries
    index_number = 0

    def get_block_path(self, current_index=None):
        if current_index is None:
            current_index = self.current_index
        return os.path.join(self.path, f"index_{self.index_number}_block_{current_index}.txt")

    def __init__(self, data_path, index_folder):
        self.path = index_folder
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.file = data_path
        self.current_index = 0
        self.index_number = SPIMI.index_number
        SPIMI.index_number += 1
        self.index = defaultdict(self._get_empty_bucket)

    def _get_empty_bucket(self):
        return Bucket(self.path)

    def add(self, term, doc_id):
        if len(self.index) + 1 > SPIMI.BLOCK_SIZE:
            self.save_block()
            self.index = defaultdict(self._get_empty_bucket)
            self.current_index += 1
        self.index[term].add_to_postings(doc_id)

    def get(self, term):
        return self.index.get(term, {})

    def save_block(self, sort=True):
        if sort:
            self.index = dict(sorted(self.index.items()))
        with open(self.get_block_path(), 'w', encoding="utf-8") as f:
            for term, bucket in self.index.items():
                f.write(f"({term},{bucket.size}):{bucket.get_pointer()}\n")

        self.index = defaultdict(self._get_empty_bucket)

    def load(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                term, (df, doc_ids) = line.split(":", 1)
                self.index[term.strip()] = eval(doc_ids)
    def load_bucket(self, bucker_pointer):
        with open(os.path.join(self.path, bucket_pointer),'r') as f:
            line = f.readline()
            postings, next = eval(line)
        return posting, next


    def build(self):
        build step
        data = pd.read_csv(self.file)
        data = data[data["language"].isin(["en", "es", "de"])]
        current_id = 0
        for index, row in data.iterrows():
            tokens = process_text(row["lyrics"] + " " + row["track_name"] + " " + row["track_artist"], row["language"])
            for token in tokens:
                self.add(token, index)
        # merge step
        self.save_block()
        sorted_index = []
        file_names = [self.get_block_path(current_index=i) for i in range(self.current_index + 1)]

        merged = dict()
        readers = [(i, open(file, 'r', encoding="utf-8")) for i, file in enumerate(file_names)]
        empty_readers = set()

        curr_reader = int()

        for i, reader in readers:
            line = reader.readline()
            term_df, bucket_pointer = line.split(":", 1)
            term, df = make_tuple(term_df)
            heapq.heappush(sorted_index, (term, (df, bucket_pointer, curr_reader)))


        merged_index = 0

        while len(empty_readers) < len(file_names):
            term, (df, bucket_pointer, curr_reader) = heapq.heappop(sorted_index)
            if len(merged) + 1 > self.BLOCK_SIZE:
                with open(os.path.join(self.path, f"index_{self.index_number}_merged_{merged_index}.txt"), 'w', encoding="utf-8") as f:
                    for term, bucket in merged:
                        f.write(f"({term},{df}):{bucket_pointer}\n")
                merged = dict()

            if term in merged:
                next = merged[term]
                while next is not None: 
                    temp = next
                    postings, next = self.load_bucket(next)
                with open(os.path.join(self.path, temp), "r") as f:
                    f.write(f"({postings},{bucket_pointer})")
            else:
                merged[term] = bucket_pointer

            pos, reader = readers[curr_reader]
            if pos in empty_readers:
                continue
            line = reader.readline()
            if not line:
                empty_readers.add(pos)
                reader.close()
                continue
            term_df, bucket_pointer = line.split(":", 1)
            term, df = make_tuple(term_df)
            heapq.heappush(sorted_index, (term, (df, bucket_pointer, curr_reader)))


        # delete unmerged indexes
        for i in range(self.current_index + 1):
            file = self.get_block_path(i)
            os.remove(file)

    def search_query_in_index(self, query):
        with open(os.path.join(self.path, f"merged_index_{self.index_number}.txt"), 'r', encoding="utf-8") as f:
            for line in f:
                term, doc_ids = line.split(":", 1)
                if term == query:
                    return eval(doc_ids)
        return set()

