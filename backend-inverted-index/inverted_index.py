import heapq
import os
from collections import defaultdict
import math

import pandas as pd

from data_processing import process_text


def make_tuple(string):
    first, second = string.split(",", 1)
    first = first[1:]
    second = second[:-1]
    return first, int(second)


class Bucket:
    BUCKET_SIZE = 4096
    id = 0

    def __init__(self, folder_path, next_bucket=None):
        self.id = Bucket.id
        self.path = folder_path
        Bucket.id += 1
        self.postings = defaultdict(int)
        self.next_bucket = next_bucket
        self.first_bucket = self.id
        self.size = 0

    def serialize(self):
        if self.next_bucket is None:
            return f"({dict.__repr__(self.postings)}, None)"
        else:
            return f"({dict.__repr__(self.postings)}, '{self.next_bucket}')"

    def get_path(self):
        return os.path.join(self.path, self.get_pointer())

    def get_pointer(self):
        return f"bucket_{self.first_bucket}.txt"

    def add_to_postings(self, doc_id):
        if (
                doc_id not in self.postings.keys()
                and len(self.postings) + 1 > Bucket.BUCKET_SIZE
        ):
            self.save_bucket()
            self.id = Bucket.id + 1
            Bucket.id += 1
            self.postings = defaultdict(int)
            self.next_bucket = None
        self.postings[doc_id] += 1
        self.size += 1

    def save_bucket(self, concatenate=True):
        if concatenate:
            self.next_bucket = Bucket.id + 1
        with open(self.get_path(), "w") as f:
            f.write(self.serialize())


class SPIMI:
    BLOCK_SIZE = 4096  # n of entries
    index_number = 0

    def get_block_path(self, current_index=None):
        if current_index is None:
            current_index = self.current_index
        return os.path.join(
            self.path, f"index_{self.index_number}_block_{current_index}.txt"
        )

    def __init__(self, data_path, index_folder):
        self.path = index_folder
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.file = data_path
        self.current_index = 0
        self.index_number = SPIMI.index_number
        SPIMI.index_number += 1
        self.index = defaultdict(self._get_empty_bucket)
        self.merged_index = 0

    def _get_empty_bucket(self):
        return Bucket(self.path)

    def add(self, term, doc_id):
        if len(self.index) + 1 > SPIMI.BLOCK_SIZE:
            self.save_block()
            self.save_buckets_in_block()
            self.index = defaultdict(self._get_empty_bucket)
            self.current_index += 1
        self.index[term].add_to_postings(doc_id)

    def get(self, term):
        return self.index.get(term, {})

    def save_buckets_in_block(self):
        for term, bucket in self.index.items():
            bucket.save_bucket(concatenate=False)

    def save_block(self, sort=True):
        if sort:
            self.index = dict(sorted(self.index.items()))
        with open(self.get_block_path(), "w", encoding="utf-8") as f:
            for term, bucket in self.index.items():
                f.write(f"({term},{bucket.size}):{bucket.get_pointer()}\n")

    def load_bucket(self, bucket_pointer):
        bucket_pointer = bucket_pointer.rstrip()
        with open(os.path.join(self.path, bucket_pointer), "r") as f:
            line = f.readline()
            postings, next = eval(line)
        return postings, next

    def build(self):
        # build step
        data = pd.read_csv(self.file)
        data = data[data["language"].isin(["en", "es", "de"])]
        for _, row in data.iterrows():
            tokens = process_text(
                row["lyrics"] + " " + row["track_name"] + " " + row["track_artist"],
                row["language"],
            )
            for token in tokens:
                self.add(token, row["track_id"])
        # merge step
        self.save_block()
        self.save_buckets_in_block()
        sorted_index = []
        file_names = [
            self.get_block_path(current_index=i) for i in range(self.current_index + 1)
        ]

        merged = dict()
        readers = [
            (i, open(file, "r", encoding="utf-8")) for i, file in enumerate(file_names)
        ]
        empty_readers = set()

        curr_reader = 0

        for i, reader in readers:
            line = reader.readline()
            term_df, bucket_pointer = line.rstrip().split(":", 1)
            term, df = make_tuple(term_df)
            heapq.heappush(sorted_index, (term, (df, bucket_pointer, i)))

        while len(empty_readers) < len(file_names):
            term, (df, bucket_pointer, curr_reader) = heapq.heappop(sorted_index)
            if len(merged) > self.BLOCK_SIZE - 1:
                with open(
                        os.path.join(self.path, f"index_{self.index_number}_merged_{self.merged_index}.txt", ),
                        "w",
                        encoding="utf-8",
                ) as f:
                    for term, df_bucket in merged.items():
                        f.write(f"({term},{df_bucket[0]}):{df_bucket[1]}\n")
                merged = dict()
                self.merged_index = + 1

            if term in merged:
                lhs_postings, lhs_next = self.load_bucket(merged[term][1])
                rhs_postings, rhs_next = self.load_bucket(bucket_pointer)
                merged[term][0] += df
                merge_postings = True
                while lhs_next is not None:
                    lhs_postings, lhs_next = self.load_bucket(lhs_next)

                while merge_postings:
                    if len(lhs_postings) + len(rhs_postings) < Bucket.BUCKET_SIZE:
                        for doc_id, tf in rhs_postings.items():
                            if doc_id in lhs_postings:
                                lhs_postings[doc_id] += tf
                            else:
                                lhs_postings[doc_id] = tf
                        os.remove(os.path.join(self.path, bucket_pointer))
                        if rhs_next is None:
                            merge_postings = False
                        else:
                            rhs_postings, rhs_next = self.load_bucket(rhs_next)
                            bucket_pointer = rhs_next
                    else:
                        lhs_next = bucket_pointer
                        merge_postings = False
                with open(os.path.join(self.path, merged[term][1]), "w") as f:
                    if lhs_next is not None:
                        f.write(f"({lhs_postings},'{lhs_next}')")
                    else:
                        f.write(f"({lhs_postings},None)")
            else:
                merged[term] = [df, bucket_pointer]

            pos, reader = readers[curr_reader]
            if pos in empty_readers:
                continue
            line = reader.readline()
            if not line:
                empty_readers.add(pos)
                reader.close()
                continue
            term_df, bucket_pointer = line.rstrip().split(":", 1)
            term, df = make_tuple(term_df)
            heapq.heappush(sorted_index, (term, (df, bucket_pointer, curr_reader)))

        def search(query, k=10):
            """
            Searches the SPIMI index and returns the top k most relevant documents.

            Args:
                query (str): The natural language query.
                index_path (str): Path to the merged SPIMI index file.
                k (int, optional): The number of top results to return (default: 10).

            Returns:
                list: A list of tuples (doc_id, score), sorted by relevance in descending order.
            """

            # Process the query
            query_terms = process_text(query, language="en")  # Use the same processing as in indexing

            # Load the merged index
            index = {}

            for i in range(self.merged_index):
                with open(os.path.join(self.path, f"index_{self.index_number}_merged_{i}")) as f:
                    for line in f:
                        term, (df, bucket) = line.rstrip().split(":", 1)
                        index[term] = (int(df), bucket)

            # Calculate TF-IDF scores
            scores = defaultdict(float)
            for term in query_terms:
                if term in index:
                    next = 0
                    while next is not None:
                        postings, next = self.load_bucket(index[term])
                        idf = math.log(18, 454 / df)
                        for doc_id, tf in postings.items():
                            scores[doc_id] += tf * idf

            # Get top k results
            top_k = heapq.nlargest(k, scores.items(), key=lambda x: x[1])

            return top_k
