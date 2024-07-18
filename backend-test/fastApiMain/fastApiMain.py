from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
from typing import Optional
import time
from backend_inverted_index.postgres_index.database import get_database_connection
from backend_inverted_index.custom_inverted_index.inverted_index import SPIMI
import pandas as pd
import numpy as np
from backend_multidimensional_index.rtree import RTree
from backend_multidimensional_index.faiss_index import FaissIndex
import os



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchSongsResponse(BaseModel):
    execution_time: float
    results: list


def read_feature_vectors(csv_file):
    df = pd.read_csv(csv_file,skiprows=1, header=None)
    #df = pd.read_csv(csv_file, skiprows=1, names=['track_id', 'features'])

    fv = {row[0]: np.array(row[1:]) for row in df.itertuples(index=False)}
    #fv = {row['track_id']: np.fromstring(row['features'].strip('[]'), sep=' ') for _, row in df.iterrows()}

    return fv


@app.get('/')
def hello_world():
    return{'Levanto'}

@app.get("/indexSearch")
async def search_songs(
    q: str = Query(..., description="Search query"),
    k: Optional[int] = Query(100, description="Number of rows returned by query, default is 100"),
    indexType: Optional[str] = Query("default", description="Type of index to use")
):
    start_time = time.time()
    serialized_result = []
    
    try:        
        if indexType == "default" or indexType == "POSTGRES":
            conn = await get_database_connection()

            query = """
                SELECT track_id, track_name, track_artist, lyrics
                FROM spotify_table
                WHERE author_lyrics_tsvector @@ to_tsquery('english', $1)
                LIMIT $2
            """
            result = await conn.fetch(query, q, k)

            await conn.close()

            serialized_result = [
                {
                    "track_id": row["track_id"], 
                    "track_name": row["track_name"], 
                    "track_artist": row["track_artist"],
                    "lyrics": row["lyrics"]
                }
                for row in result
            ]
        
        elif indexType == "SPIMI":
            index = SPIMI("custom_inverted_index/spotify_songs.csv","indexes/")
            results = index.search_query_in_index(q)
            raise HTTPException(status_code=501, detail="Not Implemented")
        
        else:
            raise HTTPException(status_code=400, detail="Invalid indexType")
        
        
        end_time = time.time()  # End timing
        execution_time = end_time - start_time
        
        return {
            "execution_time": execution_time,
            "results": serialized_result
        }
    
    except asyncpg.exceptions.PostgresError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")



@app.get("/multiDimensionalSearch")
async def search_songs_md(
    q: str = Query(..., description="Track id"),
    k: Optional[int] = Query(100, description="Number of rows returned by query, default is 100"),
    indexType: Optional[str] = Query("default", description="Type of index to use")
):
    start_time = time.time()
    serialized_result = []
    fv = read_feature_vectors('backend_multidimensional_index/song_features.csv')
    #print("FV: ")
    #print(fv)

    try:        
        if indexType == "RTREE":
        
            if q not in fv:
                raise HTTPException(status_code=400, detail="Song not found")
            
            query_point = fv[q]
            rtree = RTree(fv)
            results = rtree.knn_search(query_point, k)
    
            serialized_result = [
                {
                    "track_id": row[0]
                }
                for row in results
            ]
        
        elif indexType == "SECUENCIAL":
            raise HTTPException(status_code=501, detail="Not Implemented")

        elif indexType == "default" or indexType == "HIGHD":
            if q not in fv:
                raise HTTPException(status_code=400, detail="Song not found")
            
            vectors = np.array(list(fv.values()))
            track_ids = list(fv.keys())
            query_vector = fv[q]
            faiss_index = FaissIndex(nlist=30, nprobe=10)

            if os.path.exists('faiss_index.index'):
                os.remove('faiss_index.index')
                faiss_index.create_index(vectors)
                # faiss_index.get_index()
            else:
                faiss_index.create_index(vectors)

            
            results = faiss_index.knn_search(np.array([query_vector]), k, track_ids)

            serialized_result = [
                {
                    "track_id": row[0]
                }
                for row in results
            ]

            #raise HTTPException(status_code=501, detail="Not Implemented")
        else:
            raise HTTPException(status_code=400, detail="Invalid indexType")
        
        
        end_time = time.time()  # End timing
        execution_time = end_time - start_time
        
        return {
            "execution_time": execution_time,
            "results": serialized_result
        }
    
    except asyncpg.exceptions.PostgresError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
