from collections import defaultdict, Counter
from sys import getsizeof
from data_processing import process_text
import heapq
import json
import pandas as pd
import os
import matplotlib.pyplot as plt
import math
import hashlib
import pickle


class SPIMMI:
    def __init__(self, file, language='english', block_size=1000, index_dir='index'):
        self.file = file
        self.language = language
        self.block_size = block_size
        self.index_dir = index_dir
        self.term_doc_freq = defaultdict(list)
        self.doc_lengths = {}
        self.doc_count = 0
        self.track_ids = {}
        
        # Crear el directorio del índice si no existe
        if not os.path.exists(index_dir):
            os.makedirs(index_dir)
        
    def add_document(self, doc_id, text, language, track_id):
        tokens = process_text(text, language)
        term_freq = Counter(tokens)
        norm = 0
        
        for term, freq in term_freq.items():
            tf = 1 + math.log10(freq)
            self.term_doc_freq[term].append((doc_id, tf))
            norm += tf ** 2
        
        self.doc_lengths[doc_id] = math.sqrt(norm)
        self.track_ids[doc_id] = track_id
        self.doc_count += 1
        
        # Si el número de documentos procesados en memoria supera el tamaño del bloque, escribir en disco
        if self.doc_count % self.block_size == 0:
            self.write_block_to_disk()
            self.term_doc_freq.clear()
    
    def write_block_to_disk(self):
        block_id = self.doc_count // self.block_size
        block_path = os.path.join(self.index_dir, f'block_{block_id}.txt')
        
        with open(block_path, 'w') as f:
            json.dump(self.term_doc_freq, f)
    
    def merge_blocks(self):
        merged_index = defaultdict(list)
        
        for block_file in os.listdir(self.index_dir):
            block_path = os.path.join(self.index_dir, block_file)
            with open(block_path, 'r') as f:
                block_index = json.load(f)
                for term, postings in block_index.items():
                    merged_index[term].extend(postings)
        
        # Guardar el índice fusionado
        index_path = os.path.join(self.index_dir, 'merged_index.txt')
        with open(index_path, 'w') as f:
            json.dump(merged_index, f)
    
    def calculate_idf(self, term, doc_count, doc_freq):
        return math.log10(doc_count / doc_freq)
    
    def load_index(self):
        index_path = os.path.join(self.index_dir, 'merged_index.txt')
        with open(index_path, 'r') as f:
            return json.load(f)
    
    def query(self, query_text, top_k=10):
        tokens = process_text(query_text, self.language)
        index = self.load_index()
        
        scores = defaultdict(float)
        query_term_freq = Counter(tokens)
        query_norm = 0
        
        for term, freq in query_term_freq.items():
            if term in index:
                tf = 1 + math.log10(freq)
                idf = self.calculate_idf(term, self.doc_count, len(index[term]))
                query_weight = tf * idf
                query_norm += query_weight ** 2
                
                for doc_id, doc_tf in index[term]:
                    doc_weight = doc_tf * idf
                    scores[doc_id] += query_weight * doc_weight
        
        query_norm = math.sqrt(query_norm)
        for doc_id in scores:
            scores[doc_id] /= (self.doc_lengths[doc_id] * query_norm)
        
        ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [(self.track_ids[doc_id], score) for doc_id, score in ranked_docs[:top_k]]

    def build(self):
        data = pd.read_csv(self.file)
        data['text'] = data.apply(lambda row: f"{row['track_id']} {row['track_name']} {row['lyrics']}" if pd.notna(row['lyrics']) else f"{row['track_id']} {row['track_name']}", axis=1)
        self.doc_count = len(data)
        
        for index, row in data.iterrows():
            text = row['text']
            language = row.get('language', 'en')
            track_id = row['track_id']
            if pd.notna(text):
                self.add_document(index, text, language, track_id)
        
        if self.term_doc_freq:
            self.write_block_to_disk()
        
        self.merge_blocks()

    def visualize_query_results(self, query_text, top_k):
        results = self.query(query_text, top_k=top_k)
        
        if not results:
            print("No results found for the query.")
            return
        
        # Create a DataFrame from the results
        results_df = pd.DataFrame(results, columns=['Document ID', 'Relevance Score'])
        
        # Display the results in a tabular format
        print("Top {} results for the query '{}':".format(top_k, query_text))
        print(results_df)
        
        # Plot the results
        plt.figure(figsize=(10, 6))
        plt.bar(results_df['Document ID'], results_df['Relevance Score'], color='blue')
        plt.xlabel('Document ID')
        plt.ylabel('Relevance Score')
        plt.title('Top {} Results for Query: "{}"'.format(top_k, query_text))
        plt.xticks(rotation=45)
        #guardar la imagen
        plt.savefig('query_results.png')

# Código para probar la 
file_path = "spotify_songs.csv"
index_folder = "indexes/"
spimmi = SPIMMI(file='spotify_songs.csv', language='english', block_size=1000, index_dir='index')
spimmi.build()
# Realizar una consulta
query = "If you get to hear"
# top_docs = spimmi.query(query, top_k=5)
# print(top_docs)
spimmi.visualize_query_results(query, top_k=5)

