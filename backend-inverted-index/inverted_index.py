from collections import defaultdict
from sys import getsizeof
import os

class Index:
    pass


class SPIMI(Index):
    BUFFER = 4096
    current_index = 0

    def __init__(self, path):
        self.index = defaultdict(list)
        self.path = path

    def add(self, term, doc_id):
        self.index[term].append(doc_id)

        if getsizeof(self.index) > self.BUFFER:
            self.save(os.path.join(self.path, f"index_{self.current_index}.bin"))
            self.current_index += 1

    def get(self, term):
        return self.index.get(term, [])

    def save(self, path):
        self.index = sorted(self.index)
        with open(path, 'w') as f:
            for term, doc_ids in self.index.items():
                f.write(f'{term}: {doc_ids}\n')
        self.index = defaultdict(list)

    def load(self, path):
        with open(path, 'r') as f:
            for line in f:
                term, doc_ids = line.split(':')
                self.index[term.strip()] = eval(doc_ids)

