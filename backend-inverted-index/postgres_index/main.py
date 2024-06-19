from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
from typing import Optional
import time
from postgres_index.database import get_database_connection
from custom_inverted_index.inverted_index import SPIMI

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
