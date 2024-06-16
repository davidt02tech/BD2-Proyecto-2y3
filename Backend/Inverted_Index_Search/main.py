from fastapi import FastAPI, HTTPException, Query
import asyncpg
from database import get_database_connection

app = FastAPI()

@app.get("/ginIndexSearch/")
async def search_songs(q: str = Query(..., description="Search query")):
    try:
        conn = await get_database_connection()
        
        # Execute full-text search query
        query = """
            SELECT track_name, track_artist, lyrics
            FROM spotify_table
            WHERE author_lyrics_tsvector @@ to_tsquery('english', $1)
        """
        result = await conn.fetch(query, q)
        
        await conn.close()
        
        return result
    
    except asyncpg.exceptions.PostgresError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")



@app.get("/customIndexSearch/")
async def search_songs(q: str = Query(..., description="Search query")):
    try:
        conn = await get_database_connection()
        
        # Execute full-text search query
        query = """
            SELECT track_name, track_artist, lyrics
            FROM spotify_table
            WHERE author_lyrics_tsvector @@ to_tsquery('english', $1)
        """
        result = await conn.fetch(query, q)
        
        await conn.close()
        
        return result
    
    except asyncpg.exceptions.PostgresError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
